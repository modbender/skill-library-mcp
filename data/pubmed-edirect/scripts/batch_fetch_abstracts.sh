#!/bin/bash
# batch_fetch_abstracts.sh
# Fetch abstracts for a list of PMIDs

set -e  # Exit on error

INPUT_FILE="${1:-pmids.txt}"
OUTPUT_DIR="${2:-abstracts}"
DELAY="${3:-0.5}"  # Delay between requests in seconds

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found"
    echo "Usage: $0 [input_file] [output_dir] [delay_seconds]"
    echo "Default: pmids.txt abstracts 0.5"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Count total PMIDs
total=$(wc -l < "$INPUT_FILE")
echo "Processing $total PMIDs from $INPUT_FILE"
echo "Output directory: $OUTPUT_DIR"
echo "Delay between requests: ${DELAY}s"

# Process each PMID
count=0
success=0
fail=0

while read pmid; do
    # Skip empty lines
    [ -z "$pmid" ] && continue
    
    count=$((count + 1))
    output_file="${OUTPUT_DIR}/${pmid}.txt"
    
    echo -n "[$count/$total] PMID $pmid: "
    
    # Fetch abstract
    if efetch -db pubmed -id "$pmid" -format abstract > "$output_file" 2>/dev/null; then
        # Check if we got actual content (not empty or error)
        if [ -s "$output_file" ] && ! grep -q "Error" "$output_file" 2>/dev/null; then
            echo "✓"
            success=$((success + 1))
        else
            echo "✗ (empty/error)"
            rm -f "$output_file"
            fail=$((fail + 1))
        fi
    else
        echo "✗ (fetch failed)"
        fail=$((fail + 1))
    fi
    
    # Delay to respect rate limits
    if [ "$count" -lt "$total" ]; then
        sleep "$DELAY"
    fi
    
done < "$INPUT_FILE"

# Summary
echo ""
echo "=== Summary ==="
echo "Total processed: $count"
echo "Successful: $success"
echo "Failed: $fail"
echo "Output in: $OUTPUT_DIR/"

# Create combined file
if [ "$success" -gt 0 ]; then
    cat "$OUTPUT_DIR"/*.txt > "${OUTPUT_DIR}_combined.txt" 2>/dev/null || true
    echo "Combined file: ${OUTPUT_DIR}_combined.txt"
fi