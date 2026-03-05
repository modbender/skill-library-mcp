#!/usr/bin/env python3
"""
pre-fetch.py — Fetch newsletters from Gmail API and produce compact JSON
that Haiku can read without context overflow.

Writes newsletter-inbox.json with just the fields needed for summarisation:
  threadId, messageId, source, subject, snippet, date

Usage: python3 pre-fetch.py
"""
import json, sys, os, re
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

INBOX_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'newsletter-inbox.json')
TOKEN_FILE = os.environ.get('BRIEFED_GMAIL_TOKEN_FILE', os.path.expanduser('~/.openclaw/workspace/briefed-gmail-token.json'))
CLIENT_SECRET_FILE = os.environ.get('BRIEFED_GMAIL_CLIENT_SECRET', os.path.expanduser('~/client_secret.json'))
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Subject/sender substrings that mark an email as transactional (case-insensitive)
SKIP_SUBJECT_PATTERNS = [
    'your invoice', 'your receipt', 'your order',
    'payment confirmation', 'domain renewal', 'verify your email',
    'password reset', 'has been charged', 'has shipped',
    'subscription confirmed', 'unsubscribe confirmation',
    '[action needed]', 'action required',
    'account activity statement',
    "you've got new correspondence",
    'we sent your payout',
    "we've found you",
    'new property alert',
    'property in ',
    'properties in ',
    'pre-order ',
    'simpler pricing',
    'data writes',
    'api access is turned off',
    'your claude api',
    'members info',
    '72-hour reminder',
    'seiko',
    '1 new!',
    'suggested properties',
    'book now!',
    'identity document expires',
    'document renewal',
    'renewal reminder',
    'account alert',
    'withdrawal privileges',
    'you have a new message from linkedin',
    'linkedin notification',
]

SKIP_SENDERS = [
    'ebay', 'rightmove', 'zoopla', 'trading 212', 'tsb',
    'barclays', 'hsbc', 'natwest', 'lloyds',
    'amazon', 'paypal', 'stripe',
    'kucoin', 'locrating',
]


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise RuntimeError(
                    f"Missing OAuth client file: {CLIENT_SECRET_FILE}\n"
                    "Set BRIEFED_GMAIL_CLIENT_SECRET to your Google OAuth client JSON."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def is_transactional(subject, sender):
    subj = (subject or '').lower()
    send = (sender or '').lower()
    return any(p in subj for p in SKIP_SUBJECT_PATTERNS) or any(p in send for p in SKIP_SENDERS)


def get_sender_name(from_header):
    m = re.match(r'^"?([^"<]+)"?\s*(?:<[^>]+>)?$', (from_header or '').strip())
    if m:
        name = m.group(1).strip().strip('"')
        return name if name else (from_header or '')
    return from_header or ''


def headers_map(payload):
    out = {}
    for h in payload.get('headers', []):
        name = h.get('name', '').lower()
        if name:
            out[name] = h.get('value', '')
    return out


def fallback_date(msg):
    internal = msg.get('internalDate')
    if internal:
        try:
            ts = int(internal) / 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception:
            pass
    return ''


def main():
    print('Connecting to Gmail API...', flush=True)
    try:
        service = get_gmail_service()
    except Exception as e:
        print(f'Auth error: {e}', file=sys.stderr)
        sys.exit(1)

    query = 'category:updates OR category:promotions newer_than:1d'
    print('Fetching newsletter list...', flush=True)
    try:
        resp = service.users().messages().list(userId='me', q=query, maxResults=30).execute()
        messages = resp.get('messages', [])
    except Exception as e:
        print(f'Error fetching list: {e}', file=sys.stderr)
        sys.exit(1)

    print(f'Found {len(messages)} emails. Filtering...', flush=True)

    newsletters = []
    seen_threads = set()

    for m in messages:
        msg_id = m.get('id')
        thread_id = m.get('threadId')
        if not msg_id or not thread_id or thread_id in seen_threads:
            continue
        seen_threads.add(thread_id)

        try:
            full = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        except Exception as e:
            print(f'  Skip {thread_id}: {e}', file=sys.stderr)
            continue

        payload = full.get('payload', {})
        h = headers_map(payload)
        subject = h.get('subject', '(no subject)')
        source = get_sender_name(h.get('from', ''))
        date = h.get('date', '') or fallback_date(full)
        snippet = (full.get('snippet') or '')[:400]

        if is_transactional(subject, source):
            print(f'  SKIP (transactional): {source} — {subject[:50]}')
            continue

        newsletters.append({
            'threadId': thread_id,
            'messageId': msg_id,
            'source': source,
            'subject': subject,
            'snippet': snippet,
            'date': date,
        })
        print(f'  KEEP: {source} — {subject[:60]}')

    with open(INBOX_FILE, 'w') as f:
        json.dump({'count': len(newsletters), 'newsletters': newsletters}, f, indent=2)

    print(f'\nDone. {len(newsletters)} newsletters written to newsletter-inbox.json')


if __name__ == '__main__':
    main()
