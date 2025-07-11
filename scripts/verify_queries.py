#!/usr/bin/env python3
"""
Verify Queries Against Available Data
Checks that all queries in queries.yaml can be answered with the available data
"""

import yaml
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

def load_data():
    """Load all token data"""
    eth = pd.read_csv('data/eth_daily.csv')
    sol = pd.read_csv('data/sol_daily.csv')
    tao = pd.read_csv('data/tao_daily.csv')
    
    # Convert date column
    for df in [eth, sol, tao]:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    
    return eth, sol, tao

def verify_queries():
    """Verify all queries against available data"""
    print("🔍 VERIFYING QUERIES AGAINST AVAILABLE DATA")
    print("=" * 60)
    
    # Load data
    eth, sol, tao = load_data()
    
    # Load queries
    with open('data/queries.yaml', 'r') as f:
        queries_data = yaml.safe_load(f)
    
    queries = queries_data['queries']
    
    print(f"📊 Data Summary:")
    print(f"   ETH: {len(eth)} days, {eth.index.min()} to {eth.index.max()}")
    print(f"   SOL: {len(sol)} days, {sol.index.min()} to {sol.index.max()}")
    print(f"   TAO: {len(tao)} days, {tao.index.min()} to {tao.index.max()}")
    print()
    
    # Check data quality issues
    print("🔍 Data Quality Issues:")
    
    # Check for intraday variation
    eth_no_intraday = (eth['high'] == eth['low']).all()
    sol_no_intraday = (sol['high'] == sol['low']).all()
    tao_no_intraday = (tao['high'] == tao['low']).all()
    
    if eth_no_intraday and sol_no_intraday and tao_no_intraday:
        print("   ⚠️  No intraday variation: high=low=close for all tokens")
        print("   📝 Questions requiring intraday data will need modification")
    
    # Check for missing data
    for token, df in [('ETH', eth), ('SOL', sol), ('TAO', tao)]:
        missing_days = df.isnull().sum()
        if missing_days.any():
            print(f"   ⚠️  {token} has missing data: {missing_days.to_dict()}")
    
    print()
    
    # Verify each query
    print("📋 Query Verification:")
    issues = []
    
    for query in queries:
        query_id = query['id']
        question = query['question']
        category = query['category']
        truth = query['truth']
        
        # Check for problematic patterns
        problems = []
        
        # Check for intraday references
        if any(term in question.lower() for term in ['intraday', 'high-low', 'high low', 'high-low swing']):
            problems.append("References intraday data (not available)")
        
        # Check for future date references
        if '2025' in question and 'june' in question.lower() or 'july' in question.lower():
            problems.append("References future dates (may confuse LLMs)")
        
        # Check for specific date ranges that might not match data
        if '30-day period' in question and 'june 9 to july 8' in question.lower():
            # Verify this matches our data
            start_date = pd.to_datetime('2025-06-09')
            end_date = pd.to_datetime('2025-07-08')
            data_start = eth.index.min()
            data_end = eth.index.max()
            
            if data_start != start_date or data_end != end_date:
                problems.append(f"Date range mismatch: data is {data_start} to {data_end}")
        
        # Check for volume-related questions
        if 'volume' in question.lower() and any(token in question.upper() for token in ['SOL', 'ETH', 'TAO']):
            # Verify volume data exists
            if 'volume' not in eth.columns or 'volume' not in sol.columns or 'volume' not in tao.columns:
                problems.append("Volume data required but may be missing")
        
        if problems:
            issues.append({
                'query_id': query_id,
                'category': category,
                'problems': problems
            })
            print(f"   ❌ {query_id}: {', '.join(problems)}")
        else:
            print(f"   ✅ {query_id}: OK")
    
    print()
    
    if issues:
        print("🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue['query_id']} ({issue['category']}): {', '.join(issue['problems'])}")
    else:
        print("✅ All queries verified successfully!")
    
    # Summary statistics
    total_queries = len(queries)
    problematic_queries = len(issues)
    good_queries = total_queries - problematic_queries
    
    print()
    print("📊 SUMMARY:")
    print(f"   Total queries: {total_queries}")
    print(f"   Good queries: {good_queries}")
    print(f"   Problematic queries: {problematic_queries}")
    print(f"   Success rate: {(good_queries/total_queries)*100:.1f}%")
    
    return issues

def suggest_fixes(issues):
    """Suggest fixes for identified issues"""
    if not issues:
        return
    
    print("\n🔧 SUGGESTED FIXES:")
    
    for issue in issues:
        query_id = issue['query_id']
        problems = issue['problems']
        
        print(f"\n   📝 {query_id}:")
        
        for problem in problems:
            if "intraday" in problem.lower():
                print("      → Replace intraday questions with daily change questions")
            elif "future dates" in problem.lower():
                print("      → Add context that this is historical data from 2025")
            elif "volume" in problem.lower():
                print("      → Verify volume data is available in CSV files")
            elif "date range" in problem.lower():
                print("      → Update question to match actual data date range")

def main():
    """Main function"""
    issues = verify_queries()
    suggest_fixes(issues)
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} queries with potential issues")
        print("Consider updating these queries before running evaluations")
    else:
        print("\n✅ All queries are ready for evaluation!")

if __name__ == "__main__":
    main() 