#!/usr/bin/env python3
"""
Dynamic Data Generator
Generates fresh CSV data for token analytics evaluation
"""

import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class DynamicDataGenerator:
    """Generates dynamic CSV data for token analytics"""
    
    def __init__(self, output_dir: str = 'data'):
        self.output_dir = output_dir
        # Updated token list to include all tokens needed for the new queries
        self.tokens = [
            'ethereum',      # ETH
            'solana',        # SOL
            'bittensor',     # TAO
            'bitcoin',       # BTC
            'cardano',       # ADA
            'avalanche-2',   # AVAX
            'matic-network', # MATIC
            'uniswap',       # UNI
            'dogecoin',      # DOGE
            'binancecoin',   # BNB
            'polkadot'       # DOT
        ]
        self.token_symbols = ['ETH', 'SOL', 'TAO', 'BTC', 'ADA', 'AVAX', 'MATIC', 'UNI', 'DOGE', 'BNB', 'DOT']
        
    def fetch_coingecko_data(self, token_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Fetch data from CoinGecko API with retry logic"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        # Load API key
        import os
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('COINGECKO_API_KEY')
        
        if api_key:
            print(f"🔑 Using CoinGecko API key: {api_key[:10]}...")
        else:
            quit("No CoinGecko API key found")
        
        for attempt in range(max_retries):
            try:
                print(f"🔗 Fetching real data from CoinGecko for {token_id}... (attempt {attempt + 1}/{max_retries})")
                url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
                
                # CoinGecko API key goes in headers, not params
                headers = {}
                if api_key:
                    headers['x-cg-demo-api-key'] = api_key
                    print(f"🔑 Added API key to headers")
                
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 429:  # Rate limit
                    print(f"⚠️  Rate limit hit for {token_id}, waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                    
                response.raise_for_status()
                
                data = response.json()
                
                # Extract price data
                prices = data['prices']
                volumes = data['total_volumes']
                
                print(f"✅ Received {len(prices)} price points and {len(volumes)} volume points")
                
                # Convert to DataFrame
                df = pd.DataFrame(prices, columns=['timestamp', 'close'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Add volume data
                volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
                df['volume'] = volume_df['volume']
                
                # For real data, we need to create realistic OHLC
                # Since CoinGecko only provides daily close prices, we'll estimate OHLC
                df['open'] = df['close'].shift(1)
                
                # Create realistic high/low based on close price with some variation
                # This is an approximation since we don't have intraday data
                price_variation = df['close'] * 0.02  # 2% variation
                df['high'] = df['close'] + price_variation * np.random.uniform(0.5, 1.5, len(df))
                df['low'] = df['close'] - price_variation * np.random.uniform(0.5, 1.5, len(df))
                
                # Ensure high >= close >= low
                df['high'] = df[['close', 'high']].max(axis=1)
                df['low'] = df[['close', 'low']].min(axis=1)
                
                # Clean up
                df = df.dropna()
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                
                print(f"✅ Successfully processed real data for {token_id}")
                print(f"   Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
                print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
                
                return df
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limit
                    print(f"⚠️  Rate limit hit for {token_id}, waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"❌ HTTP Error fetching data for {token_id}: {e}")
                    return None
            except Exception as e:
                print(f"❌ Error fetching data for {token_id}: {e}")
                return None
        
        print(f"❌ Failed to fetch data for {token_id} after {max_retries} attempts")
        return None
    

    
    def generate_data(self, days: int = 30) -> Dict[str, pd.DataFrame]:
        """Generate data for all tokens using CoinGecko API"""
        print(f"🔄 Generating data for {days} days...")
        print(f"📊 Fetching data for {len(self.tokens)} tokens: {', '.join(self.token_symbols)}")
        
        data = {}
        
        for token_id, symbol in zip(self.tokens, self.token_symbols):
            print(f"\n📊 Processing {symbol} ({token_id})...")
            
            df = self.fetch_coingecko_data(token_id, days)
            if df is None:
                print(f"❌ Failed to fetch data for {symbol} from CoinGecko API")
                continue
            else:
                print(f"✅ Using REAL CoinGecko data for {symbol}")
            
            # Add delay between API calls to prevent rate limiting
            if symbol != self.token_symbols[-1]:  # Not the last token
                print(f"⏳ Waiting 3 seconds before next API call...")
                time.sleep(3)
            
            if df is not None:
                data[symbol] = df
                print(f"✅ Generated {len(df)} days of data for {symbol}")
            else:
                print(f"❌ Failed to generate data for {symbol}")
        
        return data
    
    def save_csv_files(self, data: Dict[str, pd.DataFrame]):
        """Save data to CSV files"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        for symbol, df in data.items():
            filename = f"{symbol.lower()}_daily.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            df.to_csv(filepath, index=False)
            print(f"💾 Saved {filename} ({len(df)} rows)")
    
    def update_metadata(self, data: Dict[str, pd.DataFrame]):
        """Update metadata about the generated data"""
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'data_points': {symbol: len(df) for symbol, df in data.items()},
            'date_range': {
                symbol: {
                    'start': df['date'].min().isoformat(),
                    'end': df['date'].max().isoformat()
                } for symbol, df in data.items()
            },
            'tokens': list(data.keys())
        }
        
        metadata_file = os.path.join(self.output_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📝 Updated metadata: {metadata_file}")
    
    def run(self, days: int = 30):
        """Main method to generate and save data"""
        print("🚀 DYNAMIC DATA GENERATOR")
        print("=" * 50)
        print(f"📊 Will fetch data for {len(self.tokens)} tokens")
        print(f"📅 Days: {days}")
        print("=" * 50)
        
        # Generate data
        data = self.generate_data(days)
        
        if not data:
            print("❌ No data generated!")
            return False
        
        # Save to CSV files
        self.save_csv_files(data)
        
        # Update metadata
        self.update_metadata(data)
        
        print(f"\n🎉 Data generation completed!")
        print(f"✅ Generated data for {len(data)} tokens")
        print(f"📁 Files saved to: {self.output_dir}")
        
        return True

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dynamic Data Generator')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate')
    
    args = parser.parse_args()
    
    generator = DynamicDataGenerator()
    success = generator.run(days=args.days)
    
    if success:
        print("\n🎉 All done!")
        return 0
    else:
        print("\n❌ Failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 