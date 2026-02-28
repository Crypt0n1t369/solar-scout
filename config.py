# Configuration for Latvia Solar Scout
# Fill in your API keys here

import os

# API Keys (set via environment or fill manually)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
BING_MAPS_KEY = os.getenv("BING_MAPS_KEY", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
LINKEDIN_COOKIE = os.getenv("LINKEDIN_COOKIE", "")  # For browser automation

# Settings
TARGET_COUNT = 10
PANEL_SIZE_M2 = 2.0
PANEL_WATTAGE = 350
ROOF_COVERAGE_RATIO = 0.6
LAND_MULTIPLIER = 2.0
DETECTION_CONFIDENCE = 0.7

# Paths
DATA_DIR = "/home/drg/.openclaw/workspace/solar-scout/data"
OUTPUT_DIR = "/home/drg/.openclaw/workspace/solar-scout/output/images"
LOG_DIR = "/home/drg/.openclaw/workspace/solar-scout/logs"

# Latvian business registers
COMPANY_REGISTERS = [
    "https://www.lursoft.lv/",
    "https://www.lvportals.lv/",
]

# Search queries for discovery
DISCOVERY_QUERIES = [
    "manufacturing company Latvia factory",
    "industrial factory Latvia manufacturing",
    "metalworking company Latvia",
    "woodworking factory Latvia",
    "food processing plant Latvia",
    "warehouse industrial building Latvia",
]
