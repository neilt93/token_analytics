#!/usr/bin/env python3
"""
Fix queries.yaml format by converting numpy values to regular Python numbers
"""

import yaml
import numpy as np

def fix_queries_yaml():
    """Fix the YAML format by converting numpy values to regular Python numbers"""
    
    # Load the current queries
    with open('data/queries.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    # Convert numpy values to regular Python numbers
    def convert_numpy_values(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_values(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    # Convert all numpy values
    fixed_data = convert_numpy_values(data)
    
    # Save the fixed version
    with open('data/queries.yaml', 'w') as f:
        yaml.dump(fixed_data, f, default_flow_style=False, sort_keys=False)
    
    print("✅ Fixed queries.yaml - converted numpy values to regular Python numbers")
    
    # Print summary
    total_questions = len(fixed_data['queries'])
    easy_questions = sum(1 for q in fixed_data['queries'] if q['id'].startswith('easy_'))
    hard_questions = total_questions - easy_questions
    
    print(f"📊 Total questions: {total_questions}")
    print(f"📈 Easy questions: {easy_questions}")
    print(f"🎯 Hard questions: {hard_questions}")

if __name__ == "__main__":
    fix_queries_yaml() 