#!/usr/bin/env python3
"""
Real LLM Integration Example
Shows how to connect to actual LLM APIs and evaluate them
"""

import sys
import os
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import TokenAnalyticsEvaluator

# Uncomment and configure the APIs you want to use
# import openai
# import requests

class LLMIntegration:
    def __init__(self):
        self.evaluator = TokenAnalyticsEvaluator()
        
    def get_chatgpt_response(self, question, api_key=None):
        """
        Get response from OpenAI ChatGPT
        Requires: pip install openai
        """
        try:
            # Uncomment and configure your OpenAI API key
            # openai.api_key = api_key or "your-openai-api-key"
            
            # response = openai.ChatCompletion.create(
            #     model="gpt-4",
            #     messages=[
            #         {"role": "system", "content": "You are a financial data analyst. Answer questions about cryptocurrency price data accurately and concisely."},
            #         {"role": "user", "content": question}
            #     ],
            #     temperature=0.1
            # )
            # return response.choices[0].message.content
            
            # Placeholder response for demo
            return f"ChatGPT response to: {question[:50]}..."
            
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")
            return "Error: Could not get ChatGPT response"
    
    def get_perplexity_response(self, question, api_key=None):
        """
        Get response from Perplexity AI
        Requires: pip install requests
        """
        try:
            # Uncomment and configure your Perplexity API key
            # headers = {
            #     "Authorization": f"Bearer {api_key or 'your-perplexity-api-key'}",
            #     "Content-Type": "application/json"
            # }
            # 
            # data = {
            #     "model": "llama-3.1-sonar-small-128k-online",
            #     "messages": [
            #         {"role": "system", "content": "You are a financial data analyst. Answer questions about cryptocurrency price data accurately and concisely."},
            #         {"role": "user", "content": question}
            #     ]
            # }
            # 
            # response = requests.post(
            #     "https://api.perplexity.ai/chat/completions",
            #     headers=headers,
            #     json=data
            # )
            # 
            # return response.json()["choices"][0]["message"]["content"]
            
            # Placeholder response for demo
            return f"Perplexity response to: {question[:50]}..."
            
        except Exception as e:
            print(f"Error calling Perplexity API: {e}")
            return "Error: Could not get Perplexity response"
    
    def get_anthropic_response(self, question, api_key=None):
        """
        Get response from Anthropic Claude
        Requires: pip install anthropic
        """
        try:
            # Uncomment and configure your Anthropic API key
            # import anthropic
            # client = anthropic.Anthropic(api_key=api_key or "your-anthropic-api-key")
            # 
            # response = client.messages.create(
            #     model="claude-3-sonnet-20240229",
            #     max_tokens=1000,
            #     messages=[
            #         {"role": "user", "content": f"You are a financial data analyst. Answer this question about cryptocurrency price data accurately and concisely: {question}"}
            #     ]
            # )
            # 
            # return response.content[0].text
            
            # Placeholder response for demo
            return f"Claude response to: {question[:50]}..."
            
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return "Error: Could not get Claude response"
    
    def collect_responses_from_llm(self, llm_name, api_key=None):
        """
        Collect responses from a specific LLM for all benchmark queries
        """
        print(f"🤖 Collecting responses from {llm_name}...")
        
        responses = {}
        queries = self.evaluator.queries['queries']
        
        for i, query in enumerate(queries, 1):
            question = query['question']
            query_id = query['id']
            
            print(f"  [{i}/{len(queries)}] Query: {query_id}")
            
            # Get response based on LLM type
            if llm_name.lower() == "chatgpt":
                response = self.get_chatgpt_response(question, api_key)
            elif llm_name.lower() == "perplexity":
                response = self.get_perplexity_response(question, api_key)
            elif llm_name.lower() == "claude":
                response = self.get_anthropic_response(question, api_key)
            else:
                response = f"Unknown LLM: {llm_name}"
            
            responses[query_id] = response
            
            # Rate limiting - be nice to APIs
            time.sleep(1)
        
        return responses
    
    def run_full_evaluation(self, llm_name, api_key=None):
        """
        Run complete evaluation for a specific LLM
        """
        print(f"🚀 Starting evaluation for {llm_name}")
        print("=" * 60)
        
        # Collect responses
        responses = self.collect_responses_from_llm(llm_name, api_key)
        
        # Save raw responses
        with open(f"test/{llm_name.lower()}_raw_responses.json", 'w') as f:
            json.dump(responses, f, indent=2)
        
        # Run evaluation
        print(f"\n📊 Evaluating {llm_name} responses...")
        summary = self.evaluator.run_evaluation(responses, llm_name)
        
        # Print results
        self.evaluator.print_summary(summary)
        
        # Save results
        self.evaluator.save_results(summary, f"test/{llm_name.lower()}_evaluation_results.json")
        
        return summary
    
    def compare_multiple_llms(self, llm_configs):
        """
        Compare multiple LLMs side by side
        llm_configs = [{"name": "ChatGPT", "api_key": "..."}, ...]
        """
        print("🏆 MULTI-LLM COMPARISON")
        print("=" * 80)
        
        results = {}
        
        for config in llm_configs:
            llm_name = config["name"]
            api_key = config.get("api_key")
            
            try:
                summary = self.run_full_evaluation(llm_name, api_key)
                results[llm_name] = summary
                
                print(f"\n✅ Completed evaluation for {llm_name}")
                
            except Exception as e:
                print(f"❌ Error evaluating {llm_name}: {e}")
                continue
        
        # Generate comparison report
        self.generate_comparison_report(results)
        
        return results
    
    def generate_comparison_report(self, results):
        """
        Generate a detailed comparison report
        """
        if not results:
            print("No results to compare!")
            return
        
        print("\n" + "=" * 80)
        print("📊 COMPARISON REPORT")
        print("=" * 80)
        
        # Sort by accuracy
        sorted_results = sorted(results.items(), key=lambda x: x[1]['accuracy_percentage'], reverse=True)
        
        # Print comparison table
        print(f"{'LLM':<15} {'Accuracy':<10} {'Correct':<12} {'Hallucinations':<15} {'Avg Error':<10}")
        print("-" * 80)
        
        for llm_name, summary in sorted_results:
            print(f"{llm_name:<15} {summary['accuracy_percentage']:<10.1f}% {summary['correct_answers']:<12}/{summary['total_queries']} {summary['hallucination_count']:<15} ({summary['hallucination_rate']:.1f}%) {summary['average_absolute_error']:<10.2f}")
        
        # Winner
        winner = sorted_results[0]
        print(f"\n🏆 Winner: {winner[0]} with {winner[1]['accuracy_percentage']:.1f}% accuracy!")
        
        # Save comparison report
        comparison_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'winner': winner[0],
            'winner_accuracy': winner[1]['accuracy_percentage']
        }
        
        with open("test/llm_comparison_report.json", 'w') as f:
            json.dump(comparison_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test/llm_comparison_report.json")

def main():
    """
    Main function - run this to evaluate LLMs
    """
    print("🤖 LLM Evaluation System")
    print("=" * 50)
    
    # Initialize
    llm_integration = LLMIntegration()
    
    # Example: Evaluate a single LLM
    print("\n1️⃣ Single LLM Evaluation")
    print("-" * 30)
    
    # Uncomment and configure your API keys
    # summary = llm_integration.run_full_evaluation("ChatGPT", "your-openai-api-key")
    
    # Example: Compare multiple LLMs
    print("\n2️⃣ Multi-LLM Comparison")
    print("-" * 30)
    
    # Configure your LLMs here
    llm_configs = [
        # {"name": "ChatGPT", "api_key": "your-openai-api-key"},
        # {"name": "Perplexity", "api_key": "your-perplexity-api-key"},
        # {"name": "Claude", "api_key": "your-anthropic-api-key"},
    ]
    
    # Uncomment to run comparison
    # if llm_configs:
    #     llm_integration.compare_multiple_llms(llm_configs)
    # else:
    #     print("Please configure LLM API keys in the script first!")
    
    print("\n📝 To use this script:")
    print("1. Install required packages: pip install openai anthropic requests")
    print("2. Add your API keys to the llm_configs list")
    print("3. Uncomment the evaluation calls")
    print("4. Run: python real_llm_integration.py")

if __name__ == "__main__":
    main() 