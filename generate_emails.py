#!/usr/bin/env python3
"""Generate personalized email drafts for validated leads.

Reads from docs/leads_outreach_validated.csv (produced by regenerate_validated.py),
ensuring consistency with send_emails.py.
"""

import csv

# Feminine Latvian first names (need "Godātā" instead of "Godātais")
LATVIAN_FEMININE_NAMES = {
    "marina", "anna", "karina", "kristīne", "līga", "liga",
    "maija", "daina", "aira", "vera", "solvita", "zanda",
    "ginta", "inga", "lāsma", "egita", "santa", "ilva", "estere",
    "diana", "loreta", "monta", "rūta", "laura", "karoline",
}


def is_feminine_name(first_name: str) -> bool:
    """Return True if the first name is known to be feminine in Latvian."""
    return first_name.strip().lower() in LATVIAN_FEMININE_NAMES


# Read directly from the validated CSV (same source as send_emails.py)
with open("docs/leads_outreach_validated.csv") as f:
    valid = list(csv.DictReader(f))

total_kw = sum(float(r.get("capacity_kw", 0) or 0) for r in valid)
total_mw = total_kw / 1000

# Generate email drafts
with open('docs/email_drafts_validated.md', 'w') as f:
    f.write(f'# Validated Outreach Emails — {len(valid)} Companies Ready to Send\n\n')
    f.write(f'Total: {len(valid)} companies | {total_mw:.1f} MW\n\n')
    f.write(
        '> ⚠️ Email validation: strict MX check — requires valid mail server (not localhost, not null MX)\n'
        '> ⚠️ Draft preview — replace [YOUR NAME] / [YOUR@EMAIL.COM] / [PHONE] before sending\n\n'
        '---\n\n'
    )
    
    for c in valid:
        company = c.get('company', '')
        name = c.get('decision_maker', '[DECISION MAKER]')
        title = c.get('title', '')
        email = c.get('email', '')
        phone = c.get('phone', '')
        address = c.get('address', '')
        capacity = int(float(c.get('capacity_kw', 0) or 0))
        industry = c.get('industry', '')

        first_name = name.split()[0] if name else ''
        greeting_lv = f"Godātā {name}," if is_feminine_name(first_name) else f"Godātais {name},"

        subject_lv = f"SaulesPaneļi Latvija — Bezmaksas konsultācija jūsu ražotnei"
        latvian = f"""**TO:** {email}
**SUBJECT (LV):** {subject_lv}

{greeting_lv}

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
print(f'📊 Total validated capacity: {total_mw:.1f} MW ({len(valid)} companies)')
