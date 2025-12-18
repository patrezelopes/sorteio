#!/usr/bin/env python3
import re

# Read base.py
with open('base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract all usernames
usernames = []
for line in lines:
    # Find all @ mentions in the line
    matches = re.findall(r'@([a-zA-Z0-9._]+)', line)
    usernames.extend(matches)

# Remove duplicates while preserving order
seen = set()
unique_usernames = []
for username in usernames:
    if username not in seen:
        seen.add(username)
        unique_usernames.append(username)

# Write to base.txt
with open('base.txt', 'w', encoding='utf-8') as f:
    for username in unique_usernames:
        f.write(username + '\n')

print(f'Successfully exported {len(unique_usernames)} unique usernames to base.txt')
