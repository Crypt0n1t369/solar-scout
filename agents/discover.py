"""
Phase 1: Company Discovery Module
Uses OpenClaw browser for reliable search
"""

import json
import asyncio
import os
from datetime import datetime


async def discover_with_browser(max_results=20):
    """
    Use browser to search for Latvian manufacturing companies
    """
    from browser import browser
    
    discovered = []
    seen_names = set()
    
    print(f"🔍 Starting company discovery via browser...")
    
    # Latvian manufacturing search queries
    queries = [
        "Latvia manufacturing companies directory",
        "Latvian factory industrial companies list", 
        "SIA Latvia manufacturing production",
        "Riga industrial zone factories",
    ]
    
    for query in queries:
        print(f"  Searching: {query}")
        
        try:
            # Open Google search
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
            
            result = await browser(action="navigate", targetUrl=search_url)
            
            # Wait for results
            await asyncio.sleep(3)
            
            # Get snapshot
            snapshot = await browser(action="snapshot", compact=True, maxChars=15000)
            
            print(f"    Got {len(snapshot.get('text', ''))} chars")
            
            # Extract results from snapshot text
            text = snapshot.get("text", "")
            
            # Look for result titles
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # Skip short lines or navigation
                if len(line) < 10:
                    continue
                if any(x in line.lower() for x in ['menu', 'cookie', 'privacy', 'sign in', 'settings']):
                    continue
                
                # This is a rough heuristic - in reality we'd parse the DOM
                # For now, collect potential company names
                if line and line not in seen_names and len(line) > 5:
                    seen_names.add(line)
                    discovered.append({
                        "name": line[:60],
                        "source_url": f"google search: {query}",
                        "discovered_at": datetime.now().isoformat(),
                        "search_query": query
                    })
                    
        except Exception as e:
            print(f"    Error: {e}")
        
        await asyncio.sleep(1)
    
    # Deduplicate
    unique = {}
    for c in discovered:
        key = c["name"].lower().strip()[:30]
        if key not in unique:
            unique[key] = c
    
    final = list(unique.values())
    print(f"✅ Discovery complete: {len(final)} unique entries")
    
    return final[:max_results]


async def run_discovery():
    """Main execution"""
    print("\n" + "="*60)
    print("PHASE 1: COMPANY DISCOVERY (Browser)")
    print("="*60)
    
    try:
        companies = await discover_with_browser(max_results=20)
    except Exception as e:
        print(f"Browser failed: {e}")
        companies = []
    
    output_file = "/home/drg/.openclaw/workspace/solar-scout/data/companies_raw.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved {len(companies)} entries")
    
    return companies


if __name__ == "__main__":
    asyncio.run(run_discovery())
