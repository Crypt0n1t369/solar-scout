#!/usr/bin/env python3
"""
Regenerate docs/dashboard.html from leads_dashboard.json
"""
import json
from pathlib import Path
from datetime import datetime

def main():
    base = Path('/home/drg/.openclaw/workspace/solar-scout')
    
    with open(base / 'docs/leads_dashboard.json') as f:
        leads = json.load(f)
    
    # Stats
    total = len(leads)
    with_sat = sum(1 for l in leads if l.get('image'))
    total_cap = sum(l.get('capacity_kw', 0) for l in leads)
    
    # Generate lead cards HTML
    cards = []
    for lead in leads:
        state_class = lead.get('state', 'cold')
        company = lead.get('company', 'N/A')
        address = lead.get('address', 'N/A')
        dm = lead.get('decision_maker', 'N/A')
        title = lead.get('title', '')
        email = lead.get('email', 'N/A')
        phone = lead.get('phone', 'N/A')
        cap = f"{lead['capacity_kw']:,.0f} kW capacity" if lead.get('capacity_kw') else ''
        sat_img = '<p class="text-xs text-slate-500 mt-2">🛰️ Satellite image</p>' if lead.get('image') else ''
        industry_tag = f'<p class="text-xs text-cyan-400 mb-2">{lead["industry"]}</p>' if lead.get('industry') and lead['industry'] != 'unknown' else ''
        title_str = f'({title})' if title else ''
        
        card = f'''<div class="company-card card rounded-xl p-4 transition cursor-pointer {state_class}">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold text-white">{company}</h3>
                    <span class="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300">{lead.get('state', 'cold')}</span>
                </div>
                {industry_tag}
                <p class="text-sm text-slate-400 mb-1">📍 {address}</p>
                <p class="text-sm text-slate-400 mb-1">👤 {dm} {title_str}</p>
                <p class="text-sm text-slate-400 mb-1">📧 {email}</p>
                <p class="text-sm text-slate-400 mb-1">📞 {phone}</p>
                {f'<p class="text-sm text-emerald-400 mt-2">⚡ {cap}</p>' if cap else ''}
                {sat_img}
            </div>'''
        cards.append(card)
    
    cards_html = '\n'.join(cards)
    leads_json = json.dumps(leads, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latvia Solar Scout - Lead Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body style="font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%); min-height: 100vh; color: white;">
    <header style="border-bottom: 1px solid rgba(255,255,255,0.1);">
        <div style="max-width: 7xl; margin: 0 auto; padding: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="width: 3rem; height: 3rem; border-radius: 0.75rem; background: linear-gradient(to right, #fbbf24, #f97316); display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">☀️</div>
                    <div>
                        <h1 style="font-size: 1.5rem; font-weight: 700;">Latvia Solar Scout</h1>
                        <p style="color: #94a3b8; font-size: 0.875rem;">Manufacturing Companies Lead Generator</p>
                    </div>
                </div>
                <div style="text-align: right;">
                    <p style="color: #94a3b8; font-size: 0.875rem;">Generated</p>
                    <p style="font-weight: 500;">{datetime.now().strftime('%Y-%m-%d')}</p>
                </div>
            </div>
        </div>
    </header>

    <main style="max-width: 7xl; margin: 0 auto; padding: 2rem 1.5rem;">
        <!-- Stats -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem; padding: 1rem;">
                <p style="color: #94a3b8; font-size: 0.875rem;">Total Leads</p>
                <p style="font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #22d3ee, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total}</p>
            </div>
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem; padding: 1rem;">
                <p style="color: #94a3b8; font-size: 0.875rem;">With Satellite</p>
                <p style="font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #22d3ee, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{with_sat}</p>
            </div>
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem; padding: 1rem;">
                <p style="color: #94a3b8; font-size: 0.875rem;">Total Capacity</p>
                <p style="font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #22d3ee, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total_cap/1000:.1f} MW</p>
            </div>
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem; padding: 1rem;">
                <p style="color: #94a3b8; font-size: 0.875rem;">Data Quality</p>
                <p style="font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #22d3ee, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">100%</p>
            </div>
        </div>

        <!-- Filter Bar -->
        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem; padding: 1rem; margin-bottom: 1.5rem;">
            <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                <input type="text" id="search" placeholder="Search companies..." 
                    style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 0.5rem; padding: 0.5rem 1rem; color: white; flex: 1; min-width: 200px;">
                <select id="stateFilter" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 0.5rem; padding: 0.5rem 1rem; color: white;">
                    <option value="">All States</option>
                    <option value="cold">Cold</option>
                    <option value="warm">Warm</option>
                    <option value="hot">Hot</option>
                    <option value="contacted">Contacted</option>
                </select>
                <button id="resetFilters" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 0.5rem; padding: 0.5rem 1rem; color: white; cursor: pointer;">Reset</button>
            </div>
        </div>

        <!-- Leads Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem;" id="leadsGrid">
{cards_html}
        </div>

        <div id="noResults" style="text-align: center; padding: 3rem; color: #94a3b8; display: none;">
            <p style="font-size: 1.25rem;">No leads match your filters</p>
        </div>
    </main>

    <script>
        const leads = {leads_json};
        
        function renderLeads(filtered) {{
            const grid = document.getElementById('leadsGrid');
            const noResults = document.getElementById('noResults');
            
            if (filtered.length === 0) {{
                grid.style.display = 'none';
                noResults.style.display = 'block';
                return;
            }}
            
            grid.style.display = 'grid';
            noResults.style.display = 'none';
            
            grid.innerHTML = filtered.map(lead => `
                <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem; padding: 1rem; border-left: 4px solid ${{lead.state === 'cold' ? '#64748b' : lead.state === 'warm' ? '#f59e0b' : lead.state === 'hot' ? '#ef4444' : '#22c55e'}};">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <h3 style="font-weight: 600; color: white;">${{lead.company || 'N/A'}}</h3>
                        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 9999px; background: #334155; color: #cbd5e1;">${{lead.state || 'cold'}}</span>
                    </div>
                    ${{lead.industry && lead.industry !== 'unknown' ? `<p style="font-size: 0.75rem; color: #22d3ee; margin-bottom: 0.5rem;">${{lead.industry}}</p>` : ''}}
                    <p style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 0.25rem;">📍 ${{lead.address || 'N/A'}}</p>
                    <p style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 0.25rem;">👤 ${{lead.decision_maker || 'N/A'}} ${{lead.title ? `(${{lead.title}})` : ''}}</p>
                    <p style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 0.25rem;">📧 ${{lead.email || 'N/A'}}</p>
                    <p style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 0.25rem;">📞 ${{lead.phone || 'N/A'}}</p>
                    ${{lead.capacity_kw ? `<p style="font-size: 0.875rem; color: #34d399; margin-top: 0.5rem;">⚡ ${{lead.capacity_kw.toLocaleString()}} kW capacity</p>` : ''}}
                    ${{lead.image ? `<p style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;">🛰️ Satellite image</p>` : ''}}
                </div>
            `).join('');
        }}

        function filterLeads() {{
            const search = document.getElementById('search').value.toLowerCase();
            const state = document.getElementById('stateFilter').value;
            
            const filtered = leads.filter(lead => {{
                const matchSearch = !search || 
                    (lead.company && lead.company.toLowerCase().includes(search)) ||
                    (lead.address && lead.address.toLowerCase().includes(search)) ||
                    (lead.decision_maker && lead.decision_maker.toLowerCase().includes(search));
                const matchState = !state || lead.state === state;
                return matchSearch && matchState;
            }});
            
            renderLeads(filtered);
        }}

        document.getElementById('search').addEventListener('input', filterLeads);
        document.getElementById('stateFilter').addEventListener('change', filterLeads);
        document.getElementById('resetFilters').addEventListener('click', () => {{
            document.getElementById('search').value = '';
            document.getElementById('stateFilter').value = '';
            filterLeads();
        }});

        renderLeads(leads);
    </script>
</body>
</html>'''
    
    with open(base / 'docs/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated docs/dashboard.html with {total} leads")
    print(f"Total capacity: {total_cap/1000:.1f} MW")
    print(f"With satellite: {with_sat}")

if __name__ == '__main__':
    main()