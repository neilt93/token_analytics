#!/usr/bin/env python3
"""
Run ChatGPT Evaluation
Simple script to evaluate ChatGPT with your API key
"""

import sys
import os
import json
import time
import requests
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import TokenAnalyticsEvaluator

# Load environment variables
load_dotenv()

def get_chatgpt_response(question, api_key):
    """
    Get response from ChatGPT
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a financial data analyst. Answer questions about cryptocurrency price data accurately and concisely. Provide specific numbers and percentages when asked."
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            "temperature": 0.1
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return f"Error: API returned {response.status_code}"
            
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return f"Error: {str(e)}"

def run_chatgpt_evaluation(api_key):
    """
    Run complete evaluation for ChatGPT
    """
    print("🤖 CHATGPT EVALUATION")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Get all queries
    queries = evaluator.queries['queries']
    
    print(f"📋 Found {len(queries)} benchmark queries")
    print("🔄 Collecting responses from ChatGPT...")
    print()
    
    # Collect responses
    responses = {}
    for i, query in enumerate(queries, 1):
        question = query['question']
        query_id = query['id']
        
        print(f"[{i:2d}/{len(queries)}] {query_id}: {question[:60]}...")
        
        # Get response from ChatGPT
        response = get_chatgpt_response(question, api_key)
        responses[query_id] = response
        
        # Show response preview
        print(f"    Response: {response[:80]}...")
        print()
        
        # Rate limiting - be nice to the API
        time.sleep(1)
    
    # Save raw responses
    print("💾 Saving raw responses...")
    with open("test/chatgpt_raw_responses.json", 'w') as f:
        json.dump(responses, f, indent=2)
    
    # Run evaluation
    print("📊 Running evaluation...")
    summary = evaluator.run_evaluation(responses, "ChatGPT")
    
    # Print results
    print("\n" + "=" * 60)
    evaluator.print_summary(summary)
    
    # Save results
    evaluator.save_results(summary, "test/chatgpt_evaluation_results.json")
    
    print(f"\n📄 Results saved to: test/chatgpt_evaluation_results.json")
    print(f"📄 Raw responses saved to: test/chatgpt_raw_responses.json")
    
    return summary

def main():
    """
    Main function
    """
    print("🚀 ChatGPT Token Analytics Evaluation")
    print("=" * 60)
    
    # Try to get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OpenAI API key found!")
        print("Please create a .env file with your API key:")
        print("1. Copy env_example.txt to .env")
        print("2. Replace 'sk-your-api-key-here' with your actual API key")
        print("3. Run this script again")
        return
    
    if not api_key.startswith("sk-"):
        print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    try:
        # Run evaluation
        summary = run_chatgpt_evaluation(api_key)
        
        # Show final summary
        print("\n" + "🎉 EVALUATION COMPLETE!")
        print("=" * 60)
        print(f"✅ ChatGPT achieved {summary['accuracy_percentage']:.1f}% accuracy")
        print(f"📊 Correct answers: {summary['correct_answers']}/{summary['total_queries']}")
        print(f"❌ Hallucinations: {summary['hallucination_count']} ({summary['hallucination_rate']:.1f}%)")
        print(f"📈 Average error: {summary['average_absolute_error']:.2f}")
        
        # Performance rating
        if summary['accuracy_percentage'] >= 90:
            rating = "🏆 EXCELLENT"
        elif summary['accuracy_percentage'] >= 80:
            rating = "🥇 GREAT"
        elif summary['accuracy_percentage'] >= 70:
            rating = "🥈 GOOD"
        elif summary['accuracy_percentage'] >= 60:
            rating = "🥉 FAIR"
        else:
            rating = "⚠️  NEEDS IMPROVEMENT"
        
        print(f"\n{rating} - {summary['accuracy_percentage']:.1f}% accuracy")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")

if __name__ == "__main__":
    main() 