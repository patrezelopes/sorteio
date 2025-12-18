import re

# Read the base.py file
with open('base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all usernames that start with @
usernames = re.findall(r'@([a-zA-Z0-9._]+)', content)

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

print(f'Exported {len(unique_usernames)} unique usernames to base.txt')
