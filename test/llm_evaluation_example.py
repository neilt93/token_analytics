#!/usr/bin/env python3
"""
Example: How to use the Token Analytics Evaluation System with real LLMs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import TokenAnalyticsEvaluator

def get_llm_responses_example():
    """
    Example of how to collect responses from different LLMs
    Replace these with actual API calls to your LLMs
    """
    
    # Example: ChatGPT responses (replace with actual API calls)
    chatgpt_responses = {
        'pct_tao_above_400': "Based on the data, TAO was above $400 for approximately 9.7% of the days in the 30-day period.",
        'pct_sol_above_150': "SOL was above $150 for about 45.2% of the days during this period.",
        'pct_eth_above_2500': "ETH was above $2500 for roughly 64.5% of the days.",
        'sol_price_change_30d': "SOL's price decreased by about 1.16% over the 30-day period.",
        'eth_price_change_30d': "ETH's price increased by approximately 2.31% over the 30-day period.",
        'tao_price_change_30d': "TAO's price decreased by around 16.59% over the 30-day period.",
        'highest_avg_volume': "ETH had the highest average daily volume among the three tokens.",
        'total_volume_ranking': "Ranked by total volume: ETH, SOL, TAO.",
        'eth_highest_close_date': "ETH had its highest close on 2025-06-11.",
        'sol_lowest_close_date': "SOL had its lowest close on 2025-06-23.",
        'rank_by_avg_close': "Ranked by average close price: ETH, TAO, SOL.",
        'most_volatile_token': "TAO was the most volatile token during this period.",
        'sol_volatility_range': "SOL's price range was approximately $33.15 over the period.",
        'best_performer_30d': "ETH was the best performer over the 30-day period.",
        'worst_performer_30d': "TAO was the worst performer over the 30-day period."
    }
    
    # Example: Perplexity responses (replace with actual API calls)
    perplexity_responses = {
        'pct_tao_above_400': "TAO closed above $400 for 9.7% of the trading days.",
        'pct_sol_above_150': "SOL was above $150 for 45.2% of the days.",
        'pct_eth_above_2500': "ETH traded above $2500 for 64.5% of the period.",
        'sol_price_change_30d': "SOL declined by 1.16% over the 30 days.",
        'eth_price_change_30d': "ETH gained 2.31% during the period.",
        'tao_price_change_30d': "TAO fell by 16.59% over the 30-day period.",
        'highest_avg_volume': "ETH had the highest average daily volume.",
        'total_volume_ranking': "Volume ranking: ETH, SOL, TAO.",
        'eth_highest_close_date': "ETH's highest close was on 2025-06-11.",
        'sol_lowest_close_date': "SOL's lowest close occurred on 2025-06-23.",
        'rank_by_avg_close': "Average close ranking: ETH, TAO, SOL.",
        'most_volatile_token': "TAO showed the highest volatility.",
        'sol_volatility_range': "SOL's price range was $33.15.",
        'best_performer_30d': "ETH was the best performing token.",
        'worst_performer_30d': "TAO was the worst performing token."
    }
    
    # Example: Your custom agent responses (replace with actual API calls)
    your_agent_responses = {
        'pct_tao_above_400': "TAO was above $400 for 9.7% of days.",
        'pct_sol_above_150': "SOL was above $150 for 45.2% of days.",
        'pct_eth_above_2500': "ETH was above $2500 for 64.5% of days.",
        'sol_price_change_30d': "SOL decreased by 1.16%.",
        'eth_price_change_30d': "ETH increased by 2.31%.",
        'tao_price_change_30d': "TAO decreased by 16.59%.",
        'highest_avg_volume': "ETH had highest average volume.",
        'total_volume_ranking': "ETH, SOL, TAO by volume.",
        'eth_highest_close_date': "2025-06-11.",
        'sol_lowest_close_date': "2025-06-23.",
        'rank_by_avg_close': "ETH, TAO, SOL by average close.",
        'most_volatile_token': "TAO was most volatile.",
        'sol_volatility_range': "SOL range was $33.15.",
        'best_performer_30d': "ETH was best performer.",
        'worst_performer_30d': "TAO was worst performer."
    }
    
    return {
        'ChatGPT': chatgpt_responses,
        'Perplexity': perplexity_responses,
        'Your Agent': your_agent_responses
    }

def evaluate_multiple_llms():
    """
    Evaluate multiple LLMs and compare their performance
    """
    
    print("🚀 LLM Evaluation Example")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Get responses from different LLMs
    llm_responses = get_llm_responses_example()
    
    # Evaluate each LLM
    results = {}
    for llm_name, responses in llm_responses.items():
        print(f"\n📊 Evaluating {llm_name}...")
        summary = evaluator.run_evaluation(responses, llm_name)
        results[llm_name] = summary
        
        # Print summary
        evaluator.print_summary(summary)
        
        # Save results
        evaluator.save_results(summary, f"test/{llm_name.lower().replace(' ', '_')}_results.json")
    
    # Compare results
    print("\n" + "=" * 80)
    print("🏆 LLM COMPARISON SUMMARY")
    print("=" * 80)
    
    comparison_data = []
    for llm_name, summary in results.items():
        comparison_data.append({
            'LLM': llm_name,
            'Accuracy': f"{summary['accuracy_percentage']:.1f}%",
            'Correct': f"{summary['correct_answers']}/{summary['total_queries']}",
            'Hallucinations': f"{summary['hallucination_count']} ({summary['hallucination_rate']:.1f}%)",
            'Avg Error': f"{summary['average_absolute_error']:.2f}"
        })
    
    # Print comparison table
    print(f"{'LLM':<15} {'Accuracy':<10} {'Correct':<12} {'Hallucinations':<15} {'Avg Error':<10}")
    print("-" * 80)
    for data in comparison_data:
        print(f"{data['LLM']:<15} {data['Accuracy']:<10} {data['Correct']:<12} {data['Hallucinations']:<15} {data['Avg Error']:<10}")
    
    # Find winner
    best_llm = max(results.items(), key=lambda x: x[1]['accuracy_percentage'])
    print(f"\n🏆 Winner: {best_llm[0]} with {best_llm[1]['accuracy_percentage']:.1f}% accuracy!")

def show_how_to_integrate_with_real_apis():
    """
    Show how to integrate with real LLM APIs
    """
    
    print("\n" + "=" * 80)
    print("🔧 HOW TO INTEGRATE WITH REAL LLM APIs")
    print("=" * 80)
    
    print("""
