#!/usr/bin/env python3
"""
Test New Queries with LLM-based Evaluation
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval import TokenAnalyticsEvaluator

# Load environment variables
load_dotenv()

def test_new_queries():
    """Test the new queries with sample responses"""
    
    # Initialize evaluator with LLM API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found!")
        print("Please add OPENAI_API_KEY to your .env file")
        return
    
    evaluator = TokenAnalyticsEvaluator(llm_api_key=api_key)
    
    # Test cases for new queries
    test_cases = [
        {
            "query_id": "pct_days_sol_up_eth_down",
            "question": "What percentage of days did SOL close higher while ETH closed lower during the 30-day period from June 9 to July 8 2025?",
            "category": "conditional_threshold",
            "truth": 3.45,
            "agent_response": "Based on the data analysis, SOL closed higher while ETH closed lower on approximately 3.45% of the days during the 30-day period from June 9 to July 8, 2025. This represents 1 out of 29 trading days where this specific condition occurred."
        },
        {
            "query_id": "eth_biggest_single_day_loss",
            "question": "What was ETH's largest single-day percentage loss during the 30-day period?",
            "category": "volatility",
            "truth": -5.62,
            "agent_response": "ETH's largest single-day percentage loss during the 30-day period was -5.62%. This occurred on a day when ETH experienced significant downward pressure in the market."
        },
        {
            "query_id": "sol_days_close_eq_or_above_open",
            "question": "On how many days did SOL close at or above its daily opening price during the 30-day period?",
            "category": "streak_analysis",
            "truth": 14,
            "agent_response": "SOL closed at or above its daily opening price on 14 days during the 30-day period from June 9 to July 8, 2025."
        },
        {
            "query_id": "sol_days_close_above_10dma",
            "question": "What percentage of days did SOL close above its 10-day moving average during the 30-day period?",
            "category": "rolling_stats",
            "truth": 37.93,
            "agent_response": "SOL closed above its 10-day moving average on 37.93% of the days during the 30-day period. This indicates that SOL spent a significant portion of the time above its short-term trend line."
        },
        {
            "query_id": "rank_by_max_intraday_swing",
            "question": "Rank SOL, ETH, and TAO by their largest single-day high-low percentage swing during the 30-day period.",
            "category": "performance_comparison",
            "truth": ["SOL", "ETH", "TAO"],
            "agent_response": "Ranked by their largest single-day high-low percentage swing during the 30-day period: 1. SOL, 2. ETH, 3. TAO. SOL had the highest intraday volatility, followed by ETH, and then TAO."
        },
        {
            "query_id": "pct_days_all_up",
            "question": "What percentage of days did SOL, ETH, and TAO all close higher than the previous day during the 30-day period?",
            "category": "conditional_threshold",
            "truth": 34.48,
            "agent_response": "All three tokens (SOL, ETH, and TAO) closed higher than the previous day on 34.48% of the days during the 30-day period. This represents approximately 10 out of 29 trading days where all three cryptocurrencies experienced positive daily returns."
        }
    ]
    
    print("🧪 Testing New Queries with LLM-based Evaluation")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['query_id']}")
        print(f"Question: {test_case['question']}")
        print(f"Category: {test_case['category']}")
        print(f"Truth: {test_case['truth']}")
        
        # Run evaluation
        result = evaluator.evaluate_agent_response(
            test_case['query_id'],
            test_case['agent_response'],
            "Test Agent"
        )
        
        print(f"Extracted: {result['predicted']}")
        print(f"Correct: {result['correct']}")
        print(f"Error Type: {result['error_type']}")
        print(f"Hallucination: {result['is_hallucination']}")
        
        if result['absolute_error'] is not None:
            print(f"Absolute Error: {result['absolute_error']:.2f}")
        
        print("-" * 40)

def test_with_real_responses():
    """Test with more realistic agent responses"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found!")
        return
    
    evaluator = TokenAnalyticsEvaluator(llm_api_key=api_key)
    
    # More realistic test cases
    realistic_cases = [
        {
            "query_id": "pct_days_sol_up_eth_down",
            "question": "What percentage of days did SOL close higher while ETH closed lower during the 30-day period from June 9 to July 8 2025?",
            "category": "conditional_threshold",
            "truth": 3.45,
            "agent_response": "Based on my analysis of the market data, SOL closed higher while ETH closed lower on about 3.45% of the trading days in the specified period. This represents a relatively rare occurrence where SOL outperformed ETH on the same day."
        },
        {
            "query_id": "eth_biggest_single_day_loss",
            "question": "What was ETH's largest single-day percentage loss during the 30-day period?",
            "category": "volatility",
            "truth": -5.62,
            "agent_response": "ETH experienced its largest single-day loss of -5.62% during the 30-day period. This significant drop occurred during a period of market volatility."
        },
        {
            "query_id": "rank_by_max_intraday_swing",
            "question": "Rank SOL, ETH, and TAO by their largest single-day high-low percentage swing during the 30-day period.",
            "category": "performance_comparison",
            "truth": ["SOL", "ETH", "TAO"],
            "agent_response": "When ranking by maximum intraday swing percentage, the order is: SOL first, followed by ETH, and then TAO. SOL showed the highest intraday volatility among the three tokens."
        }
    ]
    
    print("\n🔄 Testing with Realistic Responses")
    print("=" * 50)
    
    for i, test_case in enumerate(realistic_cases, 1):
        print(f"\n📊 Test {i}: {test_case['query_id']}")
        
        result = evaluator.evaluate_agent_response(
            test_case['query_id'],
            test_case['agent_response'],
            "Realistic Agent"
        )
        
        print(f"Expected: {test_case['truth']}")
        print(f"Extracted: {result['predicted']}")
        print(f"Correct: {result['correct']}")
        print(f"Error: {result['error_type']}")

def main():
    """Main function"""
    print("🤖 Testing New Queries with LLM-based Evaluation")
    print("=" * 60)
    
    # Test basic functionality
    test_new_queries()
    
    # Test with realistic responses
    test_with_real_responses()
    
    print("\n✅ New queries test completed!")

if __name__ == "__main__":
    main() 