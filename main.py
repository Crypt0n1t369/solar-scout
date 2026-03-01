#!/usr/bin/env python3
"""
🌞 LATVIA SOLAR SCOUT - LEAD MAGNET AGENT
==========================================
Robust lead generation using DuckDuckGo + BeautifulSoup

Usage:
    python3 main.py --country LV --query "manufacturing warehouse factory" --max-results 50
"""

import asyncio
import argparse
import json
import random
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Core imports
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# ============================================================================
# CONFIGURATION
# ============================================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv/121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv/121.0) Gecko/20100101 Firefox/121.0",
]

DEFAULT_QUERIES = {
    "LV": [
        "site:lv manufacturing company SIA",
        "site:lv industrial warehouse factory production",
        "Latvia factory industrial manufacturing list",
        "Riga manufacturing warehouse companies",
        "Latvia metal working fabrication SIA",
        "Latvia food processing production company",
        "Latvia woodworking furniture factory",
        "Latvia construction materials manufacturing",
        "Latvia logistics warehouse distribution center",
        "Latvia SME industrial production business",
    ],
    "EE": [
        "Estonia manufacturing companies",
        "Estonia industrial warehouse factories",
    ],
    "LT": [
        "Lithuania manufacturing companies",
        "Lithuania industrial warehouse factories",
    ],
}

# ============================================================================
# UTILITIES
# ============================================================================

