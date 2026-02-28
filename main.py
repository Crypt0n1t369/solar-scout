#!/usr/bin/env python3
"""
Latvia Solar Scout - Main Orchestrator
Runs all phases to discover, validate, and enrich solar leads
"""

import asyncio
import json
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.discover import run_discovery
from agents.validate import run_validation
from agents.detector import run_detection
from agents.capacity import run_capacity_analysis
from agents.enrich import run_enrichment
from agents.annotate import run_annotation, generate_summary


async def main():
    """
    Main execution pipeline
    """
    print("="*60)
    print("🌞 LATVIA SOLAR SCOUT - LEAD MAGNET AGENT")
    print("="*60)
    print("Finding manufacturing companies without solar in Latvia\n")
    
    # Phase 1: Discovery
    companies = await run_discovery()
    
    if not companies:
        print("❌ No companies discovered. Exiting.")
        return
    
    # Phase 2: Address Validation
    companies = await run_validation(companies)
    
    # Phase 3: Solar Detection
    companies = await run_detection(companies)
    
    # Phase 4: Capacity Calculation
    companies = run_capacity_analysis(companies)
    
    # Phase 5: Decision Maker Enrichment
    companies = await run_enrichment(companies)
    
    # Phase 6: Image Annotation
    companies = run_annotation(companies)
    
    # Generate final report
    targets = generate_summary(companies)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    print(f"Total companies processed: {len(companies)}")
    print(f"Qualified leads: {len(targets)}")
    print("\nResults saved to: /home/drg/.openclaw/workspace/solar-scout/data/companies_final.json")
    
    return companies


if __name__ == "__main__":
    asyncio.run(main())
