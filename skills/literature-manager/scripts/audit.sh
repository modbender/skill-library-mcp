#!/usr/bin/env bash
# Full audit of a references/ directory.
# Usage: audit.sh <references_dir/>
# Checks: PDF validity, MD existence, index.json integrity, cross-file consistency.

set -uo pipefail

REFDIR="${1:-.}"
ERRORS=0
WARNINGS=0
TOTAL_PDF=0
TOTAL_MD=0

echo "=== Literature Audit: $REFDIR ==="
echo ""

# 0. Check dependencies
for cmd in pdftotext python3 curl file; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Missing dependency: $cmd"
    ERRORS=$((ERRORS + 1))
  fi
done

# 1. Count and verify PDFs
echo "--- PDF Verification ---"
while IFS= read -r -d '' pdf; do
  TOTAL_PDF=$((TOTAL_PDF + 1))
  basename_pdf=$(basename "$pdf")
  
  if ! file -b "$pdf" | grep -q "PDF"; then
    echo "❌ Not valid PDF: $pdf"
    ERRORS=$((ERRORS + 1))
  else
    # Check title extractable
    title=$(pdftotext "$pdf" - 2>/dev/null | head -10 | grep -v '^$' | head -1)
    if [[ -z "$title" ]]; then
      echo "⚠️  No title extracted: $basename_pdf"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done < <(find "$REFDIR" -path "*/papers/*.pdf" -print0 2>/dev/null)
echo "PDFs found: $TOTAL_PDF"
echo ""

# 2. Count and verify Markdowns
echo "--- Markdown Verification ---"
while IFS= read -r -d '' md; do
  TOTAL_MD=$((TOTAL_MD + 1))
  if [[ ! -s "$md" ]]; then
    echo "❌ Empty markdown: $md"
    ERRORS=$((ERRORS + 1))
  fi
done < <(find "$REFDIR" -path "*/markdown/*.md" -print0 2>/dev/null)
echo "Markdowns found: $TOTAL_MD"
echo ""

# 3. Cross-check: every PDF has a markdown
echo "--- Cross-file Consistency ---"
while IFS= read -r -d '' pdf; do
  basename_noext=$(basename "$pdf" .pdf)
  category_dir=$(dirname "$(dirname "$pdf")")
  expected_md="$category_dir/markdown/${basename_noext}.md"
  if [[ ! -f "$expected_md" ]]; then
    echo "❌ Missing markdown for: $(basename "$pdf")"
    ERRORS=$((ERRORS + 1))
  fi
done < <(find "$REFDIR" -path "*/papers/*.pdf" -print0 2>/dev/null)

# 4. Check index.json
INDEX="$REFDIR/index.json"
if [[ -f "$INDEX" ]]; then
  echo ""
  echo "--- index.json Verification ---"
  if python3 -c "import json; json.load(open('$INDEX'))" 2>/dev/null; then
    PAPER_COUNT=$(python3 -c "import json; d=json.load(open('$INDEX')); print(len(d.get('papers', d if isinstance(d, list) else [])))")
    echo "index.json entries: $PAPER_COUNT"
    
    if [[ "$PAPER_COUNT" -ne "$TOTAL_PDF" ]]; then
      echo "⚠️  index.json ($PAPER_COUNT) != PDF count ($TOTAL_PDF)"
      WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check for missing files referenced in index
    MISSING=$(python3 -c "
import json, os
d = json.load(open('$INDEX'))
papers = d.get('papers', d if isinstance(d, list) else [])
for p in papers:
    for key in ['pdf_path', 'markdown_path']:
        path = p.get(key, '')
        full = os.path.join('$REFDIR', path)
        if path and not os.path.exists(full):
            print(f'Missing: {path}')
" 2>/dev/null)
    if [[ -n "$MISSING" ]]; then
      echo "❌ Files referenced in index.json but missing:"
      echo "$MISSING"
      ERRORS=$((ERRORS + $(echo "$MISSING" | grep -c .)))
    else
      echo "✅ All index.json paths verified"
    fi
    
    # Check for duplicate IDs
    DUPES=$(python3 -c "
import json
d = json.load(open('$INDEX'))
papers = d.get('papers', d if isinstance(d, list) else [])
ids = [p.get('id','') for p in papers]
seen = set()
for i in ids:
    if i in seen: print(f'Duplicate ID: {i}')
    seen.add(i)
" 2>/dev/null)
    if [[ -n "$DUPES" ]]; then
      echo "❌ $DUPES"
      ERRORS=$((ERRORS + $(echo "$DUPES" | grep -c .)))
    else
      echo "✅ No duplicate IDs"
    fi
  else
    echo "❌ index.json is not valid JSON"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "⚠️  No index.json found"
  WARNINGS=$((WARNINGS + 1))
fi

# 5. Check README.md
README="$REFDIR/README.md"
if [[ -f "$README" ]]; then
  README_SIZE=$(wc -c < "$README")
  echo ""
  echo "--- README.md ---"
  echo "Size: $README_SIZE bytes"
  if [[ $README_SIZE -lt 1000 ]]; then
    echo "⚠️  README seems small"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo "⚠️  No README.md found"
  WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "=== Summary ==="
echo "PDFs: $TOTAL_PDF | Markdowns: $TOTAL_MD"
echo "Errors: $ERRORS | Warnings: $WARNINGS"
if [[ $ERRORS -eq 0 ]]; then
  echo "✅ AUDIT PASSED"
  exit 0
else
  echo "❌ AUDIT FAILED"
  exit 1
fi
