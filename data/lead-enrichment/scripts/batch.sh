#!/bin/bash
# lead-enrichment/scripts/batch.sh — Process multiple leads from a file

set -euo pipefail

# --- Argument Parsing ---
INPUT_FILE=""
OUTPUT_DIR=""
PARALLEL=1
ENRICH_SCRIPT="$(dirname "$0")/enrich.sh"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --input) INPUT_FILE="$2"; shift ;;
        --output) OUTPUT_DIR="$2"; shift ;;
        --parallel) PARALLEL="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# --- Input Validation ---
if [[ -z "$INPUT_FILE" || -z "$OUTPUT_DIR" ]]; then
  echo "Error: --input and --output arguments are required."
  echo "Usage: ./batch.sh --input leads.csv --output enriched/ --parallel 3"
  exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# --- Main Logic ---
echo "📦 Starting batch enrichment from '$INPUT_FILE'"
echo "   Outputting to '$OUTPUT_DIR' with $PARALLEL parallel worker(s)."

process_lead() {
    local line="$1"
    local output_dir="$2"
    local script_path="$3"

    # Simple CSV parsing (name,company)
    name=$(echo "$line" | cut -d',' -f1 | tr -d '"')
    company=$(echo "$line" | cut -d',' -f2 | tr -d '"')

    if [[ -z "$name" || -z "$company" ]]; then
        echo "Skipping invalid line: $line"
        return
    fi
    
    # Sanitize for filename
    name_slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '-')
    company_slug=$(echo "$company" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '-')
    output_filename="${output_dir}/${name_slug}-${company_slug}.json"

    echo "   -> Processing: $name, $company"
    "$script_path" --name "$name" --company "$company" --output "$output_filename" > /dev/null
    echo "   <- Finished: $name, $company"
}

export -f process_lead
export OUTPUT_DIR
export ENRICH_SCRIPT

# Read the file and pipe to xargs for parallel processing
# Skips header line with tail -n +2
tail -n +2 "$INPUT_FILE" | xargs -I {} -P "$PARALLEL" bash -c 'process_lead "{}" "$OUTPUT_DIR" "$ENRICH_SCRIPT"'

echo "✅ Batch enrichment complete."
echo "   Enriched profiles are in '$OUTPUT_DIR'"
