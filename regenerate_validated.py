#!/usr/bin/env python3
"""Regenerate validated email list with proper MX validation."""

import json
import subprocess
import csv

data = json.load(open('docs/leads_outreach_real.json'))

def is_valid_email(email):
    """Check if email domain has a valid MX record (accepts mail)."""
    domain = email.split('@')[1] if '@' in email else ''
    if not domain:
        return False
    try:
        mx = subprocess.run(['dig', '+short', domain, 'MX'], capture_output=True, text=True, timeout=3)
        out = mx.stdout.strip()
        if not out:
            return False
        parts = out.split()
        # Null MX (0 .) means domain explicitly refuses mail
        if len(parts) >= 2 and parts[1] == '.':
            return False
        # localhost is not a real mail server
        if 'localhost' in out:
            return False
        return True
    except:
        return False

# Filter to valid emails
valid = [c for c in data if is_valid_email(c.get('email', ''))]
valid.sort(key=lambda x: -x.get('capacity_kw', 0))

# Write validated CSV
fieldnames = ['company', 'decision_maker', 'title', 'email', 'phone', 'address', 'industry', 'capacity_kw']
with open('docs/leads_outreach_validated.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for c in valid:
        writer.writerow({
            'company': c.get('company', ''),
            'decision_maker': c.get('decision_maker', ''),
            'title': c.get('title', ''),
            'email': c.get('email', ''),
            'phone': c.get('phone', ''),
            'address': c.get('address', ''),
            'industry': c.get('industry', ''),
            'capacity_kw': c.get('capacity_kw', ''),
        })

print(f'✅ Validated: {len(valid)} companies, {sum(v.get("capacity_kw",0) for v in valid)/1000:.1f} MW')
print(f'   → docs/leads_outreach_validated.csv')

# Show removed
removed = [c for c in data if c.get('email') and not is_valid_email(c.get('email', ''))]
print(f'\n❌ Removed ({len(removed)}):')
for c in removed:
    domain = c.get('email', '').split('@')[1] if '@' in c.get('email', '') else ''
    # Quick check why invalid
    try:
        mx = subprocess.run(['dig', '+short', domain, 'MX'], capture_output=True, text=True, timeout=3)
        reason = mx.stdout.strip() or 'NO MX RECORD'
    except:
        reason = 'DNS ERROR'
    print(f'   {c["company"]}: {c.get("email","")} → {reason}')
