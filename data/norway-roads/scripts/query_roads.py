#!/usr/bin/env python3
"""
Norway Roads - Real-time road closures and conditions
Uses NVDB API to fetch Vegstengning (485) and Vegsperring (607) objects
"""

import sys
import json
import urllib.request
from datetime import datetime

# City to county mapping for filtering
CITY_COUNTIES = {
    'oslo': ['Oslo', 'Viken'],
    'bergen': ['Vestland'],
    'stavanger': ['Rogaland'],
    'trondheim': ['Trøndelag'],
    'tromsø': ['Troms og Finnmark'],
    'tromso': ['Troms og Finnmark'],
    'kristiansand': ['Agder'],
    'ålesund': ['Møre og Romsdal'],
    'alesund': ['Møre og Romsdal'],
    'bodø': ['Nordland'],
    'bodo': ['Nordland'],
}

# County to region mapping for major routes
ROUTE_COUNTIES = {
    ('oslo', 'bergen'): ['Viken', 'Vestland'],
    ('oslo', 'trondheim'): ['Viken', 'Innlandet', 'Trøndelag'],
    ('bergen', 'stavanger'): ['Vestland', 'Rogaland'],
    ('oslo', 'stavanger'): ['Viken', 'Rogaland'],
}

def fetch_closures():
    """Fetch road closures (Vegstengning, type 485)"""
    url = "https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/485?inkluder=lokasjon,egenskaper&antall=100"
    
    req = urllib.request.Request(
        url,
        headers={
            'Accept': 'application/vnd.vegvesen.nvdb-v3-rev1+json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def fetch_barriers():
    """Fetch road barriers (Vegsperring, type 607)"""
    url = "https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/607?inkluder=lokasjon,egenskaper&antall=50"
    
    req = urllib.request.Request(
        url,
        headers={
            'Accept': 'application/vnd.vegvesen.nvdb-v3-rev1+json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def parse_closure(obj):
    """Parse a closure object into readable format"""
    props = {p['navn']: p.get('verdi') for p in obj.get('egenskaper', [])}
    lokasjon = obj.get('lokasjon', {})
    
    # Get county/municipality
    fylker = lokasjon.get('fylker', [])
    kommuner = lokasjon.get('kommuner', [])
    
    result = {
        'type': 'closure',
        'id': obj.get('id'),
        'location': props.get('Stedsangivelse', 'Unknown location'),
        'road': None,
        'county': fylker[0] if fylker else None,
        'municipality': kommuner[0] if kommuner else None,
        'from_date': props.get('Stengt fra dato'),
        'from_time': props.get('Stengt fra klokkeslett'),
        'to_date': props.get('Stengt til dato'),
        'to_time': props.get('Stengt til klokkeslett'),
        'cause': props.get('Skredtype'),  # Snow, rock, etc.
        'description': None
    }
    
    # Build description
    desc = result['location']
    if result['cause']:
        desc += f" ({result['cause']})"
    if result['from_date']:
        desc += f" - Closed from {result['from_date']}"
        if result['to_date']:
            desc += f" to {result['to_date']}"
    
    result['description'] = desc
    return result

def parse_barrier(obj):
    """Parse a barrier object into readable format"""
    props = {p['navn']: p.get('verdi') for p in obj.get('egenskaper', [])}
    lokasjon = obj.get('lokasjon', {})
    
    fylker = lokasjon.get('fylker', [])
    kommuner = lokasjon.get('kommuner', [])
    
    return {
        'type': 'barrier',
        'id': obj.get('id'),
        'road': None,
        'county': fylker[0] if fylker else None,
        'municipality': kommuner[0] if kommuner else None,
        'description': props.get('Beskrivelse', 'Physical road barrier')
    }

def get_road_conditions(from_city=None, to_city=None, road_filter=None):
    """Get road conditions with optional filtering"""
    try:
        closures_data = fetch_closures()
        barriers_data = fetch_barriers()
        
        closures = [parse_closure(obj) for obj in closures_data.get('objekter', [])]
        barriers = [parse_barrier(obj) for obj in barriers_data.get('objekter', [])]
        
        all_conditions = closures + barriers
        
        # Filter by route
        if from_city and to_city:
            from_lower = from_city.lower()
            to_lower = to_city.lower()
            
            # Get relevant counties
            route_key = tuple(sorted([from_lower, to_lower]))
            if route_key in ROUTE_COUNTIES:
                relevant = ROUTE_COUNTIES[route_key]
            else:
                relevant = []
                if from_lower in CITY_COUNTIES:
                    relevant.extend(CITY_COUNTIES[from_lower])
                if to_lower in CITY_COUNTIES:
                    relevant.extend(CITY_COUNTIES[to_lower])
            
            if relevant:
                all_conditions = [
                    c for c in all_conditions 
                    if c.get('county') in relevant or 
                       any(r.lower() in str(c.get('description', '')).lower() for r in relevant)
                ]
        
        # Filter by road
        if road_filter:
            all_conditions = [
                c for c in all_conditions 
                if road_filter.upper() in str(c.get('description', '')).upper()
            ]
        
        return {
            'success': True,
            'count': len(all_conditions),
            'closures': closures,
            'barriers': barriers,
            'filtered': all_conditions if (from_city or to_city or road_filter) else None,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def format_output(data, from_city=None, to_city=None, road_filter=None):
    """Format conditions for display"""
    
    if not data['success']:
        return f"❌ Error: {data['error']}"
    
    conditions = data.get('filtered') or (data['closures'] + data['barriers'])
    
    if not conditions:
        if from_city and to_city:
            return f"✅ No road closures reported between {from_city} and {to_city}."
        elif road_filter:
            return f"✅ No closures reported on {road_filter}."
        else:
            return "✅ No road closures or barriers currently reported in Norway."
    
    lines = []
    
    if from_city and to_city:
        lines.append(f"🚧 {len(conditions)} closure(s)/barrier(s) on route {from_city} → {to_city}\n")
    elif road_filter:
        lines.append(f"🚧 {len(conditions)} issue(s) matching '{road_filter}'\n")
    else:
        lines.append(f"🚧 Road conditions in Norway\n")
        lines.append(f"   • {len(data['closures'])} scheduled closures")
        lines.append(f"   • {len(data['barriers'])} physical barriers\n")
    
    # Show closures
    closures_to_show = [c for c in conditions if c['type'] == 'closure'][:8]
    if closures_to_show:
        lines.append("🔴 ROAD CLOSURES:")
        for c in closures_to_show:
            county = c.get('county', 'Unknown')
            lines.append(f"  • {c['description']} [{county}]")
        lines.append("")
    
    # Show barriers
    barriers_to_show = [c for c in conditions if c['type'] == 'barrier'][:3]
    if barriers_to_show:
        lines.append("⚠️  PHYSICAL BARRIERS:")
        for b in barriers_to_show:
            county = b.get('county', 'Unknown')
            lines.append(f"  • {b['description']} [{county}]")
    
    return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Query Norway road conditions')
    parser.add_argument('--road', '-R', help='Filter by road/location name')
    parser.add_argument('--from', '-f', dest='from_city', help='Starting city')
    parser.add_argument('--to', '-t', help='Destination city')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    data = get_road_conditions(args.from_city, args.to, args.road)
    
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_output(data, args.from_city, args.to, args.road))

if __name__ == '__main__':
    main()
