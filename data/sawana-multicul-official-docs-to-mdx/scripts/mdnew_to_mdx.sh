#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <source_url> <output_mdx_path>" >&2
  exit 1
fi

source_url="$1"
out_file="$2"
retrieved_at="$(date -u +%F)"

raw_file="$(mktemp)"
body_file="$(mktemp)"
content_file="$(mktemp)"
clean_file="$(mktemp)"
trap 'rm -f "$raw_file" "$body_file" "$content_file" "$clean_file"' EXIT

curl -sS -D - "https://markdown.new/${source_url}" > "$raw_file"

awk 'BEGIN{p=0} /^Markdown Content:/{p=1; next} p{print}' "$raw_file" > "$body_file"

src_title=""
src_description=""
if awk 'NR==1{exit ($0=="---" ? 0 : 1)}' "$body_file"; then
  src_title="$(awk 'BEGIN{inside=0} /^---$/{if(inside==0){inside=1; next}else{exit}} inside && /^title:[[:space:]]/{sub(/^title:[[:space:]]*/, ""); print; exit}' "$body_file")"
  src_description="$(awk 'BEGIN{inside=0} /^---$/{if(inside==0){inside=1; next}else{exit}} inside && /^description:[[:space:]]/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$body_file")"
fi

if [ -z "$src_title" ]; then
  src_title="Official Doc"
fi
if [ -z "$src_description" ]; then
  src_description="Converted from docs via markdown.new"
fi

awk '
BEGIN { in_fm=0 }
NR==1 && $0=="---" { in_fm=1; next }
in_fm && $0=="---" { in_fm=0; next }
in_fm { next }
{
  if ($0 ~ /^\[Skip to main content\]/) next
  if ($0 ~ /^\[\]\(https:\/\/[^)]*\)\[Docs\]\(\/home\)$/) next
  if ($0 ~ /^Copy as Markdown$/) next
  if ($0 ~ /^Copied!$/) next
  if ($0 ~ /^On this page$/) next
  if ($0 ~ /^[[:space:]]*\* \[[^]]+\]\(#[^)]+\)[[:space:]]*$/) next
  line=$0
  gsub(/\[​\]\(#[^)]+ "Direct link to [^"]+"\)/, "", line)
  print line
}
' "$body_file" > "$content_file"

awk '
{ if ($0 ~ /^[[:space:]]*$/) { blank++; if (blank <= 1) print ""; next } blank=0; print }
' "$content_file" > "$clean_file"

mkdir -p "$(dirname "$out_file")"
{
  echo "---"
  echo "title: ${src_title}"
  echo "description: ${src_description}"
  echo "sourceUrl: ${source_url}"
  echo "retrievedAt: ${retrieved_at}"
  echo "---"
  echo
  cat "$clean_file"
} > "$out_file"

echo "Wrote ${out_file}"
