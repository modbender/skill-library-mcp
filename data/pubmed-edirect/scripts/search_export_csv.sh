#!/bin/bash
# search_export_csv.sh
# Search PubMed and export results to CSV

set -e

QUERY="$1"
MAX_RESULTS="${2:-100}"
OUTPUT_FILE="${3:-search_results.csv}"

if [ -z "$QUERY" ]; then
    echo "Error: Search query required"
    echo "Usage: $0 \"search query\" [max_results] [output_file]"
    echo "Example: $0 \"CRISPR [TIAB]\" 50 crispr_results.csv"
    exit 1
fi

echo "Searching PubMed for: $QUERY"
echo "Max results: $MAX_RESULTS"
echo "Output file: $OUTPUT_FILE"

# First, get the total count
echo -n "Getting result count... "
total=$(esearch -db pubmed -query "$QUERY" | \
    xtract -pattern Count -element Count)
echo "$total results found"

if [ "$total" -eq 0 ]; then
    echo "No results found for query: $QUERY"
    exit 0
fi

# Determine how many to fetch
to_fetch=$(( total < MAX_RESULTS ? total : MAX_RESULTS ))
echo "Fetching $to_fetch results..."

# Create CSV header
echo "pmid,year,month,title,journal,first_author,has_abstract" > "$OUTPUT_FILE"

# Fetch and process results
esearch -db pubmed -query "$QUERY" -retmax "$to_fetch" | \
    efetch -format xml | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID \
        -block PubDate -sep "-" -element Year,Month \
        -element Article/ArticleTitle \
        -element Journal/Title \
        -block Author -position first -sep " " -element LastName,Initials \
        -if Abstract -exists -lbl "YES" -else -lbl "NO" | \
    awk '
    BEGIN {FS="\t"; OFS=","}
    {
        # Escape quotes in titles
        gsub(/"/, "\"\"", $4)
        gsub(/"/, "\"\"", $5)
        
        # Print CSV row
        print "\"" $1 "\",\"" $2 "\",\"" $3 "\",\"" $4 "\",\"" $5 "\",\"" $6 "\",\"" $7 "\""
    }' >> "$OUTPUT_FILE"

# Count lines in output (excluding header)
result_count=$(($(wc -l < "$OUTPUT_FILE") - 1))

echo ""
echo "=== Export Complete ==="
echo "Query: $QUERY"
echo "Total available: $total"
echo "Exported: $result_count"
echo "File: $OUTPUT_FILE"

# Show sample of data
if [ "$result_count" -gt 0 ]; then
    echo ""
    echo "=== Sample of exported data ==="
    head -5 "$OUTPUT_FILE" | column -t -s, | head -6
fi

# Generate summary statistics
if [ "$result_count" -gt 1 ]; then
    echo ""
    echo "=== Summary Statistics ==="
    
    # Year distribution
    echo "Year distribution:"
    tail -n +2 "$OUTPUT_FILE" | cut -d, -f2 | sed 's/"//g' | \
        sort | uniq -c | sort -rn | head -10 | \
        while read count year; do
            printf "  %-4s: %3d papers\n" "$year" "$count"
        done
    
    # Journals
    echo ""
    echo "Top journals:"
    tail -n +2 "$OUTPUT_FILE" | cut -d, -f5 | sed 's/"//g' | \
        sort | uniq -c | sort -rn | head -5 | \
        while read count journal; do
            printf "  %-40s: %3d papers\n" "$journal" "$count"
        done
fi