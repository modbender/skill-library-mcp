from api import get_fasting_times

def handle_fasting_command(args):
    data = get_fasting_times()
    if not data or 'data' not in data:
        print("Could not retrieve fasting times.")
        return

    # Assuming similar structure to prayer times or specific fasting endpoint structure
    # Adjust based on actual API response structure for /v1/fasting
    # For now, relying on standard timings usually found in prayer response or specific fasting response
    
    # NOTE: If /v1/fasting returns same structure as prayer, use that. 
    # If not, adapt. Let's assume standard response.
    timings = data['data']['timings']
    date_readable = data['data']['date']['readable']

    print(f"Fasting Schedule for {date_readable}:")
    print(f"Imsak (Stop Eating): {timings['Imsak']}")
    print(f"Maghrib (Break Fast): {timings['Maghrib']}")
