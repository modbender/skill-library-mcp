"""
Gmail deep cleaner — comprehensive inbox cleanup in 4 steps:
  1. Trash all promotions, social, forums (by age)
  2. Archive old read emails from inbox
  3. Mark old unread as read
  4. Permanently purge existing trash

Usage:
  python deep_clean.py
  python deep_clean.py --token /path/to/token.pkl
  python deep_clean.py --promo-days 7 --archive-days 30 --unread-days 14
  python deep_clean.py --skip-trash-purge
  python deep_clean.py --dry-run
"""
import sys, os, pickle, argparse, time
sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_TOKEN = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_token.pkl')

parser = argparse.ArgumentParser(description='Deep clean Gmail inbox')
parser.add_argument('--token', default=DEFAULT_TOKEN)
parser.add_argument('--promo-days', type=int, default=0,    help='Trash promotions older than N days (0=all, default:0)')
parser.add_argument('--archive-days', type=int, default=60, help='Archive read inbox emails older than N days (default:60)')
parser.add_argument('--unread-days', type=int, default=30,  help='Mark old unread as read after N days (default:30)')
parser.add_argument('--skip-archive', action='store_true',  help='Skip step 2 (archive old read)')
parser.add_argument('--skip-mark-read', action='store_true',help='Skip step 3 (mark old unread as read)')
parser.add_argument('--skip-trash-purge', action='store_true', help='Skip step 4 (purge existing trash)')
parser.add_argument('--dry-run', action='store_true',       help='Count only, no changes')
parser.add_argument('--max', type=int, default=10000,       help='Max messages per query')
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

def get_ids(query, max_results=10000):
    ids = []
    page_token = None
    while len(ids) < max_results:
        params = {'userId': 'me', 'q': query, 'maxResults': min(500, max_results - len(ids))}
        if page_token:
            params['pageToken'] = page_token
        try:
            r = service.users().messages().list(**params).execute()
        except Exception as e:
            print(f"  [ERROR] {e}"); break
        msgs = r.get('messages', [])
        ids.extend([m['id'] for m in msgs])
        page_token = r.get('nextPageToken')
        if not page_token or not msgs:
            break
    return ids

def batch_op(ids, op, label):
    total = 0
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i+1000]
        try:
            if op == 'trash':
                service.users().messages().batchModify(userId='me', body={
                    'ids': chunk, 'removeLabelIds': ['INBOX'], 'addLabelIds': ['TRASH']
                }).execute()
            elif op == 'archive':
                service.users().messages().batchModify(userId='me', body={
                    'ids': chunk, 'removeLabelIds': ['INBOX']
                }).execute()
            elif op == 'read':
                service.users().messages().batchModify(userId='me', body={
                    'ids': chunk, 'removeLabelIds': ['UNREAD']
                }).execute()
            elif op == 'delete':
                service.users().messages().batchDelete(userId='me', body={'ids': chunk}).execute()
            total += len(chunk)
            print(f"  [{label}] {op} {total}/{len(ids)}")
            time.sleep(0.1)
        except Exception as e:
            print(f"  [ERROR] {e}"); time.sleep(2)
    return total

promo_age = f"older_than:{args.promo_days}d" if args.promo_days > 0 else ""

STEP1_QUERIES = [
    (f"category:promotions {promo_age}".strip(),          "Promotions"),
    ("category:social older_than:30d",                    "Social >30d"),
    ("category:forums older_than:30d",                    "Forums >30d"),
    ("unsubscribe older_than:90d -from:linkedin.com -from:google.com -from:microsoft.com -from:apple.com -from:amazon.com -from:paypal.com -from:stripe.com", "Newsletter >90d"),
]

STEP2_QUERIES = [
    (f"in:inbox is:read older_than:{args.archive_days}d -label:important -is:starred", f"Read inbox >{args.archive_days}d"),
    ("in:inbox category:updates is:read older_than:14d",  "Updates read >14d"),
    ("in:inbox category:social is:read older_than:14d",   "Social read >14d"),
]

print("=" * 60)
print("GMAIL DEEP CLEANER")
if args.dry_run:
    print("  *** DRY RUN — no changes ***")
print("=" * 60)

grand_trash = grand_archive = 0

# STEP 1: Trash promotions + newsletters
print(f"\n── STEP 1: Trash Promotions & Newsletters ──")
for q, lbl in STEP1_QUERIES:
    ids = get_ids(q, args.max)
    if not ids:
        print(f"  [0] {lbl}")
        continue
    print(f"  [{len(ids)}] {lbl}")
    if not args.dry_run:
        grand_trash += batch_op(ids, 'trash', lbl)
    else:
        grand_trash += len(ids)

# STEP 2: Archive old read emails
if not args.skip_archive:
    print(f"\n── STEP 2: Archive Old Read Emails ──")
    for q, lbl in STEP2_QUERIES:
        ids = get_ids(q, args.max)
        if not ids:
            print(f"  [0] {lbl}")
            continue
        print(f"  [{len(ids)}] {lbl}")
        if not args.dry_run:
            grand_archive += batch_op(ids, 'archive', lbl)
        else:
            grand_archive += len(ids)

# STEP 3: Mark old unread as read
if not args.skip_mark_read:
    print(f"\n── STEP 3: Mark Old Unread as Read (>{args.unread_days}d) ──")
    ids = get_ids(f"in:inbox is:unread older_than:{args.unread_days}d -label:important -is:starred", args.max)
    if ids:
        print(f"  [{len(ids)}] Old unread")
        if not args.dry_run:
            batch_op(ids, 'read', 'Old unread')
    else:
        print("  [0] Nothing found")

# STEP 4: Purge trash
if not args.skip_trash_purge:
    print(f"\n── STEP 4: Purge Existing Trash ──")
    ids = get_ids("in:trash older_than:1d", args.max)
    if ids:
        print(f"  [{len(ids)}] In trash")
        if not args.dry_run:
            batch_op(ids, 'delete', 'Trash purge')
    else:
        print("  [0] Trash already empty")

print(f"\n{'='*60}")
print(f"{'DRY RUN' if args.dry_run else 'DONE'}")
print(f"  Trashed:  {grand_trash}")
print(f"  Archived: {grand_archive}")
print("=" * 60)
