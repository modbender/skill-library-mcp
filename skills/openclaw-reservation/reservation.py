"""
Unified Restaurant Reservation Skill
Integrates Ontopo, Tabit, TheFork, OpenTable and Recommendations.
"""
from . import ontopo, tabit, thefork, opentable, recommender
import json

def search_restaurants(city: str, query: str = None, date: str = None, 
                       time: str = None, size: int = 2) -> dict:
    """
    Search for restaurants and check availability where possible.
    Returns: { recommendations: [], search_results: [] }
    """
    results = {
        "city": city,
        "query": query,
        "recommendations": [],
        "search_results": []
    }
    
    # 1. Get Recommendations (Michelin, Time Out, etc.)
    results["recommendations"] = recommender.search_recommendations(city)
    
    # 2. Search for the specific query if provided
    if query:
        # Israel search
        if city.lower() in ["tel aviv", "tel-aviv", "israel", "hertzliya", "jerusalem"]:
            # Check Ontopo
            ontopo_venues = ontopo.search_venue(query)
            for v in ontopo_venues:
                slug = ontopo.get_post_slug(v.get("url_slug"))
                results["search_results"].append({
                    "name": v.get("title"),
                    "platform": "Ontopo",
                    "post_slug": slug,
                    "url_slug": v.get("url_slug"),
                    "address": v.get("address"),
                    "can_check_api": True
                })
            
            # Check Tabit
            tabit_venues = tabit.search_venue(query)
            for v in tabit_venues:
                results["search_results"].append({
                    "name": v.get("name"),
                    "platform": "Tabit",
                    "id": v.get("_id"),
                    "address": v.get("address"),
                    "can_check_api": v.get("reservation_method") == "onlineBooking"
                })
        
        # Abroad search
        else:
            # TheFork (Europe)
            fork_url = thefork.search_restaurant_url(query, city)
            results["search_results"].append({
                "name": query,
                "platform": "TheFork",
                "browser_url": fork_url,
                "can_check_api": False
            })
            
            # OpenTable/Resy (USA/World)
            ot_info = opentable.get_booking_url(query, date, time, size)
            results["search_results"].append({
                "name": query,
                "platform": ot_info.get("platform"),
                "browser_url": ot_info.get("url"),
                "can_check_api": False
            })
            
    return results

def check_availability_bulk(restaurants: list[dict], date: str, 
                            time: str, size: int) -> list[dict]:
    """
    Checks availability for multiple restaurants across different platforms.
    For browser-only platforms, returns the booking URL.
    """
    results = []
    for r in restaurants:
        try:
            name = r.get("name")
            platform = r.get("platform")
            
            if platform == "Ontopo" and r.get("post_slug"):
                avail = ontopo.check_availability(r["post_slug"], date, time, size)
                r["availability"] = avail
                r["display_text"] = ontopo.format_availability(avail, name, date, time)
            
            elif platform == "Tabit" and r.get("id") and r.get("can_check_api"):
                # Use Tabit temp-reservation check
                # Note: This creates a 10-15min hold!
                avail = tabit.check_availability(r["id"], date, time, size)
                r["availability"] = avail
                if avail["available"]:
                    r["display_text"] = f"✅ {name} — table held for {date} {time} (area: {avail['area']}). Confirm to book."
                else:
                    r["display_text"] = f"❌ {name} — no availability ({avail['description_string']})."
            
            elif platform in ["TheFork", "OpenTable", "Resy"]:
                # Just return the URL
                r["available"] = "Maybe (check browser)"
                r["display_text"] = f"🔗 {name} ({platform}): Book at {r.get('browser_url')}"
            
            results.append(r)
        except:
            continue
            
    return results

def format_recommendation_report(results: dict) -> str:
    """Format the results into a readable report for the user."""
    lines = [f"🍽️ Restaurant Recommendations for {results['city']}:"]
    
    # Separate by source
    by_source = {}
    for r in results["recommendations"]:
        src = r["source"]
        if src not in by_source: by_source[src] = []
        by_source[src].append(r)
        
    for src, recs in by_source.items():
        lines.append(f"\n✨ From {src}:")
        for r in recs[:5]:
            award = f" ({r.get('award')})" if r.get("award") else ""
            lines.append(f"  • {r['name']}{award} — {r.get('cuisine', '')}")
            if r.get("booking_url"):
                lines.append(f"    🔗 {r['booking_url']}")
                
    return "\n".join(lines)
