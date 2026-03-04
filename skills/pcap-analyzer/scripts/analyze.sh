#!/usr/bin/env bash
set -euo pipefail

PCAP=""
FOCUS=""

usage() {
  echo "Usage: analyze.sh /full/path/to/file.pcap|pcapng [--focus-host IP]" >&2
  exit 2
}

PCAP="${1:-}"; shift || true
[[ -z "$PCAP" ]] && usage
[[ ! -f "$PCAP" ]] && { echo "PCAP not found: $PCAP" >&2; exit 2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --focus-host) FOCUS="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -n "$FOCUS" ]]; then
  echo "[*] Focus host: $FOCUS"
fi

# Preferred: your existing summarizer (best output)
if [[ -x /home/tom/openclaw-tools/pcap_summary.sh ]]; then
  /home/tom/openclaw-tools/pcap_summary.sh "$PCAP" "$FOCUS"
  exit 0
fi

# Fallback: basic tshark summaries
echo "== Protocol hierarchy =="
tshark -r "$PCAP" -q -z io,phs || true

echo -e "\n== Top IPv4 endpoints =="
tshark -r "$PCAP" -q -z endpoints,ip 2>/dev/null | head -n 60 || true

echo -e "\n== Top TCP conversations =="
tshark -r "$PCAP" -q -z conv,tcp 2>/dev/null | head -n 60 || true

echo -e "\n== Top UDP conversations =="
tshark -r "$PCAP" -q -z conv,udp 2>/dev/null | head -n 60 || true

