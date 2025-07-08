#!/usr/bin/env python3
"""
Example usage of the Token Analytics Evaluation System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import TokenAnalyticsEvaluator

def main():
    """Example of how to evaluate an AI agent"""
    
    print("🚀 Token Analytics Evaluation - Example Usage")
    print("=" * 60)
    
    # Initialize the evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Example agent responses (replace with your actual agent responses)
    agent_responses = {
        'pct_tao_above_400': "TAO was above $400 for 9.7% of the days in the 30-day period.",
        'pct_sol_above_150': "SOL was above $150 for 45.2% of the days.",
        'pct_eth_above_2500': "ETH was above $2500 for 64.5% of the days.",
        'sol_price_change_30d': "SOL's price decreased by 1.16% over the 30-day period.",
        'eth_price_change_30d': "ETH's price increased by 2.31% over the 30-day period.",
        'tao_price_change_30d': "TAO's price decreased by 16.59% over the 30-day period.",
        'highest_avg_volume': "ETH had the highest average daily volume.",
        'total_volume_ranking': "Ranked by total volume: ETH, SOL, TAO.",
        'eth_highest_close_date': "ETH had its highest close on 2025-06-11.",
        'sol_lowest_close_date': "SOL had its lowest close on 2025-06-23.",
        'rank_by_avg_close': "Ranked by average close price: ETH, TAO, SOL.",
        'most_volatile_token': "TAO was the most volatile token during this period.",
        'sol_volatility_range': "SOL's price range was $33.15 over the period.",
        'best_performer_30d': "ETH was the best performer over the 30-day period.",
        'worst_performer_30d': "TAO was the worst performer over the 30-day period."
    }
    
    # Run the evaluation
    print("📊 Evaluating agent responses...")
    summary = evaluator.run_evaluation(agent_responses, "Example Agent")
    
    # Print the results
    evaluator.print_summary(summary)
    
    # Save results to file
    evaluator.save_results(summary, "example_evaluation_results.json")
    
    print("\n💡 To evaluate your own agent:")
    print("1. Replace the agent_responses dictionary with your agent's responses")
    print("2. Change 'Example Agent' to your agent's name")
    print("3. Run this script again")
    
    print("\n📋 Available query IDs:")
    for query in evaluator.queries['queries']:
        print(f"   • {query['id']}: {query['question']}")

if __name__ == "__main__":
    main() 