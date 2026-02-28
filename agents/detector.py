"""
Phase 3: Solar Panel Detection using Computer Vision
Analyzes satellite images to detect presence of solar panels
Uses PIL instead of OpenCV
"""

import json
import os
from PIL import Image, ImageStat, ImageFilter
import urllib.request
import ssl

OUTPUT_DIR = "/home/drg/.openclaw/workspace/solar-scout/output/images"


def download_satellite_image(url: str, company_name: str) -> str:
    """
    Download satellite image to local file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
    safe_name = safe_name.replace(' ', '_')
    filename = f"{safe_name}_sat.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(filepath):
        return filepath
    
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        
        print(f"   📥 Downloaded: {filename}")
        return filepath
        
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return None


def detect_solar_pil(image_path: str) -> dict:
    """
    Detect solar panels using PIL-based image analysis
    """
    if not image_path or not os.path.exists(image_path):
        return {"detected": False, "confidence": 0.0, "details": "No image"}
    
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for faster processing
        img = img.resize((400, 300))
        
        # Get image statistics
        stats = ImageStat.Stat(img)
        
        # Solar panel characteristics:
        # - Blue/dark blue color (low red, medium-high blue)
        # - Often creates grid patterns
        # - Higher contrast in certain areas
        
        r, g, b = stats.mean
        
        # Color-based detection
        # Solar panels: higher blue relative to red
        blue_ratio = b / r if r > 0 else 0
        darkness = (r + g + b) / 3  # 0-255 scale
        
        # Calculate variance (grid patterns have higher variance)
        variance = stats.stddev[0]
        
        # Decision logic - require higher confidence
        detected = False
        confidence = 0.0
        details = ""
        
        # Heuristics for solar detection - stricter criteria
        # Must have BOTH blue color AND high variance to detect solar
        if blue_ratio > 1.15 and darkness < 100 and variance > 55:
            # Blue-ish and dark - possible solar
            confidence = 0.5
            detected = True
            details = f"Blue-ish tone detected (ratio: {blue_ratio:.2f})"
        elif variance > 50:
            # High variance might indicate panels
            confidence = 0.4
            detected = True
            details = f"High variance pattern detected ({variance:.1f})"
        else:
            confidence = 0.15
            details = f"No solar pattern (blue_ratio: {blue_ratio:.2f}, variance: {variance:.1f})"
        
        # Additional check: edge detection for rectangular shapes
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_stats = ImageStat.Stat(edges)
        edge_mean = edge_stats.mean[0]
        
        if edge_mean > 30:
            confidence = min(0.9, confidence + 0.2)
            details += f", edges: {edge_mean:.1f}"
        
        return {
            "detected": detected,
            "confidence": round(confidence, 2),
            "details": details,
            "blue_ratio": round(blue_ratio, 3),
            "mean_brightness": round(darkness, 1),
            "variance": round(variance, 1)
        }
        
    except Exception as e:
        return {
            "detected": False,
            "confidence": 0.0,
            "details": f"Error: {str(e)}"
        }


async def analyze_company(company: dict) -> dict:
    """
    Full analysis for one company
    """
    name = company.get("name", "Unknown")
    validation = company.get("validation", {})
    
    if not validation.get("verified"):
        company["solar_analysis"] = {
            "detected": None,
            "confidence": 0.0,
            "details": "Address not validated"
        }
        return company
    
    image_url = validation.get("satellite_image_url", "")
    if not image_url:
        company["solar_analysis"] = {
            "detected": None,
            "confidence": 0.0,
            "details": "No satellite image"
        }
        return company
    
    print(f"\n🔬 Analyzing: {name[:40]}")
    print(f"   Downloading satellite image...")
    
    # Download image
    local_path = download_satellite_image(image_url, name)
    
    if not local_path or not os.path.exists(local_path):
        company["solar_analysis"] = {
            "detected": None,
            "confidence": 0.0,
            "details": "Image download failed"
        }
        return company
    
    company["solar_analysis_image"] = local_path
    
    # Run detection
    print(f"   Running CV detection...")
    result = detect_solar_pil(local_path)
    
    company["solar_analysis"] = {
        "detected": result["detected"],
        "confidence": result["confidence"],
        "details": result["details"]
    }
    
    status = "☀️ HAS SOLAR" if result["detected"] else "❌ NO SOLAR"
    print(f"   {status} (confidence: {result['confidence']:.0%})")
    print(f"   Details: {result['details']}")
    
    return company


async def run_detection(companies: list) -> list:
    """
    Run solar detection on all validated companies
    """
    print("\n" + "="*60)
    print("PHASE 3: SOLAR PANEL DETECTION")
    print("="*60)
    
    analyzed = []
    
    for company in companies:
        if not company.get("validation", {}).get("verified"):
            analyzed.append(company)
            continue
        
        result = await analyze_company(company)
        analyzed.append(result)
    
    output_file = "/home/drg/.openclaw/workspace/solar-scout/data/companies_detected.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)
    
    solar_count = len([c for c in analyzed if c.get("solar_analysis", {}).get("detected") == True])
    no_solar_count = len([c for c in analyzed if c.get("solar_analysis", {}).get("detected") == False])
    
    print(f"\n💾 Analyzed {len(analyzed)} companies")
    print(f"   ☀️ Has solar: {solar_count}")
    print(f"   ❌ No solar: {no_solar_count}")
    
    return analyzed


if __name__ == "__main__":
    import asyncio
    
    test_img = "/home/drg/.openclaw/workspace/solar-scout/output/images/test.jpg"
    if os.path.exists(test_img):
        result = detect_solar_pil(test_img)
        print(json.dumps(result, indent=2))
