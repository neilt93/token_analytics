import pandas as pd
import yaml
import os
import numpy as np
from datetime import datetime, timedelta

def load_token_data():
    """Load all token data from CSV files"""
    data = {}
    for token in ['sol', 'eth', 'tao']:
        filename = f"data/{token}_daily.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['date'] = pd.to_datetime(df['date'])
            data[token.upper()] = df
        else:
            print(f"Warning: {filename} not found")
    return data

def calculate_current_prices(data):
    """Calculate current prices for each token"""
    current_prices = {}
    for token, df in data.items():
        current_prices[token] = df['close'].iloc[-1]
    return current_prices

def calculate_24h_changes(data):
    """Calculate 24-hour price changes"""
    changes = {}
    for token, df in data.items():
        if len(df) >= 2:
            current = df['close'].iloc[-1]
            previous = df['close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            changes[token] = change_pct
    return changes

def calculate_30d_changes(data):
    """Calculate 30-day price changes"""
    changes = {}
    for token, df in data.items():
        if len(df) >= 30:
            current = df['close'].iloc[-1]
            thirty_days_ago = df['close'].iloc[-30]
            change_pct = ((current - thirty_days_ago) / thirty_days_ago) * 100
            changes[token] = change_pct
    return changes

def calculate_average_prices(data):
    """Calculate average prices over the dataset period"""
    avg_prices = {}
    for token, df in data.items():
        avg_prices[token] = df['close'].mean()
    return avg_prices

def calculate_volumes(data):
    """Calculate current and average volumes"""
    volumes = {}
    for token, df in data.items():
        volumes[token] = {
            'current': df['volume'].iloc[-1],
            'average': df['volume'].mean(),
            'total': df['volume'].sum()
        }
    return volumes

def calculate_market_caps(data):
    """Estimate market caps (using volume as proxy since we don't have supply data)"""
    # This is a simplified calculation - in reality you'd need circulating supply
    market_caps = {}
    for token, df in data.items():
        # Using average price * average volume as rough market cap proxy
        avg_price = df['close'].mean()
        avg_volume = df['volume'].mean()
        market_caps[token] = avg_price * avg_volume / 1e6  # Convert to millions
    return market_caps

def calculate_technical_indicators(data):
    """Calculate basic technical indicators"""
    indicators = {}
    
    for token, df in data.items():
        # RSI (simplified 14-period)
        if len(df) >= 14:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators[token] = {
                'rsi': rsi.iloc[-1],
                'price': df['close'].iloc[-1]
            }
    
    return indicators

def calculate_trends(data):
    """Calculate if tokens are trending up or down"""
    trends = {}
    for token, df in data.items():
        if len(df) >= 7:
            # Compare 7-day average to current price
            week_avg = df['close'].tail(7).mean()
            current = df['close'].iloc[-1]
            trends[token] = "up" if current > week_avg else "down"
    return trends

def calculate_volatility(data):
    """Calculate volatility metrics"""
    volatility = {}
    for token, df in data.items():
        returns = df['close'].pct_change().dropna()
        volatility[token] = {
            'std_dev': returns.std() * 100,  # Convert to percentage
            'range': (df['close'].max() - df['close'].min()) / df['close'].min() * 100
        }
    return volatility

def calculate_truth_values():
    """Calculate truth values for new queries"""
    data = load_token_data()
    
    if not data:
        print("No data found. Please ensure CSV files are in the current directory.")
        return
    
    print("🔍 Calculating truth values for new queries...")
    print("=" * 80)
    
    # Calculate various metrics
    current_prices = calculate_current_prices(data)
    changes_24h = calculate_24h_changes(data)
    changes_30d = calculate_30d_changes(data)
    avg_prices = calculate_average_prices(data)
    volumes = calculate_volumes(data)
    market_caps = calculate_market_caps(data)
    indicators = calculate_technical_indicators(data)
    trends = calculate_trends(data)
    volatility = calculate_volatility(data)
    
    # Load the new queries file
    try:
        with open('data/queries_new.yaml', 'r') as f:
            queries = yaml.safe_load(f)
    except FileNotFoundError:
        print("queries_new.yaml not found!")
        return
    
    # Update queries with calculated truth values
    updated_queries = queries.copy()
    
    for query in updated_queries['queries']:
        query_id = query['id']
        question = query['question'].lower()
        
        # Set default truth value
        truth_value = None
        
        # Single token easy queries
        if 'eth_price_current' in query_id:
            truth_value = current_prices.get('ETH')
        elif 'btc_price' in query_id:
            # We don't have BTC data, so this would be null
            truth_value = None
        elif 'tao_24h_change' in query_id:
            truth_value = changes_24h.get('TAO')
        elif 'tao_up_down_today' in query_id:
            change = changes_24h.get('TAO', 0)
            truth_value = "up" if change > 0 else "down"
        elif 'doge_market_cap' in query_id:
            # We don't have DOGE data
            truth_value = None
        elif 'bnb_trading_volume' in query_id:
            # We don't have BNB data
            truth_value = None
        elif 'avalanche_basic_stats' in query_id:
            # We don't have AVAX data
            truth_value = None
        elif 'ada_ath' in query_id:
            # We don't have ADA data
            truth_value = None
            
        # Single token medium queries
        elif 'sol_buy_timing' in query_id:
            # This is subjective, but we can provide current trend
            truth_value = trends.get('SOL', "neutral")
        elif 'btc_avg_price_month' in query_id:
            # We don't have BTC data
            truth_value = None
        elif 'matic_trending' in query_id:
            # We don't have MATIC data
            truth_value = None
        elif 'uniswap_liquidity' in query_id:
            # We don't have UNI data
            truth_value = None
        elif 'cardano_eur_price' in query_id:
            # We don't have Cardano data
            truth_value = None
            
        # Single token hard queries
        elif 'eth_higher_than_opened_june' in query_id:
            # Count days in June where close > open
            eth_data = data['ETH']
            june_data = eth_data[eth_data['date'].dt.month == 6]
            if len(june_data) > 0:
                higher_days = (june_data['close'] > june_data['open']).sum()
                truth_value = higher_days
            else:
                truth_value = None
        elif 'tao_avg_price_month' in query_id:
            truth_value = avg_prices.get('TAO')
        elif 'matic_rsi_now' in query_id:
            # We don't have MATIC data
            truth_value = None
        elif 'dot_macd_crossover' in query_id:
            # We don't have DOT data
            truth_value = None
            
        # Multi-token queries
        elif 'eth_vs_sol_investment' in query_id:
            # Compare 30-day performance
            eth_change = changes_30d.get('ETH', 0)
            sol_change = changes_30d.get('SOL', 0)
            if eth_change > sol_change:
                truth_value = "ETH"
            elif sol_change > eth_change:
                truth_value = "SOL"
            else:
                truth_value = "Equal"
        elif 'btc_eth_prices_today' in query_id:
            # We don't have BTC data
            truth_value = None
            
        # Multi-token hard queries
        elif 'eth_vs_sol_avg_daily_change_year' in query_id:
            # Calculate average daily returns
            eth_data = data['ETH']
            sol_data = data['SOL']
            
            eth_returns = eth_data['close'].pct_change().dropna().mean() * 100
            sol_returns = sol_data['close'].pct_change().dropna().mean() * 100
            
            if eth_returns > sol_returns:
                truth_value = "ETH"
            elif sol_returns > eth_returns:
                truth_value = "SOL"
            else:
                truth_value = "Equal"
        elif 'tao_eth_30d_volatility' in query_id:
            # Compare volatility
            tao_vol = volatility.get('TAO', {}).get('std_dev', 0)
            eth_vol = volatility.get('ETH', {}).get('std_dev', 0)
            
            if tao_vol > eth_vol:
                truth_value = "TAO"
            elif eth_vol > tao_vol:
                truth_value = "ETH"
            else:
                truth_value = "Equal"
                
        # Trick questions - these should remain null
        elif any(keyword in query_id for keyword in ['sentient', 'yourmomma', 'april_31st', 'halloween', 'pepe', 'bittensor', 'elon', 'safe', 'fartcoin']):
            truth_value = None
            
        # Token research queries - these are subjective
        elif any(keyword in query_id for keyword in ['best_tokens', 'trending', 'talks', 'ai_tokens', 'low_cap']):
            truth_value = None
            
        # Update the query with calculated truth value
        query['truth'] = truth_value
        
        # Print the calculation
        if truth_value is not None:
            print(f"✅ {query_id}: {truth_value}")
        else:
            print(f"❌ {query_id}: No data available")
    
    # Save updated queries
    with open('data/queries_new_with_truth.yaml', 'w') as f:
        yaml.dump(updated_queries, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n📊 Summary:")
    print(f"Total queries: {len(updated_queries['queries'])}")
    calculated = sum(1 for q in updated_queries['queries'] if q['truth'] is not None)
    print(f"Calculated truth values: {calculated}")
    print(f"Remaining null (trick questions, missing data): {len(updated_queries['queries']) - calculated}")
    
    print(f"\n💾 Updated queries saved to: data/queries_new_with_truth.yaml")

if __name__ == "__main__":
    calculate_truth_values() 