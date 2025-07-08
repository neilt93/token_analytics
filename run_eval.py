#!/usr/bin/env python3
"""
Simple Evaluation Runner
Run LLM evaluations using environment variables
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_perplexity_eval():
    """Run Perplexity evaluation"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in .env file")
        print("Run: python setup_env.py to configure your API keys")
        return
    
    print("🤖 Running Perplexity evaluation...")
    os.system(f"python test/run_perplexity_eval.py")

def main():
    """Main function"""
    print("🚀 LLM Evaluation Runner")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Run: python setup_env.py to set up your environment")
        return
    
    # Check available API keys
    available_llms = []
    
    if os.getenv('PERPLEXITY_API_KEY'):
        available_llms.append('Perplexity')
    if os.getenv('OPENAI_API_KEY'):
        available_llms.append('OpenAI')
    if os.getenv('ANTHROPIC_API_KEY'):
        available_llms.append('Anthropic')
    
    if not available_llms:
        print("❌ No API keys found in .env file")
        print("Run: python setup_env.py to configure your API keys")
        return
    
    print(f"✅ Available LLMs: {', '.join(available_llms)}")
    print()
    
    # Show options
    print("Choose an evaluation to run:")
    if 'Perplexity' in available_llms:
        print("1. Perplexity AI")
    if 'OpenAI' in available_llms:
        print("2. OpenAI (ChatGPT)")
    if 'Anthropic' in available_llms:
        print("3. Anthropic (Claude)")
    print("4. Setup/Check environment")
    
    choice = input("\nEnter choice: ").strip()
    
    if choice == '1' and 'Perplexity' in available_llms:
        run_perplexity_eval()
    elif choice == '2' and 'OpenAI' in available_llms:
        print("🔄 OpenAI evaluation not implemented yet")
    elif choice == '3' and 'Anthropic' in available_llms:
        print("🔄 Anthropic evaluation not implemented yet")
    elif choice == '4':
        os.system("python setup_env.py")
    else:
        print("❌ Invalid choice or LLM not available")

if __name__ == "__main__":
    main() 