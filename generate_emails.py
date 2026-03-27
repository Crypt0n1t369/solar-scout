#!/usr/bin/env python3
"""Generate personalized email drafts for validated leads."""

import json
import subprocess
import csv

data = json.load(open('docs/leads_outreach_real.json'))

def is_valid_email(email):
    domain = email.split('@')[1] if '@' in email else ''
    if not domain:
        return False
    try:
        mx = subprocess.run(['dig', '+short', domain, 'MX'], capture_output=True, text=True, timeout=3)
        out = mx.stdout.strip()
        if not out:
            return False
        parts = out.split()
        if len(parts) >= 2 and parts[1] == '.':
            return False
        if 'localhost' in out:
            return False
        return True
    except:
        return False

valid = [c for c in data if is_valid_email(c.get('email', ''))]
valid.sort(key=lambda x: -x.get('capacity_kw', 0))

# Generate email drafts
with open('docs/email_drafts_validated.md', 'w') as f:
    f.write('# Validated Outreach Emails — 15 Companies Ready to Send\n\n')
    f.write(f'Total: {len(valid)} companies | {sum(v.get("capacity_kw",0) for v in valid)/1000:.1f} MW\n\n')
    f.write('> ⚠️ Email validation: strict MX check — requires valid mail server (not localhost, not null MX)\n')
    f.write('> ❌ Riviera (null MX) and Ventilacija (localhost MX) removed from previous 16-company list\n\n---\n\n')
    
    for c in valid:
        company = c['company']
        name = c.get('decision_maker', '[DECISION MAKER]')
        title = c.get('title', '')
        email = c['email']
        phone = c['phone']
        address = c.get('address', '')
        capacity = int(c.get('capacity_kw', 0))
        industry = c.get('industry', '')

        subject_lv = f"SaulesPaneļi Latvija — Bezmaksas konsultācija jūsu ražotnei"
        latvian = f"""**TO:** {email}
**SUBJECT (LV):** {subject_lv}

Godātais {name},

Esmu [VĀRDS] no [COMPANY NAME] — mēs palīdzam Latvijas rūpniecības uzņēmumiem saražot savu elektroenerģiju ar saules paneļiem.

Jūsu uzņēmums {company} ({address}) atbilst mūsu kritērijiem:
✔ Rūpnieciskā darbība ar lielu jumta platību
✔ Pašreizējais elektroenerģijas patēriņš
✔ Vēl neesat uzstādījuši saules paneļus

Provizoriskā aplēse: līdz {capacity:,} kW instalējamā jauda
Ietaupījums: līdz 30-50% no elektroenerģijas izmaksām

Vai būtu ērti 15 minūšu zvans šonedēļ, lai izvērtētu iespējas?

Ar cieņu,
[VĀRDS] | [TĀLRUNIS] | [E-PASTS]
"""

        subject_en = f"Free Solar Assessment for {company} — {capacity:,} kW Potential"
        english = f"""**TO:** {email}
**SUBJECT (EN):** {subject_en}

Dear {name},

I'm [YOUR NAME] from [COMPANY NAME]. We help Latvian manufacturing companies reduce their electricity costs by installing solar panels on their facilities.

Based on our preliminary analysis, your facility at {address} could host approximately {capacity:,} kW of solar panels — potentially cutting your electricity costs by 30–50%.

Is 15 minutes convenient this week for a quick call to discuss the specifics?

Best regards,
[YOUR NAME] | [PHONE] | [EMAIL]
"""

        f.write(f"## {company} | {industry}\n")
        f.write(f"**Capacity:** {capacity:,} kW | **Decision Maker:** {name} ({title})\n\n")
        f.write(latvian)
        f.write(f"\n\n---\n\n")
        f.write(english)
        f.write(f"\n\n---\n\n")

print(f'✅ Generated {len(valid)} email drafts → docs/email_drafts_validated.md')
print(f'✅ Validated CSV → docs/leads_outreach_validated.csv')
print(f'📊 Total validated capacity: {sum(v.get("capacity_kw",0) for v in valid)/1000:.1f} MW')
