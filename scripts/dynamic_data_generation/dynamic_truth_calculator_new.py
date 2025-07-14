#!/usr/bin/env python3
"""
Dynamic Truth Calculator for New Queries
Calculates truth values dynamically from CSV data for new query types
"""

import pandas as pd
import numpy as np
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Union
import json

class DynamicTruthCalculatorNew:
    """Calculates truth values dynamically from CSV data for new query types"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.data = {}
        self.load_data()
    
    def load_data(self):
        """Load all CSV data files"""
        print("📊 Loading CSV data...")
        
        # Expected tokens based on the updated data generator
        expected_tokens = ['eth', 'sol', 'tao', 'btc', 'ada', 'avax', 'matic', 'uni', 'doge', 'bnb', 'dot']
        
        for token in expected_tokens:
            filename = f"{token}_daily.csv"
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath)
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    
                    # Calculate daily returns
                    df['daily_return'] = df['close'].pct_change() * 100
                    
                    symbol = token.upper()
                    self.data[symbol] = df
                    print(f"✅ Loaded {symbol}: {len(df)} days")
                    
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
            else:
                print(f"⚠️  {filename} not found")
    
    def calculate_current_price(self, token: str) -> Union[float, None]:
        """Calculate current price for a token"""
        if token not in self.data:
            return None
        return float(self.data[token]['close'].iloc[-1])
    
    def calculate_24h_change(self, token: str) -> Union[float, None]:
        """Calculate 24-hour price change"""
        if token not in self.data or len(self.data[token]) < 2:
            return None
        
        df = self.data[token]
        current = df['close'].iloc[-1]
        previous = df['close'].iloc[-2]
        return float(((current - previous) / previous) * 100)
    
    def calculate_30d_change(self, token: str) -> Union[float, None]:
        """Calculate 30-day price change"""
        if token not in self.data or len(self.data[token]) < 30:
            return None
        
        df = self.data[token]
        current = df['close'].iloc[-1]
        thirty_days_ago = df['close'].iloc[-30]
        return float(((current - thirty_days_ago) / thirty_days_ago) * 100)
    
    def calculate_average_price(self, token: str) -> Union[float, None]:
        """Calculate average price over the dataset period"""
        if token not in self.data:
            return None
        return float(self.data[token]['close'].mean())
    
    def calculate_trend(self, token: str) -> Union[str, None]:
        """Calculate if token is trending up or down"""
        if token not in self.data or len(self.data[token]) < 7:
            return None
        
        df = self.data[token]
        week_avg = df['close'].tail(7).mean()
        current = df['close'].iloc[-1]
        return "up" if current > week_avg else "down"
    
    def calculate_green_days_in_month(self, token: str, month: int) -> Union[int, None]:
        """Calculate number of days in a month where close > open"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        # Filter for specific month
        month_data = df[df.index.month == month]
        
        if len(month_data) == 0:
            return None
        
        green_days = (month_data['close'] > month_data['open']).sum()
        return int(green_days)
    
    def calculate_volatility_comparison(self, token1: str, token2: str) -> Union[str, None]:
        """Compare volatility between two tokens"""
        if token1 not in self.data or token2 not in self.data:
            return None
        
        df1 = self.data[token1]
        df2 = self.data[token2]
        
        # Calculate standard deviation of daily returns
        vol1 = df1['daily_return'].std()
        vol2 = df2['daily_return'].std()
        
        if vol1 > vol2:
            return token1
        elif vol2 > vol1:
            return token2
        else:
            return "Equal"
    
    def calculate_performance_comparison(self, token1: str, token2: str) -> Union[str, None]:
        """Compare performance between two tokens"""
        if token1 not in self.data or token2 not in self.data:
            return None
        
        df1 = self.data[token1]
        df2 = self.data[token2]
        
        # Calculate average daily returns
        avg_return1 = df1['daily_return'].mean()
        avg_return2 = df2['daily_return'].mean()
        
        if avg_return1 > avg_return2:
            return token1
        elif avg_return2 > avg_return1:
            return token2
        else:
            return "Equal"
    
    def calculate_30d_performance_comparison(self, token1: str, token2: str) -> Union[str, None]:
        """Compare 30-day performance between two tokens"""
        change1 = self.calculate_30d_change(token1)
        change2 = self.calculate_30d_change(token2)
        
        if change1 is None or change2 is None:
            return None
        
        if change1 > change2:
            return token1
        elif change2 > change1:
            return token2
        else:
            return "Equal"
    
    def calculate_market_cap_estimate(self, token: str) -> Union[float, None]:
        """Estimate market cap using price and volume"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        avg_price = df['close'].mean()
        avg_volume = df['volume'].mean()
        
        # Rough estimate: price * volume / 1e6 for millions
        return float(avg_price * avg_volume / 1e6)
    
    def calculate_volume(self, token: str) -> Union[float, None]:
        """Calculate current volume for a token"""
        if token not in self.data:
            return None
        return float(self.data[token]['volume'].iloc[-1])
    
    def calculate_truth_for_query(self, query: Dict) -> Any:
        """Calculate truth value for a specific query"""
        query_id = query['id']
        category = query['category']
        
        # Single token easy queries
        if category == 'single_token_easy':
            if 'eth_price_current' in query_id:
                return self.calculate_current_price('ETH')
            elif 'btc_price' in query_id:
                return self.calculate_current_price('BTC')
            elif 'tao_24h_change' in query_id:
                return self.calculate_24h_change('TAO')
            elif 'tao_up_down_today' in query_id:
                change = self.calculate_24h_change('TAO')
                if change is not None:
                    return "up" if change > 0 else "down"
                return None
            elif 'ada_ath' in query_id:
                # For ATH, we'll use the highest price in our dataset
                if 'ADA' in self.data:
                    return float(self.data['ADA']['close'].max())
                return None
            elif 'avalanche_basic_stats' in query_id:
                # Return average price for basic stats
                return self.calculate_average_price('AVAX')
            elif 'doge_market_cap' in query_id:
                return self.calculate_market_cap_estimate('DOGE')
            elif 'bnb_trading_volume' in query_id:
                return self.calculate_volume('BNB')
            elif 'cardano_eur_price' in query_id:
                # We have USD prices, but for EUR we'd need conversion
                # For now, return USD price as approximation
                return self.calculate_current_price('ADA')
        
        # Single token medium queries
        elif category == 'single_token_medium':
            if 'sol_buy_timing' in query_id:
                return self.calculate_trend('SOL')
            elif 'btc_avg_price_month' in query_id:
                return self.calculate_average_price('BTC')
            elif 'matic_trending' in query_id:
                return self.calculate_trend('MATIC')
            elif 'uniswap_liquidity' in query_id:
                # Use volume as proxy for liquidity
                return self.calculate_volume('UNI')
            elif 'tao_avg_price_month' in query_id:
                return self.calculate_average_price('TAO')
        
        # Single token hard queries
        elif category == 'single_token_hard':
            if 'eth_higher_than_opened_june' in query_id:
                return self.calculate_green_days_in_month('ETH', 6)  # June = 6
            elif 'matic_rsi_now' in query_id:
                # Calculate RSI for MATIC
                if 'MATIC' in self.data:
                    df = self.data['MATIC']
                    if len(df) >= 14:
                        delta = df['close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        return float(rsi.iloc[-1])
                return None
            elif 'dot_macd_crossover' in query_id:
                # Calculate MACD for DOT
                if 'DOT' in self.data:
                    df = self.data['DOT']
                    if len(df) >= 26:
                        ema12 = df['close'].ewm(span=12).mean()
                        ema26 = df['close'].ewm(span=26).mean()
                        macd = ema12 - ema26
                        signal = macd.ewm(span=9).mean()
                        # Return current MACD value
                        return float(macd.iloc[-1])
                return None
        
        # Multi-token queries
        elif category == 'multi_token_medium':
            if 'eth_vs_sol_investment' in query_id:
                return self.calculate_30d_performance_comparison('ETH', 'SOL')
            elif 'btc_eth_prices_today' in query_id:
                # Return a comparison string
                btc_price = self.calculate_current_price('BTC')
                eth_price = self.calculate_current_price('ETH')
                if btc_price and eth_price:
                    return f"BTC: ${btc_price:.2f}, ETH: ${eth_price:.2f}"
                return None
        
        # Multi-token hard queries
        elif category == 'multi_token_hard':
            if 'eth_vs_sol_avg_daily_change_year' in query_id:
                return self.calculate_performance_comparison('ETH', 'SOL')
            elif 'tao_eth_30d_volatility' in query_id:
                return self.calculate_volatility_comparison('TAO', 'ETH')
        
        # Trick questions - these should remain null
        elif category == 'trick_question':
            return None
        
        # Token research queries - these are subjective
        elif category == 'token_research':
            return None
        
        # Default: return None if we can't calculate
        return None
    
    def to_native(self, val):
        """Convert numpy types to native Python types"""
        if isinstance(val, (np.generic,)):
            return val.item()
        if isinstance(val, list):
            return [self.to_native(x) for x in val]
        if isinstance(val, dict):
            return {k: self.to_native(v) for k, v in val.items()}
        return val

    def update_queries_with_dynamic_truth(self, queries_file: str = 'data/queries_new.yaml'):
        """Update queries with dynamically calculated truth values"""
        print("🔄 Updating new queries with dynamic truth values...")
        
        # Load queries
        with open(queries_file, 'r') as f:
            queries_data = yaml.safe_load(f)
        
        updated_count = 0
        
        for query in queries_data['queries']:
            dynamic_truth = self.calculate_truth_for_query(query)
            
            if dynamic_truth is not None:
                old_truth = query['truth']
                # Convert to native Python types
                query['truth'] = self.to_native(dynamic_truth)
                
                updated_count += 1
                
                print(f"✅ Updated {query['id']}: {old_truth} → {query['truth']}")
            else:
                print(f"⚠️  Could not calculate truth for {query['id']}")
        
        # Save updated queries
        output_file = queries_file.replace('.yaml', '_dynamic.yaml')
        with open(output_file, 'w') as f:
            yaml.dump(queries_data, f, default_flow_style=False, indent=2)
        
        print(f"\n✅ Updated {updated_count} queries with dynamic truth values")
        print(f"💾 Saved to: {output_file}")
        return updated_count

def main():
    """Main function"""
    calculator = DynamicTruthCalculatorNew()
    
    # Update queries with dynamic truth
    updated_count = calculator.update_queries_with_dynamic_truth('data/queries_new.yaml')
    
    print(f"\n🎉 Dynamic truth calculation completed!")
    print(f"Updated {updated_count} queries")

if __name__ == "__main__":
    main() 