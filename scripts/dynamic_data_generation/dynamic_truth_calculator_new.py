#!/usr/bin/env python3
"""
Dynamic Truth Calculator (NEW)
Wraps the original DynamicTruthCalculator but labels subjective / trick / research queries as "human".
"""

from dynamic_truth_calculator import DynamicTruthCalculator
import yaml
import numpy as np
from typing import Any, Dict
import re


class DynamicTruthCalculatorNew(DynamicTruthCalculator):
    """Extends DynamicTruthCalculator with human-label logic"""

    def to_native(self, val):
        """Convert numpy and pandas types to native Python types"""
        import pandas as pd
        if isinstance(val, (np.generic,)):
            return val.item()
        if isinstance(val, np.ndarray):
            return val.tolist()
        if 'pandas' in str(type(val)):
            # For pandas Series or DataFrame, convert to dict or list
            if hasattr(val, 'to_dict'):
                return val.to_dict()
            if hasattr(val, 'tolist'):
                return val.tolist()
        if isinstance(val, dict):
            return {k: self.to_native(v) for k, v in val.items()}
        if isinstance(val, list):
            return [self.to_native(x) for x in val]
        return val

    def calculate_truth_for_query(self, query: Dict) -> Any:
        """Calculate truth value for a specific query with improved ID matching"""
        query_id = query['id']
        category = query['category']
        
        # Handle basic price queries
        if query_id in ['eth_price_current', 'btc_price', 'pepe_price']:
            token = query_id.split('_')[0].upper()
            return self.calculate_basic_price(token, 'current_price')
        
        # Handle 24h change queries
        elif query_id == 'tao_24h_change':
            if 'TAO' in self.data:
                df = self.data['TAO']
                if len(df) >= 2:
                    yesterday_close = df['close'].iloc[-2]
                    today_close = df['close'].iloc[-1]
                    change = ((today_close - yesterday_close) / yesterday_close) * 100
                    return round(change, 2)
        
        # Handle average price queries
        elif query_id in ['btc_avg_price_month', 'tao_avg_price_month']:
            token = query_id.split('_')[0].upper()
            if token in self.data:
                df = self.data[token]
                avg_price = df['close'].mean()
                return round(avg_price, 2)
        
        # Handle ATH queries
        elif query_id == 'ada_ath':
            if 'ADA' in self.data:
                ath = self.data['ADA']['high'].max()
                return round(ath, 2)
        
        # Handle green days queries
        elif query_id == 'eth_higher_than_opened_june':
            if 'ETH' in self.data:
                df = self.data['ETH']
                # Filter for June (assuming data includes June)
                june_data = df[df.index.month == 6]
                if len(june_data) > 0:
                    green_days = (june_data['close'] > june_data['open']).sum()
                    return int(green_days)
        
        elif query_id == 'xrp_green_days_may_2024':
            if 'XRP' in self.data:
                df = self.data['XRP']
                # Filter for May 2024
                may_2024_data = df[(df.index.month == 5) & (df.index.year == 2024)]
                if len(may_2024_data) > 0:
                    green_days = (may_2024_data['close'] > may_2024_data['open']).sum()
                    return int(green_days)
        
        # Handle specific date queries
        elif query_id in ['eth_close_14_06_2025', 'eth_open_15_06_2025', 'sol_close_16_06_2025', 
                         'sol_open_17_06_2025', 'tao_close_18_06_2025']:
            parts = query_id.split('_')
            token = parts[0].upper()
            price_type = parts[1]  # 'close' or 'open'
            day = int(parts[2])
            month = int(parts[3])
            year = int(parts[4])
            
            if token in self.data:
                df = self.data[token]
                target_date = f"{year}-{month:02d}-{day:02d}"
                try:
                    if price_type == 'close':
                        price = df.loc[target_date, 'close']
                    else:
                        price = df.loc[target_date, 'open']
                    return round(price, 2)
                except KeyError:
                    return None
        
        # Handle volume queries
        elif query_id in ['eth_volume_17_06_2025', 'sol_volume_18_06_2025', 'tao_volume_20_06_2025']:
            parts = query_id.split('_')
            token = parts[0].upper()
            day = int(parts[2])
            month = int(parts[3])
            year = int(parts[4])
            
            if token in self.data:
                df = self.data[token]
                target_date = f"{year}-{month:02d}-{day:02d}"
                try:
                    volume = df.loc[target_date, 'volume']
                    return round(volume, 2)
                except KeyError:
                    return None
        
        # Handle extreme value queries
        elif query_id in ['eth_highest_10_14_06_2025', 'sol_lowest_15_19_06_2025', 'tao_peak_19_06_2025']:
            # Use regex to extract token, value_type, start_day, end_day, month, year
            m = re.match(r"(\w+)_(highest|lowest|peak)_(\d+)(?:_(\d+))?_(\d+)_?(\d+)?", query_id)
            if not m:
                return None
            token = m.group(1).upper()
            value_type = m.group(2)
            start_day = int(m.group(3))
            end_day = int(m.group(4)) if m.group(4) else start_day
            month = int(m.group(5))
            year = int(m.group(6)) if m.group(6) else 2025  # fallback year
            if token in self.data:
                df = self.data[token]
                try:
                    start_date = f"{year}-{month:02d}-{start_day:02d}"
                    end_date = f"{year}-{month:02d}-{end_day:02d}"
                    period_data = df.loc[start_date:end_date]
                    if value_type == 'highest' or value_type == 'peak':
                        value = period_data['high'].max()
                    elif value_type == 'lowest':
                        value = period_data['low'].min()
                    else:
                        return None
                    return round(value, 2)
                except Exception:
                    return None
        
        # Handle ranking queries
        elif query_id == 'rank_tokens_30d_return':
            returns = {}
            for token in self.data:
                df = self.data[token]
                if len(df) >= 30:
                    start_price = df['close'].iloc[-30]
                    end_price = df['close'].iloc[-1]
                    returns[token] = ((end_price - start_price) / start_price) * 100
            
            sorted_tokens = sorted(returns.items(), key=lambda x: x[1], reverse=True)
            return [token for token, _ in sorted_tokens]
        
        # Handle correlation queries
        elif query_id == 'grt_rtl_correlation':
            if 'GRT' in self.data and 'RTL' in self.data:
                grt_df = self.data['GRT']
                rtl_df = self.data['RTL']
                
                # Align the data by date
                common_dates = grt_df.index.intersection(rtl_df.index)
                if len(common_dates) > 0:
                    grt_returns = grt_df.loc[common_dates, 'close'].pct_change()
                    rtl_returns = rtl_df.loc[common_dates, 'close'].pct_change()
                    
                    # Calculate correlation
                    correlation = grt_returns.corr(rtl_returns)
                    return round(correlation, 4)
        
        # Handle total return queries
        elif query_id == 'op_total_return_june_2025':
            if 'OP' in self.data:
                df = self.data['OP']
                june_2025_data = df[(df.index.month == 6) & (df.index.year == 2025)]
                if len(june_2025_data) > 0:
                    start_price = june_2025_data['close'].iloc[0]
                    end_price = june_2025_data['close'].iloc[-1]
                    total_return = ((end_price - start_price) / start_price) * 100
                    return round(total_return, 2)
        
        # Handle up/down today queries
        elif query_id == 'tao_up_down_today':
            if 'TAO' in self.data:
                df = self.data['TAO']
                if len(df) >= 2:
                    yesterday_close = df['close'].iloc[-2]
                    today_close = df['close'].iloc[-1]
                    if today_close > yesterday_close:
                        return "up"
                    elif today_close < yesterday_close:
                        return "down"
                    else:
                        return "unchanged"
        
        # Handle multi-token comparison queries
        elif query_id in ['btc_eth_prices_today', 'doge_vs_shib', 'tao_vs_sol_volume_today']:
            if query_id == 'btc_eth_prices_today':
                tokens = ['BTC', 'ETH']
            elif query_id == 'doge_vs_shib':
                tokens = ['DOGE', 'SHIB']
            elif query_id == 'tao_vs_sol_volume_today':
                tokens = ['TAO', 'SOL']
            
            prices = {}
            for token in tokens:
                if token in self.data:
                    prices[token] = self.data[token]['close'].iloc[-1]
            
            if len(prices) == len(tokens):
                return prices
        
        # Handle biggest gains queries
        elif query_id == 'biggest_gains_today_btc_eth_sol':
            tokens = ['BTC', 'ETH', 'SOL']
            gains = {}
            
            for token in tokens:
                if token in self.data:
                    df = self.data[token]
                    if len(df) >= 2:
                        yesterday_close = df['close'].iloc[-2]
                        today_close = df['close'].iloc[-1]
                        gain = ((today_close - yesterday_close) / yesterday_close) * 100
                        gains[token] = round(gain, 2)
            
            if gains:
                # Return the token with biggest gain
                best_token = max(gains.items(), key=lambda x: x[1])
                return f"{best_token[0]}: {best_token[1]}%"
        
        # For queries we can't calculate, return None
        return None

    def update_queries_with_dynamic_truth(self, queries_file: str = 'data/queries.yaml') -> int:
        """Calculate / label truths and write output in place to queries.yaml"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries_data = yaml.safe_load(f)

        updated = 0
        for q in queries_data['queries']:
            category = q.get('category')
            truth_val: Any = None

            if category in ('token_research', 'trick_question'):
                # subjective / trick → human
                truth_val = 'human'
            else:
                truth_val = self.calculate_truth_for_query(q)
                # if still None after calc for data-driven types, leave as null
                if truth_val is None and category.startswith('multi_token'):
                    # some multi-token comparisons we cannot resolve → human
                    truth_val = 'human'

            if truth_val is not None:
                q['truth'] = self.to_native(truth_val)
                updated += 1

        # Always write in place to queries.yaml
        with open(queries_file, 'w', encoding='utf-8') as f:
            yaml.dump(queries_data, f, default_flow_style=False, indent=2, sort_keys=False)

        print(f"💾 Saved updated queries to {queries_file} ({updated} updated)")
        return updated


def main():
    calc = DynamicTruthCalculatorNew(data_dir='../../data')
    calc.update_queries_with_dynamic_truth('../../data/queries.yaml')


if __name__ == '__main__':
    main() 