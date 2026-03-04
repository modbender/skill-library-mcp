#!/usr/bin/env bash
set -euo pipefail

NAME=""
URL=""
AUTH="No"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --url) URL="$2"; shift 2 ;;
    --auth) AUTH="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$NAME" || -z "$URL" ]]; then
  echo "Usage: gen_usage.sh --name <API_NAME> --url <API_URL> [--auth No|apiKey|OAuth]"
  exit 2
fi

echo "# $NAME 使用示例"
echo
echo "## curl"
if [[ "$AUTH" == "No" ]]; then
  cat <<EOF
curl -s "$URL"
EOF
else
  cat <<EOF
curl -s "$URL" \\
  -H "Authorization: Bearer <YOUR_TOKEN>"
EOF
fi

echo
echo "## Python"
if [[ "$AUTH" == "No" ]]; then
  cat <<EOF
import requests
r = requests.get("$URL", timeout=20)
print(r.status_code)
print(r.text[:500])
EOF
else
  cat <<EOF
import requests
headers = {"Authorization": "Bearer <YOUR_TOKEN>"}
r = requests.get("$URL", headers=headers, timeout=20)
print(r.status_code)
print(r.text[:500])
EOF
fi

echo
echo "## JavaScript (fetch)"
if [[ "$AUTH" == "No" ]]; then
  cat <<EOF
const res = await fetch("$URL");
const text = await res.text();
console.log(res.status, text.slice(0, 500));
EOF
else
  cat <<EOF
const res = await fetch("$URL", {
  headers: { Authorization: "Bearer <YOUR_TOKEN>" }
});
const text = await res.text();
console.log(res.status, text.slice(0, 500));
EOF
fi
