from common import build_parser, emit, get_client_and_inbox, log_action


def main() -> None:
    p = build_parser("Set message read/unread state")
    p.add_argument("message_id")
    p.add_argument("state", choices=["read", "unread"])
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    client, inbox = get_client_and_inbox(args)
    log_action("set_read_state.start", inbox=inbox, message_id=args.message_id, state=args.state, dry_run=args.dry_run)

    add_labels = ["read"] if args.state == "read" else ["unread"]
    remove_labels = ["unread"] if args.state == "read" else ["read"]

    if not args.dry_run:
        updated = client.inboxes.messages.update(
            inbox_id=inbox,
            message_id=args.message_id,
            add_labels=add_labels,
            remove_labels=remove_labels,
        )
        labels = updated.labels
    else:
        labels = None

    log_action("set_read_state.done", inbox=inbox, message_id=args.message_id, state=args.state, dry_run=args.dry_run)
    emit(
        {
            "inbox": inbox,
            "message_id": args.message_id,
            "state": args.state,
            "dry_run": args.dry_run,
            "labels_after": labels,
        }
    )


if __name__ == "__main__":
    main()
