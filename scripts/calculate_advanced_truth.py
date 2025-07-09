#!/usr/bin/env python3
"""
Calculate Truth Values for Advanced Queries
Calculates all truth values and explanations for the 20 advanced queries
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml

def load_data():
    """Load all token data"""
    eth_data = pd.read_csv('data/eth_daily.csv')
    sol_data = pd.read_csv('data/sol_daily.csv')
    tao_data = pd.read_csv('data/tao_daily.csv')
    
    # Convert date column
    for df in [eth_data, sol_data, tao_data]:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    
    return eth_data, sol_data, tao_data

def calculate_truth_values():
    """Calculate all truth values and explanations"""
    
    eth_data, sol_data, tao_data = load_data()
    
    # Filter to 30-day period (June 9 to July 8, 2025)
    start_date = '2025-06-09'
    end_date = '2025-07-08'
    
    eth = eth_data.loc[start_date:end_date]
    sol = sol_data.loc[start_date:end_date]
    tao = tao_data.loc[start_date:end_date]
    
    results = {}
    
    # 1. Simple threshold (new level)
    tao_above_420 = (tao['close'] > 420).sum()
    pct_tao_above_420 = (tao_above_420 / len(tao)) * 100
    results['pct_tao_above_420_30d'] = {
        'truth': round(pct_tao_above_420, 2),
        'explanation': f"{tao_above_420} out of {len(tao)} days had TAO close above $420"
    }
    
    # 2. Inverse threshold
    sol_below_140 = (sol['close'] < 140).sum()
    pct_sol_below_140 = (sol_below_140 / len(sol)) * 100
    results['pct_sol_below_140_30d'] = {
        'truth': round(pct_sol_below_140, 2),
        'explanation': f"{sol_below_140} out of {len(sol)} days had SOL close below $140"
    }
    
    # 3. Conditional same-day threshold
    # Calculate daily returns
    eth_returns = eth['close'].pct_change()
    sol_returns = sol['close'].pct_change()
    
    # Both green on same day
    both_green = ((eth_returns > 0) & (sol_returns > 0)).sum()
    pct_both_green = (both_green / len(eth_returns.dropna())) * 100
    results['pct_days_both_sol_eth_green_30d'] = {
        'truth': round(pct_both_green, 2),
        'explanation': f"{both_green} out of {len(eth_returns.dropna())} days had both SOL and ETH close higher than previous day"
    }
    
    # 4. First-half price change (June 9-23)
    sol_first_half = sol.loc['2025-06-09':'2025-06-23']
    sol_first_half_change = ((sol_first_half['close'].iloc[-1] / sol_first_half['close'].iloc[0]) - 1) * 100
    results['sol_price_change_first_half'] = {
        'truth': round(sol_first_half_change, 2),
        'explanation': f"SOL went from ${sol_first_half['close'].iloc[0]:.2f} to ${sol_first_half['close'].iloc[-1]:.2f}, a {sol_first_half_change:.2f}% change"
    }
    
    # 5. Second-half price change (June 24-July 8)
    eth_second_half = eth.loc['2025-06-24':'2025-07-08']
    eth_second_half_change = ((eth_second_half['close'].iloc[-1] / eth_second_half['close'].iloc[0]) - 1) * 100
    results['eth_price_change_second_half'] = {
        'truth': round(eth_second_half_change, 2),
        'explanation': f"ETH went from ${eth_second_half['close'].iloc[0]:.2f} to ${eth_second_half['close'].iloc[-1]:.2f}, a {eth_second_half_change:.2f}% change"
    }
    
    # 6. Biggest single-week gain for TAO
    tao_weekly_gains = []
    for i in range(len(tao) - 6):
        week_start = tao.iloc[i]['close']
        week_end = tao.iloc[i + 6]['close']
        gain = ((week_end / week_start) - 1) * 100
        week_start_date = tao.index[i].strftime('%Y-%m-%d')
        tao_weekly_gains.append((week_start_date, gain))
    
    max_week_gain = max(tao_weekly_gains, key=lambda x: x[1])
    results['tao_biggest_weekly_gain'] = {
        'truth': f"Week of {max_week_gain[0]} : +{max_week_gain[1]:.2f} %",
        'explanation': f"TAO's largest 7-day gain was {max_week_gain[1]:.2f}% starting {max_week_gain[0]}"
    }
    
    # 7. Longest bullish streak for SOL above $155
    sol_above_155 = sol['close'] > 155
    current_streak = 0
    max_streak = 0
    
    for is_above in sol_above_155:
        if is_above:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    results['sol_longest_streak_above_155'] = {
        'truth': max_streak,
        'explanation': f"SOL closed above $155 for {max_streak} consecutive days at its longest streak"
    }
    
    # 8. Longest red-day streak for ETH
    eth_red_days = eth_returns < 0
    current_red_streak = 0
    max_red_streak = 0
    
    for is_red in eth_red_days.dropna():
        if is_red:
            current_red_streak += 1
            max_red_streak = max(max_red_streak, current_red_streak)
        else:
            current_red_streak = 0
    
    results['eth_longest_consecutive_red_days'] = {
        'truth': max_red_streak,
        'explanation': f"ETH had {max_red_streak} consecutive down days in its longest losing streak"
    }
    
    # 9. Rolling 5-day max return for TAO
    tao_5d_returns = []
    for i in range(len(tao) - 4):
        start_price = tao.iloc[i]['close']
        end_price = tao.iloc[i + 4]['close']
        return_5d = ((end_price / start_price) - 1) * 100
        tao_5d_returns.append(return_5d)
    
    max_5d_return = max(tao_5d_returns)
    results['tao_max_5d_rolling_return'] = {
        'truth': round(max_5d_return, 2),
        'explanation': f"TAO's highest 5-day rolling return was {max_5d_return:.2f}%"
    }
    
    # 10. Rolling 3-day min return for SOL
    sol_3d_returns = []
    for i in range(len(sol) - 2):
        start_price = sol.iloc[i]['close']
        end_price = sol.iloc[i + 2]['close']
        return_3d = ((end_price / start_price) - 1) * 100
        sol_3d_returns.append(return_3d)
    
    min_3d_return = min(sol_3d_returns)
    results['sol_min_3d_rolling_return'] = {
        'truth': round(min_3d_return, 2),
        'explanation': f"SOL's lowest 3-day rolling return was {min_3d_return:.2f}%"
    }
    
    # 11. Volume spike day (z-score) for SOL
    sol_volume_mean = sol['volume'].mean()
    sol_volume_std = sol['volume'].std()
    sol_volume_zscore = (sol['volume'] - sol_volume_mean) / sol_volume_std
    
    max_zscore_day = sol_volume_zscore.idxmax()
    max_zscore_value = sol_volume_zscore.max()
    
    results['sol_highest_volume_zscore_day'] = {
        'truth': max_zscore_day.strftime('%Y-%m-%d'),
        'explanation': f"SOL had highest volume z-score of {max_zscore_value:.2f} on {max_zscore_day.strftime('%Y-%m-%d')}"
    }
    
    # 12. Conditional volume mean for ETH when SOL drops >5%
    sol_drops_gt5 = sol_returns < -0.05
    eth_volume_when_sol_drops = eth.loc[sol_drops_gt5.index[sol_drops_gt5], 'volume'].mean()
    
    results['eth_avg_volume_when_sol_drop_gt5'] = {
        'truth': round(eth_volume_when_sol_drops, 2),
        'explanation': f"ETH's average volume was ${eth_volume_when_sol_drops:.2f} on days when SOL fell more than 5%"
    }
    
    # 13. Highest intraday swing for TAO
    tao_intraday_swings = (tao['high'] - tao['low']) / tao['close'] * 100
    max_swing_day = tao_intraday_swings.idxmax()
    max_swing_value = tao_intraday_swings.max()
    
    results['tao_highest_intraday_swing_date'] = {
        'truth': max_swing_day.strftime('%Y-%m-%d'),
        'explanation': f"TAO had largest intraday swing of {max_swing_value:.2f}% on {max_swing_day.strftime('%Y-%m-%d')}"
    }
    
    # 14. Range > 5% days count for ETH
    eth_intraday_ranges = (eth['high'] - eth['low']) / eth['close'] * 100
    eth_days_range_gt5 = (eth_intraday_ranges > 5).sum()
    
    results['eth_days_range_gt5pct'] = {
        'truth': eth_days_range_gt5,
        'explanation': f"ETH had {eth_days_range_gt5} days where intraday range exceeded 5% of closing price"
    }
    
    # 15. % above 7-day moving average for SOL
    sol_7d_ma = sol['close'].rolling(7).mean()
    sol_above_7d_ma = (sol['close'] > sol_7d_ma).sum()
    pct_sol_above_7d_ma = (sol_above_7d_ma / len(sol)) * 100
    
    results['pct_sol_close_above_7dma'] = {
        'truth': round(pct_sol_above_7d_ma, 2),
        'explanation': f"{sol_above_7d_ma} out of {len(sol)} days SOL closed above its 7-day moving average"
    }
    
    # 16. Sharpe ratio ranking
    # Calculate daily returns and Sharpe ratios
    eth_sharpe = eth_returns.mean() / eth_returns.std() * np.sqrt(252)
    sol_sharpe = sol_returns.mean() / sol_returns.std() * np.sqrt(252)
    tao_returns = tao['close'].pct_change()
    tao_sharpe = tao_returns.mean() / tao_returns.std() * np.sqrt(252)
    
    sharpe_ratios = [('ETH', eth_sharpe), ('SOL', sol_sharpe), ('TAO', tao_sharpe)]
    sharpe_ranking = [token for token, _ in sorted(sharpe_ratios, key=lambda x: x[1], reverse=True)]
    
    results['rank_by_sharpe_30d'] = {
        'truth': sharpe_ranking,
        'explanation': f"Sharpe ratios: ETH {eth_sharpe:.3f}, SOL {sol_sharpe:.3f}, TAO {tao_sharpe:.3f}"
    }
    
    # 17. Total return ranking
    eth_total_return = ((eth['close'].iloc[-1] / eth['close'].iloc[0]) - 1) * 100
    sol_total_return = ((sol['close'].iloc[-1] / sol['close'].iloc[0]) - 1) * 100
    tao_total_return = ((tao['close'].iloc[-1] / tao['close'].iloc[0]) - 1) * 100
    
    total_returns = [('ETH', eth_total_return), ('SOL', sol_total_return), ('TAO', tao_total_return)]
    total_return_ranking = [token for token, _ in sorted(total_returns, key=lambda x: x[1], reverse=True)]
    
    results['rank_by_total_return_30d'] = {
        'truth': total_return_ranking,
        'explanation': f"Total returns: ETH {eth_total_return:.2f}%, SOL {sol_total_return:.2f}%, TAO {tao_total_return:.2f}%"
    }
    
    # 18. Volatility ranking
    eth_volatility = ((eth['high'].max() - eth['low'].min()) / eth['close'].mean()) * 100
    sol_volatility = ((sol['high'].max() - sol['low'].min()) / sol['close'].mean()) * 100
    tao_volatility = ((tao['high'].max() - tao['low'].min()) / tao['close'].mean()) * 100
    
    volatilities = [('ETH', eth_volatility), ('SOL', sol_volatility), ('TAO', tao_volatility)]
    volatility_ranking = [token for token, _ in sorted(volatilities, key=lambda x: x[1], reverse=True)]
    
    results['rank_by_volatility_30d'] = {
        'truth': volatility_ranking,
        'explanation': f"Volatility ranges: ETH {eth_volatility:.2f}%, SOL {sol_volatility:.2f}%, TAO {tao_volatility:.2f}%"
    }
    
    # 19. Conditional threshold combo
    eth_above_2700 = eth['close'] > 2700
    sol_above_160_when_eth_above_2700 = (sol.loc[eth_above_2700.index[eth_above_2700], 'close'] > 160).sum()
    total_eth_above_2700 = eth_above_2700.sum()
    pct_sol_above_160_when_eth_above_2700 = (sol_above_160_when_eth_above_2700 / total_eth_above_2700) * 100 if total_eth_above_2700 > 0 else 0
    
    results['pct_sol_above_160_when_eth_above_2700'] = {
        'truth': round(pct_sol_above_160_when_eth_above_2700, 2),
        'explanation': f"SOL closed above $160 on {sol_above_160_when_eth_above_2700} out of {total_eth_above_2700} days when ETH was above $2700"
    }
    
    # 20. Standard deviation of daily returns for ETH
    eth_returns_std = eth_returns.std() * 100
    
    results['eth_stddev_daily_return_30d'] = {
        'truth': round(eth_returns_std, 4),
        'explanation': f"ETH's daily returns had a standard deviation of {eth_returns_std:.4f}%"
    }
    
    return results

def update_queries_file():
    """Update the queries.yaml file with calculated truth values"""
    
    # Load current queries
    with open('data/queries.yaml', 'r') as f:
        queries_data = yaml.safe_load(f)
    
    # Calculate truth values
    truth_values = calculate_truth_values()
    
    # Update queries with truth values
    for query in queries_data['queries']:
        query_id = query['id']
        if query_id in truth_values:
            query['truth'] = truth_values[query_id]['truth']
            query['explanation'] = truth_values[query_id]['explanation']
    
    # Save updated queries
    with open('data/queries.yaml', 'w') as f:
        yaml.dump(queries_data, f, default_flow_style=False, sort_keys=False)
    
    print("✅ Updated queries.yaml with calculated truth values!")
    print(f"📊 Calculated {len(truth_values)} truth values")
    
    # Print summary
    print("\n📋 Summary of calculated values:")
    for query_id, values in truth_values.items():
        print(f"   • {query_id}: {values['truth']}")

if __name__ == "__main__":
    update_queries_file() 