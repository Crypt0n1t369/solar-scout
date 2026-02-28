"""
Phase 4: Solar Capacity Calculator - Improved
Uses actual building detection from satellite images
"""

import json
import os
from PIL import Image, ImageFilter

PANEL_SIZE_M2 = 2.0
PANEL_WATTAGE = 350
ROOF_COVERAGE_RATIO = 0.5  # More realistic
LAND_MULTIPLIER = 1.5


def detect_building_area(image_path: str) -> dict:
    """
    Detect actual building footprint from satellite image
    Uses edge detection and color segmentation
    """
    if not image_path or not os.path.exists(image_path):
        return {"roof_m2": 0, "land_m2": 0, "total_m2": 0}
    
    try:
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for faster processing
        img = img.resize((300, 300))
        
        # Method: Detect building-like areas (gray/concrete surfaces)
        # Convert to grayscale
        gray = img.convert('L')
        
        # Get histogram
        hist = gray.histogram()
        
        # Buildings tend to be mid-gray (around 100-180)
        building_pixels = sum(hist[80:180])
        total_pixels = sum(hist)
        
        if total_pixels == 0:
            return {"roof_m2": 0, "land_m2": 0, "total_m2": 0}
        
        building_ratio = building_pixels / total_pixels
        
        # Also try edge detection for structure detection
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_pixels = sum(1 for p in edges.getdata() if p > 30)
        edge_ratio = edge_pixels / total_pixels
        
        # Calculate real area based on detected building coverage
        # At zoom 16: ~0.5m per pixel, so 300x300 pixels = 150x150m = 22,500 m2 total area
        total_image_m2 = 22500  # meters squared for 300x300 at zoom 16
        
        # Building footprint (conservative estimate)
        roof_m2 = total_image_m2 * building_ratio * ROOF_COVERAGE_RATIO
        
        # Available land (parking, unused space)
        land_m2 = total_image_m2 * 0.3  # Assume 30% is usable land
        
        # Cap at reasonable values
        roof_m2 = min(roof_m2, 15000)  # Max 15000 m2 roof
        land_m2 = min(land_m2, 10000)  # Max 10000 m2 land
        
        return {
            "roof_m2": round(roof_m2, 2),
            "land_m2": round(land_m2, 2),
            "total_m2": round(roof_m2 + land_m2, 2),
            "building_ratio": round(building_ratio, 3),
            "edge_ratio": round(edge_ratio, 3),
            "method": "building_detection"
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"roof_m2": 0, "land_m2": 0, "total_m2": 0}


def calculate_max_panels(area_m2: float) -> int:
    return int(area_m2 / PANEL_SIZE_M2)


def calculate_max_kw(panel_count: int) -> float:
    return (panel_count * PANEL_WATTAGE) / 1000


def calculate_installation_cost(panel_count: int, cost_per_watt: float = 0.70) -> float:
    kw = calculate_max_kw(panel_count)
    return kw * 1000 * cost_per_watt


def calculate_annual_revenue(panel_count: int) -> dict:
    kw = calculate_max_kw(panel_count)
    kwh_per_kwp = 1000
    annual_kwh = kw * kwh_per_kwp
    price_per_kwh = 0.15
    annual_revenue = annual_kwh * price_per_kwh
    
    return {
        "annual_kwh": round(annual_kwh),
        "annual_revenue_eur": round(annual_revenue, 2),
        "payback_years": round(calculate_installation_cost(panel_count) / annual_revenue, 1) if annual_revenue > 0 else 0
    }


def analyze_company(company: dict) -> dict:
    name = company.get("name", "Unknown")
    solar = company.get("solar_analysis", {})
    
    print(f"\n📐 Calculating capacity for: {name[:40]}")
    
    if solar.get("detected") == True:
        company["capacity"] = {
            "max_panels": 0,
            "estimated_kw": 0,
            "reason": "Solar panels already present"
        }
        print(f"   ⏭️ Skipping - solar already installed")
        return company
    
    image_path = company.get("solar_analysis_image")
    if not image_path or not os.path.exists(image_path):
        company["capacity"] = {
            "max_panels": 0,
            "estimated_kw": 0,
            "reason": "No satellite image"
        }
        return company
    
    # Use improved building detection
    area = detect_building_area(image_path)
    
    print(f"   Building: {area['building_ratio']:.1%} coverage")
    print(f"   Roof: {area['roof_m2']:.0f} m², Land: {area['land_m2']:.0f} m²")
    
    max_panels = calculate_max_panels(area["total_m2"])
    max_kw = calculate_max_kw(max_panels)
    cost = calculate_installation_cost(max_panels)
    revenue = calculate_annual_revenue(max_panels)
    
    company["capacity"] = {
        "max_panels": max_panels,
        "estimated_kw": round(max_kw, 2),
        "roof_m2": area["roof_m2"],
        "land_m2": area["land_m2"],
        "installable_m2": area["total_m2"],
        "building_ratio": area["building_ratio"],
        "estimated_cost_eur": round(cost, 2),
        "annual_revenue_eur": revenue["annual_revenue_eur"],
        "payback_years": revenue["payback_years"]
    }
    
    print(f"   📊 {max_panels} panels = {max_kw:.1f} kW | €{cost:,.0f}")
    
    return company


def run_capacity_analysis(companies: list) -> list:
    print("\n" + "="*60)
    print("PHASE 4: CAPACITY CALCULATION (Improved)")
    print("="*60)
    
    analyzed = []
    
    for company in companies:
        result = analyze_company(company)
        analyzed.append(result)
    
    output_file = "/home/drg/.openclaw/workspace/solar-scout/data/companies_capacity.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)
    
    with_solar = len([c for c in analyzed if c.get("solar_analysis", {}).get("detected") == True])
    without_solar = len([c for c in analyzed if c.get("solar_analysis", {}).get("detected") == False])
    potential_kw = sum(c.get("capacity", {}).get("estimated_kw", 0) for c in analyzed)
    
    print(f"\n💾 Potential: {potential_kw:.1f} kW across {without_solar} companies")
    
    return analyzed
