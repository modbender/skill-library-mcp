from api import get_random_quote
import json

def handle_quotes_command(args):
    if args.setup:
        # Generate the cron command for the agent to execute
        job = {
            "name": "islamic-companion-daily-quote",
            "schedule": {"kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Jakarta"},
            "payload": {"kind": "agentTurn", "message": "Give me my daily Islamic quote from the islamic-companion skill."},
            "sessionTarget": "isolated",
            "delivery": {"mode": "announce"}
        }
        print(f"CRON_ADD: {json.dumps(job)}")
        print("\nDaily quote automation scheduled for 08:00 AM (Asia/Jakarta).")
        return

    # Normal fetch and display
    data = get_random_quote()
    if not data or 'data' not in data:
        print("Could not retrieve a quote at this time.")
        return

    quote_data = data['data']
    text = quote_data.get('text', '')
    author = quote_data.get('author', {}).get('name', 'Unknown')
    reference = quote_data.get('reference', '')

    print(f"\n\"{text}\"")
    print(f"— {author} {f'({reference})' if reference else ''}\n")
