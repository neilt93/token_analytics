#!/usr/bin/env python3
"""
Calculate truth values for new queries
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_data():
    """Load the daily data for all tokens"""
    sol_df = pd.read_csv('data/sol_daily.csv')
    eth_df = pd.read_csv('data/eth_daily.csv')
    tao_df = pd.read_csv('data/tao_daily.csv')
    
    # Convert date column
    for df in [sol_df, eth_df, tao_df]:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
    
    return sol_df, eth_df, tao_df

def calculate_new_queries():
    """Calculate truth values for the new queries"""
    sol_df, eth_df, tao_df = load_data()
    
    # Filter to the 30-day period (June 9 to July 8, 2025)
    start_date = '2025-06-09'
    end_date = '2025-07-08'
    
    sol_period = sol_df[(sol_df['date'] >= start_date) & (sol_df['date'] <= end_date)].copy()
    eth_period = eth_df[(eth_df['date'] >= start_date) & (eth_df['date'] <= end_date)].copy()
    tao_period = tao_df[(tao_df['date'] >= start_date) & (tao_df['date'] <= end_date)].copy()
    
    # Remove the last row (duplicate timestamp)
    sol_period = sol_period.iloc[:-1]
    eth_period = eth_period.iloc[:-1]
    tao_period = tao_period.iloc[:-1]
    
    # Calculate daily returns
    sol_period['daily_return'] = sol_period['close'].pct_change()
    eth_period['daily_return'] = eth_period['close'].pct_change()
    tao_period['daily_return'] = tao_period['close'].pct_change()
    
    # Calculate intraday ranges
    sol_period['intraday_range_pct'] = (sol_period['high'] - sol_period['low']) / sol_period['close'] * 100
    eth_period['intraday_range_pct'] = (eth_period['high'] - eth_period['low']) / eth_period['close'] * 100
    tao_period['intraday_range_pct'] = (tao_period['high'] - tao_period['low']) / tao_period['close'] * 100
    
    # Calculate moving averages
    sol_period['10dma'] = sol_period['close'].rolling(10).mean()
    eth_period['10dma'] = eth_period['close'].rolling(10).mean()
    tao_period['10dma'] = tao_period['close'].rolling(10).mean()
    
    # Calculate volume averages
    sol_period['volume_avg'] = sol_period['volume'].rolling(30).mean()
    eth_period['volume_avg'] = eth_period['volume'].rolling(30).mean()
    tao_period['volume_avg'] = tao_period['volume'].rolling(30).mean()
    
    # Calculate overnight gaps
    sol_period['overnight_gap_pct'] = (sol_period['open'] - sol_period['close'].shift(1)) / sol_period['close'].shift(1) * 100
    eth_period['overnight_gap_pct'] = (eth_period['open'] - eth_period['close'].shift(1)) / eth_period['close'].shift(1) * 100
    tao_period['overnight_gap_pct'] = (tao_period['open'] - tao_period['close'].shift(1)) / tao_period['close'].shift(1) * 100
    
    results = {}
    
    # 1. pct_days_sol_up_eth_down
    sol_up = sol_period['daily_return'] > 0
    eth_down = eth_period['daily_return'] < 0
    both_conditions = sol_up & eth_down
    results['pct_days_sol_up_eth_down'] = (both_conditions.sum() / len(sol_period)) * 100
    
    # 2. tao_avg_daily_range
    results['tao_avg_daily_range'] = tao_period['intraday_range_pct'].mean()
    
    # 3. eth_biggest_single_day_loss
    eth_losses = eth_period[eth_period['daily_return'] < 0]['daily_return']
    results['eth_biggest_single_day_loss'] = eth_losses.min() * 100
    
    # 4. sol_days_close_eq_or_above_open
    sol_close_above_open = sol_period['close'] >= sol_period['open']
    results['sol_days_close_eq_or_above_open'] = sol_close_above_open.sum()
    
    # 5. pct_days_tao_vol_gt_2x_avg
    tao_high_vol = tao_period['volume'] > (tao_period['volume_avg'] * 2)
    results['pct_days_tao_vol_gt_2x_avg'] = (tao_high_vol.sum() / len(tao_period)) * 100
    
    # 6. eth_largest_gap_open_close
    eth_gaps = eth_period['overnight_gap_pct'].abs()
    results['eth_largest_gap_open_close'] = eth_gaps.max()
    
    # 7. sol_days_close_above_10dma
    sol_above_10dma = sol_period['close'] > sol_period['10dma']
    results['sol_days_close_above_10dma'] = (sol_above_10dma.sum() / len(sol_period)) * 100
    
    # 8. rank_by_max_intraday_swing
    sol_max_swing = sol_period['intraday_range_pct'].max()
    eth_max_swing = eth_period['intraday_range_pct'].max()
    tao_max_swing = tao_period['intraday_range_pct'].max()
    
    swing_ranks = [
        ('SOL', sol_max_swing),
        ('ETH', eth_max_swing),
        ('TAO', tao_max_swing)
    ]
    swing_ranks.sort(key=lambda x: x[1], reverse=True)
    results['rank_by_max_intraday_swing'] = [token for token, _ in swing_ranks]
    
    # 9. pct_days_all_up
    all_up = (sol_period['daily_return'] > 0) & (eth_period['daily_return'] > 0) & (tao_period['daily_return'] > 0)
    results['pct_days_all_up'] = (all_up.sum() / len(sol_period)) * 100
    
    # 10. tao_avg_return_on_high_vol_days
    tao_high_vol_days = tao_period[tao_period['volume'] > (tao_period['volume_avg'] * 1.5)]
    if len(tao_high_vol_days) > 0:
        results['tao_avg_return_on_high_vol_days'] = tao_high_vol_days['daily_return'].mean() * 100
    else:
        results['tao_avg_return_on_high_vol_days'] = 0.0
    
    # Print debug info
    print(f"SOL period length: {len(sol_period)}")
    print(f"ETH period length: {len(eth_period)}")
    print(f"TAO period length: {len(tao_period)}")
    print(f"SOL daily returns range: {sol_period['daily_return'].min():.4f} to {sol_period['daily_return'].max():.4f}")
    print(f"ETH daily returns range: {eth_period['daily_return'].min():.4f} to {eth_period['daily_return'].max():.4f}")
    print(f"TAO daily returns range: {tao_period['daily_return'].min():.4f} to {tao_period['daily_return'].max():.4f}")
    
    return results

def print_results():
    """Print the calculated results"""
    results = calculate_new_queries()
    
    print("\n📊 Calculated Truth Values for New Queries")
    print("=" * 60)
    
    for query_id, value in results.items():
        if isinstance(value, list):
            print(f"{query_id}: {value}")
        else:
            print(f"{query_id}: {value:.2f}")
    
    print("\n📝 YAML Format:")
    print("-" * 40)
    
    for query_id, value in results.items():
        if isinstance(value, list):
            print(f"- id: {query_id}")
            print(f"  truth:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"- id: {query_id}")
            print(f"  truth: {value:.2f}")

if __name__ == "__main__":
    print_results() 