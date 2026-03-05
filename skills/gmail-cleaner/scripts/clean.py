"""
Gmail bulk cleaner — trash emails matching sender addresses or search queries.
Processes 1000 messages per API call (Gmail batchModify limit).

Usage:
  # Trash emails from specific senders:
  python clean.py --from "spam@example.com,news@example.org"

  # Trash using a Gmail search query:
  python clean.py --query "category:promotions older_than:30d"

  # Trash multiple queries from a JSON config file:
  python clean.py --config senders.json

  # Permanently delete instead of trash:
  python clean.py --from "spam@example.com" --delete

  # Dry run (count only, don't modify):
  python clean.py --from "spam@example.com" --dry-run

Config JSON format:
  [
    {"query": "from:spam@example.com", "label": "Spam Sender"},
    {"query": "category:promotions older_than:30d", "label": "Old Promotions"}
  ]
"""
import sys, os, pickle, argparse, json, time
sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_TOKEN = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_token.pkl')

parser = argparse.ArgumentParser(description='Bulk clean Gmail messages')
parser.add_argument('--token', default=DEFAULT_TOKEN)
parser.add_argument('--from', dest='senders', help='Comma-separated sender email addresses to trash')
parser.add_argument('--query', help='Gmail search query to match messages to trash')
parser.add_argument('--config', help='Path to JSON config file with list of {query, label} objects')
parser.add_argument('--delete', action='store_true', help='Permanently delete (default: move to trash)')
parser.add_argument('--dry-run', action='store_true', help='Count only, do not modify')
parser.add_argument('--max', type=int, default=10000, help='Max messages per query (default: 10000)')
args = parser.parse_args()

try:
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    os.system(f"{sys.executable} -m pip install google-api-python-client google-auth -q")
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

with open(args.token, 'rb') as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(args.token, 'wb') as f:
        pickle.dump(creds, f)

service = build('gmail', 'v1', credentials=creds)

# Build list of (query, label) tuples
tasks = []

if args.config:
    with open(args.config, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        tasks.append((item['query'], item.get('label', item['query'][:50])))

if args.senders:
    for sender in args.senders.split(','):
        sender = sender.strip()
        tasks.append((f"from:{sender}", f"Sender: {sender}"))

if args.query:
    tasks.append((args.query, f"Query: {args.query[:50]}"))

if not tasks:
    print("ERROR: Provide --from, --query, or --config")
    sys.exit(1)

def get_ids(query, max_results=10000):
    ids = []
    page_token = None
    while len(ids) < max_results:
        params = {'userId': 'me', 'q': query, 'maxResults': min(500, max_results - len(ids))}
        if page_token:
            params['pageToken'] = page_token
        try:
            result = service.users().messages().list(**params).execute()
        except Exception as e:
            print(f"  [ERROR] list: {e}")
            break
        msgs = result.get('messages', [])
        ids.extend([m['id'] for m in msgs])
        page_token = result.get('nextPageToken')
        if not page_token or not msgs:
            break
    return ids

def batch_trash(ids):
    total = 0
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i+1000]
        service.users().messages().batchModify(
            userId='me',
            body={'ids': chunk, 'removeLabelIds': ['INBOX'], 'addLabelIds': ['TRASH']}
        ).execute()
        total += len(chunk)
        print(f"    Trashed {total}/{len(ids)}...")
        time.sleep(0.1)
    return total

def batch_delete(ids):
    total = 0
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i+1000]
        service.users().messages().batchDelete(
            userId='me', body={'ids': chunk}
        ).execute()
        total += len(chunk)
        print(f"    Deleted {total}/{len(ids)}...")
        time.sleep(0.1)
    return total

action_verb = "PERMANENTLY DELETE" if args.delete else "TRASH"
print("=" * 60)
print(f"GMAIL BULK CLEANER — {action_verb}")
if args.dry_run:
    print("  *** DRY RUN — no changes will be made ***")
print("=" * 60)

grand_total = 0
for query, label in tasks:
    print(f"\n  [{label}]")
    print(f"  Query: {query}")
    ids = get_ids(query, max_results=args.max)
    if not ids:
        print(f"  Nothing found")
        continue
    print(f"  Found: {len(ids)} messages")
    if args.dry_run:
        grand_total += len(ids)
        continue
    if args.delete:
        n = batch_delete(ids)
    else:
        n = batch_trash(ids)
    grand_total += n

print(f"\n{'='*60}")
if args.dry_run:
    print(f"DRY RUN COMPLETE — would {'delete' if args.delete else 'trash'} {grand_total} messages")
else:
    print(f"DONE — {'deleted' if args.delete else 'trashed'} {grand_total} messages total")
    if not args.delete:
        print("Gmail auto-purges trash after 30 days")
print("=" * 60)
