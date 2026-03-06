"""
Gmail inbox scanner — shows stats and top senders.
Use this FIRST to identify what to clean.

Usage:
  python scan.py
  python scan.py --token /path/to/token.pkl --sample 500
"""
import sys, os, pickle, argparse
sys.stdout.reconfigure(encoding='utf-8')

from collections import Counter

DEFAULT_TOKEN = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_token.pkl')

parser = argparse.ArgumentParser(description='Scan Gmail inbox and show top senders')
parser.add_argument('--token', default=DEFAULT_TOKEN, help='Path to token pickle file')
parser.add_argument('--sample', type=int, default=500, help='Number of messages to sample for sender analysis (default: 500)')
parser.add_argument('--top', type=int, default=40, help='Number of top senders to show (default: 40)')
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

print("=" * 60)
print("GMAIL INBOX SCANNER")
print("=" * 60)

# Quick stats
for label, q in [
    ('INBOX total',     'in:inbox'),
    ('INBOX unread',    'in:inbox is:unread'),
    ('Promotions',      'category:promotions -in:trash'),
    ('Social',          'category:social -in:trash'),
    ('Updates',         'category:updates -in:trash'),
    ('Forums',          'category:forums -in:trash'),
    ('Spam',            'in:spam'),
    ('Trash',           'in:trash'),
]:
    r = service.users().messages().list(userId='me', q=q, maxResults=1).execute()
    print(f"  {label:<20} ~{r.get('resultSizeEstimate', 0):>6,}")

print(f"\nSampling {args.sample} messages for sender analysis...")
result = service.users().messages().list(userId='me', q='-in:trash -in:spam', maxResults=args.sample).execute()
msgs = result.get('messages', [])

senders = Counter()
domains = Counter()
for m in msgs:
    detail = service.users().messages().get(
        userId='me', id=m['id'], format='metadata', metadataHeaders=['From']
    ).execute()
    for h in detail.get('payload', {}).get('headers', []):
        if h['name'] == 'From':
            addr = h['value']
            senders[addr] += 1
            # Extract domain
            if '@' in addr:
                domain = addr.split('@')[-1].rstrip('>')
                domains[domain] += 1
            break

print(f"\n{'TOP SENDERS':}")
print("-" * 60)
for s, c in senders.most_common(args.top):
    print(f"  {c:4d}  {s}")

print(f"\n{'TOP DOMAINS':}")
print("-" * 60)
for d, c in domains.most_common(20):
    print(f"  {c:4d}  {d}")

print("\n" + "=" * 60)
print("TIP: Use clean.py --from 'sender@domain.com' to trash these")
print("     Use deep_clean.py for bulk category cleanup")
print("=" * 60)
