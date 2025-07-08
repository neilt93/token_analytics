#!/usr/bin/env python3
"""
Test Perplexity AI Only
Simple script to test Perplexity with your API key from .env
"""

import sys
import os
import json
import time
import requests
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from eval import TokenAnalyticsEvaluator

# Load environment variables
load_dotenv()

def get_perplexity_response(question, api_key):
    """Get response from Perplexity AI"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar-reasoning",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a financial data analyst. Answer questions about cryptocurrency price data accurately and concisely. Provide specific numbers and percentages when asked."
                },
                {
                    "role": "user", 
                    "content": question
                }
            ]
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return f"Error: API returned {response.status_code}"
            
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        return f"Error: {str(e)}"

def main():
    """Main function"""
    print("🤖 PERPLEXITY AI TEST")
    print("=" * 40)
    
    # Get API key from environment
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in .env file!")
        print("Please create a .env file with your API key:")
        print("1. Create a .env file in this directory")
        print("2. Add: PERPLEXITY_API_KEY=pplx-your-api-key-here")
        print("3. Replace 'pplx-your-api-key-here' with your actual API key")
        return
    
    if not api_key.startswith("pplx-"):
        print("⚠️  Warning: Perplexity API keys usually start with 'pplx-'")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    print("\n🔄 Testing Perplexity...")
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    queries = evaluator.queries['queries']
    
    # Collect responses
    responses = {}
    for i, query in enumerate(queries, 1):
        question = query['question']
        query_id = query['id']
        
        print(f"[{i:2d}/{len(queries)}] {query_id}")
        
        # Get response from Perplexity
        response = get_perplexity_response(question, api_key)
        responses[query_id] = response
        
        # Show response preview
        print(f"    Response: {response[:80]}...")
        print()
        
        # Rate limiting - longer delay for reasoning model
        time.sleep(2)
    
    # Run evaluation
    print("📊 Running evaluation...")
    summary = evaluator.run_evaluation(responses, "Perplexity AI")
    
    # Print results
    print("\n" + "=" * 60)
    evaluator.print_summary(summary)
    
    # Save results
    evaluator.save_results(summary, "perplexity_results.json")
    print(f"\n📄 Results saved to: perplexity_results.json")
    
    # Performance rating
    accuracy = summary['accuracy_percentage']
    if accuracy >= 90:
        rating = "🏆 EXCELLENT"
    elif accuracy >= 80:
        rating = "🥇 GREAT"
    elif accuracy >= 70:
        rating = "🥈 GOOD"
    elif accuracy >= 60:
        rating = "🥉 FAIR"
    else:
        rating = "⚠️  NEEDS IMPROVEMENT"
    
    print(f"\n{rating} - {accuracy:.1f}% accuracy")

if __name__ == "__main__":
    main() 