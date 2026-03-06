#!/usr/bin/env python3
"""Islamic Daily Reflection Generator with Real Hijri Date"""

from datetime import datetime
import urllib.request
import json

# Regular reflections (5 examples - add 25 more later)
REGULAR_REFLECTIONS = [
    {
        "title": "🤲 Patience in Small Trials",
        "content": "When your coffee spills or traffic jams, notice your reaction. These tiny frustrations test your sabr more than big calamities because they happen daily. True patience isn't gritting teeth - it's accepting Allah's decree with a calm heart.",
        "action": "Next time something irritates you, pause and say 'Alhamdulillah 'ala kulli hal' (Praise Allah in all situations) before reacting.",
        "duration": 3,
        "reference": "\"And be patient, for Allah does not allow the reward of the good-doers to be lost.\" (Quran 11:115)"
    },
    {
        "title": "🙏 Gratitude Transforms Everything",
        "content": "You woke up today. Your heart is beating. You can read this. These aren't small things - they're miracles you've normalized. Gratitude isn't just saying Alhamdulillah; it's feeling it deeply and letting it change how you see your life.",
        "action": "Before sleeping tonight, write down 3 blessings you usually overlook (hot water, a roof, someone who loves you).",
        "duration": 5,
        "reference": "\"If you are grateful, I will surely increase you.\" (Quran 14:7)"
    },
    {
        "title": "💪 Trust When You Can't See",
        "content": "Tawakkul doesn't mean sitting idle. It means planning, working hard, then releasing the outcome to Allah. You can't control results, but you can control your effort and your trust. Do your best, then rest in Allah's wisdom.",
        "action": "Identify one worry you're carrying. Make dua about it, then consciously choose to stop obsessing. Trust Allah with it.",
        "duration": 5,
        "reference": "\"And whoever relies upon Allah - then He is sufficient for him.\" (Quran 65:3)"
    },
    {
        "title": "👁️ Live Like Allah is Watching",
        "content": "Taqwa isn't fear - it's awareness. It's remembering Allah sees you when no one else does. It's the voice that stops you from clicking that link, saying that word, taking that shortcut. Taqwa is your spiritual immune system.",
        "action": "Today, before every decision, pause and ask: 'Would I do this if I could see Allah watching me?'",
        "duration": 0,
        "reference": "\"Indeed, Allah is ever watchful over you.\" (Quran 4:1)"
    },
    {
        "title": "💎 Do It For Allah Alone",
        "content": "Ikhlas means your good deeds are for Allah, not Instagram. No one saw your charity? Good - that's when it counts most. The prayer you prayed alone in the dark? Worth more than 100 prayed for people to see. Sincerity is the currency of the Hereafter.",
        "action": "Do one good deed today that absolutely NO ONE will know about. Not even your spouse. Just you and Allah.",
        "duration": 10,
        "reference": "\"They were not commanded except to worship Allah, being sincere to Him.\" (Quran 98:5)"
    },
]

# Jummah reflections
JUMMAH_REFLECTIONS = [
    {
        "title": "📿 The Chosen Day",
        "content": "Friday isn't weekend - it's the day Allah chose above all others. Somewhere between Asr and Maghrib is an hour when every dua is accepted. Don't waste it scrolling. Turn off your phone and pour out your heart.",
        "action": "After Asr today, find quiet spot. Make dua for everyone you love by name. Ask Allah for everything you need.",
        "duration": 15,
        "reference": "\"On Friday there is an hour when Allah will give a Muslim whatever he asks for.\" (Bukhari)"
    },
]

