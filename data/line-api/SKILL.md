---
name: line-client
description: LINE messaging integration via Chrome extension gateway. Send/read LINE messages, manage contacts, groups, profile, and reactions. Authenticate with QR code login. Provides HMAC-signed API access through the Chrome extension gateway (line-chrome-gw.line-apps.com).
---

# LINE Client Skill

Full LINE messaging client via the Chrome extension gateway JSON API.

## Repo & Files

- **Repo:** `/data/workspace/line-client` ([github.com/2manslkh/line-api](https://github.com/2manslkh/line-api))
- **Main client:** `src/chrome_client.py` → `LineChromeClient`
- **QR login:** `src/auth/qr_login.py` → `QRLogin`
- **HMAC signer:** `src/hmac/signer.js` (Node.js, auto-starts on port 18944)
- **Token storage:** `~/.line-client/tokens.json`
- **Certificate cache:** `~/.line-client/sqr_cert`
- **WASM files:** `lstm.wasm` + `lstmSandbox.js` (required, in repo root)

## Quick Start

```python
import json
from pathlib import Path
from src.chrome_client import LineChromeClient

tokens = json.loads((Path.home() / ".line-client" / "tokens.json").read_text())
client = LineChromeClient(auth_token=tokens["auth_token"])

# Send a message
client.send_message("U...", "Hello!")

# Get profile
profile = client.get_profile()
```

Tokens expire in ~7 days. If expired (`APIError(10051)`), re-run QR login.

## QR Login (Authentication)

QR login requires user interaction: scan QR on phone + enter PIN.

```python
from src.hmac import HmacSigner
from src.auth.qr_login import QRLogin
import qrcode

signer = HmacSigner(mode="server")
login = QRLogin(signer)
result = login.run(
    on_qr=lambda url: send_qr_image_to_user(qrcode.make(url)),
    on_pin=lambda pin: send_pin_to_user_IMMEDIATELY(pin),  # TIME SENSITIVE!
    on_status=lambda msg: print(msg),
)
# result.auth_token, result.mid, result.refresh_token
```

**Critical:** The PIN must reach the user within ~60 seconds. Send it the instant `on_pin` fires.

### QR Login State Machine
1. `createSession` → session ID
2. `createQrCode` → callback URL (append `?secret={curve25519_pubkey}&e2eeVersion=1`)
3. `checkQrCodeVerified` — poll until scan (uses `X-Line-Session-ID`, no `origin` header)
4. **`verifyCertificate`** — MUST be called even if it fails (required state transition!)
5. `createPinCode` → 6-digit PIN (skip if cert verified in step 4)
6. `checkPinCodeVerified` — poll until user enters PIN
7. `qrCodeLoginV2` → JWT token + certificate + refresh token

### Server-Side Login Script
```bash
python scripts/qr_login_server.py /tmp/qr.png
```
Emits JSON events on stdout: `{"event": "qr", "path": "...", "url": "..."}`, `{"event": "pin", "pin": "123456"}`, `{"event": "done", "mid": "U..."}`.

## All API Methods

### Contacts & Friends

| Method | Args | Description |
|--------|------|-------------|
| `get_profile()` | — | Get your own profile (displayName, mid, statusMessage, etc.) |
| `get_contact(mid)` | mid: str | Get a single contact's profile |
| `get_contacts(mids)` | mids: list[str] | Get multiple contacts |
| `get_all_contact_ids()` | — | List all friend MIDs |
| `find_contact_by_userid(userid)` | userid: str | Search by LINE ID |
| `find_and_add_contact_by_mid(mid)` | mid: str | Add friend by MID |
| `find_contacts_by_phone(phones)` | phones: list[str] | Search by phone numbers |
| `add_friend_by_mid(mid)` | mid: str | Add friend (RelationService) |
| `get_blocked_contact_ids()` | — | List blocked MIDs |
| `get_blocked_recommendation_ids()` | — | List blocked recommendations |
| `block_contact(mid)` | mid: str | Block a contact |
| `unblock_contact(mid)` | mid: str | Unblock a contact |
| `block_recommendation(mid)` | mid: str | Block a friend suggestion |
| `update_contact_setting(mid, flag, value)` | mid, flag: int, value: str | Update contact setting (e.g. mute) |
| `get_favorite_mids()` | — | List favorited contact MIDs |
| `get_recommendation_ids()` | — | List friend suggestions |

### Messages

| Method | Args | Description |
|--------|------|-------------|
| `send_message(to, text, ...)` | to: str, text: str, reply_to: str (opt) | Send a text message. Supports replies via `reply_to=message_id` |
| `unsend_message(message_id)` | message_id: str | Unsend/delete a sent message |
| `get_recent_messages(chat_id, count=50)` | chat_id: str | Get latest messages in a chat |
| `get_previous_messages(chat_id, end_seq, count=50)` | chat_id, end_seq: int | Paginated history (older messages) |
| `get_messages_by_ids(message_ids)` | message_ids: list[str] | Fetch specific messages |
| `get_message_boxes(count=50)` | — | Get chat list with last message (inbox view) |
| `get_message_boxes_by_ids(chat_ids)` | chat_ids: list[str] | Get specific chats with last message |
| `get_message_read_range(chat_ids)` | chat_ids: list[str] | Get read receipt info |
| `send_chat_checked(chat_id, last_message_id)` | chat_id, last_message_id: str | Mark messages as read |
| `send_chat_removed(chat_id, last_message_id)` | chat_id, last_message_id: str | Remove chat from inbox |
| `send_postback(to, postback_data)` | to, postback_data: str | Send postback (bot interactions) |

### Chats & Groups

| Method | Args | Description |
|--------|------|-------------|
| `get_chats(chat_ids, with_members=True, with_invitees=True)` | chat_ids: list[str] | Get chat/group details |
| `get_all_chat_mids()` | — | List all chat MIDs (groups + invites) |
| `create_chat(name, target_mids)` | name: str, target_mids: list[str] | Create a new group chat |
| `accept_chat_invitation(chat_id)` | chat_id: str | Accept group invite |
| `reject_chat_invitation(chat_id)` | chat_id: str | Reject group invite |
| `invite_into_chat(chat_id, mids)` | chat_id: str, mids: list[str] | Invite users to group |
| `cancel_chat_invitation(chat_id, mids)` | chat_id: str, mids: list[str] | Cancel pending invites |
| `delete_other_from_chat(chat_id, mids)` | chat_id: str, mids: list[str] | Kick members from group |
| `leave_chat(chat_id)` | chat_id: str | Leave a group chat |
| `update_chat(chat_id, updates)` | chat_id: str, updates: dict | Update group name/settings |
| `set_chat_hidden_status(chat_id, hidden)` | chat_id: str, hidden: bool | Archive/unarchive a chat |
| `get_rooms(room_ids)` | room_ids: list[str] | Get legacy room info |
| `invite_into_room(room_id, mids)` | room_id: str, mids: list[str] | Invite to legacy room |
| `leave_room(room_id)` | room_id: str | Leave legacy room |

### Reactions

| Method | Args | Description |
|--------|------|-------------|
| `react(message_id, reaction_type)` | message_id: str, type: int | React to a message. Types: 2=like, 3=love, 4=laugh, 5=surprised, 6=sad, 7=angry |
| `cancel_reaction(message_id)` | message_id: str | Remove your reaction |

### Profile & Settings

| Method | Args | Description |
|--------|------|-------------|
| `update_profile_attributes(attr, value, meta={})` | attr: int, value: str | Update profile. Attrs: 2=DISPLAY_NAME, 16=STATUS_MESSAGE, 4=PICTURE_STATUS |
| `update_status_message(message)` | message: str | Shortcut: update status message |
| `update_display_name(name)` | name: str | Shortcut: update display name |
| `get_settings()` | — | Get all account settings |
| `get_settings_attributes(attr_bitset)` | attr_bitset: int | Get specific settings |
| `update_settings_attributes(attr_bitset, settings)` | attr_bitset: int, settings: dict | Update settings |

### Polling & Events

| Method | Args | Description |
|--------|------|-------------|
| `get_last_op_revision()` | — | Get latest operation revision number |
| `fetch_ops(count=50)` | — | Fetch pending operations (may long-poll) |
| `poll()` | — | Generator yielding operations as they arrive |
| `on_message(handler)` | handler: Callable(msg, client) | Start polling thread, calls handler on new messages. Op types: 26=SEND_MESSAGE, 27=RECEIVE_MESSAGE |
| `stop()` | — | Stop the polling thread |

### Other Services

| Method | Args | Description |
|--------|------|-------------|
| `get_server_time()` | — | Get LINE server timestamp |
| `get_configurations()` | — | Get server configurations |
| `get_rsa_key_info()` | — | Get RSA key for auth |
| `issue_channel_token(channel_id)` | channel_id: str | Issue channel token (LINE Login/LIFF) |
| `get_buddy_detail(mid)` | mid: str | Get official account info |
| `report_abuse(mid, category=0, reason="")` | mid: str | Report a user |
| `add_friend_by_mid(mid)` | mid: str | Add friend (RelationService) |
| `logout()` | — | Logout and invalidate token |

## MID Format

LINE identifies entities by MID:
- `U...` or `u...` → User (toType=0)
- `C...` or `c...` → Group chat (toType=2)
- `R...` or `r...` → Room (toType=1)

The client auto-detects `toType` from the MID prefix when sending messages.

## HMAC Signing

All API calls require `X-Hmac` header. The WASM signer handles this automatically:
- Derives key from version "3.7.1" + access token via proprietary KDF (in lstm.wasm)
- Signs `path + body` → base64 → `X-Hmac`
- Server mode: ~13ms/sign (Node.js HTTP server on port 18944, auto-started)
- Subprocess mode: ~2s/sign (fallback)

## Error Handling

```python
from src.chrome_client import APIError

try:
    client.send_message(mid, "test")
except APIError as e:
    print(e.code, e.api_message)
    # 10051 = session expired / invalid
    # 10052 = HTTP error from backend
    # 10102 = invalid arguments
```

## Architecture

```
User's Phone (LINE app)
    ↕ (scan QR / enter PIN)
LINE Servers (line-chrome-gw.line-apps.com)
    ↕ (JSON REST + X-Hmac signing)
LineChromeClient (this repo)
    ↕ (WASM HMAC via Node.js signer)
lstm.wasm + lstmSandbox.js
```

The Chrome Gateway translates JSON ↔ Thrift internally. We never deal with Thrift binary — everything is clean JSON.
