#!/usr/bin/env python3
"""Google Keep CLI for OpenClaw - lightweight wrapper around gkeepapi."""

import argparse
import json
import os
import sys

# Resolve venv path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_SITE = os.path.join(SCRIPT_DIR, ".venv", "lib")

# Find the python version dir in .venv/lib/
if os.path.isdir(VENV_SITE):
    for d in os.listdir(VENV_SITE):
        sp = os.path.join(VENV_SITE, d, "site-packages")
        if os.path.isdir(sp):
            sys.path.insert(0, sp)
            break

import gkeepapi
import gpsoauth

# --- Config ---
CONFIG_DIR = os.environ.get("GKEEP_CONFIG_DIR", os.path.join(SCRIPT_DIR, ".config"))
TOKEN_FILE = os.path.join(CONFIG_DIR, "master_token")
STATE_FILE = os.path.join(CONFIG_DIR, "state.json")
EMAIL_FILE = os.path.join(CONFIG_DIR, "email")


def ensure_config_dir():
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)


def save_email(email):
    ensure_config_dir()
    with open(EMAIL_FILE, "w") as f:
        f.write(email)
    os.chmod(EMAIL_FILE, 0o600)


def load_email():
    if os.path.exists(EMAIL_FILE):
        with open(EMAIL_FILE) as f:
            return f.read().strip()
    return None


def save_master_token(token):
    ensure_config_dir()
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    os.chmod(TOKEN_FILE, 0o600)


def load_master_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    return None


def save_state(keep):
    ensure_config_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(keep.dump(), f)
    os.chmod(STATE_FILE, 0o600)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return None


def get_keep(sync=True):
    """Authenticate and optionally sync. Returns Keep instance."""
    email = load_email()
    token = load_master_token()
    if not email or not token:
        print("Error: Not authenticated. Run: gkeep auth <email> <oauth_token>", file=sys.stderr)
        sys.exit(1)

    keep = gkeepapi.Keep()

    # Try to restore cached state for faster startup
    state = load_state()
    if state:
        keep.authenticate(email, token, state=state)
    else:
        keep.authenticate(email, token)

    if sync:
        keep.sync()
        save_state(keep)

    return keep


def note_to_dict(note):
    """Convert a note to a serializable dict."""
    result = {
        "id": note.id,
        "title": note.title,
        "type": "list" if isinstance(note, gkeepapi.node.List) else "note",
        "color": note.color.name if note.color else None,
        "pinned": note.pinned,
        "archived": note.archived,
        "trashed": note.trashed,
        "labels": [l.name for l in note.labels.all()],
    }

    if isinstance(note, gkeepapi.node.List):
        items = []
        for item in note.items:
            items.append({
                "text": item.text,
                "checked": item.checked,
                "indented": item.indented,
            })
        result["items"] = items
        result["text"] = "\n".join(
            f"[{'x' if i.checked else ' '}] {i.text}" for i in note.items
        )
    else:
        result["text"] = note.text

    return result


def format_note(note_dict, verbose=False):
    """Format a note dict for human-readable output."""
    lines = []
    title = note_dict.get("title", "(untitled)")
    ntype = note_dict.get("type", "note")
    flags = []
    if note_dict.get("pinned"):
        flags.append("pinned")
    if note_dict.get("archived"):
        flags.append("archived")
    if note_dict.get("labels"):
        flags.append(f"labels: {', '.join(note_dict['labels'])}")

    header = f"[{ntype.upper()}] {title}"
    if flags:
        header += f"  ({', '.join(flags)})"
    lines.append(header)

    if verbose:
        lines.append(f"  ID: {note_dict['id']}")
        if note_dict.get("color") and note_dict["color"] != "White":
            lines.append(f"  Color: {note_dict['color']}")

    text = note_dict.get("text", "")
    if text:
        for line in text.split("\n"):
            lines.append(f"  {line}")

    return "\n".join(lines)


# --- Commands ---

