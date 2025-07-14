#!/usr/bin/env python3
"""
Fix YAML file by removing null characters and ensuring proper structure
"""

import yaml
import re

def fix_yaml_file():
    """Fix the YAML file by removing null characters"""
    
    # Read the file as text
    with open('data/queries_new.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove null characters
    content = content.replace('\x00', '')
    
    # Remove any trailing whitespace
    content = content.rstrip()
    
    # Write back the cleaned content
    with open('data/queries_new.yaml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed YAML file by removing null characters")

if __name__ == "__main__":
    fix_yaml_file() 