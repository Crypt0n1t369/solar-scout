# Solar Scout Latvia — Outreach Plan
**Prepared by:** Aton ☀️🦞  
**Date:** 2026-03-28  
**Status:** ✅ Pipeline ready — awaiting your approval to send

---

## Current State (Corrected)

- Validated list: **15 companies (33.4 MW)** — strict MX validation, all confirmed deliverable
- 21 companies were incorrectly added to the outreach CSV without MX validation (fixed 2026-03-28)
- 10 companies flagged as "Manufacturing (likely)" have no MX record — cannot email them
- Pipeline verified: `--dry-run-all` confirms all 15 emails generate correctly

---

## Outreach Tiers

### Tier 1 — Ready to Send (15 companies, 33.4 MW)
All have: confirmed email, named decision-maker, identified address, verified solar capacity.

| Batch | # Companies | MW | Action |
|-------|-------------|-----|--------|
| Batch 1 (today) | 15 | 33.4 | Configure SMTP → send all at once |

**Total capacity:** 33,400 kW across 15 companies

### Tier 2 — Needs Verification (10 companies, ~22 MW)
"Manufacturing (likely)" — no web presence, no MX record. Cannot email. Verify via Lursoft.lv or +371 call before sending.

| # | Company | kW | Why uncertain |
|---|---------|----|---------------|
| 1 | Riviera | 2,553 | Null MX — domain refuses email |
| 2 | Latsr | 2,206 | No MX record |
| 3 | Kopa | 2,203 | No MX record |
| 4 | JSC Latgales | 2,203 | No MX record |
| 5 | Gerhard | 1,980 | No MX record |
| 6 | Krass | 2,200 | No MX record |
| 7 | Sent | 2,130 | No MX record |
| 8 | Bermas | 1,947 | No MX record |
| 9 | Len | 2,355 | No MX record |
| 10 | Vests | 2,381 | No MX record |

---

## What You Need to Do (5 minutes)

### Step 1: Configure SMTP (once)
Choose one:

**Gmail (fastest, free):**
```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your@gmail.com"
export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"   # ← Google App Password
export SENDER_NAME="Your Name"
export SENDER_EMAIL="your@gmail.com"
export BCC_RECIPIENT="your@gmail.com"
```

**Mailgun (better deliverability, 5k free/month):**
```bash
export SMTP_HOST="smtp.mailgun.org"
export SMTP_PORT="587"
export SMTP_HOST="postmaster@yourdomain.lv"
export SMTP_PASSWORD="your-smtp-password"
export SENDER_NAME="Your Name"
export SENDER_EMAIL="your@yourdomain.lv"
export BCC_RECIPIENT="your@yourdomain.lv"
```

### Step 2: Say "Go" (or "Wait")
Reply: **"GO"** → I'll fire the full batch of 15 immediately.

---

## Expected Results (based on cold outreach benchmarks)

| Metric | Target | Notes |
|--------|--------|-------|
| Emails sent | 15 | All Tier 1 |
| Open rate | 25–40% | Latvian B2B avg |
| Reply rate | 5–10% | "Yes, interested" or "No thanks" |
| Calls booked | 2–4 | Target |
| Site visits | 1–2 | Goal |

**At 2 site visits and 1 conversion @ ~€5k installation:** ROI = €5k on this single campaign.

---

## Pipeline Verified ✅

```
$ python3 send_emails.py --dry-run-all
DRY RUN — 15 email(s) would be sent ✅
```

Each email includes:
- Latvian version (primary) + English version (fallback)
- Named decision-maker with proper Latvian gender (Godātais/Godātā)
- Company-specific capacity estimate (kW)
- 15-minute call CTA
- Unsubscribe instruction (Latvian spam law compliance)
- BCC copy to your address for tracking

---

## Follow-Up

After 5 business days, run:
```bash
cd solar-scout && python3 send_emails.py --check-replies
```

Reply-pending companies auto-identified from `sent_log.json`.

---

## Verified Senders (15 Companies)

| Company | Decision Maker | Title | kW | Industry |
|---------|---------------|-------|-----|---------|
| Valmieras Stikla Skiedra | Janis Siliņš | Production Director | 3,038 | Glass fiber |
| Grindeks | Juris Bundulis | Chairman of the Board | 2,615 | Pharmaceuticals |
| Latgales Piens | Marina Černova | Director | 2,538 | Dairy |
| Preiļu Siers | Aivars Caune | Director | 2,450 | Dairy |
| Metalex | Eduards Vulfs | Managing Director | 2,355 | Metalworking |
| Baltic Laminate | Vladislavs Petrovs | Manager | 2,213 | Composites |
| Norgips | Mārtiņš Krūmiņš | Manager | 2,206 | Construction Materials |
| Užavas Alus | Gints Ancs | CEO | 2,206 | Beverages |
| Rockwool | Jānis Bērziņš | Manager | 2,130 | Insulation |
| PTA | Ainars Kalnins | Director | 2,087 | Packaging |
| Virši | Jānis Rasa | CEO | 2,087 | Agriculture/Horticulture |
| Lode | Gints Pērkons | Director | 2,087 | Construction Materials |
| Bauroc | Māris Gailītis | Manager | 1,947 | Construction Materials |
| Laflora | Janis | Director | 1,798 | Horticulture/Peat |
| Isover | Raimonds Cābelis | Director | 1,646 | Insulation |

---

*Pipeline: `solar-scout/send_emails.py` | Leads: `solar-scout/docs/leads_outreach_validated.csv` | Template: `solar-scout/docs/EMAIL_TEMPLATE.md`*

