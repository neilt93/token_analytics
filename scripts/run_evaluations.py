#!/usr/bin/env python3
"""
Combined Evaluation Script
Runs both Perplexity AI and ChatGPT evaluations on the token analytics queries
"""

import sys
import os
import json
import time
import requests
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.eval import TokenAnalyticsEvaluator

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
            "model": "sonar-pro",
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
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Perplexity API Error: {response.status_code} - {response.text}")
            return f"Error: API returned {response.status_code}"
            
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        return f"Error: {str(e)}"

def get_chatgpt_response(question, api_key):
    """Get response from ChatGPT"""
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
            print(f"ChatGPT API Error: {response.status_code} - {response.text}")
            return f"Error: API returned {response.status_code}"
            
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return f"Error: {str(e)}"

def run_perplexity_evaluation(api_key):
    """Run complete evaluation for Perplexity"""
    print("PERPLEXITY AI EVALUATION")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Get all queries
    queries = evaluator.queries['queries']
    
    print(f"Found {len(queries)} benchmark queries")
    print("Collecting responses from Perplexity...")
    print()
    
    # Collect responses
    responses = {}
    for i, query in enumerate(queries, 1):
        question = query['question']
        query_id = query['id']
        
        print(f"[{i:2d}/{len(queries)}] {query_id}: {question[:60]}...")
        
        # Get response from Perplexity
        response = get_perplexity_response(question, api_key)
        responses[query_id] = response
        
        # Show response preview
        print(f"    Response: {response[:80]}...")
        print()
        
        # Rate limiting
        time.sleep(1)
    
    # Save raw responses
    print("Saving raw responses...")
    with open("test/perplexity_raw_responses.json", 'w') as f:
        json.dump(responses, f, indent=2)
    
    # Run evaluation
    print("Running evaluation...")
    summary = evaluator.run_evaluation(responses, "Perplexity AI")
    
    # Print results
    print("\n" + "=" * 60)
    evaluator.print_summary(summary)
    
    # Save results
    evaluator.save_results(summary, "test/perplexity_evaluation_results.json")
    
    print(f"\nResults saved to: test/perplexity_evaluation_results.json")
    print(f"Raw responses saved to: test/perplexity_raw_responses.json")
    
    return summary

def run_chatgpt_evaluation(api_key):
    """Run complete evaluation for ChatGPT"""
    print("CHATGPT EVALUATION")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Get all queries
    queries = evaluator.queries['queries']
    
    print(f"Found {len(queries)} benchmark queries")
    print("Collecting responses from ChatGPT...")
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
        
        # Rate limiting
        time.sleep(1)
    
    # Save raw responses
    print("Saving raw responses...")
    with open("test/chatgpt_raw_responses.json", 'w') as f:
        json.dump(responses, f, indent=2)
    
    # Run evaluation
    print("Running evaluation...")
    summary = evaluator.run_evaluation(responses, "ChatGPT")
    
    # Print results
    print("\n" + "=" * 60)
    evaluator.print_summary(summary)
    
    # Save results
    evaluator.save_results(summary, "test/chatgpt_evaluation_results.json")
    
    print(f"\nResults saved to: test/chatgpt_evaluation_results.json")
    print(f"Raw responses saved to: test/chatgpt_raw_responses.json")
    
    return summary

def main():
    """Main function"""
    print("Combined Token Analytics Evaluation")
    print("=" * 60)
    
    # Get API keys
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not perplexity_key:
        print("ERROR: No Perplexity API key found!")
        print("Please add PERPLEXITY_API_KEY to your .env file")
        return
    
    if not openai_key:
        print("ERROR: No OpenAI API key found!")
        print("Please add OPENAI_API_KEY to your .env file")
        return
    
    try:
        # Run Perplexity evaluation
        print("\n" + "=" * 60)
        perplexity_summary = run_perplexity_evaluation(perplexity_key)
        
        # Run ChatGPT evaluation
        print("\n" + "=" * 60)
        chatgpt_summary = run_chatgpt_evaluation(openai_key)
        
        # Final comparison
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Perplexity AI: {perplexity_summary['accuracy_percentage']:.1f}% accuracy")
        print(f"ChatGPT: {chatgpt_summary['accuracy_percentage']:.1f}% accuracy")
        
        if perplexity_summary['accuracy_percentage'] > chatgpt_summary['accuracy_percentage']:
            print("Perplexity AI wins on accuracy")
        elif chatgpt_summary['accuracy_percentage'] > perplexity_summary['accuracy_percentage']:
            print("ChatGPT wins on accuracy")
        else:
            print("Tie on accuracy")
        
        print("\nAll results saved to test/ directory")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user")
    except Exception as e:
        print(f"\nError during evaluation: {e}")

if __name__ == "__main__":
    main() 