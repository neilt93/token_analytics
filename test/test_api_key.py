#!/usr/bin/env python3
"""
Test CoinGecko API Key
Simple script to verify your API key is working
"""

import requests
import os
from dotenv import load_dotenv

def test_api_key():
    """Test if the CoinGecko API key is working"""
    
    print("🔑 Testing CoinGecko API Key")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('COINGECKO_API_KEY')
    
    if not api_key:
        print("❌ No API key found in .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test simple price endpoint
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'ethereum',
        'vs_currencies': 'usd',
        'x_cg_demo_api_key': api_key
    }
    
    try:
        print("\n📡 Making API request...")
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            eth_price = data['ethereum']['usd']
            print(f"✅ API Key Working!")
            print(f"📈 ETH Price: ${eth_price:,.2f}")
            print(f"🔗 Response: {data}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_key() 