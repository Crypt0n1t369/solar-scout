#!/usr/bin/env python3
"""
Industry inference for real (known_company) leads.
Uses: (1) existing known values, (2) company name pattern matching.
"""
import json, re

INDUSTRY_PATTERNS = [
    (r'(?i)flax', 'Textile'),
    (r'(?i)textile|fabric|carpet', 'Textile'),
    (r'(?i)metal|steel|fabrication|weld|machining', 'Metalworking'),
    (r'(?i)locomotive', 'Metalworking'),
    (r'(?i)wood|furniture|mebel|koka|saplāks|tips$', 'Wood/Furniture'),
    (r'(?i)medienos', 'Wood/Furniture'),  # Lithuanian: wood
    (r'(?i)plastic|polimēr', 'Plastic'),
    (r'(?i)bread|maize', 'Food/Bread'),
    (r'(?i)dairy|piens|siers|cheese', 'Dairy'),
    (r'(?i)beverage|alus|beer|brew', 'Beverages'),
    (r'(?i)pharma|cosmetic|madara', 'Pharmaceuticals/Cosmetics'),
    (r'(?i)construction|concrete|cement|bauroc', 'Construction Materials'),
    (r'(?i)gips|gyp|norgips', 'Construction Materials'),  # Drywall/gypsum panels
    (r'(?i)gortex', 'Construction Materials'),  # Construction membrane
    (r'(?i)lode', 'Construction Materials'),  # Lode - Latvian construction materials
    (r'(?i)glass|stikl', 'Glass'),
    (r'(?i)paper|pārstrāde', 'Paper/Packaging'),
    (r'(?i)insulation|isover|rockwool', 'Insulation'),
    (r'(?i)floor|forbo|cover', 'Floor Coverings'),
    (r'(?i)heat|siltumel', 'Heating'),
    (r'(?i)vent|ventilācij', 'HVAC'),
    (r'(?i)packag|pta$', 'Packaging'),
    (r'(?i)lamināt|lamin|baltic\s*laminate', 'Composites'),
    (r'(?i)kūdra|peat|laflora', 'Horticulture/Peat'),
    (r'(?i)marine|ship|vessel', 'Shipbuilding'),
    (r'(?i)energy|power|solar|wind', 'Energy'),
    (r'(?i)rubber|elast', 'Rubber'),
    (r'(?i)alum|alutech', 'Aluminum'),
    (r'(?i)virš', 'Agriculture/Horticulture'),
]

def infer_industry(company_name: str, current: str) -> str:
    if current and current not in ('?', 'unknown', ''):
        return current
    for pattern, industry in INDUSTRY_PATTERNS:
        if re.search(pattern, company_name):
            return industry
    return 'unknown'

def main():
    with open('docs/leads_dashboard.json') as f:
        data = json.load(f)

    updated = 0
    for l in data:
        if l.get('source') != 'known_company':
            continue
        old_ind = l.get('industry', '?') or '?'
        new_ind = infer_industry(l.get('company', ''), old_ind)
        if new_ind != old_ind:
            l['industry'] = new_ind
            updated += 1

    with open('docs/leads_dashboard.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Report
    from collections import Counter
    real = [l for l in data if l.get('source') == 'known_company']
    industries = Counter(l.get('industry', '?') for l in real)
    print(f'Updated {updated} industry assignments')
    print(f'Real leads total: {len(real)}')
    print('Industry distribution:')
    for ind, cnt in industries.most_common():
        print(f'  {ind}: {cnt}')

if __name__ == '__main__':
    main()
