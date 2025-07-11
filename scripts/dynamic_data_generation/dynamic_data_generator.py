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
        self.tokens = ['ethereum', 'solana', 'bittensor']  # CoinGecko IDs
        self.token_symbols = ['ETH', 'SOL', 'TAO']
        
    def fetch_coingecko_data(self, token_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Fetch data from CoinGecko API"""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract price data
            prices = data['prices']
            volumes = data['total_volumes']
            
            # Convert to DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'close'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Add volume data
            volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            df['volume'] = volume_df['volume']
            
            # Calculate OHLC from daily data
            df['open'] = df['close'].shift(1)
            df['high'] = df['close']  # Simplified - could be enhanced with intraday data
            df['low'] = df['close']   # Simplified - could be enhanced with intraday data
            
            # Clean up
            df = df.dropna()
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {token_id}: {e}")
            return None
    
    def generate_synthetic_data(self, token_symbol: str, days: int = 30) -> pd.DataFrame:
        """Generate synthetic data for testing when API is unavailable"""
        print(f"Generating synthetic data for {token_symbol}")
        
        # Generate realistic price movements
        np.random.seed(42)  # For reproducibility
        
        # Base prices
        base_prices = {
            'ETH': 2500,
            'SOL': 150,
            'TAO': 350
        }
        
        base_price = base_prices.get(token_symbol, 100)
        
        # Generate price series with realistic volatility
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Random walk with mean reversion
        returns = np.random.normal(0, 0.02, days)  # 2% daily volatility
        prices = [base_price]
        
        for i in range(1, days):
            # Add some mean reversion
            mean_reversion = (base_price - prices[-1]) * 0.01
            new_price = prices[-1] * (1 + returns[i] + mean_reversion)
            prices.append(max(new_price, 0.1))  # Prevent negative prices
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'open': [prices[0]] + prices[:-1],
            'high': prices,  # Simplified
            'low': prices,   # Simplified
            'volume': np.random.lognormal(15, 1, days) * 1000000  # Realistic volumes
        })
        
        return df
    
    def generate_data(self, use_api: bool = True, days: int = 30) -> Dict[str, pd.DataFrame]:
        """Generate data for all tokens"""
        print(f"🔄 Generating data for {days} days...")
        
        data = {}
        
        for token_id, symbol in zip(self.tokens, self.token_symbols):
            print(f"📊 Fetching data for {symbol}...")
            
            if use_api:
                df = self.fetch_coingecko_data(token_id, days)
                if df is None:
                    print(f"⚠️  API failed for {symbol}, using synthetic data")
                    df = self.generate_synthetic_data(symbol, days)
            else:
                df = self.generate_synthetic_data(symbol, days)
            
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
    
    def run(self, use_api: bool = True, days: int = 30):
        """Main method to generate and save data"""
        print("🚀 DYNAMIC DATA GENERATOR")
        print("=" * 50)
        
        # Generate data
        data = self.generate_data(use_api, days)
        
        if not data:
            print("❌ No data generated!")
            return False
        
        # Save to CSV files
        self.save_csv_files(data)
        
        # Update metadata
        self.update_metadata(data)
        
        print(f"\n✅ Successfully generated data for {len(data)} tokens")
        return True

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate dynamic token data')
    parser.add_argument('--api', action='store_true', help='Use CoinGecko API')
    parser.add_argument('--synthetic', action='store_true', help='Use synthetic data')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate')
    
    args = parser.parse_args()
    
    generator = DynamicDataGenerator()
    
    # Default to synthetic if no API key or if explicitly requested
    use_api = args.api and not args.synthetic
    
    success = generator.run(use_api=use_api, days=args.days)
    
    if success:
        print("\n🎉 Data generation completed successfully!")
    else:
        print("\n❌ Data generation failed!")

if __name__ == "__main__":
    main() 