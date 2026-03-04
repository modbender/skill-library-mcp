"""
Gmail organizer — creates a label hierarchy, applies labels to existing emails,
and optionally creates auto-filter rules for future emails.

Usage:
  python organize.py                         # use built-in label set
  python organize.py --config labels.json   # use custom label config
  python organize.py --skip-filters         # labels only, no filters
  python organize.py --dry-run

Custom config JSON format:
{
  "labels": [
    {"name": "Business",         "color": "green"},
    {"name": "Business/Solar",   "color": "green"}
  ],
  "rules": [
    {"query": "from:cedarscy.com", "label": "Business/Solar"},
    {"query": "from:revolut.com",  "label": "Banking"}
  ],
  "filters": [
    {"from": "revolut.com", "label": "Banking"},
    {"from": "apple.com",   "label": "Tech"}
  ]
}

Colors: blue, navy, green, teal, red, purple, orange, yellow, pink
"""
import sys, os, pickle, argparse, json, time
sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_TOKEN = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_token.pkl')

COLORS = {
    'blue':   ('#4a86e8', '#ffffff'),
    'navy':   ('#0d3472', '#ffffff'),
    'green':  ('#16a766', '#ffffff'),
    'teal':   ('#149e60', '#ffffff'),
    'red':    ('#fb4c2f', '#ffffff'),
    'purple': ('#8e63ce', '#ffffff'),
    'orange': ('#e07e00', '#ffffff'),
    'yellow': ('#f2c960', '#000000'),
    'pink':   ('#f691b2', '#000000'),
}

# ── Built-in defaults (override with --config) ──────────────────────────────
DEFAULT_LABELS = [
    ("Business",                "green"),
    ("Business/Finance",        "navy"),
    ("Banking",                 "navy"),
    ("Tech",                    "purple"),
    ("Tech/Apple",              "purple"),
    ("Tech/Google",             "blue"),
    ("Tech/Microsoft",          "blue"),
    ("Personal",                "pink"),
    ("Personal/Shopping",       "pink"),
    ("Trading",                 "pink"),
    ("Social",                  "red"),
    ("Social/LinkedIn",         "navy"),
]

DEFAULT_RULES = [
    ("from:apple.com OR from:icloud.com",                           "Tech/Apple"),
    ("from:accounts.google.com OR from:google.com",                 "Tech/Google"),
    ("from:microsoft.com OR from:onedrive.com OR from:outlook.com", "Tech/Microsoft"),
    ("from:revolut.com OR from:paypal.com OR from:stripe.com",      "Banking"),
    ("from:amazon.com -from:store-news@amazon.com",                 "Personal/Shopping"),
    ("from:linkedin.com",                                           "Social/LinkedIn"),
]

DEFAULT_FILTERS = [
    ("revolut.com",              "Banking"),
    ("apple.com OR icloud.com",  "Tech/Apple"),
    ("google.com",               "Tech/Google"),
    ("microsoft.com",            "Tech/Microsoft"),
    ("linkedin.com",             "Social/LinkedIn"),
]
# ─────────────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description='Organize Gmail with labels and filters')
parser.add_argument('--token', default=DEFAULT_TOKEN)
parser.add_argument('--config', help='Path to custom labels/rules/filters JSON config')
parser.add_argument('--skip-filters', action='store_true', help='Skip creating Gmail auto-filters')
parser.add_argument('--skip-rules', action='store_true',   help='Skip applying labels to existing emails')
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

# Load config
if args.config:
    with open(args.config, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    label_defs = [(l['name'], l.get('color', 'blue')) for l in cfg.get('labels', [])]
    rules      = [(r['query'], r['label']) for r in cfg.get('rules', [])]
    filter_defs = [(f['from'], f['label']) for f in cfg.get('filters', [])]
else:
    label_defs  = DEFAULT_LABELS
    rules       = DEFAULT_RULES
    filter_defs = DEFAULT_FILTERS

print("=" * 55)
print("GMAIL ORGANIZER")
if args.dry_run:
    print("  *** DRY RUN ***")
print("=" * 55)

# STEP 1: Create labels
print("\n── STEP 1: Create Labels ──")
existing = service.users().labels().list(userId='me').execute().get('labels', [])
existing_names = {l['name']: l['id'] for l in existing}
label_ids = dict(existing_names)

for name, color in label_defs:
    if name in existing_names:
        print(f"  [skip] {name}")
        continue
    if args.dry_run:
        print(f"  [would create] {name}")
        continue
    bg, fg = COLORS.get(color, COLORS['blue'])
    try:
        r = service.users().labels().create(userId='me', body={
            'name': name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
            'color': {'backgroundColor': bg, 'textColor': fg}
        }).execute()
        label_ids[name] = r['id']
        print(f"  [✓] {name}")
    except Exception as e:
        print(f"  [!] {name}: {e}")
    time.sleep(0.1)

# STEP 2: Apply labels to existing emails
if not args.skip_rules:
    print("\n── STEP 2: Apply Labels to Existing Emails ──")
    grand = 0
    for query, label in rules:
        lid = label_ids.get(label)
        if not lid:
            print(f"  [!] No label ID for: {label}")
            continue
        ids = []
        page_token = None
        while True:
            params = {'userId': 'me', 'q': query + ' -in:trash -in:spam', 'maxResults': 500}
            if page_token:
                params['pageToken'] = page_token
            try:
                r = service.users().messages().list(**params).execute()
            except:
                break
            msgs = r.get('messages', [])
            ids.extend([m['id'] for m in msgs])
            page_token = r.get('nextPageToken')
            if not page_token or not msgs:
                break

        if not ids:
            print(f"  [0]  {label}")
            continue
        if args.dry_run:
            print(f"  [{len(ids)}]  {label} (dry run)")
            grand += len(ids)
            continue

        for i in range(0, len(ids), 1000):
            service.users().messages().batchModify(
                userId='me', body={'ids': ids[i:i+1000], 'addLabelIds': [lid]}
            ).execute()
            time.sleep(0.1)
        grand += len(ids)
        print(f"  [{len(ids)}]  {label}")

    print(f"\n  Total emails labeled: {grand}")

# STEP 3: Create filters
if not args.skip_filters:
    print("\n── STEP 3: Create Auto-Filters ──")
    print("  Note: Requires gmail.settings.basic scope (run auth.py --scopes settings)")
    created = failed = 0
    for from_q, label in filter_defs:
        lid = label_ids.get(label)
        if not lid:
            print(f"  [!] No label ID for: {label}")
            failed += 1
            continue
        if args.dry_run:
            print(f"  [would create] {from_q} → {label}")
            created += 1
            continue
        try:
            service.users().settings().filters().create(
                userId='me',
                body={
                    'criteria': {'from': from_q},
                    'action': {'addLabelIds': [lid]}
                }
            ).execute()
            print(f"  [✓] {from_q[:40]} → {label}")
            created += 1
        except Exception as e:
            print(f"  [!] {from_q[:40]}: {str(e)[:60]}")
            failed += 1
        time.sleep(0.1)
    print(f"\n  Filters: {created} created, {failed} failed")

print(f"\n{'='*55}")
print("DONE")
print("=" * 55)
