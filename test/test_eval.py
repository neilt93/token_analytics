#!/usr/bin/env python3
"""
Simple test script to verify the evaluation system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import TokenAnalyticsEvaluator

def test_evaluation():
    """Test the evaluation system with sample responses"""
    
    print("🧪 Testing Token Analytics Evaluation System")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Sample agent responses (some correct, some incorrect)
    test_responses = {
        'pct_tao_above_400': "TAO was above $400 for approximately 9.7% of the days.",
        'pct_sol_above_150': "SOL was above $150 for about 45% of the days.",
        'pct_eth_above_2500': "ETH was above $2500 for roughly 65% of the days.",
        'sol_price_change_30d': "SOL's price decreased by about 1.2% over the 30-day period.",
        'eth_price_change_30d': "ETH's price increased by approximately 2.3% over the 30-day period.",
        'tao_price_change_30d': "TAO's price decreased by about 16.6% over the 30-day period.",
        'highest_avg_volume': "ETH had the highest average daily volume.",
        'total_volume_ranking': "Ranked by total volume: ETH, SOL, TAO.",
        'eth_highest_close_date': "ETH had its highest close on 2025-06-11.",
        'sol_lowest_close_date': "SOL had its lowest close on 2025-06-23.",
        'rank_by_avg_close': "Ranked by average close price: ETH, TAO, SOL.",
        'most_volatile_token': "TAO was the most volatile token.",
        'sol_volatility_range': "SOL's price range was approximately $33.15.",
        'best_performer_30d': "ETH was the best performer over the 30-day period.",
        'worst_performer_30d': "TAO was the worst performer over the 30-day period."
    }
    
    # Run evaluation
    print("📊 Running evaluation...")
    summary = evaluator.run_evaluation(test_responses, "Test Agent")
    
    # Print results
    evaluator.print_summary(summary)
    
    # Save results
    evaluator.save_results(summary, "test_evaluation_results.json")
    
    print("\n✅ Test completed successfully!")
    print("💡 You can now use this system to evaluate real AI agents.")

if __name__ == "__main__":
    test_evaluation() 