def cmd_auth(args):
    """Exchange OAuth token for master token and store credentials."""
    email = args.email
    oauth_token = args.oauth_token
    android_id = args.android_id or "0123456789abcdef"

    print(f"Exchanging token for {email}...")
    try:
        master_response = gpsoauth.exchange_token(email, oauth_token, android_id)
        if "Token" not in master_response:
            print(f"Error: Token exchange failed. Response: {json.dumps(master_response, indent=2)}", file=sys.stderr)
            sys.exit(1)

        master_token = master_response["Token"]
        save_email(email)
        save_master_token(master_token)

        # Verify by authenticating
        keep = gkeepapi.Keep()
        keep.authenticate(email, master_token)
        keep.sync()
        save_state(keep)

        notes = list(keep.all())
        print(f"Authenticated successfully! Found {len(notes)} notes.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_auth_master(args):
    """Store a pre-obtained master token directly."""
    email = args.email
    master_token = args.master_token

    save_email(email)
    save_master_token(master_token)

    try:
        keep = gkeepapi.Keep()
        keep.authenticate(email, master_token)
        keep.sync()
        save_state(keep)
        notes = list(keep.all())
        print(f"Authenticated successfully! Found {len(notes)} notes.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """List notes."""
    keep = get_keep()

    notes = []
    for note in keep.all():
        if note.trashed and not args.trashed:
            continue
        if not args.archived and note.archived:
            continue
        if args.pinned and not note.pinned:
            continue
        if args.label:
            note_labels = [l.name.lower() for l in note.labels.all()]
            if args.label.lower() not in note_labels:
                continue
        notes.append(note)

    if args.json:
        print(json.dumps([note_to_dict(n) for n in notes], indent=2))
    else:
        if not notes:
            print("No notes found.")
            return
        for note in notes:
            print(format_note(note_to_dict(note), verbose=args.verbose))
            print()


def cmd_search(args):
    """Search notes by text."""
    keep = get_keep()
    query = args.query.lower()

    results = []
    for note in keep.all():
        if note.trashed:
            continue
        title = (note.title or "").lower()
        text = (note.text or "").lower()
        if query in title or query in text:
            results.append(note)

    if args.json:
        print(json.dumps([note_to_dict(n) for n in results], indent=2))
    else:
        if not results:
            print(f"No notes matching '{args.query}'.")
            return
        print(f"Found {len(results)} note(s) matching '{args.query}':\n")
        for note in results:
            print(format_note(note_to_dict(note), verbose=args.verbose))
            print()


def cmd_get(args):
    """Get a specific note by ID or title."""
    keep = get_keep()

    note = None
    try:
        note = keep.get(args.identifier)
    except Exception:
        pass

    if note is None:
        for n in keep.all():
            if n.title and n.title.lower() == args.identifier.lower():
                note = n
                break

    if note is None:
        print(f"Note not found: {args.identifier}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(note_to_dict(note), indent=2))
    else:
        print(format_note(note_to_dict(note), verbose=True))


def cmd_create(args):
    """Create a new note or list."""
    keep = get_keep()

    if args.list:
        note = keep.createList(args.title or "", [
            (item, False) for item in (args.items or [])
        ])
    else:
        note = keep.createNote(args.title or "", args.text or "")

    if args.pin:
        note.pinned = True
    if args.color:
        try:
            note.color = gkeepapi.node.ColorValue[args.color]
        except KeyError:
            print(f"Warning: Unknown color '{args.color}'. Valid: {', '.join(c.name for c in gkeepapi.node.ColorValue)}", file=sys.stderr)
    if args.label:
        for label_name in args.label:
            label = keep.findLabel(label_name)
            if label is None:
                label = keep.createLabel(label_name)
            note.labels.add(label)

    keep.sync()
    save_state(keep)

    if args.json:
        print(json.dumps(note_to_dict(note), indent=2))
    else:
        print(f"Created: {note.title or '(untitled)'} (ID: {note.id})")


def cmd_edit(args):
    """Edit an existing note."""
    keep = get_keep()

    note = None
    try:
        note = keep.get(args.identifier)
    except Exception:
        pass
    if note is None:
        for n in keep.all():
            if n.title and n.title.lower() == args.identifier.lower():
                note = n
                break
    if note is None:
        print(f"Note not found: {args.identifier}", file=sys.stderr)
        sys.exit(1)

    if args.title is not None:
        note.title = args.title
    if args.text is not None:
        note.text = args.text
    if args.pin is not None:
        note.pinned = args.pin
    if args.archive is not None:
        note.archived = args.archive
    if args.color:
        try:
            note.color = gkeepapi.node.ColorValue[args.color]
        except KeyError:
            print(f"Warning: Unknown color '{args.color}'.", file=sys.stderr)

    keep.sync()
    save_state(keep)

    if args.json:
        print(json.dumps(note_to_dict(note), indent=2))
    else:
        print(f"Updated: {note.title or '(untitled)'} (ID: {note.id})")


def cmd_delete(args):
    """Delete (trash) a note."""
    keep = get_keep()

    note = None
    try:
        note = keep.get(args.identifier)
    except Exception:
        pass
    if note is None:
        for n in keep.all():
            if n.title and n.title.lower() == args.identifier.lower():
                note = n
                break
    if note is None:
        print(f"Note not found: {args.identifier}", file=sys.stderr)
        sys.exit(1)

    title = note.title or "(untitled)"
    note.delete()
    keep.sync()
    save_state(keep)
    print(f"Trashed: {title}")


def cmd_labels(args):
    """List all labels."""
    keep = get_keep()
    labels = keep.labels()
    if args.json:
        print(json.dumps([{"name": l.name, "id": l.id} for l in labels], indent=2))
    else:
        if not labels:
            print("No labels.")
            return
        for l in labels:
            print(f"  {l.name}")


def cmd_dump(args):
    """Dump all notes as JSON (for backup/export)."""
    keep = get_keep()
    notes = [note_to_dict(n) for n in keep.all() if not n.trashed]
    print(json.dumps(notes, indent=2))


def cmd_check(args):
    """Check/uncheck a list item."""
    keep = get_keep()

    note = None
    try:
        note = keep.get(args.note_id)
    except Exception:
        pass
    if note is None:
        for n in keep.all():
            if n.title and n.title.lower() == args.note_id.lower():
                note = n
                break

    if note is None or not isinstance(note, gkeepapi.node.List):
        print(f"List not found: {args.note_id}", file=sys.stderr)
        sys.exit(1)

    query = args.item_text.lower()
    matched = False
    for item in note.items:
        if query in item.text.lower():
            item.checked = not args.uncheck
            matched = True
            action = "Unchecked" if args.uncheck else "Checked"
            print(f"{action}: {item.text}")
            if not args.all:
                break

    if not matched:
        print(f"No item matching '{args.item_text}' in list.", file=sys.stderr)
        sys.exit(1)

    keep.sync()
    save_state(keep)


def cmd_add_item(args):
    """Add an item to a list."""
    keep = get_keep()

    note = None
    try:
        note = keep.get(args.note_id)
    except Exception:
        pass
    if note is None:
        for n in keep.all():
            if n.title and n.title.lower() == args.note_id.lower():
                note = n
                break

    if note is None or not isinstance(note, gkeepapi.node.List):
        print(f"List not found: {args.note_id}", file=sys.stderr)
        sys.exit(1)

    for text in args.items:
        note.add(text, False)
        print(f"Added: {text}")

    keep.sync()
    save_state(keep)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        prog="gkeep",
        description="Google Keep CLI for OpenClaw"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # auth
    p_auth = subparsers.add_parser("auth", help="Authenticate with OAuth token")
    p_auth.add_argument("email", help="Google account email")
    p_auth.add_argument("oauth_token", help="OAuth token from EmbeddedSetup cookie")
    p_auth.add_argument("--android-id", default=None, help="Android device ID (default: generic)")
    p_auth.set_defaults(func=cmd_auth)

    # auth-master
    p_auth_m = subparsers.add_parser("auth-master", help="Authenticate with pre-obtained master token")
    p_auth_m.add_argument("email", help="Google account email")
    p_auth_m.add_argument("master_token", help="Master token")
    p_auth_m.set_defaults(func=cmd_auth_master)

    # list
    p_list = subparsers.add_parser("list", help="List notes")
    p_list.add_argument("--archived", action="store_true", help="Include archived")
    p_list.add_argument("--trashed", action="store_true", help="Include trashed")
    p_list.add_argument("--pinned", action="store_true", help="Only pinned")
    p_list.add_argument("--label", help="Filter by label")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.add_argument("-v", "--verbose", action="store_true", help="Show IDs and details")
    p_list.set_defaults(func=cmd_list)

    # search
    p_search = subparsers.add_parser("search", help="Search notes")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--json", action="store_true", help="JSON output")
    p_search.add_argument("-v", "--verbose", action="store_true", help="Show IDs and details")
    p_search.set_defaults(func=cmd_search)

    # get
    p_get = subparsers.add_parser("get", help="Get a note by ID or title")
    p_get.add_argument("identifier", help="Note ID or title")
    p_get.add_argument("--json", action="store_true", help="JSON output")
    p_get.set_defaults(func=cmd_get)

    # create
    p_create = subparsers.add_parser("create", help="Create a note or list")
    p_create.add_argument("--title", "-t", help="Note title")
    p_create.add_argument("--text", help="Note body text")
    p_create.add_argument("--list", action="store_true", help="Create a list instead of a note")
    p_create.add_argument("--items", nargs="+", help="List items (with --list)")
    p_create.add_argument("--pin", action="store_true", help="Pin the note")
    p_create.add_argument("--color", help="Note color")
    p_create.add_argument("--label", action="append", help="Add label (repeatable)")
    p_create.add_argument("--json", action="store_true", help="JSON output")
    p_create.set_defaults(func=cmd_create)

    # edit
    p_edit = subparsers.add_parser("edit", help="Edit a note")
    p_edit.add_argument("identifier", help="Note ID or title")
    p_edit.add_argument("--title", help="New title")
    p_edit.add_argument("--text", help="New text")
    p_edit.add_argument("--pin", type=lambda x: x.lower() == "true", help="Pin (true/false)")
    p_edit.add_argument("--archive", type=lambda x: x.lower() == "true", help="Archive (true/false)")
    p_edit.add_argument("--color", help="New color")
    p_edit.add_argument("--json", action="store_true", help="JSON output")
    p_edit.set_defaults(func=cmd_edit)

    # delete
    p_del = subparsers.add_parser("delete", help="Trash a note")
    p_del.add_argument("identifier", help="Note ID or title")
    p_del.set_defaults(func=cmd_delete)

    # labels
    p_labels = subparsers.add_parser("labels", help="List all labels")
    p_labels.add_argument("--json", action="store_true", help="JSON output")
    p_labels.set_defaults(func=cmd_labels)

    # dump
    p_dump = subparsers.add_parser("dump", help="Dump all notes as JSON")
    p_dump.set_defaults(func=cmd_dump)

    # check
    p_check = subparsers.add_parser("check", help="Check/uncheck a list item")
    p_check.add_argument("note_id", help="List note ID or title")
    p_check.add_argument("item_text", help="Item text to match")
    p_check.add_argument("--uncheck", action="store_true", help="Uncheck instead of check")
    p_check.add_argument("--all", action="store_true", help="Match all items containing text")
    p_check.set_defaults(func=cmd_check)

    # add-item
    p_add = subparsers.add_parser("add-item", help="Add items to a list")
    p_add.add_argument("note_id", help="List note ID or title")
    p_add.add_argument("items", nargs="+", help="Items to add")
    p_add.set_defaults(func=cmd_add_item)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
