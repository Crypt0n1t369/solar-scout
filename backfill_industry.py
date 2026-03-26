#!/usr/bin/env python3
"""
Backfill industry field in leads_dashboard.json using real_companies.json and real_leads.json
"""
import json
import re
from pathlib import Path

def normalize(s):
    if not s:
        return ''
    s = s.lower().strip()
    s = re.sub(r'[\s\-_.,]+', '', s)
    return s

def partial_match(name1, name2):
    """Check if names share significant overlap"""
    n1, n2 = normalize(name1), normalize(name2)
    if not n1 or not n2:
        return False
    if n1 == n2:
        return True
    # Substring check
    if n1 in n2 or n2 in n1:
        return True
    # Word overlap - split on spaces and check first 2 major words
    words1 = [w for w in re.split(r'[\s\-]+', name1.lower()) if len(w) > 3]
    words2 = [w for w in re.split(r'[\s\-]+', name2.lower()) if len(w) > 3]
    if words1 and words2:
        common = set(words1[:3]) & set(words2[:3])
        if common:
            return True
    return False

def main():
    base = Path('/home/drg/.openclaw/workspace/solar-scout')
    
    # Load sources
    with open(base / 'real_companies.json') as f:
        companies = json.load(f)
    with open(base / 'real_leads.json') as f:
        real_leads = json.load(f)
    with open(base / 'docs/leads_dashboard.json') as f:
        leads = json.load(f)

    # Build lookup: normalized_name -> industry
    industry_lookup = {}
    for c in companies + real_leads:
        n = normalize(c.get('name', ''))
        ind = c.get('industry', '')
        if n and ind and ind != 'unknown':
            # Keep first (most specific) match
            if n not in industry_lookup:
                industry_lookup[n] = ind

    print(f"Industry lookup entries: {len(industry_lookup)}")

    # Backfill
    updated = 0
    unmatched = []
    for lead in leads:
        company = lead.get('company', '')
        current_ind = lead.get('industry', '')
        
        if current_ind and current_ind != 'unknown':
            continue  # already has industry

        norm_c = normalize(company)
        
        # Try exact match
        if norm_c in industry_lookup:
            lead['industry'] = industry_lookup[norm_c]
            updated += 1
            continue

        # Try partial match
        matched = False
        for lookup_name, industry in industry_lookup.items():
            if partial_match(company, lookup_name):
                lead['industry'] = industry
                updated += 1
                matched = True
                break
        
        if not matched:
            unmatched.append(company)

    print(f"Updated: {updated}")
    print(f"Unmatched: {len(unmatched)}")
    if unmatched[:10]:
        print("Sample unmatched:", unmatched[:10])

    # Save
    with open(base / 'docs/leads_dashboard.json', 'w') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    
    print("Saved docs/leads_dashboard.json")

    # Also regenerate CSV
    import csv
    with open(base / 'docs/leads_dashboard.csv', 'w', newline='', encoding='utf-8') as f:
        if leads:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)
    print("Saved docs/leads_dashboard.csv")

if __name__ == '__main__':
    main()