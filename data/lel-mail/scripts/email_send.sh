#!/usr/bin/env bash
# ~/.openclaw/workspace/skills/lel-mail/scripts/email_send.sh
#Usage: email_send.sh --recipient <recipient> --subject <subject> --body <body> [--cc ...] [--bcc ...]
#CC/BCC are comma-separated lists. Use empty values to skip.

set -euo pipefail

usage() {
echo "Usage: email_send.sh <sender> <recipient> [subject] [body] [--cc ...] [--bcc ...]"
echo " or: email_send.sh --sender <sender> --recipient <recipient> --subject <subject> --body <body> [--cc ...] [--bcc ...]"
echo "CC/BCC are comma-separated lists. Use empty values to skip."
}

# Defaults
SENDER=""
RECIPIENT=""
SUBJECT=""
BODY=""
CC=""
BCC=""

# First, check if user used named flags
if [[ "$1" == --sender || "$1" == --sender=* || "$1" == --recipient-* || "$1" == --recipient || "$1" == --subject-* || "$1" == --subject || "$1" == --body-* || "$1" == --body ]]; then
# We'll parse all flags below; ensure we start with no leftovers
SENDER=""
RECIPIENT=""
SUBJECT=""
BODY=""
shift 0
fi

# If flags are used, parse them (support both --field value and --field=value)
while [[ $# -gt 0 ]]; do
case "$1" in
--sender)
shift
SENDER="${1:-}"; shift
;;
--sender=*)
SENDER="${1#*=}"; shift
;;
--recipient)
shift
RECIPIENT="${1:-}"; shift
;;
--recipient=*)
RECIPIENT="${1#*=}"; shift
;;
--subject)
shift
SUBJECT="${1:-}"; shift
;;
--subject=*)
SUBJECT="${1#*=}"; shift
;;
--body)
shift
BODY="${1:-}"; shift
;;
--body=*)
BODY="${1#*=}"; shift
;;
--cc)
shift
CC="${CC:+$CC,}${1:-}"; shift
;;
--cc=*)
CC="${1#*=}"; shift
;;
--bcc)
shift
BCC="${BCC:+$BCC,}${1:-}"; shift
;;
--bcc=*)
BCC="${1#*=}"; shift
;;
--help|-h)
usage
exit 0
;;
*)
# If no flags were used and we haven't consumed the 3 positional args, try to read as positional
if [[ -z "$RECIPIENT" ]]; then
RECIPIENT="$1"; shift
elif [[ -z "$SUBJECT" ]]; then
SUBJECT="$1"; shift
elif [[ -z "$BODY" ]]; then
BODY="$1"; shift
else
echo "Unknown arg: $1"
usage
exit 2
fi
;;
esac
done

# Fallback: if no named flags used, try to read the first three positionals
if [[ -z "$RECIPIENT" && -n "${1-}" ]]; then
# assume original invocation was positional
RECIPIENT="$1"; shift
SUBJECT="${1:-}"; shift 2>/dev/null || true
BODY="${1:-}"
fi

# Final guard
if [[ -z "$SENDER" ]]; then
echo "Sender is required."
usage
exit 2
fi
if [[ -z "$RECIPIENT" ]]; then
echo "Recipient is required."
usage
exit 2
fi

# Normalize CC/BCC to empty strings if not set
CC="${CC:-}"
BCC="${BCC:-}"

export SENDER RECIPIENT SUBJECT BODY CC BCC

python3 - <<PY
import json
import os
from datetime import datetime

SENDER = "${SENDER}"
RECIPIENT = "${RECIPIENT}"
SUBJECT   = "${SUBJECT}"
BODY      = "${BODY}"
CC_RAW    = "${CC}"
BCC_RAW   = "${BCC}"

QUEUE_PATH = os.path.expanduser("~/.config/lel-mail/queue.json")

def parse_recipients(raw: str):
    """
    Turn a comma-separated string into a clean list of emails.
    Empty or whitespace-only strings result in [].
    """
    if not raw:
        return []
    return [addr.strip() for addr in raw.split(",") if addr.strip()]


def load_queue(path: str):
    """
    Load existing queue file or initialize a new one
    if it doesn't exist or is malformed.
    """
    if not os.path.exists(path):
        return {"last_sent": None, "remaining": []}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Basic shape validation
        if not isinstance(data, dict):
            raise ValueError("queue root must be an object")
        if "last_sent" not in data:
            data["last_sent"] = None
        if "remaining" not in data or not isinstance(data["remaining"], list):
            data["remaining"] = []
        return data
    except Exception:
        # If corrupt, start fresh but *don't* crash the enqueue
        return {"last_sent": None, "remaining": []}


def save_queue(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp_path, path)


def main():
    cc_list = parse_recipients(CC_RAW)
    bcc_list = parse_recipients(BCC_RAW)

    queue = load_queue(QUEUE_PATH)

    new_entry = {
        "SENDER": SENDER,
        "RECIPIENT": RECIPIENT,
        "SUBJECT": SUBJECT,
        "BODY": BODY,
        "CC": cc_list,
        "BCC": bcc_list,
    }

    queue["remaining"].append(new_entry)

    # Do NOT change last_sent here; that’s for the sender process
    save_queue(QUEUE_PATH, queue)


if __name__ == "__main__":
    main()
PY

echo "Email scheduled successfully to $RECIPIENT"
