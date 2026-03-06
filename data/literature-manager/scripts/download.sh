#!/usr/bin/env bash
# Download a paper PDF by DOI or URL, trying multiple sources.
# Usage: download.sh <DOI_or_URL> <output_dir/> [filename]
# Exit 0 on success, 1 on failure (needs manual download).

set -euo pipefail

INPUT="$1"
OUTDIR="${2:-.}"
FILENAME="${3:-}"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

mkdir -p "$OUTDIR"

# Determine if input is DOI or URL
if [[ "$INPUT" =~ ^10\. ]]; then
  DOI="$INPUT"
  URL=""
elif [[ "$INPUT" =~ doi\.org/(10\.[^[:space:]]+) ]]; then
  DOI="${BASH_REMATCH[1]}"
  URL="$INPUT"
else
  DOI=""
  URL="$INPUT"
fi

# Generate filename from DOI if not provided
if [[ -z "$FILENAME" && -n "$DOI" ]]; then
  FILENAME="$(echo "$DOI" | sed 's|/|_|g; s|\.|-|g').pdf"
elif [[ -z "$FILENAME" ]]; then
  FILENAME="paper_$(date +%s).pdf"
fi

OUTPATH="$OUTDIR/$FILENAME"

try_download() {
  local url="$1"
  local label="$2"
  curl -sL --max-time 30 --connect-timeout 10 -H "User-Agent: $UA" -o "$OUTPATH" "$url" 2>/dev/null
  if file -b "$OUTPATH" | grep -q "PDF"; then
    echo "✅ Downloaded from $label: $OUTPATH"
    return 0
  fi
  rm -f "$OUTPATH"
  return 1
}

# Strategy 1: Direct URL if provided
if [[ -n "$URL" ]]; then
  try_download "$URL" "direct URL" && exit 0
fi

# Strategy 2: Publisher PDF patterns (for DOI)
if [[ -n "$DOI" ]]; then
  # Nature family
  if [[ "$DOI" =~ ^10\.1038/ ]]; then
    ARTICLE_ID="${DOI#10.1038/}"
    try_download "https://www.nature.com/articles/${ARTICLE_ID}.pdf" "Nature" && exit 0
  fi

  # eLife
  if [[ "$DOI" =~ ^10\.7554/eLife\. ]]; then
    ARTICLE_ID="${DOI#10.7554/eLife.}"
    try_download "https://elifesciences.org/articles/${ARTICLE_ID}.pdf" "eLife" && exit 0
  fi

  # bioRxiv / medRxiv
  if [[ "$DOI" =~ ^10\.1101/ ]]; then
    try_download "https://www.biorxiv.org/content/${DOI}v1.full.pdf" "bioRxiv" && exit 0
  fi

  # PNAS
  if [[ "$DOI" =~ ^10\.1073/pnas ]]; then
    try_download "https://www.pnas.org/doi/pdf/${DOI}" "PNAS" && exit 0
  fi

  # Frontiers
  if [[ "$DOI" =~ ^10\.3389/ ]]; then
    try_download "https://www.frontiersin.org/articles/${DOI}/pdf" "Frontiers" && exit 0
  fi

  # Springer / BMC
  if [[ "$DOI" =~ ^10\.(1007|1186)/ ]]; then
    try_download "https://link.springer.com/content/pdf/${DOI}.pdf" "Springer" && exit 0
  fi
fi

# Strategy 3: EuropePMC via DOI lookup
if [[ -n "$DOI" ]]; then
  PMC_ID=$(curl -sL --max-time 15 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=${DOI}&retmode=xml" 2>/dev/null | grep -o '<Id>[^<]*' | head -1 | sed 's/<Id>//')
  if [[ -n "$PMC_ID" ]]; then
    try_download "https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC${PMC_ID}&blobtype=pdf" "EuropePMC" && exit 0
  fi
fi

# Strategy 4: arXiv (search by DOI)
if [[ -n "$DOI" ]]; then
  ARXIV_ID=$(curl -sL --max-time 15 "http://export.arxiv.org/api/query?search_query=doi:${DOI}&max_results=1" 2>/dev/null | grep -o 'arxiv\.org/abs/[^<"]*' | head -1 | sed 's|arxiv.org/abs/||')
  if [[ -n "$ARXIV_ID" ]]; then
    try_download "https://arxiv.org/pdf/${ARXIV_ID}" "arXiv" && exit 0
  fi
fi

# Strategy 5: Sci-Hub
# Legal note: Sci-Hub may violate publisher terms or laws in some jurisdictions.
# Use only if you understand and accept the legal implications.
if [[ -n "$DOI" ]]; then
  try_download "https://sci-hub.box/${DOI}" "Sci-Hub" && exit 0
fi

echo "❌ Could not download: $INPUT"
echo "   Manual download needed. DOI: ${DOI:-N/A}"
exit 1
