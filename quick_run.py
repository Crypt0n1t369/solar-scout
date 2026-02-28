#!/usr/bin/env python3
"""
Quick run - just enrichment + final steps
"""

import json
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.enrich import run_enrichment
from agents.capacity import run_capacity_analysis
from agents.annotate import run_annotation, generate_summary


async def main():
    print("="*60)
    print("QUICK RUN - Enrichment + Final")
    print("="*60)
    
    # Load detected companies
    with open("data/companies_detected.json") as f:
        companies = json.load(f)
    
    print(f"Loaded {len(companies)} companies")
    
    # Enrichment
    companies = await run_enrichment(companies)
    
    # Capacity analysis
    companies = run_capacity_analysis(companies)
    
    # Annotation
    companies = run_annotation(companies)
    
    # Summary
    targets = generate_summary(companies)
    
    print(f"\n✅ COMPLETE: {len(targets)} targets")
    
    return companies


if __name__ == "__main__":
    asyncio.run(main())
