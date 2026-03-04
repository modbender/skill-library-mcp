"""
Minimal pyzotero wrapper for the zotero skill.
Requires: pip install pyzotero

Usage: import functions below in cli or other scripts.

Environment variables (optional):
  ZOTERO_API_KEY: Your Zotero API key (required for execution)
  ZOTERO_USER_ID: Your personal library user ID (alternative to --user CLI flag)
  ZOTERO_GROUP_ID: Your group library ID (alternative to --group CLI flag)

If environment variables are set, they are used automatically as defaults.
Command-line arguments override environment variables when provided.
"""
from pyzotero import zotero
import os
import json
import sys

API_KEY_ENV = os.environ.get("ZOTERO_API_KEY")
USER_ID_ENV = os.environ.get("ZOTERO_USER_ID")
GROUP_ID_ENV = os.environ.get("ZOTERO_GROUP_ID")
if not API_KEY_ENV:
    # lazy: allow import but raise on use
    API_KEY_ENV = None
if not USER_ID_ENV:
    USER_ID_ENV = None
if not GROUP_ID_ENV:
    GROUP_ID_ENV = None

class ZoteroClient:
    def __init__(self, user_id=None, group_id=None, is_group=False, api_key=None):
        # Try to get credentials from arguments first, then fallback to environment
        api_key = api_key or API_KEY_ENV
        final_user_id = user_id or USER_ID_ENV
        final_group_id = group_id or GROUP_ID_ENV
        
        if not api_key:
            raise ValueError(
                "ZOTERO_API_KEY not found. Please set the environment variable:\n"
                "  export ZOTERO_API_KEY='your_key_here'\n"
                "Or pass api_key parameter to ZoteroClient()"
            )
        
        # Log which credentials are being used
        cred_source = []
        if user_id:
            cred_source.append(f"user_id={user_id} (from argument)")
        elif USER_ID_ENV:
            cred_source.append(f"user_id={USER_ID_ENV} (from ZOTERO_USER_ID env var)")
        
        if group_id:
            cred_source.append(f"group_id={group_id} (from argument)")
        elif GROUP_ID_ENV:
            cred_source.append(f"group_id={GROUP_ID_ENV} (from ZOTERO_GROUP_ID env var)")
        
        if is_group:
            cred_source.append("mode=group")
        else:
            cred_source.append("mode=user")
        
        # Required: either user_id or group_id must be provided
        if not final_user_id and not final_group_id:
            raise ValueError(
                "Either user_id or group_id must be provided.\n"
                "Set via environment variables:\n"
                "  export ZOTERO_USER_ID='your_user_id'\n"
                "  export ZOTERO_GROUP_ID='your_group_id'\n"
                "Or pass them as arguments to ZoteroClient()"
            )
        
        self.api_key = api_key
        
        if is_group and final_group_id:
            self.zot = zotero.Zotero(final_group_id, 'group', api_key)
            sys.stderr.write(f"✓ Initialized Zotero client for group: {final_group_id}\n")
        elif final_user_id:
            self.zot = zotero.Zotero(final_user_id, 'user', api_key)
            sys.stderr.write(f"✓ Initialized Zotero client for user: {final_user_id}\n")
        else:
            raise ValueError('Either user_id or group_id must be provided')

    def search_items(self, q=None, params=None, limit=25, sort=None):
        params = params or {}
        if q:
            params['q'] = q
        if sort:
            params['sort'] = sort
        return self.zot.items(params=params, limit=limit)

    def create_item(self, item_json):
        # item_json should follow Zotero item structure
        return self.zot.create_items([item_json])

    def update_item(self, item_key, patch_data):
        # patch_data: dict of fields to update (title, tags, etc.)
        # Zotero requires full item data for update; fetch current, modify, then update
        current = self.zot.item(item_key)
        if 'data' in current:
            data = current['data']
        else:
            data = current
        data.update(patch_data)
        return self.zot.update_item(item_key, data)

    def add_note(self, parent_item_key, note_content):
        note = {
            'itemType': 'note',
            'note': note_content,
            'parentItem': parent_item_key
        }
        return self.zot.create_items([note])

    def upload_attachment(self, parent_item_key, file_path, filename=None, content_type='application/pdf'):
        # Upload a file as a child attachment to an existing item
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        filename = filename or os.path.basename(file_path)
        # pyzotero provides a convenience method:
        with open(file_path, 'rb') as fh:
            return self.zot.attachment_simple_upload(parent_item_key, fh, filename)

    def delete_item(self, item_key):
        return self.zot.delete_item(item_key)

    def list_groups(self):
        return self.zot.groups()

    def list_collections(self):
        return self.zot.collections()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--user', help='userID')
    p.add_argument('--group', help='groupID')
    p.add_argument('--group-mode', action='store_true')
    args = p.parse_args()
    # quick smoke test (no destructive ops)
    client = ZoteroClient(user_id=args.user, group_id=args.group, is_group=args.group_mode)
    print('Groups:', client.list_groups())