def get_random_headers() -> Dict[str, str]:
    """Generate randomized request headers."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def random_delay(min_sec: float = 2.0, max_sec: float = 5.0) -> None:
    """Random delay to avoid bot detection."""
    delay = random.uniform(min_sec, max_sec)
    print(f"    💤 Waiting {delay:.1f}s...")
    time.sleep(delay)


def safe_request(url: str, timeout: int = 15, max_retries: int = 3) -> Optional[requests.Response]:
    """Make HTTP request with retries and error handling."""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=get_random_headers(),
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            print(f"    ⏱️  Timeout (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.HTTPError as e:
            print(f"    ⚠️  HTTP {e.response.status_code} (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            # Handle DNS and connection errors
            error_str = str(e).lower()
            if 'dns' in error_str or 'name or service not known' in error_str:
                print(f"    🔴 DNS failure (attempt {attempt + 1}/{max_retries})")
            else:
                print(f"    ❌ Request error: {e} (attempt {attempt + 1}/{max_retries})")
        
        if attempt < max_retries - 1:
            wait_time = random.uniform(5, 15)
            print(f"    ⏳ Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
    
    return None


# ============================================================================
# SEARCH PHASE
# ============================================================================

def search_duckduckgo(query: str, max_results: int = 50) -> List[Dict[str, str]]:
    """
    Search using DuckDuckGo (no API key required).
    Returns list of {title, url, body}
    """
    results = []
    ddgs = DDGS()
    
    print(f"  🔍 DDGS: {query}")
    
    # Domains to exclude (non-relevant)
    exclude_domains = ["zhihu.com", "baidu.com", "weibo.com", "qq.com", 
                       "alibaba.com", "tmall.com", "taobao.com", "jd.com"]
    
    try:
        # Get more results than needed (DDGS returns ~10 per call)
        # Use region filter for better local results
        for r in ddgs.text(query, max_results=max_results * 2, region="lv-lv", safesearch="Off"):
            url = r.get("href", "")
            
            # Filter out excluded domains
            if any(ex in url.lower() for ex in exclude_domains):
                continue
                
            results.append({
                "title": r.get("title", ""),
                "url": url,
                "body": r.get("body", ""),
                "source": "duckduckgo"
            })
            if len(results) >= max_results:
                break
    except Exception as e:
        print(f"    ❌ DDGS error: {e}")
    
    return results


def search_searxng(query: str, max_results: int = 50) -> List[Dict[str, str]]:
    """
    Fallback: Search via public SearXNG instance.
    """
    # Public instances (rotate if one fails)
    searx_instances = [
        "https://searxng.site",
        "https://searxng.website",
        "https://searx.tiekoetter.com",
    ]
    
    results = []
    
    for instance in searx_instances:
        try:
            url = f"{instance}/search"
            params = {
                "q": query,
                "format": "json",
                "engines": "google,bing",
                "language": "en",
            }
            
            print(f"  🔍 SearXNG ({instance}): {query}")
            
            response = requests.get(url, params=params, headers=get_random_headers(), timeout=20)
            response.raise_for_status()
            data = response.json()
            
            for r in data.get("results", [])[:max_results]:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "body": r.get("content", ""),
                    "source": f"searxng:{instance}"
                })
                if len(results) >= max_results:
                    break
            
            if results:
                break
                
        except Exception as e:
            print(f"    ⚠️  SearXNG {instance} failed: {e}")
            continue
    
    return results


def discover_companies(country: str, queries: List[str], max_per_query: int = 15) -> List[Dict[str, Any]]:
    """
    Phase 1: Company Discovery
    Uses DuckDuckGo with fallback to SearXNG
    """
    print("\n" + "=" * 60)
    print("PHASE 1: COMPANY DISCOVERY (DuckDuckGo + SearXNG)")
    print("=" * 60)
    
    all_results = []
    seen_urls = set()
    
    for i, query in enumerate(queries):
        print(f"\n[{i+1}/{len(queries)}] {query}")
        
        # Try DuckDuckGo first
        results = search_duckduckgo(query, max_results=max_per_query)
        
        # Fallback to SearXNG if no results
        if not results:
            print(f"    🔄 Falling back to SearXNG...")
            results = search_searxng(query, max_results=max_per_query)
        
        # Deduplicate by URL
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)
        
        print(f"    ✅ Got {len(results)} results (total: {len(all_results)})")
        
        # Random delay between queries
        if i < len(queries) - 1:
            random_delay(3, 6)
    
    print(f"\n💾 Discovered {len(all_results)} unique URLs")
    return all_results


# ============================================================================
# SCRAPING PHASE
# ============================================================================

def scrape_company_info(url: str) -> Optional[Dict[str, Any]]:
    """
    Phase 2: Extract company details from URL.
    Returns company info dict or None if failed.
    """
    response = safe_request(url, timeout=15)
    if not response:
        return None
    
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract company name from title or h1
        company_name = ""
        if soup.title:
            company_name = soup.title.string or ""
        h1 = soup.find("h1")
        if h1:
            company_name = h1.get_text(strip=True) or company_name
        
        # Remove common suffixes
        for suffix in [" - Wikipedia", " | Official Website", " - Official Site"]:
            company_name = company_name.replace(suffix, "")
        
        # Extract description from meta tags or paragraphs
        description = ""
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]
        
        # Look for contact info
        email = ""
        phone = ""
        address = ""
        
        # Search in text for common patterns
        text = soup.get_text()
        
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            email = email_match.group(0)
        
        phone_match = re.search(r'\+?[\d\s\-\(\)]{7,20}', text)
        if phone_match:
            phone = phone_match.group(0)
        
        # Look for address-like patterns
        address_patterns = [
            r'\d+\s+[\w\s]+,\s*\d{5}\s+\w+',  # Street, ZIP City
            r'\w+\s+street\s+\d+.*?\w+',       # street address
        ]
        for pattern in address_patterns:
            addr_match = re.search(pattern, text, re.IGNORECASE)
            if addr_match:
                address = addr_match.group(0)
                break
        
        return {
            "name": company_name[:100],
            "url": url,
            "description": description[:500],
            "email": email,
            "phone": phone,
            "address": address,
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"    ❌ Parse error: {e}")
        return None


def enrich_companies(companies: List[Dict[str, Any]], max_to_scrape: int = 30) -> List[Dict[str, Any]]:
    """
    Phase 2: Enrich company data by scraping their websites.
    """
    print("\n" + "=" * 60)
    print("PHASE 2: COMPANY ENRICHMENT (Scraping)")
    print("=" * 60)
    
    enriched = []
    
    # Prioritize likely company URLs (filter out search engines, directories)
    priority_urls = []
    exclude_domains = ["google", "bing", "yahoo", "wikipedia", "facebook", "linkedin", 
                       "twitter", "instagram", "youtube", "pinterest", "reddit"]
    
    for c in companies:
        url = c.get("url", "")
        if not url:
            continue
        if not any(ex in url.lower() for ex in exclude_domains):
            priority_urls.append(c)
    
    # Limit scraping
    to_scrape = priority_urls[:max_to_scrape]
    
    print(f"  📊 Scraping {len(to_scrape)} URLs (filtered from {len(companies)})")
    
    for i, company in enumerate(to_scrape):
        url = company.get("url", "")
        print(f"\n[{i+1}/{len(to_scrape)}] {url[:60]}...")
        
        info = scrape_company_info(url)
        
        if info:
            # Merge with original data
            merged = {**company, **info}
            enriched.append(merged)
            print(f"    ✅ {info.get('name', 'Unknown')[:40]}")
        else:
            # Keep original if scrape failed
            enriched.append(company)
            print(f"    ⚠️  Kept original data")
        
        # Random delay between scrapes
        if i < len(to_scrape) - 1:
            random_delay(2, 4)
    
    print(f"\n💾 Enriched {len(enriched)} companies")
    return enriched


# ============================================================================
# VALIDATION & FILTERING
# ============================================================================

def validate_companies(companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Phase 3: Validate and filter for likely manufacturing/industrial companies.
    """
    print("\n" + "=" * 60)
    print("PHASE 3: VALIDATION & FILTERING")
    print("=" * 60)
    
    # Keywords indicating manufacturing/industrial
    positive_keywords = [
        "manufacturing", "factory", "production", "industrial", "warehouse",
        "metal", "wood", "food", "加工", "production", "fabrik",
        "manufacturing", "fabrication", "machining", "assembly",
        "logistics", "distribution", "storage", "wholesale",
        "construction", "materials", "equipment", "machinery"
    ]
    
    # Keywords to exclude (not real manufacturing targets)
    exclude_keywords = [
        "retail", "restaurant", "cafe", "shop", "store",
        "bank", "insurance", "finance", "legal", "consulting",
        "school", "university", "hospital", "clinic",
        "government", "municipality", "association"
    ]
    
    validated = []
    
    for c in companies:
        text = f"{c.get('title', '')} {c.get('body', '')} {c.get('name', '')} {c.get('description', '')}".lower()
        
        # Must have at least one positive keyword
        has_positive = any(kw in text for kw in positive_keywords)
        
        # Must not have too many exclude keywords
        exclude_count = sum(1 for kw in exclude_keywords if kw in text)
        
        if has_positive and exclude_count < 2:
            c["validation"] = "passed"
            c["validation_reason"] = "matches manufacturing/industrial criteria"
            validated.append(c)
        else:
            c["validation"] = "failed"
            c["validation_reason"] = f"positive={has_positive}, exclude_count={exclude_count}"
    
    print(f"  ✅ Validated: {len(validated)}/{len(companies)} passed")
    return validated


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline(country: str = "LV", max_results: int = 50, custom_queries: List[str] = None):
    """
    Run full lead generation pipeline.
    """
    print("\n" + "🌞" * 20)
    print(f"LATVIA SOLAR SCOUT - LEAD MAGNET AGENT")
    print(f"Target: {country}")
    print(f"Max results: {max_results}")
    print("🌞" * 20 + "\n")
    
    # Determine queries
    if custom_queries:
        queries = custom_queries
    else:
        queries = DEFAULT_QUERIES.get(country, DEFAULT_QUERIES["LV"])
    
    # Phase 1: Discovery
    discovered = discover_companies(country, queries, max_per_query=max_results // len(queries))
    
    if not discovered:
        print("\n❌ No companies discovered. Exiting.")
        return []
    
    # Save raw discovery
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    raw_file = output_dir / f"companies_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(discovered, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved raw discovery to {raw_file}")
    
    # Phase 2: Enrichment (scrape websites)
    enriched = enrich_companies(discovered, max_to_scrape=min(30, len(discovered)))
    
    # Phase 3: Validation
    validated = validate_companies(enriched)
    
    # Save final leads
    leads_file = output_dir / f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(leads_file, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)
    
    print(f"\n" + "=" * 60)
    print(f"✅ COMPLETE - {len(validated)} validated leads saved to:")
    print(f"   {leads_file}")
    print("=" * 60)
    
    return validated


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solar Scout - Lead Generation Agent")
    parser.add_argument("--country", default="LV", help="Country code (LV, EE, LT)")
    parser.add_argument("--query", help="Custom search query (overrides default)")
    parser.add_argument("--queries", nargs="+", help="Custom search queries")
    parser.add_argument("--max-results", type=int, default=50, help="Max results per query")
    parser.add_argument("--min-employees", type=int, default=10, help="Min employees (heuristic)")
    
    args = parser.parse_args()
    
    queries = None
    if args.queries:
        queries = args.queries
    elif args.query:
        queries = [args.query]
    
    run_pipeline(country=args.country, max_results=args.max_results, custom_queries=queries)
