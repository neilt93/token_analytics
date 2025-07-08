import pandas as pd
import yaml
import os

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

def calculate_truth_values():
    """Calculate truth values for all benchmark queries"""
    data = load_token_data()
    
    if not data:
        print("No data found. Please ensure CSV files are in the current directory.")
        return
    
    print("🔍 Calculating truth values from actual data...")
    print("=" * 80)
    
    # Percentage threshold calculations
    print("\n📊 PERCENTAGE THRESHOLD CALCULATIONS:")
    
    # TAO above $400
    tao_data = data['TAO']
    tao_above_400 = (tao_data['close'] > 400).sum()
    tao_pct_above_400 = (tao_above_400 / len(tao_data)) * 100
    print(f"TAO above $400: {tao_above_400}/{len(tao_data)} days = {tao_pct_above_400:.2f}%")
    
    # SOL above $150
    sol_data = data['SOL']
    sol_above_150 = (sol_data['close'] > 150).sum()
    sol_pct_above_150 = (sol_above_150 / len(sol_data)) * 100
    print(f"SOL above $150: {sol_above_150}/{len(sol_data)} days = {sol_pct_above_150:.2f}%")
    
    # ETH above $2500
    eth_data = data['ETH']
    eth_above_2500 = (eth_data['close'] > 2500).sum()
    eth_pct_above_2500 = (eth_above_2500 / len(eth_data)) * 100
    print(f"ETH above $2500: {eth_above_2500}/{len(eth_data)} days = {eth_pct_above_2500:.2f}%")
    
    # Price change calculations
    print("\n📈 PRICE CHANGE CALCULATIONS:")
    
    # SOL price change
    sol_first = sol_data['close'].iloc[0]
    sol_last = sol_data['close'].iloc[-1]
    sol_change = ((sol_last - sol_first) / sol_first) * 100
    print(f"SOL: ${sol_first:.2f} → ${sol_last:.2f} = {sol_change:+.2f}%")
    
    # ETH price change
    eth_first = eth_data['close'].iloc[0]
    eth_last = eth_data['close'].iloc[-1]
    eth_change = ((eth_last - eth_first) / eth_first) * 100
    print(f"ETH: ${eth_first:.2f} → ${eth_last:.2f} = {eth_change:+.2f}%")
    
    # TAO price change
    tao_first = tao_data['close'].iloc[0]
    tao_last = tao_data['close'].iloc[-1]
    tao_change = ((tao_last - tao_first) / tao_first) * 100
    print(f"TAO: ${tao_first:.2f} → ${tao_last:.2f} = {tao_change:+.2f}%")
    
    # Volume analysis
    print("\n📊 VOLUME ANALYSIS:")
    
    avg_volumes = {}
    total_volumes = {}
    
    for token, df in data.items():
        avg_vol = df['volume'].mean()
        total_vol = df['volume'].sum()
        avg_volumes[token] = avg_vol
        total_volumes[token] = total_vol
        
        if avg_vol >= 1e9:
            print(f"{token} avg volume: ${avg_vol/1e9:.2f}B, total: ${total_vol/1e9:.2f}B")
        elif avg_vol >= 1e6:
            print(f"{token} avg volume: ${avg_vol/1e6:.2f}M, total: ${total_vol/1e6:.2f}M")
        else:
            print(f"{token} avg volume: ${avg_vol:.0f}, total: ${total_vol:.0f}")
    
    # Highest average volume
    highest_avg_token = max(avg_volumes, key=avg_volumes.get)
    print(f"Highest avg volume: {highest_avg_token}")
    
    # Volume ranking
    volume_ranking = sorted(total_volumes.items(), key=lambda x: x[1], reverse=True)
    volume_ranking_tokens = [token for token, vol in volume_ranking]
    print(f"Volume ranking: {volume_ranking_tokens}")
    
    # Price analysis
    print("\n📅 PRICE ANALYSIS:")
    
    # ETH highest close
    eth_highest_idx = eth_data['close'].idxmax()
    eth_highest_date = eth_data.loc[eth_highest_idx, 'date'].strftime('%Y-%m-%d')
    eth_highest_price = eth_data.loc[eth_highest_idx, 'close']
    print(f"ETH highest close: {eth_highest_date} at ${eth_highest_price:.2f}")
    
    # SOL lowest close
    sol_lowest_idx = sol_data['close'].idxmin()
    sol_lowest_date = sol_data.loc[sol_lowest_idx, 'date'].strftime('%Y-%m-%d')
    sol_lowest_price = sol_data.loc[sol_lowest_idx, 'close']
    print(f"SOL lowest close: {sol_lowest_date} at ${sol_lowest_price:.2f}")
    
    # Average close prices
    avg_closes = {}
    for token, df in data.items():
        avg_closes[token] = df['close'].mean()
    
    # Ranking by average close
    close_ranking = sorted(avg_closes.items(), key=lambda x: x[1], reverse=True)
    close_ranking_tokens = [token for token, price in close_ranking]
    print(f"Ranking by avg close: {close_ranking_tokens}")
    for token, price in close_ranking:
        print(f"  {token}: ${price:.2f}")
    
    # Volatility analysis
    print("\n📊 VOLATILITY ANALYSIS:")
    
    volatilities = {}
    for token, df in data.items():
        price_range = df['close'].max() - df['close'].min()
        price_range_pct = (price_range / df['close'].min()) * 100
        volatilities[token] = price_range_pct
        print(f"{token} price range: ${price_range:.2f} ({price_range_pct:.1f}%)")
    
    most_volatile = max(volatilities, key=volatilities.get)
    print(f"Most volatile: {most_volatile}")
    
    # Performance comparison
    print("\n🏆 PERFORMANCE COMPARISON:")
    changes = {
        'SOL': sol_change,
        'ETH': eth_change,
        'TAO': tao_change
    }
    
    best_performer = max(changes, key=changes.get)
    worst_performer = min(changes, key=changes.get)
    
    print(f"Best performer: {best_performer} ({changes[best_performer]:+.2f}%)")
    print(f"Worst performer: {worst_performer} ({changes[worst_performer]:+.2f}%)")
    
    # Verify against queries.yaml
    print("\n" + "=" * 80)
    print("✅ VERIFICATION SUMMARY:")
    print("=" * 80)
    
    # Load queries.yaml to compare
    try:
        with open('data/queries.yaml', 'r') as f:
            queries = yaml.safe_load(f)
        
        verification_results = []
        
        for query in queries['queries']:
            query_id = query['id']
            expected = query['truth']
            
            # Get calculated value
            calculated = None
            if query_id == 'pct_tao_above_400':
                calculated = tao_pct_above_400
            elif query_id == 'pct_sol_above_150':
                calculated = sol_pct_above_150
            elif query_id == 'pct_eth_above_2500':
                calculated = eth_pct_above_2500
            elif query_id == 'sol_price_change_30d':
                calculated = sol_change
            elif query_id == 'eth_price_change_30d':
                calculated = eth_change
            elif query_id == 'tao_price_change_30d':
                calculated = tao_change
            elif query_id == 'highest_avg_volume':
                calculated = highest_avg_token
            elif query_id == 'total_volume_ranking':
                calculated = volume_ranking_tokens
            elif query_id == 'eth_highest_close_date':
                calculated = eth_highest_date
            elif query_id == 'sol_lowest_close_date':
                calculated = sol_lowest_date
            elif query_id == 'rank_by_avg_close':
                calculated = close_ranking_tokens
            elif query_id == 'most_volatile_token':
                calculated = most_volatile
            elif query_id == 'sol_volatility_range':
                calculated = sol_data['close'].max() - sol_data['close'].min()
            elif query_id == 'best_performer_30d':
                calculated = best_performer
            elif query_id == 'worst_performer_30d':
                calculated = worst_performer
            
            # Compare
            if isinstance(expected, (int, float)) and isinstance(calculated, (int, float)):
                match = abs(expected - calculated) < 0.1
            else:
                match = expected == calculated
            
            status = "✅" if match else "❌"
            verification_results.append({
                'query_id': query_id,
                'expected': expected,
                'calculated': calculated,
                'match': match
            })
            
            print(f"{status} {query_id}: Expected {expected}, Calculated {calculated}")
        
        # Summary
        matches = sum(1 for r in verification_results if r['match'])
        total = len(verification_results)
        print(f"\n📊 Verification Results: {matches}/{total} queries match ({matches/total*100:.1f}%)")
        
        if matches == total:
            print("🎉 All queries verified successfully!")
        else:
            print("⚠️  Some queries need to be updated in queries.yaml")
            
    except FileNotFoundError:
        print("queries.yaml not found. Run this script after creating the queries file.")

if __name__ == "__main__":
    calculate_truth_values() 