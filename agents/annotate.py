"""
Phase 6: Image Annotation
Annotates satellite images with pinpoints at company locations
Uses PIL for image manipulation
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/home/drg/.openclaw/workspace/solar-scout/output/images"


def annotate_satellite_image(company: dict) -> str:
    """
    Create annotated image with pinpoint for company location
    """
    name = company.get("name", "Unknown")
    image_path = company.get("solar_analysis_image")
    
    if not image_path or not os.path.exists(image_path):
        print(f"   ❌ No image to annotate for {name}")
        return None
    
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
    safe_name = safe_name.replace(' ', '_')
    annotated_path = os.path.join(OUTPUT_DIR, f"{safe_name}_annotated.jpg")
    
    try:
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        draw = ImageDraw.Draw(img)
        
        center_x = width // 2
        center_y = height // 2
        
        # Draw pin marker (red)
        # Outer circle
        draw.ellipse([center_x-20, center_y-20, center_x+20, center_y+20], fill=(255, 0, 0))
        # Inner circle
        draw.ellipse([center_x-12, center_y-12, center_x+12, center_y+12], fill=(255, 255, 255))
        # Center dot
        draw.ellipse([center_x-5, center_y-5, center_x+5, center_y+5], fill=(255, 0, 0))
        
        # Crosshairs
        draw.line([center_x-30, center_y, center_x-10, center_y], fill=(255, 0, 0), width=2)
        draw.line([center_x+10, center_y, center_x+30, center_y], fill=(255, 0, 0), width=2)
        draw.line([center_x, center_y-30, center_x, center_y-10], fill=(255, 0, 0), width=2)
        draw.line([center_x, center_y+10, center_x, center_y+30], fill=(255, 0, 0), width=2)
        
        # Company name label
        text = name[:25] + "..." if len(name) > 25 else name
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Draw text background
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        draw.rectangle([10, height - text_height - 25, text_width + 20, height - 10], fill=(0, 0, 150))
        draw.text((15, height - text_height - 20), text, fill=(255, 255, 255), font=font)
        
        # Solar status badge
        solar = company.get("solar_analysis", {})
        detected = solar.get("detected")
        
        if detected == False:
            badge_text = "OPPORTUNITY"
            badge_color = (0, 180, 0)
        elif detected == True:
            badge_text = "HAS SOLAR"
            badge_color = (200, 0, 0)
        else:
            badge_text = "UNKNOWN"
            badge_color = (200, 200, 0)
        
        # Badge
        badge_w = len(badge_text) * 9 + 10
        draw.rectangle([width - badge_w - 10, 10, width - 10, 35], fill=badge_color)
        draw.text((width - badge_w, 15), badge_text, fill=(255, 255, 255), font=font)
        
        # Capacity info
        capacity = company.get("capacity", {})
        if capacity.get("estimated_kw", 0) > 0:
            kw_text = f"{capacity['estimated_kw']:.1f} kW"
            draw.text((width - badge_w - 80, 40), kw_text, fill=(0, 200, 0), font=font)
        
        # Save
        img.save(annotated_path, "JPEG", quality=90)
        
        print(f"   ✅ Annotated: {os.path.basename(annotated_path)}")
        return annotated_path
        
    except Exception as e:
        print(f"   ❌ Annotation error: {e}")
        return None


def run_annotation(companies: list) -> list:
    print("\n" + "="*60)
    print("PHASE 6: IMAGE ANNOTATION")
    print("="*60)
    
    annotated = []
    
    for company in companies:
        name = company.get("name", "Unknown")
        print(f"\n🖼️ Annotating: {name[:40]}")
        
        annotated_path = annotate_satellite_image(company)
        
        if annotated_path:
            company["output_image"] = annotated_path
        else:
            company["output_image"] = None
        
        annotated.append(company)
    
    output_file = "/home/drg/.openclaw/workspace/solar-scout/data/companies_final.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(annotated, f, ensure_ascii=False, indent=2)
    
    with_image = len([c for c in annotated if c.get("output_image")])
    
    print(f"\n💾 Saved to {output_file}")
    print(f"   🖼️ Annotated: {with_image}")
    
    return annotated


def generate_summary(companies: list) -> list:
    print("\n" + "="*60)
    print("FINAL SUMMARY REPORT")
    print("="*60)
    
    targets = [
        c for c in companies 
        if c.get("solar_analysis", {}).get("detected") == False
        and c.get("decision_maker", {}).get("name")
    ]
    
    print(f"\n🎯 TARGET COMPANIES: {len(targets)}")
    
    total_kw = 0
    
    for i, c in enumerate(targets, 1):
        name = c.get("name", "Unknown")
        dm = c.get("decision_maker", {})
        capacity = c.get("capacity", {})
        
        print(f"\n{i}. {name}")
        print(f"   📍 {c.get('validation', {}).get('display_name', 'N/A')[:60]}")
        print(f"   👤 {dm.get('name', 'N/A')} - {dm.get('title', 'N/A')}")
        print(f"   📞 {dm.get('phone', 'N/A')}")
        print(f"   ✉️ {dm.get('email', 'N/A')}")
        print(f"   ⚡ {capacity.get('estimated_kw', 0):.1f} kW potential")
        
        total_kw += capacity.get("estimated_kw", 0)
    
    print(f"\n📊 TOTAL POTENTIAL: {total_kw:.1f} kW")
    
    return targets
