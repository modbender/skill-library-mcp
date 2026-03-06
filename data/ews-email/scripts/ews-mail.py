#!/usr/bin/env python3
"""EWS Mail CLI - himalaya-compatible interface over Exchange Web Services."""
import sys, json, argparse, os
from exchangelib import (
    Credentials, Account, Configuration, DELEGATE,
    Message, Mailbox, FileAttachment
)
import urllib3
urllib3.disable_warnings()

SERVER = os.environ.get("EWS_SERVER", "")
EMAIL = os.environ.get("EWS_EMAIL", "")
PASSWORD = os.environ.get("EWS_PASSWORD", "")

if not all([SERVER, EMAIL, PASSWORD]):
    print("Error: EWS_SERVER, EWS_EMAIL, EWS_PASSWORD environment variables must be set.", file=sys.stderr)
    sys.exit(1)
CACHE_FILE = os.path.expanduser("~/.openclaw/.ews-mail-cache.json")

def get_account():
    creds = Credentials(username=EMAIL, password=PASSWORD)
    config = Configuration(server=SERVER, credentials=creds)
    return Account(primary_smtp_address=EMAIL, config=config,
                   autodiscover=False, access_type=DELEGATE)

def get_folder(account, folder_name):
    name = (folder_name or "inbox").lower()
    mapping = {
        "inbox": account.inbox, "sent": account.sent,
        "drafts": account.drafts, "trash": account.trash, "junk": account.junk,
    }
    if name in mapping:
        return mapping[name]
    for f in account.root.walk():
        if f.name and f.name.lower() == name:
            return f
    return account.inbox

