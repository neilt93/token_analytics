import pandas as pd
import os
from tabulate import tabulate

def pretty_print_csv_data(csv_file):
    """
    Pretty print data from a CSV file with formatted output
    
    Args:
        csv_file (str): Path to the CSV file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Get token name from filename
        token_name = os.path.basename(csv_file).replace('_daily.csv', '').upper()
        
        print(f"\n{'='*80}")
        print(f"📊 {token_name} TOKEN DATA")
        print(f"{'='*80}")
        
        # Format the data for better display
        df_display = df.copy()
        df_display['date'] = pd.to_datetime(df_display['date']).dt.strftime('%Y-%m-%d')
        
        # Format price columns to 2 decimal places
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            df_display[col] = df_display[col].apply(lambda x: f"${x:.2f}")
        
        # Format volume to millions/billions for readability
        def format_volume(volume):
            if volume >= 1e9:
                return f"${volume/1e9:.2f}B"
            elif volume >= 1e6:
                return f"${volume/1e6:.2f}M"
            else:
                return f"${volume:.0f}"
        
        df_display['volume'] = df['volume'].apply(format_volume)
        
        # Display first 10 rows
        print(f"\n📈 First 10 days of data:")
        print(tabulate(df_display.head(10), headers='keys', tablefmt='grid', showindex=False))
        
        # Display last 5 rows
        print(f"\n📉 Last 5 days of data:")
        print(tabulate(df_display.tail(5), headers='keys', tablefmt='grid', showindex=False))
        
        # Summary statistics
        print(f"\n📊 Summary Statistics:")
        print(f"   • Total days: {len(df)}")
        print(f"   • Date range: {df_display['date'].iloc[0]} to {df_display['date'].iloc[-1]}")
        
        # Calculate some basic stats
        close_prices = df['close']
        volumes = df['volume']
        
        print(f"   • Price range: ${close_prices.min():.2f} - ${close_prices.max():.2f}")
        print(f"   • Average price: ${close_prices.mean():.2f}")
        print(f"   • Average volume: {format_volume(volumes.mean())}")
        print(f"   • Total volume: {format_volume(volumes.sum())}")
        
        # Calculate price change
        price_change = ((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]) * 100
        print(f"   • Price change: {price_change:+.2f}%")
        
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

def main():
    """
    Main function to pretty print all token data
    """
    print("🚀 TOKEN ANALYTICS DATASET - PRETTY PRINT")
    print("=" * 80)
    print("📋 This is REAL data fetched from CoinGecko API (not synthetic)")
    print("=" * 80)
    
    # List of CSV files in data directory
    csv_files = [
        'data/sol_daily.csv',
        'data/eth_daily.csv', 
        'data/tao_daily.csv'
    ]
    
    # Check if files exist and print data
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            pretty_print_csv_data(csv_file)
        else:
            print(f"\n❌ File not found: {csv_file}")
    
    print(f"\n{'='*80}")
    print("✅ Data display complete!")
    print("💡 This real market data can be used to test AI agents on questions like:")
    print("   • 'What percentage of days did SOL close above $150?'")
    print("   • 'How much did ETH price change over the last 30 days?'")
    print("   • 'Which token had the highest volume on average?'")
    print("   • 'Compare the volatility of SOL vs ETH vs TAO'")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 