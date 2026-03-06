from api import get_calendar_by_city
from datetime import datetime

def handle_calendar_command(args):
    now = datetime.now()
    month = args.month or now.month
    year = args.year or now.year
    city = args.city
    country = args.country
    
    # If not provided, try to use config location name if it's a city string
    if not city:
        from api import load_config
        config = load_config()
        # Fallback logic: Assume config name is "City, Country" or just "City"
        loc_name = config['location'].get('name', 'Jakarta')
        parts = loc_name.split(',')
        city = parts[0].strip()
        country = parts[1].strip() if len(parts) > 1 else "Indonesia"

    data = get_calendar_by_city(city, country, month, year)
    
    if not data or 'data' not in data:
        print(f"Could not retrieve calendar for {city}, {country}.")
        return

    print(f"\nPrayer Calendar for {month}/{year} - {city}, {country}\n")
    print(f"{'Date':<12} {'Fajr':<8} {'Dhuhr':<8} {'Asr':<8} {'Maghrib':<8} {'Isha':<8}")
    print("-" * 60)
    
    for day in data['data']:
        date_readable = day['date']['gregorian']['date']
        timings = day['timings']
        
        # Clean up time strings (remove timezone suffix if present)
        fajr = timings['Fajr'].split(' ')[0]
        dhuhr = timings['Dhuhr'].split(' ')[0]
        asr = timings['Asr'].split(' ')[0]
        maghrib = timings['Maghrib'].split(' ')[0]
        isha = timings['Isha'].split(' ')[0]
        
        print(f"{date_readable:<12} {fajr:<8} {dhuhr:<8} {asr:<8} {maghrib:<8} {isha:<8}")
