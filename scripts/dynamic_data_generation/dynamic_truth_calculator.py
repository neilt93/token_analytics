#!/usr/bin/env python3
"""
Dynamic Truth Calculator
Calculates truth values dynamically from CSV data
"""

import pandas as pd
import numpy as np
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Union
import json

class DynamicTruthCalculator:
    """Calculates truth values dynamically from CSV data"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.data = {}
        self.load_data()
    
    def load_data(self):
        """Load all CSV data files"""
        print("📊 Loading CSV data...")
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('_daily.csv'):
                symbol = filename.split('_')[0].upper()
                filepath = os.path.join(self.data_dir, filename)
                
                try:
                    df = pd.read_csv(filepath)
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    
                    # Calculate daily returns
                    df['daily_return'] = df['close'].pct_change() * 100
                    
                    self.data[symbol] = df
                    print(f"✅ Loaded {symbol}: {len(df)} days")
                    
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
    
    def calculate_basic_price(self, token: str, metric: str) -> Union[float, str]:
        """Calculate basic price metrics"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        
        if metric == 'current_price':
            return float(df['close'].iloc[-1])
        elif metric == 'highest_price':
            return float(df['high'].max())
        elif metric == 'lowest_price':
            return float(df['low'].min())
        elif metric == 'total_return':
            start_price = df['close'].iloc[0]
            end_price = df['close'].iloc[-1]
            return ((end_price - start_price) / start_price) * 100
        
        return None
    
    def calculate_green_days(self, token: str) -> int:
        """Calculate number of green days (close > open)"""
        if token not in self.data:
            return 0
        
        df = self.data[token]
        green_days = (df['close'] > df['open']).sum()
        return int(green_days)
    
    def calculate_ranking(self, metric: str) -> List[str]:
        """Calculate rankings for various metrics"""
        rankings = []
        
        if metric == 'return':
            returns = {}
            for token in self.data:
                returns[token] = self.calculate_basic_price(token, 'total_return')
            
            # Sort by return (highest first)
            sorted_tokens = sorted(returns.items(), key=lambda x: x[1], reverse=True)
            return [token for token, _ in sorted_tokens]
        
        elif metric == 'volume':
            volumes = {}
            for token in self.data:
                volumes[token] = self.data[token]['volume'].mean()
            
            # Sort by volume (highest first)
            sorted_tokens = sorted(volumes.items(), key=lambda x: x[1], reverse=True)
            return [token for token, _ in sorted_tokens]
        
        elif metric == 'volatility':
            volatilities = {}
            for token in self.data:
                df = self.data[token]
                price_range = (df['high'].max() - df['low'].min()) / df['close'].mean() * 100
                volatilities[token] = price_range
            
            # Sort by volatility (highest first)
            sorted_tokens = sorted(volatilities.items(), key=lambda x: x[1], reverse=True)
            return [token for token, _ in sorted_tokens]
        
        elif metric == 'max_daily_change':
            max_changes = {}
            for token in self.data:
                df = self.data[token]
                max_changes[token] = df['daily_return'].abs().max()
            
            # Sort by max change (highest first)
            sorted_tokens = sorted(max_changes.items(), key=lambda x: x[1], reverse=True)
            return [token for token, _ in sorted_tokens]
        
        return []
    
    def calculate_percentage_threshold(self, token: str, threshold: float, above: bool = True) -> float:
        """Calculate percentage of days above/below threshold"""
        if token not in self.data:
            return 0.0
        
        df = self.data[token]
        
        if above:
            days_above = (df['close'] > threshold).sum()
        else:
            days_above = (df['close'] < threshold).sum()
        
        total_days = len(df)
        return (days_above / total_days) * 100
    
    def calculate_conditional_threshold(self, condition: str) -> float:
        """Calculate conditional thresholds"""
        if condition == 'both_sol_eth_green':
            sol_df = self.data.get('SOL')
            eth_df = self.data.get('ETH')
            
            if sol_df is None or eth_df is None:
                return 0.0
            
            # Calculate daily changes
            sol_changes = sol_df['close'].pct_change() > 0
            eth_changes = eth_df['close'].pct_change() > 0
            
            # Both green on same day
            both_green = (sol_changes & eth_changes).sum()
            total_days = len(sol_changes) - 1  # Exclude first day (no previous)
            
            return (both_green / total_days) * 100 if total_days > 0 else 0.0
        
        elif condition == 'sol_up_eth_down':
            sol_df = self.data.get('SOL')
            eth_df = self.data.get('ETH')
            
            if sol_df is None or eth_df is None:
                return 0.0
            
            # Calculate daily changes
            sol_changes = sol_df['close'].pct_change() > 0
            eth_changes = eth_df['close'].pct_change() < 0
            
            # SOL up and ETH down on same day
            sol_up_eth_down = (sol_changes & eth_changes).sum()
            total_days = len(sol_changes) - 1  # Exclude first day
            
            return (sol_up_eth_down / total_days) * 100 if total_days > 0 else 0.0
        
        elif condition == 'sol_above_160_when_eth_above_2700':
            sol_df = self.data.get('SOL')
            eth_df = self.data.get('ETH')
            
            if sol_df is None or eth_df is None:
                return 0.0
            
            # Days when ETH is above 2700
            eth_above_2700 = eth_df['close'] > 2700
            
            if eth_above_2700.sum() == 0:
                return 0.0  # No days with ETH above 2700
            
            # On those days, how many times was SOL above 160?
            sol_above_160_on_eth_days = (sol_df['close'] > 160) & eth_above_2700
            
            return (sol_above_160_on_eth_days.sum() / eth_above_2700.sum()) * 100
        
        return 0.0
    
    def calculate_price_change(self, token: str, period: str) -> float:
        """Calculate price change for specific periods"""
        if token not in self.data:
            return 0.0
        
        df = self.data[token]
        
        if period == 'first_half':
            mid_point = len(df) // 2
            start_price = df['close'].iloc[0]
            end_price = df['close'].iloc[mid_point]
        elif period == 'second_half':
            mid_point = len(df) // 2
            start_price = df['close'].iloc[mid_point]
            end_price = df['close'].iloc[-1]
        else:
            return 0.0
        
        return ((end_price - start_price) / start_price) * 100
    
    def calculate_rolling_stats(self, token: str, metric: str) -> Union[float, str]:
        """Calculate rolling statistics"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        
        if metric == 'max_5d_rolling_return':
            rolling_returns = df['close'].pct_change(5) * 100
            return float(rolling_returns.max())
        
        elif metric == 'min_3d_rolling_return':
            rolling_returns = df['close'].pct_change(3) * 100
            return float(rolling_returns.min())
        
        elif metric == 'biggest_weekly_gain':
            # Find the week with biggest gain
            weekly_returns = df['close'].pct_change(7) * 100
            max_week_idx = weekly_returns.idxmax()
            max_gain = weekly_returns.max()
            
            return f"Week of {max_week_idx.strftime('%Y-%m-%d')} : +{max_gain:.2f} %"
        
        elif metric == 'pct_close_above_7dma':
            # Calculate 7-day moving average
            df['7dma'] = df['close'].rolling(window=7).mean()
            
            # Count days where close is above 7dma (excluding first 6 days)
            valid_days = df.dropna()
            days_above_7dma = (valid_days['close'] > valid_days['7dma']).sum()
            total_valid_days = len(valid_days)
            
            return (days_above_7dma / total_valid_days) * 100 if total_valid_days > 0 else 0.0
        
        return None
    
    def calculate_streak_analysis(self, token: str, metric: str) -> Union[int, str]:
        """Calculate streak analysis"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        
        if metric == 'longest_streak_above_155':
            # For SOL, find longest streak above $155
            above_155 = df['close'] > 155
            streaks = (above_155 != above_155.shift()).cumsum()
            longest_streak = above_155.groupby(streaks).sum().max()
            return int(longest_streak)
        
        elif metric == 'longest_consecutive_red_days':
            # Find longest streak of negative daily returns
            red_days = df['daily_return'] < 0
            streaks = (red_days != red_days.shift()).cumsum()
            longest_streak = red_days.groupby(streaks).sum().max()
            return int(longest_streak)
        
        return None
    
    def calculate_volatility_stats(self, token: str, metric: str) -> Union[float, str]:
        """Calculate volatility statistics"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        
        if metric == 'stddev_daily_return':
            return float(df['daily_return'].std())
        
        elif metric == 'biggest_single_day_loss':
            return float(df['daily_return'].min())
        
        elif metric == 'days_change_gt5pct':
            return int((df['daily_return'].abs() > 5).sum())
        
        elif metric == 'highest_daily_change_date':
            max_change_idx = df['daily_return'].abs().idxmax()
            return max_change_idx.strftime('%Y-%m-%d')
        
        elif metric == 'avg_daily_change':
            return float(df['daily_return'].mean())
        
        elif metric == 'highest_intraday_swing_date':
            # Calculate intraday swing as (high - low) / close * 100
            df['intraday_swing'] = (df['high'] - df['low']) / df['close'] * 100
            max_swing_idx = df['intraday_swing'].idxmax()
            return max_swing_idx.strftime('%Y-%m-%d')
        
        elif metric == 'days_range_gt5pct':
            # Calculate intraday range as percentage of closing price
            df['intraday_range'] = (df['high'] - df['low']) / df['close'] * 100
            return int((df['intraday_range'] > 5).sum())
        
        return None
    
    def calculate_volume_analysis(self, token: str, metric: str) -> Union[float, str]:
        """Calculate volume analysis"""
        if token not in self.data:
            return None
        
        df = self.data[token]
        
        if metric == 'highest_volume_zscore_day':
            # Find day with highest volume z-score
            volume_mean = df['volume'].mean()
            volume_std = df['volume'].std()
            z_scores = (df['volume'] - volume_mean) / volume_std
            max_zscore_idx = z_scores.idxmax()
            return max_zscore_idx.strftime('%Y-%m-%d')
        
        elif metric == 'pct_days_vol_gt_2x_avg':
            avg_volume = df['volume'].mean()
            days_high_vol = (df['volume'] > 2 * avg_volume).sum()
            return (days_high_vol / len(df)) * 100
        
        return None
    
    def calculate_conditional_volume(self, condition: str) -> Union[float, None]:
        """Calculate conditional volume metrics"""
        if condition == 'eth_avg_volume_when_sol_drop_gt5':
            sol_df = self.data.get('SOL')
            eth_df = self.data.get('ETH')
            
            if sol_df is None or eth_df is None:
                return None
            
            # Find days when SOL dropped more than 5%
            sol_drops_gt5 = sol_df['daily_return'] < -5
            drop_dates = sol_df[sol_drops_gt5].index
            
            if len(drop_dates) == 0:
                return None  # No days with SOL drops > 5%
            
            # Get ETH volume on those specific dates
            eth_volume_on_drop_days = eth_df.loc[drop_dates, 'volume']
            
            return float(eth_volume_on_drop_days.mean())
        
        return None
    
    def calculate_truth_for_query(self, query: Dict) -> Any:
        """Calculate truth value for a specific query"""
        query_id = query['id']
        category = query['category']
        
        # Basic price queries
        if category == 'basic_price':
            if 'current_price' in query_id:
                token = query_id.split('_')[1].upper()
                return self.calculate_basic_price(token, 'current_price')
        
        elif category == 'basic_extremes':
            if 'highest_price' in query_id:
                token = query_id.split('_')[1].upper()
                return self.calculate_basic_price(token, 'highest_price')
            elif 'lowest_price' in query_id:
                token = query_id.split('_')[1].upper()
                return self.calculate_basic_price(token, 'lowest_price')
        
        elif category == 'basic_return':
            if 'total_return' in query_id:
                token = query_id.split('_')[1].upper()
                return self.calculate_basic_price(token, 'total_return')
        
        elif category == 'basic_counting':
            if 'green_days' in query_id:
                token = query_id.split('_')[1].upper()
                return self.calculate_green_days(token)
        
        elif category == 'basic_ranking':
            if 'rank_by_return' in query_id:
                return self.calculate_ranking('return')
            elif 'rank_by_volume' in query_id:
                return self.calculate_ranking('volume')
            elif 'rank_by_volatility' in query_id:
                return self.calculate_ranking('volatility')
        
        elif category == 'percentage_threshold':
            if 'pct_tao_above_420' in query_id:
                return self.calculate_percentage_threshold('TAO', 420, above=True)
            elif 'pct_sol_below_140' in query_id:
                return self.calculate_percentage_threshold('SOL', 140, above=False)
        
        elif category == 'conditional_threshold':
            if 'both_sol_eth_green' in query_id:
                return self.calculate_conditional_threshold('both_sol_eth_green')
            elif 'sol_up_eth_down' in query_id:
                return self.calculate_conditional_threshold('sol_up_eth_down')
            elif 'pct_sol_above_160_when_eth_above_2700' in query_id:
                return self.calculate_conditional_threshold('sol_above_160_when_eth_above_2700')
        
        elif category == 'price_change':
            if 'sol_price_change_first_half' in query_id:
                return self.calculate_price_change('SOL', 'first_half')
            elif 'eth_price_change_second_half' in query_id:
                return self.calculate_price_change('ETH', 'second_half')
        
        elif category == 'rolling_stats':
            if 'tao_max_5d_rolling_return' in query_id:
                return self.calculate_rolling_stats('TAO', 'max_5d_rolling_return')
            elif 'sol_min_3d_rolling_return' in query_id:
                return self.calculate_rolling_stats('SOL', 'min_3d_rolling_return')
            elif 'tao_biggest_weekly_gain' in query_id:
                return self.calculate_rolling_stats('TAO', 'biggest_weekly_gain')
            elif 'pct_sol_close_above_7dma' in query_id:
                return self.calculate_rolling_stats('SOL', 'pct_close_above_7dma')
        
        elif category == 'streak_analysis':
            if 'sol_longest_streak_above_155' in query_id:
                return self.calculate_streak_analysis('SOL', 'longest_streak_above_155')
            elif 'eth_longest_consecutive_red_days' in query_id:
                return self.calculate_streak_analysis('ETH', 'longest_consecutive_red_days')
        
        elif category == 'volatility':
            if 'tao_highest_daily_change_date' in query_id:
                return self.calculate_volatility_stats('TAO', 'highest_daily_change_date')
            elif 'tao_highest_intraday_swing_date' in query_id:
                return self.calculate_volatility_stats('TAO', 'highest_intraday_swing_date')
            elif 'eth_days_change_gt5pct' in query_id:
                return self.calculate_volatility_stats('ETH', 'days_change_gt5pct')
            elif 'eth_days_range_gt5pct' in query_id:
                return self.calculate_volatility_stats('ETH', 'days_range_gt5pct')
            elif 'eth_biggest_single_day_loss' in query_id:
                return self.calculate_volatility_stats('ETH', 'biggest_single_day_loss')
        
        elif category == 'volatility_stat':
            if 'eth_stddev_daily_return' in query_id:
                return self.calculate_volatility_stats('ETH', 'stddev_daily_return')
            elif 'tao_avg_daily_change' in query_id:
                return self.calculate_volatility_stats('TAO', 'avg_daily_change')
        
        elif category == 'volume_analysis':
            if 'sol_highest_volume_zscore_day' in query_id:
                return self.calculate_volume_analysis('SOL', 'highest_volume_zscore_day')
            elif 'pct_days_tao_vol_gt_2x_avg' in query_id:
                return self.calculate_volume_analysis('TAO', 'pct_days_vol_gt_2x_avg')
        
        elif category == 'conditional_volume':
            if 'eth_avg_volume_when_sol_drop_gt5' in query_id:
                return self.calculate_conditional_volume('eth_avg_volume_when_sol_drop_gt5')
        
        elif category == 'performance_comparison':
            if 'rank_by_max_daily_change' in query_id:
                return self.calculate_ranking('max_daily_change')
            elif 'rank_by_sharpe' in query_id:
                # Simplified Sharpe ratio calculation
                sharpe_ratios = {}
                for token in self.data:
                    df = self.data[token]
                    avg_return = df['daily_return'].mean()
                    std_return = df['daily_return'].std()
                    sharpe_ratios[token] = avg_return / std_return if std_return > 0 else 0
                
                sorted_tokens = sorted(sharpe_ratios.items(), key=lambda x: x[1], reverse=True)
                return [token for token, _ in sorted_tokens]
            elif 'rank_by_total_return' in query_id:
                return self.calculate_ranking('return')
            elif 'rank_by_volatility' in query_id:
                return self.calculate_ranking('volatility')
        
        # Default: return None if we can't calculate
        return None
    
    def to_native(self, val):
        import numpy as np
        if isinstance(val, (np.generic,)):
            return val.item()
        if isinstance(val, list):
            return [self.to_native(x) for x in val]
        if isinstance(val, dict):
            return {k: self.to_native(v) for k, v in val.items()}
        return val

    def update_queries_with_dynamic_truth(self, queries_file: str = 'data/queries.yaml'):
        """Update queries.yaml with dynamically calculated truth values"""
        print("🔄 Updating queries with dynamic truth values...")
        
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
        with open(queries_file, 'w') as f:
            yaml.dump(queries_data, f, default_flow_style=False, indent=2)
        
        print(f"\n✅ Updated {updated_count} queries with dynamic truth values")
        return updated_count

def main():
    """Main function"""
    calculator = DynamicTruthCalculator()
    
    # Update queries with dynamic truth
    updated_count = calculator.update_queries_with_dynamic_truth()
    
    print(f"\n🎉 Dynamic truth calculation completed!")
    print(f"Updated {updated_count} queries")

if __name__ == "__main__":
    main() 