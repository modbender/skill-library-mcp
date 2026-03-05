"""
Gmail OAuth authentication helper.
Creates/refreshes a token file for use by other gmail-cleaner scripts.

Usage:
  python auth.py                                   # use defaults
  python auth.py --credentials creds.json --token token.pkl
  python auth.py --credentials creds.json --token token.pkl --scopes settings

Scopes:
  basic    (default) - read/modify/delete messages + labels
  settings           - adds gmail.settings.basic (required for creating filters)
  all                - all scopes
"""
import sys, os, pickle, argparse
sys.stdout.reconfigure(encoding='utf-8')

SCOPE_SETS = {
    'basic': [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly',
    ],
    'settings': [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.settings.basic',
    ],
    'all': [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.settings.basic',
        'https://www.googleapis.com/auth/gmail.labels',
    ],
}

DEFAULT_CREDS = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_credentials.json')
DEFAULT_TOKEN = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'gmail_token.pkl')

parser = argparse.ArgumentParser(description='Gmail OAuth authentication')
parser.add_argument('--credentials', default=DEFAULT_CREDS, help='Path to OAuth credentials JSON from Google Cloud Console')
parser.add_argument('--token', default=DEFAULT_TOKEN, help='Where to save/load the token')
parser.add_argument('--scopes', default='settings', choices=['basic', 'settings', 'all'], help='Scope set to request')
args = parser.parse_args()

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("Installing required packages...")
    os.system(f"{sys.executable} -m pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client -q")
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

scopes = SCOPE_SETS[args.scopes]
creds = None

# Try to load existing token
if os.path.exists(args.token):
    with open(args.token, 'rb') as f:
        creds = pickle.load(f)

# Refresh if expired
if creds and creds.expired and creds.refresh_token:
    print("Refreshing existing token...")
    creds.refresh(Request())
elif not creds or not creds.valid:
    if not os.path.exists(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}")
        print("Download it from Google Cloud Console > APIs & Services > Credentials > OAuth 2.0 Client IDs > Desktop app > Download JSON")
        sys.exit(1)
    print(f"Starting OAuth flow for scopes: {args.scopes}")
    print("A browser window will open. Sign in and grant permissions.")
    flow = InstalledAppFlow.from_client_secrets_file(args.credentials, scopes)
    creds = flow.run_local_server(port=0)

# Save token
os.makedirs(os.path.dirname(args.token), exist_ok=True)
with open(args.token, 'wb') as f:
    pickle.dump(creds, f)

print(f"\n✅ Token saved to: {args.token}")
print(f"   Scopes: {args.scopes}")
print(f"   Valid: {creds.valid}")
print(f"   Account: {getattr(creds, 'id_token', {}).get('email', 'unknown') if hasattr(creds, 'id_token') else 'check above'}")
