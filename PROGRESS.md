# SOLAR SCOUT - LATVIA LEAD GENERATION
## Status: 🔄 In Progress

### Goal
Generate 50+ additional verified leads for solar installation companies in Latvia (SMEs with self-owned premises, high energy consumption)

### Current Leads
- **Existing:** 20 verified companies in `data/real_leads.json`
- **Need:** 50+ more

### Approach
Using Selenium + Firefox for browser automation to bypass search engine blocks.

### Files
- `main.py` - Main pipeline (discover → enrich → validate)
- `requirements.txt` - Dependencies
- `data/` - Output directory

### Recent Progress
1. ✅ Firefox automation working (found 107 links in test)
2. ⚠️ main.py hangs on execution - needs debugging
3. 🔄 Switching to simpler approach: direct HTTP scraping

### Test Results
- Firefox: 107 links found on DuckDuckGo
- Selenium works but main.py has blocking issue

### Next Steps
1. Debug main.py execution hang
2. Run full discovery pipeline
3. Extract company data
4. Validate and save leads
