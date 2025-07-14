#!/usr/bin/env python3
"""
Dynamic Data Generator
Generates fresh CSV data for token analytics evaluation using ONLY real CoinGecko data
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class DynamicDataGenerator:
    """Generates dynamic CSV data for token analytics using ONLY real data"""
    
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
            'polkadot',      # DOT
            'pepe',          # PEPE
            'fartcoin',      # FARTCOIN
            'shiba-inu',     # SHIB
            'the-graph',     # GRT
            'rootstock',     # RTL
            'modo',          # MODO
            'optimism',      # OP
            'ripple'         # XRP
        ]
        self.token_symbols = ['ETH', 'SOL', 'TAO', 'BTC', 'ADA', 'AVAX', 'MATIC', 'UNI', 'DOGE', 'BNB', 'DOT', 'PEPE', 'FARTCOIN', 'SHIB', 'GRT', 'RTL', 'MODO', 'OP', 'XRP']
        
    def fetch_coingecko_data(self, token_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Fetch ONLY real data from CoinGecko API - no estimation"""
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
                print(f"🔗 Fetching REAL data from CoinGecko for {token_id}... (attempt {attempt + 1}/{max_retries})")
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
                
                # Extract ONLY real data from CoinGecko
                prices = data['prices']
                volumes = data['total_volumes']
                
                print(f"✅ Received {len(prices)} REAL price points and {len(volumes)} REAL volume points")
                
                # Convert to DataFrame with ONLY real data
                df = pd.DataFrame(prices, columns=['timestamp', 'close'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Add ONLY real volume data
                volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
                df['volume'] = volume_df['volume']
                
                # For CoinGecko daily data, we only have close prices and volumes
                # We'll use close price as the primary price and set open/high/low to close
                df['open'] = df['close']  # Use close as open since we don't have intraday data
                df['high'] = df['close']  # Use close as high since we don't have intraday data  
                df['low'] = df['close']   # Use close as low since we don't have intraday data
                
                # Clean up - only keep real data
                df = df.dropna()
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                
                print(f"✅ Successfully processed REAL data for {token_id}")
                print(f"   Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
                print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
                print(f"   Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
                
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
        """Generate data for all tokens using ONLY real CoinGecko data"""
        print(f"🔄 Generating data for {days} days...")
        print(f"📊 Fetching REAL data for {len(self.tokens)} tokens: {', '.join(self.token_symbols)}")
        
        data = {}
        
        for token_id, symbol in zip(self.tokens, self.token_symbols):
            print(f"\n📊 Processing {symbol} ({token_id})...")
            
            df = self.fetch_coingecko_data(token_id, days)
            if df is None:
                print(f"❌ Failed to fetch data for {symbol} from CoinGecko API")
                continue
            else:
                print(f"✅ Using ONLY REAL CoinGecko data for {symbol}")
            
            # Add delay between API calls to prevent rate limiting
            if symbol != self.token_symbols[-1]:  # Not the last token
                print(f"⏳ Waiting 3 seconds before next API call...")
                time.sleep(3)
            
            if df is not None:
                data[symbol] = df
                print(f"✅ Generated {len(df)} days of REAL data for {symbol}")
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
            print(f"💾 Saved {filename} ({len(df)} rows of REAL data)")
    
    def update_metadata(self, data: Dict[str, pd.DataFrame]):
        """Update metadata about the generated data"""
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'data_source': 'CoinGecko API - REAL data only',
            'data_points': {symbol: len(df) for symbol, df in data.items()},
            'date_range': {
                symbol: {
                    'start': df['date'].min().isoformat(),
                    'end': df['date'].max().isoformat()
                } for symbol, df in data.items()
            },
            'tokens': list(data.keys()),
            'note': 'All data is real from CoinGecko API - no estimation or made-up values'
        }
        
        metadata_file = os.path.join(self.output_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📝 Updated metadata: {metadata_file}")
    
    def run(self, days: int = 30):
        """Main method to generate and save data"""
        print("🚀 DYNAMIC DATA GENERATOR - REAL DATA ONLY")
        print("=" * 60)
        print(f"📊 Will fetch REAL data for {len(self.tokens)} tokens")
        print(f"📅 Days: {days}")
        print(f"⚠️  NO estimation or made-up values - ONLY real CoinGecko data")
        print("=" * 60)
        
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
        print(f"✅ Generated REAL data for {len(data)} tokens")
        print(f"📁 Files saved to: {self.output_dir}")
        print(f"⚠️  All data is real from CoinGecko - no estimation used")
        
        return True

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dynamic Data Generator - Real Data Only')
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