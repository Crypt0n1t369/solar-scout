#!/usr/bin/env python3
"""
Mail-merge sender for Solar Scout outreach.
Reads validated leads from docs/leads_outreach_validated.csv and sends personalized emails via SMTP.

Usage:
    python send_emails.py --dry-run           # Preview first 3 emails (no sending)
    python send_emails.py --dry-run --all     # Preview all 15 emails (no sending)
    python send_emails.py --test              # Send to first 3 recipients only
    python send_emails.py                     # Send to all 15 validated companies

Environment variables (set in config.py or shell):
    SMTP_HOST     — SMTP server (e.g. smtp.gmail.com)
    SMTP_PORT     — SMTP port (e.g. 587)
    SMTP_USER     — SMTP username (your email)
    SMTP_PASSWORD — SMTP password or app password
    SENDER_NAME   — Your name as it appears in the email signature
    SENDER_EMAIL  — Your sender email address
    BCC_RECIPIENT — Address to BCC on all emails (recommended: your own address)
"""

import os
import sys
import csv
import json
import time
import argparse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL


def load_config():
    """Load SMTP config from environment variables (with config.py as fallback for SMTP fields only)."""
    # Env vars always win for sender identity
    sender_name  = os.getenv("SENDER_NAME", "[YOUR NAME]")
    sender_email = os.getenv("SENDER_EMAIL", "[YOUR@EMAIL.COM]")
    bcc_recip    = os.getenv("BCC_RECIPIENT", "")

    # SMTP credentials: env vars first, then config.py fallback
    host     = os.getenv("SMTP_HOST", "")
    port     = int(os.getenv("SMTP_PORT", "") or 0)  # 0 = use default
    user     = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")

    if not host:
        try:
            import config
            host     = getattr(config, "SMTP_HOST", "") or host
            port_cfg = getattr(config, "SMTP_PORT", 587)
            port     = port or int(port_cfg)
            user     = getattr(config, "SMTP_USER", "") or user
            password = getattr(config, "SMTP_PASSWORD", "") or password
            sender_name  = getattr(config, "SENDER_NAME", sender_name)
            sender_email = getattr(config, "SENDER_EMAIL", sender_email)
            bcc_recip    = getattr(config, "BCC_RECIPIENT", bcc_recip)
        except (ImportError, AttributeError):
            pass

    # Default port to 587 if unset
    if not port:
        port = 587

    return {
        "host": host, "port": port, "user": user, "password": password,
        "sender_name": sender_name, "sender_email": sender_email,
        "bcc_recipient": bcc_recip,
    }


def load_leads(csv_path="docs/leads_outreach_validated.csv"):
    """Load validated leads from CSV."""
    leads = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["capacity_kw"] = float(row.get("capacity_kw", 0) or 0)
            leads.append(row)
    return leads


def build_email_body(lead, cfg, lang="lv"):
    """Return (subject, body_text) for a lead."""
    name     = lead["decision_maker"].strip()
    company  = lead["company"].strip()
    address  = lead["address"].strip()
    capacity = int(lead["capacity_kw"])
    first_name = name.split()[0] if name else name
    greeting_lv = f"Godātais {name}," if name else "Godātais/a,"
    greeting_en = f"Dear {first_name}," if first_name else "Dear sir or madam,"

    if lang == "lv":
        subject = f"SaulesPaneļi Latvija — Bezmaksas konsultācija jūsu ražotnei"
        body = f"""{greeting_lv}

Esmu {cfg['sender_name']} no {cfg['sender_email']} — mēs palīdzam Latvijas rūpniecības uzņēmumiem saražot savu elektroenerģiju ar saules paneļiem.

Jūsu uzņēmums {company} ({address}) atbilst mūsu kritērijiem:
✔ Rūpnieciskā darbība ar lielu jumta platību
✔ Pašreizējais elektroenerģijas patēriņš
✔ Vēl neesat uzstādījuši saules paneļus

Provizoriskā aplēse: līdz {capacity:,} kW instalējamā jauda
Ietaupījums: līdz 30-50% no elektroenerģijas izmaksām

Vai būtu ērti 15 minūšu zvans šonedēļ, lai izvērtētu iespējas?

Ar cieņu,
{cfg['sender_name']} | [PHONE] | {cfg['sender_email']}

---
Šis e-pasts tika nosūtīts saskaņā ar Latvijas Personas datu aizsardzības likumu.
Ja nevēlaties saņemt turpmākus paziņojumus, lūdzu, atbildiet uz šo e-pastu ar vārdu "UNSUBSCRIBE".
"""
    else:
        subject = f"Free Solar Assessment for {company} — {capacity:,} kW Potential"
        body = f"""{greeting_en}

I'm {cfg['sender_name']} from {cfg['sender_email']}. We help Latvian manufacturing companies reduce their electricity costs by installing solar panels on their facilities.

Based on our preliminary analysis, your facility at {address} could host approximately {capacity:,} kW of solar panels — potentially cutting your electricity costs by 30–50%.

Is 15 minutes convenient this week for a quick call to discuss the specifics?

Best regards,
{cfg['sender_name']} | [PHONE] | {cfg['sender_email']}

---
This email was sent in compliance with applicable email marketing regulations.
To unsubscribe, reply with "UNSUBSCRIBE" in the subject line.
"""
    return subject, body