1. OPENAI API (ChatGPT):
   ```python
   import openai
   
   def get_chatgpt_response(question):
       response = openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": question}]
       )
       return response.choices[0].message.content
   ```

2. PERPLEXITY API:
   ```python
   import requests
   
   def get_perplexity_response(question):
       response = requests.post(
           "https://api.perplexity.ai/chat/completions",
           headers={"Authorization": "Bearer YOUR_API_KEY"},
           json={"model": "llama-3.1-sonar-small-128k-online", "messages": [{"role": "user", "content": question}]}
       )
       return response.json()["choices"][0]["message"]["content"]
   ```

3. YOUR CUSTOM AGENT:
   ```python
   def get_your_agent_response(question):
       # Your custom logic here
       return your_agent.answer(question)
   ```

4. COLLECT ALL RESPONSES:
   ```python
   queries = evaluator.queries['queries']
   responses = {}
   
   for query in queries:
       question = query['question']
       responses[query['id']] = get_chatgpt_response(question)
   
   # Evaluate
   summary = evaluator.run_evaluation(responses, "ChatGPT")
   evaluator.print_summary(summary)
   ```
    """)

if __name__ == "__main__":
    # Run the example
    evaluate_multiple_llms()
    
    # Show integration guide
    show_how_to_integrate_with_real_apis() 