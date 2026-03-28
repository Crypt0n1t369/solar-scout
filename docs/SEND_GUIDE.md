# Solar Scout — Email Sending Guide

This guide walks you through setting up SMTP and sending your first outreach batch.

---

## Prerequisites

- Validated leads: `docs/leads_outreach_validated.csv` (15 companies, 33.4 MW)
- Email drafts: `docs/email_drafts_validated.md` (reviewed and ready)
- SMTP account (see options below)

---

## Step 1 — Choose Your SMTP Provider

### Option A: Gmail (free, recommended for small batches)
1. Enable 2-Factor Authentication on your Google account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Generate an App Password for "Mail"
4. Copy the 16-character password

**Settings:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   ← the app password (with spaces)
```

### Option B: Mailgun (free tier: 5,000 emails/month)
1. Sign up at mailgun.com and verify your domain
2. Go to Settings → SMTP Credentials
3. Use the SMTP login credentials provided

**Settings:**
```
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.lv
SMTP_PASSWORD=your-smtp-password
```

### Option C: SendGrid (free tier: 100 emails/day)
1. Sign up at sendgrid.com
2. Create an API key with Mail Send permission
3. Use the SMTP relay: `smtp.sendgrid.net:587`

**Settings:**
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your_api_key_here
```

### Option D: Your own mail server
Ask your hosting provider for SMTP credentials.

---

## Step 2 — Configure Credentials

### Option 1: Environment variables (recommended)
```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your@email.com"
export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
export SENDER_NAME="Jānis Zeltins"
export SENDER_EMAIL="janis@yourcompany.lv"
export BCC_RECIPIENT="janis@yourcompany.lv"  # receives a BCC copy of every email
```

### Option 2: Edit config.py
Add these fields to `config.py`:
```python
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your@email.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"
SENDER_NAME = "Jānis Zeltins"
SENDER_EMAIL = "your@email.com"
BCC_RECIPIENT = "your@email.com"
```

---

## Step 3 — Preview Emails (Dry Run)

Always preview before sending:
```bash
python3 send_emails.py --dry-run          # Preview first 3 emails
python3 send_emails.py --dry-run --all    # Preview all 15 emails
```

Verify:
- [ ] Sender name and email are correct
- [ ] Decision maker names are correct
- [ ] Company capacity (kW) looks right
- [ ] Subject lines are appropriate

---

## Step 4 — Send a Test Batch (3 emails)

Send to just the first 3 recipients to verify deliverability:
```bash
python3 send_emails.py --test
```

Wait 5 minutes, then check:
- [ ] Emails arrived in inbox (not spam)
- [ ] BCC copy received in your inbox
- [ ] Links/CTA are working

If emails went to spam: add spf/dkim records for your domain, or use a dedicated sending service (Mailgun, SendGrid).

---

## Step 5 — Send Full Batch

Once test batch is confirmed deliverable:
```bash
python3 send_emails.py
```

Each email is sent with a 30-second delay to avoid spam filters. Full batch of 15 emails takes ~7 minutes.

---

## Tracking Results

After sending, check `docs/sent_log.json` for delivery status:
```bash
cat docs/sent_log.json
```

Or use the built-in reply tracker:
```bash
python3 send_emails.py --check-replies
```

This shows:
- Which emails were sent / failed and when
- Which companies are ready for follow-up (5+ business days)
- Suggested next action (call or wait)

Expected fields per entry:
- `timestamp`: ISO 8601 UTC
- `company`: company name
- `email`: recipient address
- `capacity_kw`: estimated solar capacity
- `status`: `"sent"` or `"failed"`
- `error`: error message (if failed)
- `test`: `true` if sent via `--test` flag

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `SMTP authentication failed` | Wrong password | Regenerate app password / check SMTP credentials |
| `Connection timed out` | Firewall / wrong port | Try port 587 (TLS) or 465 (SSL) |
| All emails in spam | SPF/DKIM not set | Use Mailgun/SendGrid with verified domain, or set up Gmail SPF |
| `SMTP not configured` | Missing env vars | Set all 5 required vars or add to config.py |
| Emails rejected by recipient server | Sending too fast | Increase `--delay` to 60 seconds |

---

## Latvian Email Compliance

Your emails include:
- ✅ Latvian-language unsubscribe instruction
- ✅ BCC copy to yourself (for your records)
- ✅ Physical mailing address in footer (add to `config.py: SENDER_ADDRESS`)

**Add your physical address** to `config.py` to comply with Latvian spam law:
```python
SENDER_ADDRESS = "Riga, Latvia"
```