def build_email(lead, cfg):
    """Build a MIMEMultipart email with both LV and EN versions as alternatives."""
    company = lead["company"].strip()
    email   = lead["email"].strip()
    subject_en, body_en = build_email_body(lead, cfg, "en")
    _,      body_lv = build_email_body(lead, cfg, "lv")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject_en
    msg["From"] = f"{cfg['sender_name']} <{cfg['sender_email']}>"
    msg["To"] = email
    if cfg.get("bcc_recipient"):
        msg["Bcc"] = cfg["bcc_recipient"]
    # Attach EN first (primary), LV second (fallback)
    msg.attach(MIMEText(body_en, "plain", "utf-8"))
    msg.attach(MIMEText(body_lv, "plain", "utf-8"))
    return msg


def connect_smtp(cfg):
    """Connect to SMTP server. Returns (smtp, cfg)."""
    host, port, user, password = cfg["host"], cfg["port"], cfg["user"], cfg["password"]
    if port == 465:
        smtp = SMTP_SSL(host, port)
    else:
        smtp = SMTP(host, port)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
    smtp.login(user, password)
    return smtp


def send_email(smtp, lead, cfg):
    """Send one email (both LV+EN as alternatives). Returns (success, error)."""
    msg = build_email(lead, cfg)
    try:
        recipients = [lead["email"].strip()]
        if cfg.get("bcc_recipient"):
            recipients.append(cfg["bcc_recipient"])
        smtp.sendmail(cfg["sender_email"], recipients, msg.as_string())
        return True, None
    except Exception as e:
        return False, str(e)


def run_dry_run(leads, cfg, limit=None):
    """Print emails without sending."""
    targets = leads[:limit] if limit else leads
    print(f"\n{'='*60}")
    print(f"DRY RUN — {len(targets)} email(s) would be sent")
    print(f"{'='*60}\n")
    for i, lead in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {lead['company']} <{lead['email']}> — {int(lead['capacity_kw']):,} kW")
        for lang in ("lv", "en"):
            subject, body = build_email_body(lead, cfg, lang)
            print(f"  [{lang.upper()}] Subject: {subject}")
            preview = body[:180].replace("\n", " ").strip()
            print(f"  [{lang.upper()}] Body: {preview}...")
        print()
    return len(targets)


def run_send(leads, cfg, test_only=False, delay=30):
    """Actually send emails via SMTP. Returns (sent, failed)."""
    smtp = None
    try:
        print(f"\nConnecting to {cfg['host']}:{cfg['port']} as {cfg['user']}...")
        smtp = connect_smtp(cfg)
        print("Connected. Starting send...\n")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        print("   Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD env vars,")
        print("   or add them to config.py. See docs/SEND_GUIDE.md for setup instructions.")
        return 0, 0

    targets = leads[:3] if test_only else leads
    sent_log_path = "docs/sent_log.json"

    # Load existing log
    sent_log = []
    if os.path.exists(sent_log_path):
        try:
            sent_log = json.load(open(sent_log_path))
        except Exception:
            sent_log = []

    sent, failed = 0, []
    for i, lead in enumerate(targets, 1):
        company = lead["company"]
        email   = lead["email"]
        status_icon = "⏳"
        err_msg = None

        try:
            ok, err_msg = send_email(smtp, lead, cfg)
            if ok:
                status_icon = "✅"
                sent += 1
            else:
                status_icon = "❌"
                failed.append({"company": company, "email": email, "error": err_msg})
        except Exception as e:
            status_icon = "❌"
            err_msg = str(e)
            failed.append({"company": company, "email": email, "error": err_msg})

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "company": company,
            "email": email,
            "capacity_kw": lead["capacity_kw"],
            "status": "sent" if status_icon == "✅" else "failed",
            "error": err_msg,
            "test": test_only,
        }
        sent_log = [e for e in sent_log if e["email"] != email]  # deduplicate retries
        sent_log.append(log_entry)

        print(f"  {status_icon} [{i}/{len(targets)}] {company} <{email}>")
        if err_msg:
            print(f"       Error: {err_msg}")

        # Save log after each send (crash-resilient)
        with open(sent_log_path, "w", encoding="utf-8") as f:
            json.dump(sent_log, f, indent=2, ensure_ascii=False)

        if i < len(targets):
            print(f"  ...waiting {delay}s before next email...")
            time.sleep(delay)

    smtp.quit()

    # Summary
    print(f"\n{'='*50}")
    print(f"SEND COMPLETE — {sent} sent, {len(failed)} failed")
    if failed:
        print("Failures:")
        for f in failed:
            print(f"  ❌ {f['company']} <{f['email']}>: {f['error']}")
    print(f"Log saved to docs/sent_log.json")
    print(f"{'='*50}\n")
    return sent, failed


def main():
    parser = argparse.ArgumentParser(description="Solar Scout mail-merge sender")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview emails without sending (first 3 only)")
    parser.add_argument("--dry-run-all", action="store_true",
                        help="Preview all emails without sending")
    parser.add_argument("--test", action="store_true",
                        help="Send to first 3 recipients only (real send)")
    parser.add_argument("--delay", type=int, default=30,
                        help="Seconds between each email (default: 30)")
    args = parser.parse_args()

    cfg   = load_config()
    leads = load_leads()

    if args.dry_run:
        run_dry_run(leads, cfg, limit=3)
        return 0
    if args.dry_run_all:
        run_dry_run(leads, cfg, limit=None)
        return 0
    if not cfg["host"] or not cfg["user"] or not cfg["password"]:
        print("⚠️  SMTP not configured — cannot send.")
        print("   Set the following environment variables (or add to config.py):")
        print("   SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASSWORD")
        print("   SENDER_NAME, SENDER_EMAIL, BCC_RECIPIENT")
        print()
        print("   Run with --dry-run to preview emails without sending.")
        return 1

    if args.test:
        sent, failed = run_send(leads, cfg, test_only=True, delay=args.delay)
        return 0 if not failed else 1

    sent, failed = run_send(leads, cfg, test_only=False, delay=args.delay)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
