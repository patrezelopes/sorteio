#!/usr/bin/env python3
"""
Extract all Instagram usernames from base.py and export to base.txt
"""
import re
from pathlib import Path

def extract_usernames():
    # Read base.py
    base_py_path = Path(__file__).parent / 'base.py'
    base_txt_path = Path(__file__).parent / 'base.txt'
    
    print(f"📂 Reading from: {base_py_path}")
    
    with open(base_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all @ mentions using regex
    # Pattern: @ followed by alphanumeric characters, dots, and underscores
    all_usernames = re.findall(r'@([a-zA-Z0-9._]+)', content)
    
    print(f"🔍 Found {len(all_usernames)} total mentions")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_usernames = []
    for username in all_usernames:
        if username not in seen:
            seen.add(username)
            unique_usernames.append(username)
    
    print(f"✨ Extracted {len(unique_usernames)} unique usernames")
    
    # Write to base.txt
    with open(base_txt_path, 'w', encoding='utf-8') as f:
        for username in unique_usernames:
            f.write(username + '\n')
    
    print(f"✅ Successfully exported to: {base_txt_path}")
    print(f"📊 Total unique usernames: {len(unique_usernames)}")
    
    return unique_usernames

if __name__ == '__main__':
    usernames = extract_usernames()
    print("\n🎉 Done! First 10 usernames:")
    for i, username in enumerate(usernames[:10], 1):
        print(f"  {i}. {username}")
