#!/usr/bin/env python3
"""
Latvia Solar Scout - Load curated companies and run pipeline
"""

import json
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.latvia_companies import COMPANIES
from agents.validate import run_validation
from agents.detector import run_detection
from agents.capacity import run_capacity_analysis
from agents.enrich import run_enrichment
from agents.annotate import run_annotation, generate_summary


async def main():
    print("="*60)
    print("🌞 LATVIA SOLAR SCOUT - LEAD MAGNET AGENT")
    print("="*60)
    
    # Load curated companies
    companies = []
    for c in COMPANIES:
        companies.append({
            "name": c["name"],
            "address": c["address"],
            "website": c.get("website", ""),
            "industry": c.get("industry", ""),
            "discovered_at": datetime.now().isoformat(),
            "source": "curated_list"
        })
    
    print(f"\n📋 Loaded {len(companies)} companies from curated list")
    
    # Show first few
    for c in companies[:5]:
        print(f"  - {c['name']}: {c['address']}")
    
    # Save raw
    output_dir = "/home/drg/.openclaw/workspace/solar-scout/data"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/companies_raw.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    # Phase 2: Validation
    companies = await run_validation(companies)
    
    # Phase 3: Solar Detection
    companies = await run_detection(companies)
    
    # Phase 4: Capacity Calculation
    companies = run_capacity_analysis(companies)
    
    # Phase 5: Enrichment
    companies = await run_enrichment(companies)
    
    # Phase 6: Annotation
    companies = run_annotation(companies)
    
    # Summary
    targets = generate_summary(companies)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    print(f"Total: {len(companies)} | Targets: {len(targets)}")
    
    return companies


if __name__ == "__main__":
    asyncio.run(main())
