"""
Gmail restore — move emails from trash back to a label (skip inbox).
Useful for rescuing emails that were bulk-trashed by mistake.

Usage:
  # Restore all emails from a sender, apply a label:
  python restore.py --from healthbeat@mail.health.harvard.edu --label "Harvard Health"

  # Restore using any Gmail query:
  python restore.py --query "from:apple.com in:trash" --label "Tech/Apple"

  # Create the label if it doesn't exist, with a color:
  python restore.py --from sender@example.com --label "My Label" --color blue

  # Dry run:
  python restore.py --from sender@example.com --label "My Label" --dry-run

Available colors: blue, green, red, purple, orange, yellow, teal, navy
"""
import sys, os, pickle, argparse
sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_TOKEN = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_token.pkl')

COLORS = {
    'blue':   ('#4a86e8', '#ffffff'),
    'navy':   ('#1c4587', '#ffffff'),
    'green':  ('#16a766', '#ffffff'),
    'red':    ('#fb4c2f', '#ffffff'),
    'purple': ('#8e63ce', '#ffffff'),
    'orange': ('#e07e00', '#ffffff'),
    'yellow': ('#f2c960', '#000000'),
    'teal':   ('#149e60', '#ffffff'),
}

parser = argparse.ArgumentParser(description='Restore Gmail emails from trash')
parser.add_argument('--token', default=DEFAULT_TOKEN)
parser.add_argument('--from', dest='sender', help='Sender email address to restore')
parser.add_argument('--query', help='Gmail search query (will auto-add "in:trash")')
parser.add_argument('--label', required=True, help='Label to apply to restored emails')
parser.add_argument('--color', default='blue', choices=list(COLORS.keys()), help='Label color if creating new (default: blue)')
parser.add_argument('--skip-inbox', action='store_true', default=True, help='Keep restored emails out of inbox (default: True)')
parser.add_argument('--dry-run', action='store_true')
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

# Get or create label
existing = service.users().labels().list(userId='me').execute().get('labels', [])
label_id = None
for l in existing:
    if l['name'] == args.label:
        label_id = l['id']
        print(f"✅ Label exists: {args.label} (id: {label_id})")
        break

if not label_id and not args.dry_run:
    bg, fg = COLORS[args.color]
    result = service.users().labels().create(userId='me', body={
        'name': args.label,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
        'color': {'backgroundColor': bg, 'textColor': fg}
    }).execute()
    label_id = result['id']
    print(f"✅ Created label: {args.label} (id: {label_id})")

# Build query
if args.sender:
    query = f"from:{args.sender} in:trash"
elif args.query:
    query = args.query if 'in:trash' in args.query else args.query + ' in:trash'
else:
    print("ERROR: Provide --from or --query")
    sys.exit(1)

print(f"\nSearching: {query}")
ids = []
page_token = None
while True:
    params = {'userId': 'me', 'q': query, 'maxResults': 500}
    if page_token:
        params['pageToken'] = page_token
    result = service.users().messages().list(**params).execute()
    msgs = result.get('messages', [])
    if not msgs:
        break
    ids.extend([m['id'] for m in msgs])
    page_token = result.get('nextPageToken')
    if not page_token:
        break

print(f"Found: {len(ids)} messages in trash")

if args.dry_run:
    print(f"DRY RUN — would restore {len(ids)} emails to label '{args.label}'")
    sys.exit(0)

if not ids:
    print("Nothing to restore.")
    sys.exit(0)

# Restore: remove TRASH, apply label, optionally skip INBOX
restore_body = {
    'ids': [],
    'removeLabelIds': ['TRASH'],
    'addLabelIds': [label_id] if label_id else []
}

total = 0
for i in range(0, len(ids), 1000):
    chunk = ids[i:i+1000]
    body = {
        'ids': chunk,
        'removeLabelIds': ['TRASH'],
        'addLabelIds': [label_id] if label_id else []
    }
    service.users().messages().batchModify(userId='me', body=body).execute()
    total += len(chunk)
    print(f"  Restored {total}/{len(ids)}...")

print(f"\n✅ Restored {total} emails to label '{args.label}' (skipping inbox)")
