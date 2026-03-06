from common import (
    build_parser,
    emit,
    get_allowed_senders,
    get_client_and_inbox,
    log_action,
    sender_matches,
)


def main() -> None:
    p = build_parser("Reply to filtered messages")
    p.add_argument("--from-email", default=None, help="Override allowed sender filter")
    p.add_argument("--text", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--dedupe-label", default="AUTO_REPLIED")
    p.add_argument("--include-read", action="store_true", help="Also scan read emails")
    p.add_argument("--keep-unread", action="store_true", help="Do not mark replied emails as read")
    args = p.parse_args()

    client, inbox = get_client_and_inbox(args)
    allowed_senders = [args.from_email.lower()] if args.from_email else get_allowed_senders()
    if not allowed_senders:
        raise SystemExit("No sender allowlist set. Use --from-email or AGENTMAIL_ALLOWED_SENDERS")

    labels = None if args.include_read else ["unread"]
    log_action("reply_messages.start", inbox=inbox, allowed_senders=allowed_senders, limit=args.limit, dry_run=args.dry_run, dedupe_label=args.dedupe_label, include_read=args.include_read, keep_unread=args.keep_unread)
    resp = client.inboxes.messages.list(inbox_id=inbox, limit=args.limit, labels=labels)

    replied = []
    for m in (resp.messages or []):
        sender = str(getattr(m, "from_", ""))
        labels = set(getattr(m, "labels", []) or [])
        if not sender_matches(sender, allowed_senders):
            continue
        if args.dedupe_label in labels:
            continue

        add_labels = [args.dedupe_label]
        remove_labels = []
        if not args.keep_unread:
            add_labels.append("read")
            remove_labels.append("unread")

        if not args.dry_run:
            client.inboxes.messages.reply(
                inbox_id=inbox,
                message_id=m.message_id,
                text=args.text,
                reply_all=False,
            )
            client.inboxes.messages.update(
                inbox_id=inbox,
                message_id=m.message_id,
                add_labels=add_labels,
                remove_labels=remove_labels,
            )

        replied.append({
            "message_id": m.message_id,
            "from": sender,
            "dry_run": args.dry_run,
            "mark_read": not args.keep_unread,
        })

    log_action("reply_messages.done", inbox=inbox, replied_count=len(replied), dry_run=args.dry_run, mark_read=not args.keep_unread)
    emit({"inbox": inbox, "replied_count": len(replied), "items": replied})


if __name__ == "__main__":
    main()
