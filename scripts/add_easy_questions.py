#!/usr/bin/env python3
"""
Add Easy Questions to Token Analytics Benchmark
Creates simple questions with automated correct responses for testing basic AI capabilities
"""

import yaml
import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_existing_queries():
    """Load existing queries from YAML file"""
    with open('data/queries.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_market_data():
    """Load market data from CSV files"""
    sol_data = pd.read_csv('data/sol_daily.csv')
    eth_data = pd.read_csv('data/eth_daily.csv')
    tao_data = pd.read_csv('data/tao_daily.csv')
    
    # Convert date column
    for df in [sol_data, eth_data, tao_data]:
        df['date'] = pd.to_datetime(df['date'])
    
    return sol_data, eth_data, tao_data

def calculate_easy_metrics(sol_data, eth_data, tao_data):
    """Calculate simple metrics for easy questions"""
    
    # Basic price metrics
    sol_current = sol_data['close'].iloc[-1]
    eth_current = eth_data['close'].iloc[-1]
    tao_current = tao_data['close'].iloc[-1]
    
    sol_start = sol_data['close'].iloc[0]
    eth_start = eth_data['close'].iloc[0]
    tao_start = tao_data['close'].iloc[0]
    
    # Simple calculations
    sol_total_return = ((sol_current - sol_start) / sol_start) * 100
    eth_total_return = ((eth_current - eth_start) / eth_start) * 100
    tao_total_return = ((tao_current - tao_start) / tao_start) * 100
    
    # Volume metrics
    sol_avg_volume = sol_data['volume'].mean()
    eth_avg_volume = eth_data['volume'].mean()
    tao_avg_volume = tao_data['volume'].mean()
    
    # High/low metrics
    sol_highest = sol_data['high'].max()
    sol_lowest = sol_data['low'].min()
    eth_highest = eth_data['high'].max()
    eth_lowest = eth_data['low'].min()
    tao_highest = tao_data['high'].max()
    tao_lowest = tao_data['low'].min()
    
    # Green days (close > open)
    sol_green_days = (sol_data['close'] > sol_data['open']).sum()
    eth_green_days = (eth_data['close'] > eth_data['open']).sum()
    tao_green_days = (tao_data['close'] > tao_data['open']).sum()
    
    return {
        'sol_current': sol_current,
        'eth_current': eth_current,
        'tao_current': tao_current,
        'sol_total_return': sol_total_return,
        'eth_total_return': eth_total_return,
        'tao_total_return': tao_total_return,
        'sol_avg_volume': sol_avg_volume,
        'eth_avg_volume': eth_avg_volume,
        'tao_avg_volume': tao_avg_volume,
        'sol_highest': sol_highest,
        'sol_lowest': sol_lowest,
        'eth_highest': eth_highest,
        'eth_lowest': eth_lowest,
        'tao_highest': tao_highest,
        'tao_lowest': tao_lowest,
        'sol_green_days': sol_green_days,
        'eth_green_days': eth_green_days,
        'tao_green_days': tao_green_days,
        'total_days': len(sol_data)
    }

def create_easy_questions(metrics):
    """Create easy questions with automated correct responses"""
    
    easy_questions = [
        {
            'id': 'easy_sol_current_price',
            'question': 'What is SOL\'s current price?',
            'category': 'basic_price',
            'truth': float(round(metrics['sol_current'], 2)),
            'explanation': f'SOL current price is ${metrics["sol_current"]:.2f}'
        },
        {
            'id': 'easy_eth_current_price',
            'question': 'What is ETH\'s current price?',
            'category': 'basic_price',
            'truth': float(round(metrics['eth_current'], 2)),
            'explanation': f'ETH current price is ${metrics["eth_current"]:.2f}'
        },
        {
            'id': 'easy_tao_current_price',
            'question': 'What is TAO\'s current price?',
            'category': 'basic_price',
            'truth': float(round(metrics['tao_current'], 2)),
            'explanation': f'TAO current price is ${metrics["tao_current"]:.2f}'
        },
        {
            'id': 'easy_sol_total_return',
            'question': 'What was SOL\'s total percentage return over the 30-day period?',
            'category': 'basic_return',
            'truth': float(round(metrics['sol_total_return'], 2)),
            'explanation': f'SOL total return was {metrics["sol_total_return"]:.2f}%'
        },
        {
            'id': 'easy_eth_total_return',
            'question': 'What was ETH\'s total percentage return over the 30-day period?',
            'category': 'basic_return',
            'truth': float(round(metrics['eth_total_return'], 2)),
            'explanation': f'ETH total return was {metrics["eth_total_return"]:.2f}%'
        },
        {
            'id': 'easy_tao_total_return',
            'question': 'What was TAO\'s total percentage return over the 30-day period?',
            'category': 'basic_return',
            'truth': float(round(metrics['tao_total_return'], 2)),
            'explanation': f'TAO total return was {metrics["tao_total_return"]:.2f}%'
        },
        {
            'id': 'easy_sol_highest_price',
            'question': 'What was SOL\'s highest price during the 30-day period?',
            'category': 'basic_extremes',
            'truth': float(round(metrics['sol_highest'], 2)),
            'explanation': f'SOL highest price was ${metrics["sol_highest"]:.2f}'
        },
        {
            'id': 'easy_sol_lowest_price',
            'question': 'What was SOL\'s lowest price during the 30-day period?',
            'category': 'basic_extremes',
            'truth': float(round(metrics['sol_lowest'], 2)),
            'explanation': f'SOL lowest price was ${metrics["sol_lowest"]:.2f}'
        },
        {
            'id': 'easy_eth_highest_price',
            'question': 'What was ETH\'s highest price during the 30-day period?',
            'category': 'basic_extremes',
            'truth': float(round(metrics['eth_highest'], 2)),
            'explanation': f'ETH highest price was ${metrics["eth_highest"]:.2f}'
        },
        {
            'id': 'easy_eth_lowest_price',
            'question': 'What was ETH\'s lowest price during the 30-day period?',
            'category': 'basic_extremes',
            'truth': float(round(metrics['eth_lowest'], 2)),
            'explanation': f'ETH lowest price was ${metrics["eth_lowest"]:.2f}'
        },
        {
            'id': 'easy_tao_highest_price',
            'question': 'What was TAO\'s highest price during the 30-day period?',
            'category': 'basic_extremes',
            'truth': float(round(metrics['tao_highest'], 2)),
            'explanation': f'TAO highest price was ${metrics["tao_highest"]:.2f}'
        },
        {
            'id': 'easy_tao_lowest_price',
            'question': 'What was TAO\'s lowest price during the 30-day period?',
            'category': 'basic_extremes',
            'truth': float(round(metrics['tao_lowest'], 2)),
            'explanation': f'TAO lowest price was ${metrics["tao_lowest"]:.2f}'
        },
        {
            'id': 'easy_sol_green_days',
            'question': 'How many days did SOL close higher than it opened during the 30-day period?',
            'category': 'basic_counting',
            'truth': int(metrics['sol_green_days']),
            'explanation': f'SOL had {metrics["sol_green_days"]} green days out of {metrics["total_days"]}'
        },
        {
            'id': 'easy_eth_green_days',
            'question': 'How many days did ETH close higher than it opened during the 30-day period?',
            'category': 'basic_counting',
            'truth': int(metrics['eth_green_days']),
            'explanation': f'ETH had {metrics["eth_green_days"]} green days out of {metrics["total_days"]}'
        },
        {
            'id': 'easy_tao_green_days',
            'question': 'How many days did TAO close higher than it opened during the 30-day period?',
            'category': 'basic_counting',
            'truth': int(metrics['tao_green_days']),
            'explanation': f'TAO had {metrics["tao_green_days"]} green days out of {metrics["total_days"]}'
        },
        {
            'id': 'easy_rank_by_return',
            'question': 'Rank SOL, ETH, and TAO by their total percentage return over the 30-day period.',
            'category': 'basic_ranking',
            'truth': ['ETH', 'SOL', 'TAO'] if metrics['eth_total_return'] > metrics['sol_total_return'] > metrics['tao_total_return'] else ['SOL', 'ETH', 'TAO'] if metrics['sol_total_return'] > metrics['eth_total_return'] > metrics['tao_total_return'] else ['TAO', 'SOL', 'ETH'],
            'explanation': f'Returns: ETH {metrics["eth_total_return"]:.2f}%, SOL {metrics["sol_total_return"]:.2f}%, TAO {metrics["tao_total_return"]:.2f}%'
        },
        {
            'id': 'easy_rank_by_volume',
            'question': 'Rank SOL, ETH, and TAO by their average daily trading volume over the 30-day period.',
            'category': 'basic_ranking',
            'truth': ['ETH', 'SOL', 'TAO'] if metrics['eth_avg_volume'] > metrics['sol_avg_volume'] > metrics['tao_avg_volume'] else ['SOL', 'ETH', 'TAO'] if metrics['sol_avg_volume'] > metrics['eth_avg_volume'] > metrics['tao_avg_volume'] else ['TAO', 'SOL', 'ETH'],
            'explanation': f'Average volumes: ETH ${metrics["eth_avg_volume"]:,.0f}, SOL ${metrics["sol_avg_volume"]:,.0f}, TAO ${metrics["tao_avg_volume"]:,.0f}'
        },
        {
            'id': 'easy_rank_by_volatility',
            'question': 'Rank SOL, ETH, and TAO by their price volatility (highest to lowest price range) over the 30-day period.',
            'category': 'basic_ranking',
            'truth': ['TAO', 'ETH', 'SOL'] if (metrics['tao_highest'] - metrics['tao_lowest']) / metrics['tao_lowest'] > (metrics['eth_highest'] - metrics['eth_lowest']) / metrics['eth_lowest'] > (metrics['sol_highest'] - metrics['sol_lowest']) / metrics['sol_lowest'] else ['ETH', 'TAO', 'SOL'] if (metrics['eth_highest'] - metrics['eth_lowest']) / metrics['eth_lowest'] > (metrics['tao_highest'] - metrics['tao_lowest']) / metrics['tao_lowest'] > (metrics['sol_highest'] - metrics['sol_lowest']) / metrics['sol_lowest'] else ['SOL', 'ETH', 'TAO'],
            'explanation': f'Price ranges: TAO {((metrics["tao_highest"] - metrics["tao_lowest"]) / metrics["tao_lowest"] * 100):.1f}%, ETH {((metrics["eth_highest"] - metrics["eth_lowest"]) / metrics["eth_lowest"] * 100):.1f}%, SOL {((metrics["sol_highest"] - metrics["sol_lowest"]) / metrics["sol_lowest"] * 100):.1f}%'
        }
    ]
    
    return easy_questions

def add_easy_questions_to_queries():
    """Add easy questions to the existing queries file"""
    
    print("📊 Loading market data...")
    sol_data, eth_data, tao_data = load_market_data()
    
    print("🧮 Calculating easy metrics...")
    metrics = calculate_easy_metrics(sol_data, eth_data, tao_data)
    
    print("📝 Creating easy questions...")
    easy_questions = create_easy_questions(metrics)
    
    print("📂 Loading existing queries...")
    existing_data = load_existing_queries()
    
    # Add easy questions to the beginning of the queries list
    existing_data['queries'] = easy_questions + existing_data['queries']
    
    # Update metadata to include easy questions
    if 'metadata' not in existing_data:
        existing_data['metadata'] = {}
    
    existing_data['metadata']['easy_questions_added'] = len(easy_questions)
    existing_data['metadata']['total_questions'] = len(existing_data['queries'])
    
    # Save updated queries
    backup_file = f'data/queries_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
    print(f"💾 Creating backup: {backup_file}")
    with open('data/queries.yaml', 'r') as f:
        with open(backup_file, 'w') as backup:
            backup.write(f.read())
    
    print("💾 Saving updated queries...")
    with open('data/queries.yaml', 'w') as f:
        yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Added {len(easy_questions)} easy questions to queries.yaml")
    print(f"📊 Total questions: {len(existing_data['queries'])}")
    
    # Print summary of easy questions
    print("\n📋 Easy Questions Added:")
    for i, q in enumerate(easy_questions, 1):
        print(f"  {i}. {q['question']}")
        print(f"     Answer: {q['truth']}")
        print()

def main():
    """Main function"""
    print("🚀 Adding Easy Questions to Token Analytics Benchmark")
    print("=" * 60)
    
    # Check if data files exist
    required_files = ['data/sol_daily.csv', 'data/eth_daily.csv', 'data/tao_daily.csv', 'data/queries.yaml']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Error: {file} not found")
            print("Please ensure all data files are present")
            return
    
    add_easy_questions_to_queries()
    
    print("🎉 Easy questions added successfully!")
    print("\nNext steps:")
    print("1. Run evaluation: python scripts/run_complete_evaluation.py")
    print("2. Test with your AI agent")
    print("3. Compare performance on easy vs hard questions")

if __name__ == "__main__":
    main() 