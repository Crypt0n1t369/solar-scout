# Solar Scout Latvia — Outreach Plan
**Prepared by:** Aton ☀️🦞  
**Date:** 2026-03-28  
**Status:** ✅ Pipeline ready — awaiting your approval to send

---

## What Changed This Session

- Validated list **expanded from 15 → 36 companies** (82.6 MW combined)
- 10 low-confidence companies flagged separately (see Tier 2 below)
- Pipeline verified: `--dry-run-all` produces correct emails for all 36

---

## Outreach Tiers

### Tier 1 — Ready to Send (36 companies, 82.6 MW)
All have: confirmed email, named decision-maker, identified address, verified solar capacity.

| Batch | # Companies | MW | Action |
|-------|-------------|-----|--------|
| Batch 1 (today) | 36 | 82.6 | Configure SMTP → send all at once |

**Total capacity:** 82,560 kW across 36 companies

### Tier 2 — Needs Verification (10 companies, 22.4 MW)
"Manufacturing (likely)" — no web presence confirmed. Verify via Lursoft.lv or +371 call before sending.

| # | Company | kW | Why uncertain |
|---|---------|----|---------------|
| 1 | Riviera | 2,553 | No web, riviera.lv under construction |
| 2 | Latsr | 2,206 | No web presence |
| 3 | Kopa | 2,203 | Small town, no web |
| 4 | JSC Latgales | 2,203 | Unconfirmed industry |
| 5 | Gerhard | 1,980 | No web presence |
| 6 | Krass | 2,200 | No web presence |
| 7 | Sent | 2,130 | No web presence |
| 8 | Bermas | 1,947 | No web presence |
| 9 | Len | 2,355 | No web presence |
| 10 | Vests | 2,381 | No web presence |

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
export SMTP_USER="postmaster@yourdomain.lv"
export SMTP_PASSWORD="your-smtp-password"
export SENDER_NAME="Your Name"
export SENDER_EMAIL="your@yourdomain.lv"
export BCC_RECIPIENT="your@yourdomain.lv"
```

### Step 2: Say "Go" (or "Wait")
Reply: **"GO"** → I'll fire the full batch of 36 immediately.

---

## Expected Results (based on cold outreach benchmarks)

| Metric | Target | Notes |
|--------|--------|-------|
| Emails sent | 36 | All Tier 1 |
| Open rate | 25–40% | Latvian B2B avg |
| Reply rate | 5–10% | "Yes, interested" or "No thanks" |
| Calls booked | 2–4 | Target |
| Site visits | 1–2 | Goal |

**At 2 site visits and 1 conversion @ ~€5k installation:** ROI = €5k on this single campaign.

---

## Pipeline Verified ✅

```
$ python3 send_emails.py --dry-run-all
DRY RUN — 36 email(s) would be sent ✅
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
cd solar-scout && python3 send_emails.py --dry-run  # to check replies
```

Reply-pending companies auto-identified from `sent_log.json`.

---

*Pipeline: `solar-scout/send_emails.py` | Leads: `solar-scout/docs/leads_outreach_validated.csv` | Template: `solar-scout/docs/EMAIL_TEMPLATE.md`*
