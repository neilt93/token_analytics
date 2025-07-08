#!/usr/bin/env python3
"""
Setup Environment Variables
Helps you create a .env file with your API keys
"""

import os
import shutil

def setup_env_file():
    """
    Create .env file from template
    """
    print("🔧 Setting up environment variables")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Copy template
    if os.path.exists('env_example.txt'):
        shutil.copy('env_example.txt', '.env')
        print("✅ Created .env file from template")
    else:
        print("❌ env_example.txt not found!")
        return
    
    # Get API keys from user
    print("\n🔑 Enter your API keys (press Enter to skip):")
    print("-" * 40)
    
    # Perplexity API key
    perplexity_key = input("Perplexity API key (starts with pplx-): ").strip()
    if perplexity_key:
        update_env_file('PERPLEXITY_API_KEY', perplexity_key)
        print("✅ Perplexity API key saved")
    
    # OpenAI API key
    openai_key = input("OpenAI API key (starts with sk-): ").strip()
    if openai_key:
        update_env_file('OPENAI_API_KEY', openai_key)
        print("✅ OpenAI API key saved")
    
    # Anthropic API key
    anthropic_key = input("Anthropic API key (starts with sk-ant-): ").strip()
    if anthropic_key:
        update_env_file('ANTHROPIC_API_KEY', anthropic_key)
        print("✅ Anthropic API key saved")
    
    print("\n🎉 Environment setup complete!")
    print("You can now run the evaluation scripts without entering API keys each time.")

def update_env_file(key, value):
    """
    Update a specific key in .env file
    """
    if not os.path.exists('.env'):
        return
    
    # Read current .env file
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update the specific key
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            updated = True
            break
    
    # If key wasn't found, add it
    if not updated:
        lines.append(f'{key}={value}\n')
    
    # Write back to file
    with open('.env', 'w') as f:
        f.writelines(lines)

def check_env_setup():
    """
    Check if environment is properly set up
    """
    print("🔍 Checking environment setup...")
    print("=" * 40)
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_keys = {
        'PERPLEXITY_API_KEY': 'Perplexity',
        'OPENAI_API_KEY': 'OpenAI', 
        'ANTHROPIC_API_KEY': 'Anthropic'
    }
    
    found_keys = []
    for key, name in api_keys.items():
        value = os.getenv(key)
        if value and value != f'{key.lower().replace("_", "-")}-your-api-key-here':
            print(f"✅ {name} API key found")
            found_keys.append(name)
        else:
            print(f"❌ {name} API key not configured")
    
    if found_keys:
        print(f"\n🎉 Ready to evaluate: {', '.join(found_keys)}")
        return True
    else:
        print("\n⚠️  No API keys configured!")
        return False

def main():
    """
    Main function
    """
    print("🚀 LLM Evaluation Environment Setup")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Setup .env file with API keys")
        print("2. Check current environment setup")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            setup_env_file()
        elif choice == '2':
            check_env_setup()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 