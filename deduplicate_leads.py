#!/usr/bin/env python3
"""
Deduplicate leads_dashboard.json and save clean version.
Keeps entry with more fields populated.
"""
import json
import csv
from pathlib import Path

def count_populated(obj):
    """Count non-empty fields in a lead dict"""
    return sum(1 for v in obj.values() if v not in ('', None, 0, 'unknown'))

def main():
    base = Path('/home/drg/.openclaw/workspace/solar-scout')
    
    with open(base / 'docs/leads_dashboard.json') as f:
        leads = json.load(f)
    
    print(f"Before deduplication: {len(leads)} leads")
    
    # Find duplicates by company name
    seen = {}  # name -> lead
    dups_merged = 0
    
    for lead in leads:
        name = lead.get('company', '').strip()
        if name in seen:
            # Keep the one with more data
            existing = seen[name]
            if count_populated(lead) > count_populated(existing):
                seen[name] = lead
            dups_merged += 1
        else:
            seen[name] = lead
    
    unique_leads = list(seen.values())
    print(f"After deduplication: {len(unique_leads)} leads")
    print(f"Duplicates merged: {dups_merged}")
    
    # Sort by id
    unique_leads.sort(key=lambda x: x.get('id', 0))
    
    # Reassign IDs sequentially
    for i, lead in enumerate(unique_leads, 1):
        lead['id'] = i
    
    # Save JSON
    with open(base / 'docs/leads_dashboard.json', 'w', encoding='utf-8') as f:
        json.dump(unique_leads, f, ensure_ascii=False, indent=2)
    print("Saved docs/leads_dashboard.json")
    
    # Save CSV
    with open(base / 'docs/leads_dashboard.csv', 'w', newline='', encoding='utf-8') as f:
        if unique_leads:
            writer = csv.DictWriter(f, fieldnames=unique_leads[0].keys())
            writer.writeheader()
            writer.writerows(unique_leads)
    print("Saved docs/leads_dashboard.csv")
    
    # Report state of data
    states = {}
    for l in unique_leads:
        s = l.get('state', 'unknown')
        states[s] = states.get(s, 0) + 1
    print(f"States: {states}")

if __name__ == '__main__':
    main()