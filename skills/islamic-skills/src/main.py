import argparse
import sys
import os
import json

# Add current directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from prayer import handle_prayer_command
from fasting import handle_fasting_command
from zakat import handle_zakat_command
from scheduler import handle_sync_command
from islamic_calendar import handle_calendar_command
from quotes import handle_quotes_command
from quran_search import QuranSearch
from quran_retrieval import QuranRetrieval
from quran_formatter import QuranFormatter
from api import load_config, CONFIG_PATH

def handle_quran_command(args):
    config = load_config()
    language = config.get('quran_language', 'id')
    
    if args.search:
        qs = QuranSearch(language)
        results = qs.search_keyword(args.search)
        print(QuranFormatter.format_search_results(results, args.search))
        
    elif args.surah:
        qr = QuranRetrieval(language)
        if args.ayah:
            ayah = qr.get_ayah(args.surah, args.ayah)
            print(QuranFormatter.format_ayah(ayah))
        else:
            surah = qr.get_surah(args.surah)
            print(QuranFormatter.format_surah(surah))
    else:
        print("Please provide --search or --surah (optionally with --ayah).")

def main():
    parser = argparse.ArgumentParser(description="Islamic Companion CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Quran
    quran_parser = subparsers.add_parser('quran')
    quran_parser.add_argument('--search', type=str, help="Search keyword")
    quran_parser.add_argument('--surah', type=int, help="Surah number")
    quran_parser.add_argument('--ayah', type=int, help="Ayah number (requires --surah)")
    
    # Prayer
    p_parser = subparsers.add_parser('prayer')
    p_parser.add_argument('--today', action='store_true', help="Show today's prayer times")
    p_parser.add_argument('--sync', action='store_true', help="Sync schedule to cron")
    
    # Fasting
    f_parser = subparsers.add_parser('fasting')
    f_parser.add_argument('--today', action='store_true', help="Show fasting times")
    
    # Zakat
    z_parser = subparsers.add_parser('zakat')
    z_parser.add_argument('--nisab', action='store_true', help="Show Zakat Nisab")
    z_parser.add_argument('--currency', type=str, help="Currency code (e.g., IDR)")
    
    # Calendar
    cal_parser = subparsers.add_parser('calendar')
    cal_parser.add_argument('--city', type=str, help="City name")
    cal_parser.add_argument('--country', type=str, default="Indonesia", help="Country name (default: Indonesia)")
    cal_parser.add_argument('--month', type=int, help="Month (1-12)")
    cal_parser.add_argument('--year', type=int, help="Year (e.g., 2026)")

    # Quotes
    q_parser = subparsers.add_parser('quotes')
    q_parser.add_argument('--setup', action='store_true', help="Setup daily quote automation")
    q_parser.add_argument('--random', action='store_true', help="Get a random quote")

    # Config
    c_parser = subparsers.add_parser('config')
    c_parser.add_argument('--set-loc', nargs=2, metavar=('LAT', 'LONG'), type=float, help="Set latitude and longitude")
    c_parser.add_argument('--name', type=str, help="Location name")

    args = parser.parse_args()
    
    if args.command == 'prayer':
        if args.sync:
            handle_sync_command(args)
        elif args.today:
            handle_prayer_command(args)
        else:
            p_parser.print_help()
    elif args.command == 'fasting':
        if args.today:
            handle_fasting_command(args)
        else:
            f_parser.print_help()
    elif args.command == 'zakat':
        if args.nisab:
            handle_zakat_command(args)
        else:
            z_parser.print_help()
    elif args.command == 'calendar':
        handle_calendar_command(args)
    elif args.command == 'quotes':
        handle_quotes_command(args)
    elif args.command == 'quran':
        handle_quran_command(args)
    elif args.command == 'config':
        if args.set_loc:
            config = load_config()
            config['location']['latitude'] = args.set_loc[0]
            config['location']['longitude'] = args.set_loc[1]
            if args.name:
                config['location']['name'] = args.name
            
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Location updated to {args.name or 'custom coordinates'}: {args.set_loc}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
