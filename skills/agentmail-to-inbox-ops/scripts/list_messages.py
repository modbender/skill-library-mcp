from common import (
    build_parser,
    emit,
    get_allowed_senders,
    get_client_and_inbox,
    log_action,
    sender_matches,
)


def main() -> None:
    p = build_parser("List inbox messages")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--from-email", default=None, help="Explicit sender filter")
    p.add_argument("--label", action="append", default=[])
    p.add_argument("--ascending", action="store_true")
    p.add_argument("--include-read", action="store_true", help="Include read emails (default is unread only)")
    p.add_argument("--preview-chars", type=int, default=160)
    args = p.parse_args()

    client, inbox = get_client_and_inbox(args)
    allowed_senders = [args.from_email.lower()] if args.from_email else get_allowed_senders()
    labels = list(args.label or [])
    if not args.include_read and "unread" not in labels:
        labels.append("unread")

    log_action("list_messages.start", inbox=inbox, limit=args.limit, allowed_senders=allowed_senders, labels=labels, ascending=args.ascending, include_read=args.include_read)
    resp = client.inboxes.messages.list(
        inbox_id=inbox,
        limit=args.limit,
        labels=labels or None,
        ascending=True if args.ascending else None,
    )

    out = []
    for m in (resp.messages or []):
        sender = str(getattr(m, "from_", ""))
        if allowed_senders and not sender_matches(sender, allowed_senders):
            continue
        preview = getattr(m, "preview", None)
        if preview and args.preview_chars > 0:
            preview = preview.strip().replace("\n", " ")[: args.preview_chars]

        out.append(
            {
                "message_id": m.message_id,
                "subject": getattr(m, "subject", None),
                "from": sender,
                "timestamp": getattr(m, "timestamp", None),
                "labels": getattr(m, "labels", []),
                "preview": preview,
            }
        )

    log_action("list_messages.done", inbox=inbox, count=len(out))
    emit({"inbox": inbox, "count": len(out), "messages": out})


if __name__ == "__main__":
    main()
