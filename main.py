#!/usr/bin/env python3
"""
🌞 LATVIA SOLAR SCOUT - LEAD MAGNET AGENT
==========================================
Robust lead generation using Selenium + Firefox

Usage:
    python3 main.py --country LV --query "manufacturing warehouse factory" --max-results 50
"""

import asyncio
import argparse
import json
import random
import time
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Core imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

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

# Exclude domains (non-relevant)
EXCLUDE_DOMAINS = [
    "zhihu.com", "baidu.com", "weibo.com", "qq.com", 
    "alibaba.com", "tmall.com", "taobao.com", "jd.com",
    "youtube.com", "facebook.com", "twitter.com", "instagram.com",
    "linkedin.com", "pinterest.com", "reddit.com", "wikipedia.org",
    "duckduckgo.com", "google.com", "bing.com", "yahoo.com",
]

# ============================================================================
# BROWSER SETUP
# ============================================================================

def get_firefox_driver(headless: bool = True) -> webdriver.Firefox:
    """Initialize Firefox WebDriver."""
    opts = Options()
    if headless:
        opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    # Randomize User-Agent
    opts.set_preference("general.useragent.override", random.choice(USER_AGENTS))
    return webdriver.Firefox(options=opts)


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
    }


def random_delay(min_sec: float = 2.0, max_sec: float = 5.0) -> None:
    """Random delay to avoid bot detection."""
    delay = random.uniform(min_sec, max_sec)
    print(f"    💤 Waiting {delay:.1f}s...")
    time.sleep(delay)


def is_valid_company_url(url: str) -> bool:
    """Check if URL is a likely company website."""
    if not url or not url.startswith('http'):
        return False
    url_lower = url.lower()
    # Exclude domains
    if any(ex in url_lower for ex in EXCLUDE_DOMAINS):
        return False
    # Must have some domain structure
    if url_lower.count('/') < 3 and '.' in url.split('/')[-1]:
        return True
    return True


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
# SEARCH PHASE - SELENIUM
# ============================================================================

def search_with_firefox(driver: webdriver.Firefox, query: str) -> List[Dict[str, str]]:
    """
    Search using DuckDuckGo via Selenium + Firefox.
    Returns list of {title, url, body}
    """
    results = []
    
    print(f"  🔍 Firefox DDG: {query[:50]}...")
    
    try:
        # Navigate to DuckDuckGo
        search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&t=h_&ia=web"
        driver.get(search_url)
        
        # Wait for results to load
        time.sleep(4)
        
        # Get all links from the page
        links = driver.find_elements(By.TAG_NAME, 'a')
        
        seen_urls = set()
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                # Skip invalid or excluded URLs
                if not href or not href.startswith('http'):
                    continue
                if any(ex in href.lower() for ex in EXCLUDE_DOMAINS):
                    continue
                if href in seen_urls:
                    continue
                    
                seen_urls.add(href)
                
                # Get snippet/body if available
                try:
                    # Try to find parent to get snippet
                    parent = link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'result')]")
                    body = parent.text[:200] if parent else ""
                except:
                    body = ""
                
                # Extract title from link text
                title = text[:100] if text else href[:60]
                
                results.append({
                    "title": title,
                    "url": href,
                    "body": body,
                    "source": "duckduckgo_firefox"
                })
                
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"    ❌ Firefox error: {e}")
    
    return results


def discover_companies(country: str, queries: List[str], max_per_query: int = 15) -> List[Dict[str, Any]]:
    """
    Phase 1: Company Discovery
    Uses Selenium + Firefox
    """
    print("\n" + "=" * 60)
    print("PHASE 1: COMPANY DISCOVERY (Selenium + Firefox)")
    print("=" * 60)
    
    # Initialize Firefox
    print("  🌐 Starting Firefox...")
    driver = get_firefox_driver(headless=True)
    
    all_results = []
    seen_urls = set()
    
    try:
        for i, query in enumerate(queries):
            print(f"\n[{i+1}/{len(queries)}] {query}")
            
            # Search
            results = search_with_firefox(driver, query)
            
            # Deduplicate
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_results.append(r)
            
            print(f"    ✅ Got {len(results)} results (total: {len(all_results)})")
            
            # Random delay between queries
            if i < len(queries) - 1:
                random_delay(3, 6)
    
    finally:
        driver.quit()
        print("  🔒 Firefox closed")
    
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
        
        # Extract company name from title
        company_name = ""
        if soup.title:
            company_name = soup.title.string or ""
        
        # Clean up title
        if company_name:
            for suffix in [" - Official Website", " | Official Site", " - Wikipedia"]:
                company_name = company_name.replace(suffix, "")
        
        h1 = soup.find("h1")
        if h1:
            h1_text = h1.get_text(strip=True)
            if h1_text and len(h1_text) < 100:
                company_name = h1_text
        
        # Extract description from meta tags
        description = ""
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]
        
        # Look for contact info
        email = ""
        phone = ""
        address = ""
        
        text = soup.get_text()
        
        # Email pattern
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            email = email_match.group(0)
        
        # Phone pattern
        phone_match = re.search(r'\+?[\d\s\-\(\)]{7,20}', text)
        if phone_match:
            phone = phone_match.group(0)
        
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
    
    # Prioritize likely company URLs
    to_scrape = companies[:max_to_scrape]
    
    print(f"  📊 Scraping {len(to_scrape)} URLs")
    
    for i, company in enumerate(to_scrape):
        url = company.get("url", "")
        print(f"\n[{i+1}/{len(to_scrape)}] {url[:50]}...")
        
        info = scrape_company_info(url)
        
        if info:
            merged = {**company, **info}
            enriched.append(merged)
            print(f"    ✅ {info.get('name', 'Unknown')[:40]}")
        else:
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
        "metal", "wood", "food", "processing", "fabrication", "machining",
        "assembly", "logistics", "distribution", "storage", "wholesale",
        "construction", "materials", "equipment", "machinery",
        "workshop", "plant", "manufacture", "producer"
    ]
    
    # Keywords to exclude
    exclude_keywords = [
        "retail", "restaurant", "cafe", "shop", "store", "hotel",
        "bank", "insurance", "finance", "legal", "consulting",
        "school", "university", "hospital", "clinic", "health",
        "government", "municipality", "association", "club"
    ]
    
    validated = []
    
    for c in companies:
        # Search in all text fields
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
            c["validation_reason"] = f"positive={has_positive}, exclude={exclude_count}"
    
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
    
    # Phase 2: Enrichment
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
    parser.add_argument("--no-headless", action="store_true", help="Run browser visible")
    
    args = parser.parse_args()
    
    queries = None
    if args.queries:
        queries = args.queries
    elif args.query:
        queries = [args.query]
    
    # Override headless mode
    if args.no_headless:
        import sys
        # Patch the driver function
        import __main__
        __main__.get_firefox_driver = lambda headless=False: webdriver.Firefox(
            options=Options() if not headless else Options()
        )
    
    run_pipeline(country=args.country, max_results=args.max_results, custom_queries=queries)
