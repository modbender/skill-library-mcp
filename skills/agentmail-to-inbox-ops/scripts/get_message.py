from common import build_parser, emit, get_client_and_inbox, log_action


def main() -> None:
    p = build_parser("Get full message")
    p.add_argument("message_id")
    args = p.parse_args()

    client, inbox = get_client_and_inbox(args)
    log_action("get_message.start", inbox=inbox, message_id=args.message_id)
    m = client.inboxes.messages.get(inbox_id=inbox, message_id=args.message_id)

    log_action("get_message.done", inbox=inbox, message_id=m.message_id, attachment_count=len(m.attachments or []))
    emit(
        {
            "inbox": inbox,
            "message_id": m.message_id,
            "thread_id": m.thread_id,
            "from": str(m.from_),
            "to": [str(x) for x in (m.to or [])],
            "subject": m.subject,
            "labels": m.labels,
            "timestamp": m.timestamp,
            "text": m.text,
            "preview": m.preview,
            "attachments": [
                {
                    "attachment_id": a.attachment_id,
                    "filename": a.filename,
                    "size": a.size,
                    "content_type": a.content_type,
                }
                for a in (m.attachments or [])
            ],
        }
    )


if __name__ == "__main__":
    main()
