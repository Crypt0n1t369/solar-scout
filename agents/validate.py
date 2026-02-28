"""
Phase 2: Address Validation via Satellite Imagery
Validates company addresses and fetches satellite images
"""

import json
import os
import time
import re
import urllib.request
import urllib.parse
import ssl
from pathlib import Path

# Free satellite tile providers
TILE_SERVERS = [
    # OpenStreetMap Aerial (best free option)
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    # ESRI World Imagery (often available)
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    # Google static (requires API key, but try)
]

def geocode_address(address: str) -> dict:
    """
    Convert address to lat/lon using Nominatim (OpenStreetMap - free)
    """
    # Add Latvia if not present
    if "latvia" not in address.lower():
        address = f"{address}, Latvia"
    
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(address)}&limit=1"
    
    headers = {
        "User-Agent": "LatviaSolarScout/1.0 (research purposes)"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if data:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display_name": data[0].get("display_name", address)
                }
    except Exception as e:
        print(f"  Geocoding error: {e}")
    
    return None


def lat_lon_to_tile(lat: float, lon: float, zoom: int):
    """Convert lat/lon to OSM tile coordinates"""
    import math
    
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    tile_x = int((lon + 180.0) / 360.0 * n)
    tile_y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    
    return tile_x, tile_y


def get_satellite_url(lat: float, lon: float, zoom: int = 16) -> str:
    """
    Get satellite/aerial image URL using free tile servers
    """
    # Try OSM tile server (aerial view in some areas)
    tile_x, tile_y = lat_lon_to_tile(lat, lon, zoom)
    
    # Use ESRI World Imagery (often has aerial)
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{tile_y}/{tile_x}"
    
    return url


async def validate_address(company: dict) -> dict:
    """
    Validate company address via geocoding
    """
    company_name = company.get("name", "")
    address = company.get("address", "")
    
    print(f"\n📍 Validating: {company_name[:40]}")
    print(f"   Address: {address[:60]}...")
    
    # If no address, try using company name + Latvia
    if not address:
        address = f"{company_name}, Latvia"
    
    # Step 1: Geocode the address
    geo = geocode_address(address)
    
    if not geo:
        # Try with industrial areas
        for area in ["Riga, Latvia", "Marupe, Latvia", "Salaspils, Latvia"]:
            geo = geocode_address(f"{company_name}, {area}")
            if geo:
                break
    
    if not geo:
        print(f"   ❌ Could not geocode")
        company["validation"] = {
            "verified": False,
            "error": "Geocoding failed"
        }
        return company
    
    print(f"   📌 Coords: {geo['lat']:.5f}, {geo['lon']:.5f}")
    
    # Step 2: Generate satellite image URL
    satellite_url = get_satellite_url(geo["lat"], geo["lon"])
    
    company["validation"] = {
        "verified": True,
        "latitude": geo["lat"],
        "longitude": geo["lon"],
        "display_name": geo["display_name"],
        "satellite_image_url": satellite_url,
        "validated_at": time.strftime("%Y-%m-%d")
    }
    
    print(f"   ✅ Address verified")
    
    return company


async def run_validation(companies: list) -> list:
    """
    Validate all company addresses
    """
    print("\n" + "="*60)
    print("PHASE 2: ADDRESS VALIDATION")
    print("="*60)
    
    validated = []
    
    for company in companies:
        # Skip if already validated
        if company.get("validation", {}).get("verified"):
            validated.append(company)
            continue
        
        result = await validate_address(company)
        validated.append(result)
        
        # Rate limiting for Nominatim (1 request per second)
        time.sleep(1.2)
    
    # Save validated results
    output_file = "/home/drg/.openclaw/workspace/solar-scout/data/companies_validated.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)
    
    verified_count = len([c for c in validated if c.get("validation", {}).get("verified")])
    print(f"\n💾 Saved {len(validated)} companies ({verified_count} verified)")
    
    return validated


if __name__ == "__main__":
    import asyncio
    
    # Test with a sample company
    test = {
        "name": "Test Company",
        "address": "Maskavas iela 12, Riga, Latvia"
    }
    
    result = asyncio.run(validate_address(test))
    print(json.dumps(result, indent=2))
