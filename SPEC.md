# Solar Lead Magnet Agent - Specification Sheet

## Project Overview
- **Name:** Latvia Solar Scout
- **Purpose:** Find manufacturing companies in Latvia without solar, validate via satellite imagery, and enrich with decision-maker contacts
- **Target:** 10 verified companies with decision makers

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LATVIA SOLAR SCOUT                          │
├─────────────────────────────────────────────────────────────────┤
│  1. DISCOVERY          2. VALIDATION        3. ENRICHMENT     │
│  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐   │
│  │ Web Scraper │──────▶│ Sat Imagery │─────▶│ CV Detector │   │
│  │ (Company    │       │ (Address    │      │ (Solar      │   │
│  │  List)      │       │  Verify)    │      │  Present?)  │   │
│  └─────────────┘       └─────────────┘      └──────┬──────┘   │
│                                                    │           │
│                      ┌─────────────┐              │           │
│                      │ Capacity    │◀─────────────┘           │
│                      │ Calculator  │                            │
│                      └──────┬──────┘                            │
│                             │                                   │
│                      ┌──────▼──────┐                            │
│                      │ Decision    │                            │
│                      │ Maker       │                            │
│                      │ Enrichment  │                            │
│                      └──────┬──────┘                            │
│                             │                                   │
│                      ┌──────▼──────┐                            │
│                      │ Image       │                            │
│                      │ Annotator   │                            │
│                      └─────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Specs

### 1. Company Discovery Module
- **Input:** Search queries for "manufacturing company Latvia", "factory Latvia", "industrial facility Latvia"
- **Sources:** 
  - Google Maps Places API (or scraping)
  - business directories (e.g., lvportals.lv, company registers)
  - Yellow pages Latvia
- **Output:** List of companies with name, address, website

### 2. Address Validation (Satellite Imagery)
- **Tool:** Google Static Maps API (satellite mode) or Microsoft Bing Maps
- **Validation:**
  - Fetch satellite image centered on address
  - Verify building/factory visible
  - Store timestamp from image metadata ( freshness indicator)
- **Output:** Confirmed address with satellite proof

### 3. Solar Detection (Computer Vision)
- **Model:** YOLOv8 with custom solar panel training OR
- **Alternative:** OpenCV color detection (blue rectangular patterns)
- **Detection:** Binary - solar present / not present
- **Confidence threshold:** 70%
- **Output:** Detection result + confidence score

### 4. Capacity Calculator
- **Formula:** `max_panels = (roof_area_m2 + available_land_m2) / 2`
- **Assumptions:**
  - Average roof coverage: 60% of building footprint
  - Land available: 2x building footprint (parking, unused space)
  - Panel size: 2m² each
- **Output:** Max kW installable (assume 350W per panel)

### 5. Decision Maker Enrichment
- **Sources:**
  - Company website (about/team pages)
  - LinkedIn (via browser automation)
  - Company register ( Lursoft.lv - Latvia business register)
  - Hunter.io / Apollo for email finding
- **Target:** CEO, Operations Director, Facilities Manager, Owner
- **Output:** Name, title, phone, email

### 6. Image Annotation
- **Tool:** Python PIL or OpenCV
- **Action:** Draw red pin circle at detected address coordinates
- **Output:** Annotated satellite image saved to `output/images/`

---

## Data Schema

```json
{
  "company": {
    "name": "string",
    "address": "string",
    "website": "string",
    "source_url": "string"
  },
  "validation": {
    "satellite_image_url": "string",
    "image_date": "string",
    "verified": boolean
  },
  "solar_analysis": {
    "detected": boolean,
    "confidence": "float",
    "panel_count_estimate": "integer"
  },
  "capacity": {
    "max_panels": "integer",
    "estimated_kw": "float"
  },
  "decision_maker": {
    "name": "string",
    "title": "string",
    "phone": "string",
    "email": "string",
    "source": "string"
  },
  "output_image": "string (path)"
}
```

---

## File Structure

```
/home/drg/.openclaw/workspace/solar-scout/
├── SPEC.md                          # This file
├── config.py                        # API keys, settings
├── main.py                          # Orchestrator
├── agents/
│   ├── discover.py                  # Company discovery
│   ├── validate.py                  # Satellite validation
│   ├── detector.py                  # Solar CV detection
│   ├── capacity.py                  # Calculator
│   ├── enrich.py                    # Decision maker finder
│   └── annotate.py                  # Image annotation
├── data/
│   ├── companies_raw.json           # Initial company list
│   ├── companies_validated.json    # After satellite check
│   └── companies_final.json        # Complete results (10)
├── output/
│   └── images/                      # Annotated satellite images
└── logs/
    └── scout.log                    # Execution logs
```

---

## Workarounds & Alternatives

| Challenge | Primary Solution | Workaround 1 | Workaround 2 |
|-----------|-----------------|--------------|--------------|
| No Google Maps API key | web scraping via browser | Public company registers | Manual search |
| Satellite imagery cost | Bing Maps (free tier) | Sentinel Hub (free) | MapQuest |
| CV model accuracy | YOLOv8 fine-tuned | Color-based detection | Manual image review |
| No LinkedIn access | Browser automation | Company website parsing | Lursoft.lv register |
| Email finding fails | Hunter.io | Google search "site:linkedin.com" | Phone verification |

---

## Success Criteria

1. ✅ 10 companies discovered in Latvia with factories
2. ✅ Each company has satellite image proving address
3. ✅ Solar detection run on each image
4. ✅ Capacity calculated for solar-negative companies
5. ✅ At least 1 decision maker per company (phone or email)
6. ✅ Annotated image saved for each company

---

## API Requirements (User to Provide)

1. **Google Maps Static API** (or use free alternatives)
2. **LinkedIn** (via browser - user session)
3. Optional: Hunter.io API for email finding

---

## Execution Plan

1. **Phase 1:** Discovery - Find 20+ candidate companies
2. **Phase 2:** Validation - Verify addresses via satellite
3. **Phase 3:** Detection - Run CV on each satellite image
4. **Phase 4:** Enrichment - Find decision makers for solar-negative
5. **Phase 5:** Output - Generate final list of 10 verified leads

---

*Spec created: 2026-02-28*
*Owner: drg (visionary)*
*Builder: Aton (lobster-energy execution)*
