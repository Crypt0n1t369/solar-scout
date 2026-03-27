# Solar Scout Latvia — Outreach Email Template

## Configuration

```
SUBJECT: SaulesPaneļi Latvija — Bezmaksas konsultācija jūsu ražotnei
FROM: [YOUR_NAME] <[YOUR_EMAIL]>
REPLY-TO: [YOUR_EMAIL]
BCC: one email per recipient (mass email law compliance)
```

---

## Email Body (Latvian)

```
Saturs: Bezmaksas saules enerģijas konsultācija jūsu ražotnei

Godātais [VĀRDS],

Esmu [VĀRDS] no [COMPANY NAME] — mēs palīdzam Latvijas rūpniecības uzņēmumiem 
saražot savu elektroenerģiju ar saules paneļiem.

Jūsu uzņēmums [COMPANY NAME] ([ADDRESS]) atbilst mūsu kritērijiem:
✔ Rūpnieciskā darbība ar lielu jumta platību
✔ Pašreizējais elektroenerģijas patēriņš
✔ Vēl neesat uzstādījuši saules paneļus

Provizoriskā aplēse: līdz [CAPACITY] kW instalējamā jauda
Ietaupījums: līdz [30-50]% no elektroenerģijas izmaksām

Vai būtu ērti 15 minūšu zvans šonedēļ, lai izvērtētu iespējas?

Ar cieņu,
[VĀRDS]
[TĀLRUNIS] | [E-PASTS]
```

---

## Email Body (English — for English-speaking contacts)

```
Subject: Free Solar Assessment for [COMPANY NAME] — [CAPACITY] kW Potential

Dear [DECISION MAKER NAME],

I'm [YOUR NAME] from [COMPANY NAME]. We help Latvian manufacturing companies
reduce their electricity costs by installing solar panels on their facilities.

Based on our preliminary analysis, your facility at [ADDRESS] could host
approximately [CAPACITY] kW of solar panels — potentially cutting your
electricity costs by 30–50%.

Is 15 minutes convenient this week for a quick call to discuss the specifics?

Best regards,
[YOUR NAME]
[PHONE] | [EMAIL]
```

---

## Merge Tag Reference

| Tag | Source Field | Example |
|-----|-------------|---------|
| `{{COMPANY}}` | `company` | Grindeks |
| `{{DECISION_MAKER}}` | `decision_maker` | Juris Bundulis |
| `{{TITLE}}` | `title` | Chairman of the Board |
| `{{EMAIL}}` | `email` | info@grindeks.lv |
| `{{PHONE}}` | `phone` | +371 67039393 |
| `{{ADDRESS}}` | `address` | Krustpils iela 53, Riga |
| `{{CAPACITY_KW}}` | `capacity_kw` | 2615 |
| `{{INDUSTRY}}` | `industry` | Pharmaceuticals |

---

## Sending Strategy

### Tier 1 — High Confidence (35 companies)
Industries confirmed: Pharmaceuticals, Dairy, Construction Materials, Wood/Furniture, Food/Bread, Metalworking, Beverages, Insulation, Horticulture/Peat, Glass fiber, Shipbuilding, Plastic, Aluminum, Electronics, Heating, HVAC, Packaging, Composites, Floor Coverings

→ Send Latvian version first, English as fallback

### Tier 2 — Manufacturing (Likely) (11 companies)
Riviera, Latsr, Kopa, JSC Latgales, Gerhard, Krass, Sent, Bermas, Len, Vests, Sakart
→ Verify via Lursoft.lv or +371 phone calls BEFORE sending
→ If no response in 5 days, send anyway

---

## Personalization Notes Per Company

| Company | Latvian Name | Personalization |
|---------|-------------|----------------|
| Grindeks | — | Largest pharma in Baltics, premium target |
| Laflora | — | Peat/horticulture, potentially energy-intensive |
| Valmieras Stikla Skiedra | VSS | Glass fiber, large facility |
| Daugavpils Locomotive | DLRP | Soviet-era industrial, large roof |
| Jelgavas Tips | — | Furniture, owner-managed |
| ... | — | See leads_outreach_real.json for full data |

---

## Compliance Notes

- **BCC all recipients** — do not put email addresses in TO/SCC field
- **Unsubscribe link required** — include one-click unsubscribe
- **Company address required** — Latvian spam law (NĪDL 2014)
- **No misleading subject** — "Reklāma" tag if commercial

---

## Tracking

| Metric | Target |
|--------|--------|
| Open rate | > 35% |
| Reply rate | > 8% |
| Calls booked | > 3 of 46 |
| Site visits | > 1 |

---

*Created: 2026-03-27*
*Source data: docs/leads_outreach_real.json (46 companies, 104.9 MW total)*
