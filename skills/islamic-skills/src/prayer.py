from api import get_prayer_times

def handle_prayer_command(args):
    data = get_prayer_times()
    if not data or 'data' not in data:
        print("Could not retrieve prayer times.")
        return

    timings = data['data']['timings']
    date_readable = data['data']['date']['readable']
    
    print(f"Prayer Times for {date_readable}:")
    print(f"Fajr:    {timings['Fajr']}")
    print(f"Dhuhr:   {timings['Dhuhr']}")
    print(f"Asr:     {timings['Asr']}")
    print(f"Maghrib: {timings['Maghrib']}")
    print(f"Isha:    {timings['Isha']}")
