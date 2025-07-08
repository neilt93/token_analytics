import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

def fetch_token_ohlcv_data(token_id, days=30):
    """
    Fetch daily OHLCV data for a specific token using CoinGecko API
    
    Args:
        token_id (str): CoinGecko token ID (e.g., 'solana', 'ethereum', 'bittensor')
        days (int): Number of days of data to fetch (default: 30)
    
    Returns:
        pandas.DataFrame: DataFrame with columns [date, open, high, low, close, volume]
    """
    # CoinGecko market chart endpoint (no API key required)
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
    
    # Parameters for the API request
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }
    
    try:
        print(f"Fetching data for {token_id}...")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Extract OHLCV data from response
        prices = data['prices']  # [timestamp, price] pairs
        volumes = data['total_volumes']  # [timestamp, volume] pairs
        
        # Create DataFrame from the data
        df = pd.DataFrame(prices, columns=['timestamp', 'close'])
        
        # Convert timestamp to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Add volume data
        volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        df['volume'] = volume_df['volume']
        
        # For daily data, we'll use the close price for open/high/low since CoinGecko doesn't provide full OHLC
        # In a real scenario, you might want to use a different endpoint or service for full OHLC data
        df['open'] = df['close'].shift(1).fillna(df['close'])
        df['high'] = df['close']  # Using close as high for simplicity
        df['low'] = df['close']   # Using close as low for simplicity
        
        # Select and reorder columns
        result_df = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
        
        # Remove the first row since it will have NaN for open
        result_df = result_df.dropna().reset_index(drop=True)
        
        return result_df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {token_id}: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing response for {token_id}: {e}")
        return None

def save_token_data_to_csv(df, token_symbol):
    """
    Save token data to a CSV file
    
    Args:
        df (pandas.DataFrame): DataFrame with OHLCV data
        token_symbol (str): Token symbol for filename
    """
    filename = f"{token_symbol.lower()}_daily.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")

def main():
    """
    Main function to fetch and save token data
    """
    # Define tokens to fetch (CoinGecko IDs and their symbols)
    tokens = {
        'solana': 'SOL',
        'ethereum': 'ETH', 
        'bittensor': 'TAO'
    }
    
    print("=== Token Analytics Dataset Generator ===")
    print("Fetching daily OHLCV data from CoinGecko API...")
    print()
    
    # Fetch data for each token
    for token_id, symbol in tokens.items():
        print(f"Processing {symbol} ({token_id})...")
        
        # Fetch data with rate limiting to be respectful to the API
        df = fetch_token_ohlcv_data(token_id, days=30)
        
        if df is not None and not df.empty:
            # Save to CSV
            save_token_data_to_csv(df, symbol)
            
            # Print sample data
            print(f"\nSample data for {symbol}:")
            print(df.head().to_string(index=False))
            print(f"Total rows: {len(df)}")
            print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
            print("-" * 80)
        else:
            print(f"Failed to fetch data for {symbol}")
        
        # Rate limiting - wait 1 second between requests
        time.sleep(1)
    
    print("\n=== Dataset Generation Complete ===")
    print("Generated CSV files:")
    for symbol in tokens.values():
        print(f"  - {symbol.lower()}_daily.csv")

if __name__ == "__main__":
    main() 