def save_cache(items_map):
    with open(CACHE_FILE, "w") as f:
        json.dump(items_map, f, ensure_ascii=False)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def fmt_date(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""

def fmt_addr(mailbox):
    if not mailbox: return ""
    if mailbox.name: return f"{mailbox.name} <{mailbox.email_address}>"
    return mailbox.email_address or ""

def find_message(account, msg_id):
    """Find message by Exchange ID using account.fetch()."""
    from exchangelib import ItemId
    try:
        items = list(account.fetch(ids=[ItemId(id=msg_id)]))
        if items and items[0] is not None:
            return items[0]
    except Exception:
        pass
    return None

# --- commands ---

def cmd_folder_list(args):
    account = get_account()
    for f in account.root.walk():
        if f.name:
            total = getattr(f, 'total_count', '?') or '?'
            print(f"  {f.name} ({total})")

def cmd_envelope_list(args):
    account = get_account()
    folder = get_folder(account, args.folder)
    page, size = max(1, args.page), args.page_size
    offset = (page - 1) * size
    qs = folder.all().order_by('-datetime_received')

    if args.query:
        i = 0
        tokens = args.query
        while i < len(tokens):
            t = tokens[i].lower()
            if t in ("from", "subject", "to") and i + 1 < len(tokens):
                val = tokens[i + 1]
                if t == "from": qs = qs.filter(sender__email_address__contains=val)
                elif t == "subject": qs = qs.filter(subject__contains=val)
                elif t == "to": qs = qs.filter(to_recipients__contains=val)
                i += 2
            else:
                qs = qs.filter(subject__contains=tokens[i])
                i += 1

    items = list(qs[offset:offset + size])
    cache = {}
    print(f"Page {page} (showing {len(items)} messages)")
    print("-" * 100)
    for idx, item in enumerate(items):
        num = offset + idx + 1
        cache[str(num)] = item.id
        flag = "●" if not item.is_read else " "
        sender = fmt_addr(item.sender)[:30]
        subj = (item.subject or "(no subject)")[:60]
        print(f"{num:>4} {flag} {fmt_date(item.datetime_received)}  {sender:<30}  {subj}")
    save_cache(cache)
    if not items:
        print("No messages found.")

def cmd_message_read(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache. Run 'envelope-list' first.", file=sys.stderr)
        sys.exit(1)

    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found on server.", file=sys.stderr)
        sys.exit(1)

    if not item.is_read:
        item.is_read = True
        item.save(update_fields=['is_read'])

    print(f"From: {fmt_addr(item.sender)}")
    print(f"To: {', '.join(fmt_addr(r) for r in (item.to_recipients or []))}")
    if item.cc_recipients:
        print(f"Cc: {', '.join(fmt_addr(r) for r in item.cc_recipients)}")
    print(f"Date: {fmt_date(item.datetime_received)}")
    print(f"Subject: {item.subject or '(no subject)'}")
    attachments = [a for a in (item.attachments or []) if isinstance(a, FileAttachment)]
    if attachments:
        print(f"Attachments: {', '.join(a.name or 'unnamed' for a in attachments)}")
    print("-" * 60)
    body = item.text_body or ""
    if not body and item.body:
        body = str(item.body)
    if len(body) > 8000:
        body = body[:8000] + f"\n\n... [truncated, total {len(body)} chars]"
    print(body)

def cmd_message_send(args):
    account = get_account()
    to_list = [Mailbox(email_address=r.strip()) for r in args.to.split(',')]
    cc_list = [Mailbox(email_address=r.strip()) for r in args.cc.split(',')] if args.cc else None
    msg = Message(account=account, subject=args.subject, body=args.body,
                  to_recipients=to_list, cc_recipients=cc_list)
    msg.send()
    print(f"Sent to {args.to}: {args.subject}")

def cmd_message_reply(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache.", file=sys.stderr); sys.exit(1)
    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found.", file=sys.stderr); sys.exit(1)
    reply = item.reply_all() if args.all else item.reply()
    reply.body = args.body + "\n\n" + str(reply.body or "")
    reply.send()
    print(f"Reply sent to {fmt_addr(item.sender)}")

def cmd_message_forward(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache.", file=sys.stderr); sys.exit(1)
    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found.", file=sys.stderr); sys.exit(1)
    fwd = item.forward()
    fwd.to_recipients = [Mailbox(email_address=r.strip()) for r in args.to.split(',')]
    fwd.body = (args.body or "") + "\n\n" + str(fwd.body or "")
    fwd.send()
    print(f"Forwarded to {args.to}: {item.subject}")

def cmd_message_move(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache.", file=sys.stderr); sys.exit(1)
    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found.", file=sys.stderr); sys.exit(1)
    dest = get_folder(account, args.folder)
    item.move(dest)
    print(f"Moved message {args.id} to {args.folder}")

def cmd_message_delete(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache.", file=sys.stderr); sys.exit(1)
    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found.", file=sys.stderr); sys.exit(1)
    item.move_to_trash()
    print(f"Deleted message {args.id}")

def cmd_flag(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache.", file=sys.stderr); sys.exit(1)
    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found.", file=sys.stderr); sys.exit(1)
    flag = args.flag.lower()
    if flag in ("seen", "read"):
        item.is_read = (args.action == "add")
        item.save(update_fields=['is_read'])
    print(f"Flag '{flag}' {'added' if args.action == 'add' else 'removed'} on message {args.id}")

def cmd_attachment_download(args):
    account = get_account()
    cache = load_cache()
    msg_id = cache.get(str(args.id))
    if not msg_id:
        print(f"Message {args.id} not found in cache.", file=sys.stderr); sys.exit(1)
    item = find_message(account, msg_id)
    if not item:
        print(f"Message {args.id} not found.", file=sys.stderr); sys.exit(1)
    dest_dir = args.dir or os.getcwd()
    os.makedirs(dest_dir, exist_ok=True)
    count = 0
    for att in (item.attachments or []):
        if isinstance(att, FileAttachment) and att.content:
            path = os.path.join(dest_dir, att.name or f"attachment_{count}")
            with open(path, "wb") as f:
                f.write(att.content)
            print(f"Saved: {path}")
            count += 1
    if count == 0:
        print("No attachments found.")

def main():
    p = argparse.ArgumentParser(description="EWS Mail CLI")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("folder-list")

    el = sub.add_parser("envelope-list")
    el.add_argument("--folder", "-f", default="inbox")
    el.add_argument("--page", type=int, default=1)
    el.add_argument("--page-size", type=int, default=10)
    el.add_argument("query", nargs="*")

    mr = sub.add_parser("message-read")
    mr.add_argument("id")

    ms = sub.add_parser("message-send")
    ms.add_argument("--to", required=True)
    ms.add_argument("--cc", default=None)
    ms.add_argument("--subject", required=True)
    ms.add_argument("--body", required=True)

    mre = sub.add_parser("message-reply")
    mre.add_argument("id")
    mre.add_argument("--body", required=True)
    mre.add_argument("--all", action="store_true")

    mf = sub.add_parser("message-forward")
    mf.add_argument("id")
    mf.add_argument("--to", required=True)
    mf.add_argument("--body", default="")

    mm = sub.add_parser("message-move")
    mm.add_argument("id")
    mm.add_argument("folder")

    md = sub.add_parser("message-delete")
    md.add_argument("id")

    fa = sub.add_parser("flag-add")
    fa.add_argument("id")
    fa.add_argument("--flag", required=True)

    fr = sub.add_parser("flag-remove")
    fr.add_argument("id")
    fr.add_argument("--flag", required=True)

    ad = sub.add_parser("attachment-download")
    ad.add_argument("id")
    ad.add_argument("--dir", default=None)

    args = p.parse_args()
    cmds = {
        "folder-list": cmd_folder_list, "envelope-list": cmd_envelope_list,
        "message-read": cmd_message_read, "message-send": cmd_message_send,
        "message-reply": cmd_message_reply, "message-forward": cmd_message_forward,
        "message-move": cmd_message_move, "message-delete": cmd_message_delete,
        "flag-add": lambda a: (setattr(a, 'action', 'add'), cmd_flag(a)),
        "flag-remove": lambda a: (setattr(a, 'action', 'remove'), cmd_flag(a)),
        "attachment-download": cmd_attachment_download,
    }
    fn = cmds.get(args.cmd)
    if fn: fn(args)
    else: p.print_help()

if __name__ == "__main__":
    main()
