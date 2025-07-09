#!/usr/bin/env python3
"""
Fix Queries YAML Formatting
Convert numpy objects to regular Python types for clean YAML output
"""

import yaml
import numpy as np

def fix_queries_yaml():
    """Fix the YAML formatting by converting numpy objects to regular types"""
    
    # Load current queries
    with open('data/queries.yaml', 'r') as f:
        queries_data = yaml.safe_load(f)
    
    # Fix numpy objects in truth values
    for query in queries_data['queries']:
        if 'truth' in query:
            truth = query['truth']
            
            # Convert numpy scalars to regular Python types
            if isinstance(truth, np.floating):
                query['truth'] = float(truth)
            elif isinstance(truth, np.integer):
                query['truth'] = int(truth)
            elif isinstance(truth, np.ndarray):
                query['truth'] = truth.tolist()
    
    # Save fixed queries
    with open('data/queries.yaml', 'w') as f:
        yaml.dump(queries_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ Fixed YAML formatting issues!")
    print("📄 Updated queries.yaml with clean data types")

if __name__ == "__main__":
    fix_queries_yaml() 