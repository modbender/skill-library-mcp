"""
Example CLI for the zotero skill.

Environment variables (if set, used as defaults):
  ZOTERO_API_KEY: Your Zotero developer API key (required)
  ZOTERO_USER_ID: Your personal library user ID
  ZOTERO_GROUP_ID: Your group library ID

Usage examples (environment variables take precedence if not overridden):
  # With environment variables set:
  python cli.py search --q "deep learning"
  
  # Or override with command-line arguments:
  python cli.py search --q "deep learning" --user 12345
  python cli.py note --item 12345 --text "Add methods note" --user 12345
  python cli.py upload --item 67890 --file /path/to/foo.pdf --user 12345

Note: destructive actions require --yes to run.
"""
import argparse
import os
import json
from pyzotero_client import ZoteroClient

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest='cmd')

p_search = sub.add_parser('search')
p_search.add_argument('--q')
p_search.add_argument('--user')
p_search.add_argument('--group')
p_search.add_argument('--group-mode', action='store_true')

p_note = sub.add_parser('note')
p_note.add_argument('--item', required=True)
p_note.add_argument('--text', required=True)
p_note.add_argument('--user')
p_note.add_argument('--group')
p_note.add_argument('--group-mode', action='store_true')

p_upload = sub.add_parser('upload')
p_upload.add_argument('--item', required=True)
p_upload.add_argument('--file', required=True)
p_upload.add_argument('--user')
p_upload.add_argument('--group')
p_upload.add_argument('--group-mode', action='store_true')

p_delete = sub.add_parser('delete')
p_delete.add_argument('--item', required=True)
p_delete.add_argument('--yes', action='store_true')

args = parser.parse_args()
if not args.cmd:
    parser.print_help()
    raise SystemExit(1)

# Read environment variables as defaults
default_user = os.environ.get('ZOTERO_USER_ID')
default_group = os.environ.get('ZOTERO_GROUP_ID')

# Use command-line arguments if provided, otherwise use environment variables
user_id = getattr(args, 'user', None) or default_user
group_id = getattr(args, 'group', None) or default_group
is_group = getattr(args, 'group_mode', False)

# Inform user which values are being used from environment variables
if user_id and not getattr(args, 'user', None):
    print(f"✓ Using ZOTERO_USER_ID from environment: {user_id}", file=__import__('sys').stderr)
if group_id and not getattr(args, 'group', None):
    print(f"✓ Using ZOTERO_GROUP_ID from environment: {group_id}", file=__import__('sys').stderr)

client = ZoteroClient(user_id=user_id, group_id=group_id, is_group=is_group)

if args.cmd == 'search':
    res = client.search_items(q=args.q)
    print(json.dumps(res, indent=2, ensure_ascii=False))

elif args.cmd == 'note':
    res = client.add_note(args.item, args.text)
    print('Note created:', res)

elif args.cmd == 'upload':
    res = client.upload_attachment(args.item, args.file)
    print('Upload response:', res)

elif args.cmd == 'delete':
    if not args.yes:
        print('Refusing to delete without --yes')
    else:
        res = client.delete_item(args.item)
        print('Deleted:', res)
