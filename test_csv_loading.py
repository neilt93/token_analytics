#!/usr/bin/env python3
"""
Test CSV Loading
Check if CSV files are being loaded properly and identify any issues
"""

import pandas as pd
import numpy as np
from datetime import datetime

def test_csv_loading():
    """Test loading of CSV files and check for issues"""
    
    print("🔍 Testing CSV File Loading")
    print("=" * 50)
    
    # Test loading each CSV file
    files = ['data/eth_daily.csv', 'data/sol_daily.csv', 'data/tao_daily.csv']
    
    for file_path in files:
        print(f"\n📁 Testing: {file_path}")
        print("-" * 30)
        
        try:
            # Load the CSV
            df = pd.read_csv(file_path)
            print(f"✅ File loaded successfully")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            
            # Check data types
            print(f"   Data types:")
            for col, dtype in df.dtypes.items():
                print(f"     {col}: {dtype}")
            
            # Check for missing values
            missing = df.isnull().sum()
            if missing.sum() > 0:
                print(f"   ⚠️  Missing values: {missing.to_dict()}")
            else:
                print(f"   ✅ No missing values")
            
            # Check date column
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                print(f"   📅 Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"   📅 Total days: {len(df)}")
            
            # Check numeric columns for extreme values
            numeric_cols = ['close', 'open', 'high', 'low', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    col_data = pd.to_numeric(df[col], errors='coerce')
                    min_val = col_data.min()
                    max_val = col_data.max()
                    mean_val = col_data.mean()
                    
                    print(f"   📊 {col}:")
                    print(f"     Min: {min_val}")
                    print(f"     Max: {max_val}")
                    print(f"     Mean: {mean_val}")
                    
                    # Check for extreme values
                    if col in ['close', 'open', 'high', 'low']:
                        if min_val < 0.1:
                            print(f"     ⚠️  Very low values detected (< 0.1)")
                        if max_val > 10000:
                            print(f"     ⚠️  Very high values detected (> 10000)")
                    elif col == 'volume':
                        if mean_val > 1e12:  # 1 trillion
                            print(f"     ⚠️  Very high volume values detected (> 1 trillion)")
            
            # Check for data consistency issues
            if all(col in df.columns for col in ['high', 'low', 'close']):
                # Check if high >= low
                high_low_issues = (df['high'] < df['low']).sum()
                if high_low_issues > 0:
                    print(f"   ⚠️  {high_low_issues} rows where high < low")
                
                # Check if close is between high and low
                close_range_issues = ((df['close'] > df['high']) | (df['close'] < df['low'])).sum()
                if close_range_issues > 0:
                    print(f"   ⚠️  {close_range_issues} rows where close outside high/low range")
            
        except Exception as e:
            print(f"❌ Error loading {file_path}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    # Load all data and check date filtering
    try:
        eth_data = pd.read_csv('data/eth_daily.csv')
        sol_data = pd.read_csv('data/sol_daily.csv')
        tao_data = pd.read_csv('data/tao_daily.csv')
        
        # Convert dates
        for df in [eth_data, sol_data, tao_data]:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # Test date filtering
        start_date = '2025-06-09'
        end_date = '2025-07-08'
        
        eth_filtered = eth_data.loc[start_date:end_date]
        sol_filtered = sol_data.loc[start_date:end_date]
        tao_filtered = tao_data.loc[start_date:end_date]
        
        print(f"📅 Date filtering test:")
        print(f"   ETH: {len(eth_filtered)} days in range")
        print(f"   SOL: {len(sol_filtered)} days in range")
        print(f"   TAO: {len(tao_filtered)} days in range")
        
        # Check for data anomalies
        print(f"\n🔍 Data Anomaly Check:")
        
        # ETH anomalies
        eth_extreme_low = (eth_filtered['close'] < 1).sum()
        eth_extreme_high = (eth_filtered['close'] > 10000).sum()
        print(f"   ETH extreme values: {eth_extreme_low} very low, {eth_extreme_high} very high")
        
        # SOL anomalies
        sol_extreme_low = (sol_filtered['close'] < 100).sum()
        sol_extreme_high = (sol_filtered['close'] > 200).sum()
        print(f"   SOL extreme values: {sol_extreme_low} very low, {sol_extreme_high} very high")
        
        # TAO anomalies
        tao_extreme_low = (tao_filtered['close'] < 1).sum()
        tao_extreme_high = (tao_filtered['close'] > 500).sum()
        print(f"   TAO extreme values: {tao_extreme_low} very low, {tao_extreme_high} very high")
        
    except Exception as e:
        print(f"❌ Error in summary analysis: {str(e)}")

if __name__ == "__main__":
    test_csv_loading() 