# Ramadan reflections (add more days as needed)
RAMADAN_REFLECTIONS = {
    1: {
        "title": "🌙 The Arrival",
        "content": "Ramadan is here - gates of Paradise open, gates of Hell closed. This isn't about perfection; it's about direction. Don't try everything at once. Pick ONE spiritual habit and guard it for 30 days.",
        "action": "Write down your ONE Ramadan goal. Make it specific: 'Pray Fajr on time daily' or 'Read Quran 20 min/day'. Just one.",
        "duration": 10,
        "reference": "\"Ramadan is the month the Quran was revealed\" (Quran 2:185)"
    },
    15: {
        "title": "🌙 Halfway Point",
        "content": "Half the month is gone. Check your goal from Day 1. Struggling? Adjust your plan - it's not too late. Allah loves consistency over intensity. Small daily deeds done with sincerity outweigh one-time marathons.",
        "action": "Review your first 2 weeks. What's working? What needs adjustment? Recommit now.",
        "duration": 10,
        "reference": "\"The most beloved deed to Allah is the most regular, even if it is small.\" (Bukhari)"
    },
    21: {
        "title": "🌙 Laylatul Qadr Watch Begins",
        "content": "Tonight could be THE night - better than 1,000 months. Every moment from now until Eid matters infinitely. Don't let exhaustion rob you. Sleep less, pray more.",
        "action": "Stay awake after Isha. Pray 2 rakat, then sit in dua. Repeat: 'Allahumma innaka 'afuwwun tuhibbul 'afwa fa'fu 'anni'",
        "duration": 30,
        "reference": "\"Laylatul Qadr is better than a thousand months\" (Quran 97:3)"
    },
}

def get_hijri_date():
    """Fetch actual Hijri date from Aladhan API"""
    try:
        today = datetime.now()
        url = f"https://api.aladhan.com/v1/gToH/{today.day:02d}-{today.month:02d}-{today.year}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'IslamicReflection/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        
        hijri = data['data']['hijri']
        month_num = int(hijri['month']['number'])
        day_num = int(hijri['day'])
        month_name = hijri['month']['en']
        year = hijri['year']
        
        return month_num, day_num, month_name, year
    except Exception as e:
        print(f"Warning: Could not fetch Hijri date: {e}")
        return 0, 0, "Unknown", "1447"

def get_reflection(hijri_month, hijri_day, weekday):
    """Get appropriate reflection based on date"""
    
    # Check Ramadan (Month 9)
    if hijri_month == 9:
        if hijri_day in RAMADAN_REFLECTIONS:
            return RAMADAN_REFLECTIONS[hijri_day], f"🌙 RAMADAN DAY {hijri_day}"
        else:
            # Use Day 1 as default Ramadan reflection
            return RAMADAN_REFLECTIONS[1], f"🌙 RAMADAN DAY {hijri_day}"
    
    # Check Friday (Jumu'ah)
    if weekday == 4:  # 0=Monday, 4=Friday
        return JUMMAH_REFLECTIONS[0], "Jumu'ah"
    
    # Regular day - rotate through themes
    day_of_year = datetime.now().timetuple().tm_yday
    index = day_of_year % len(REGULAR_REFLECTIONS)
    return REGULAR_REFLECTIONS[index], ""

def main():
    today = datetime.now()
    weekday = today.weekday()
    
    # Get real Hijri date
    hijri_month, hijri_day, hijri_month_name, hijri_year = get_hijri_date()
    
    # Get appropriate reflection
    reflection, special = get_reflection(hijri_month, hijri_day, weekday)
    
    # Format output
    print("═" * 60)
    print(f"📅 {today.strftime('%A, %d %B %Y')} | {hijri_day} {hijri_month_name} {hijri_year}")
    if special:
        print(f"{special}")
    print()
    print(reflection['title'])
    print()
    print(reflection['content'])
    print()
    if reflection['duration'] > 0:
        print(f"💡 Today's Action ({reflection['duration']} min):")
    else:
        print(f"💡 Today's Action:")
    print(reflection['action'])
    
    if 'reference' in reflection:
        print()
        print(f"📖 {reflection['reference']}")
    
    print("═" * 60)

if __name__ == "__main__":
    main()