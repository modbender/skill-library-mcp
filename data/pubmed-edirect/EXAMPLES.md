# EDirect Practical Examples

## Literature Review Examples

### 1. Basic Literature Search

```bash
# Search for articles on a topic and get abstracts
esearch -db pubmed -query "CRISPR gene editing" | \
  efetch -format abstract | head -500
```

### 2. Recent Review Articles

```bash
# Find recent review articles on a topic
esearch -db pubmed -query "cancer immunotherapy" | \
  efilter -mindate 2022 -query "review [PTYP]" | \
  efetch -format abstract | head -200
```

### 3. Author Publication List

```bash
# Get publications by a specific author
esearch -db pubmed -query "Zhang Y [AUTH]" | \
  efetch -format medline | grep -A2 -B2 "TI\|AB" | head -100
```

## Data Extraction Examples

### 4. Extract Titles and PMIDs to CSV

```bash
# Create CSV of search results
esearch -db pubmed -query "machine learning healthcare" -retmax 50 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -tab "," -element MedlineCitation/PMID Article/ArticleTitle | \
  awk 'BEGIN {print "pmid,title"} {print}' > ml_healthcare.csv
```

### 5. Get Author Information

```bash
# Extract all authors from specific papers
for pmid in 1234567 2345678 3456789; do
  echo "=== PMID: $pmid ==="
  efetch -db pubmed -id "$pmid" -format xml | \
    xtract -pattern PubmedArticle \
      -block Author \
      -sep ", " -element LastName,Initials
  echo
done
```

### 6. Extract Publication Dates

```bash
# Analyze publication timeline
esearch -db pubmed -query "COVID-19 vaccine" -retmax 100 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -block PubDate \
    -sep "-" -element Year,Month | \
  sort | uniq -c | sort -rn
```

## Cross-Database Examples

### 7. Link Papers to Genes

```bash
# Find genes mentioned in Alzheimer's research
esearch -db pubmed -query "Alzheimer disease" -retmax 50 | \
  elink -target gene | \
  efilter -organism human | \
  efetch -format docsum | \
  xtract -pattern DocumentSummary -element Id Name Description | head -20
```

### 8. Find Full-Text Articles

```bash
# Get PMC IDs for open access articles
esearch -db pubmed -query "nature 2023 open access" | \
  elink -target pmc | \
  efetch -format uid | \
  while read pmcid; do
    echo "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC${pmcid}/"
  done
```

### 9. Protein Sequences from Literature

```bash
# Find protein sequences studied in papers
esearch -db pubmed -query "insulin receptor" | \
  elink -target protein | \
  efilter -organism human | \
  efetch -format fasta | head -1000
```

## Analysis Examples

### 10. Publication Trend Analysis

```bash
# Count publications per year
for year in {2010..2023}; do
  count=$(esearch -db pubmed -query "artificial intelligence" | \
    efilter -mindate "$year" -maxdate "$year" | \
    xtract -pattern Count -element Count)
  echo "$year: $count publications"
  sleep 1
done
```

### 11. Journal Analysis

```bash
# Most common journals in search results
esearch -db pubmed -query "genomics" -retmax 500 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -element Journal/Title | \
  sort | uniq -c | sort -rn | head -10
```

### 12. Collaboration Network

```bash
# Extract authors and find collaborations
esearch -db pubmed -query "single cell RNA sequencing" -retmax 100 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -block Author \
    -sep " " -element LastName,Initials | \
  sort | uniq -c | sort -rn | head -20
```

## Batch Processing Examples

### 13. Download Abstracts for PMID List

```bash
# Process file of PMIDs
cat pmids.txt | \
  while read pmid; do
    echo "=== PMID: $pmid ===" >> abstracts.txt
    efetch -db pubmed -id "$pmid" -format abstract >> abstracts.txt
    echo "" >> abstracts.txt
    sleep 0.5
  done
```

### 14. Bulk Export to RIS Format

```bash
# Export for reference manager
esearch -db pubmed -query "your search" -retmax 100 | \
  efetch -format medline > references.ris
```

### 15. Parallel Processing of Queries

```bash
# Search multiple terms in parallel
search_terms=("cancer" "diabetes" "alzheimer" "cardiovascular")
for term in "${search_terms[@]}"; do
  (
    esearch -db pubmed -query "$term" -retmax 50 | \
      efetch -format xml > "${term}_results.xml"
    echo "Completed: $term"
  ) &
done
wait
```

## Real-World Research Scenarios

### 16. Systematic Review Helper

```bash
#!/bin/bash
# systematic_review.sh - Aid in systematic review

QUERY="$1"
OUTPUT_DIR="systematic_review_$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# Get total count
total=$(esearch -db pubmed -query "$QUERY" | \
  xtract -pattern Count -element Count)
echo "Total results: $total"

# Fetch in batches
for offset in $(seq 0 100 $total); do
  esearch -db pubmed -query "$QUERY" -retstart $offset -retmax 100 | \
    efetch -format xml > "$OUTPUT_DIR/batch_${offset}.xml"
  echo "Fetched batch starting at $offset"
  sleep 2
done

# Extract key information
cat "$OUTPUT_DIR"/*.xml | \
  xtract -pattern PubmedArticle \
    -element MedlineCitation/PMID \
    -block PubDate -sep "-" -element Year,Month \
    -element Article/ArticleTitle \
    -block Abstract -element AbstractText | \
  awk 'BEGIN {FS="\t"; OFS=","} {print $1,$2,$3,$4,$5}' > \
  "$OUTPUT_DIR/summary.csv"
```

### 17. Literature Alert System

```bash
#!/bin/bash
# literature_alert.sh - Check for new publications

LAST_CHECK="2024-01-01"
QUERY="CRISPR therapeutics"

# Check for new papers since last check
new_count=$(esearch -db pubmed -query "$QUERY" | \
  efilter -mindate "$LAST_CHECK" | \
  xtract -pattern Count -element Count)

if [ "$new_count" -gt 0 ]; then
  echo "Found $new_count new publications!"
  esearch -db pubmed -query "$QUERY" | \
    efilter -mindate "$LAST_CHECK" | \
    efetch -format abstract | head -500
else
  echo "No new publications found."
fi
```

### 18. Grant Proposal References

```bash
# Gather references for specific methods
methods=("RNA-seq" "ChIP-seq" "ATAC-seq" "single-cell RNA-seq")
for method in "${methods[@]}"; do
  echo "=== $method ===" >> methods_references.txt
  esearch -db pubmed -query "$method [TIAB] AND 2023 [PDAT]" -retmax 10 | \
    efetch -format medline | \
    grep -E "^(TI|AB|PMID|SO):" >> methods_references.txt
  echo "" >> methods_references.txt
  sleep 1
done
```

## Educational Examples

### 19. Teaching PubMed Search Syntax

```bash
# Demonstrate field qualifiers
echo "=== Different search types ==="
echo "1. Title only:"
esearch -db pubmed -query "cancer [TITL]" -retmax 3 | efetch -format uid
sleep 1

echo "2. Title/Abstract:"
esearch -db pubmed -query "cancer [TIAB]" -retmax 3 | efetch -format uid
sleep 1

echo "3. MeSH terms:"
esearch -db pubmed -query "neoplasms [MESH]" -retmax 3 | efetch -format uid
```

### 20. Compare Search Strategies

```bash
# Compare different search approaches
strategies=(
  '"lung cancer"'
  'lung AND cancer'
  'lung cancer [TIAB]'
  '((lung OR pulmonary) AND (cancer OR carcinoma)) [TIAB]'
)

for strategy in "${strategies[@]}"; do
  count=$(esearch -db pubmed -query "$strategy" | \
    xtract -pattern Count -element Count)
  printf "%-50s %8d results\n" "$strategy" "$count"
  sleep 1
done
```

## Integration Examples

### 21. Combine with Zotero

```bash
# Export to CSV for Zotero import
esearch -db pubmed -query "your research topic" -retmax 200 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -element MedlineCitation/PMID \
    -element Article/ArticleTitle \
    -block Author -position first -sep " " -element LastName,Initials \
    -element Journal/Title \
    -block PubDate -sep "/" -element Year,Month | \
  awk 'BEGIN {FS="\t"; print "PMID,Title,First Author,Journal,Year"} 
       {print $1","$2","$3","$4","$5}' > zotero_import.csv
```

### 22. Create Reading List

```bash
# Generate HTML reading list
echo "<html><body><h1>Literature Reading List</h1>" > reading_list.html

esearch -db pubmed -query "important topic" -retmax 20 | \
  efetch -format xml | \
  while read -r line; do
    if [[ "$line" =~ "<ArticleTitle>" ]]; then
      title=$(echo "$line" | sed 's/<[^>]*>//g')
      echo "<h2>$title</h2>" >> reading_list.html
    elif [[ "$line" =~ "<AbstractText>" ]]; then
      abstract=$(echo "$line" | sed 's/<[^>]*>//g')
      echo "<p>$abstract</p><hr>" >> reading_list.html
    fi
  done

echo "</body></html>" >> reading_list.html
```

### 23. Monitor Competitor Publications

```bash
#!/bin/bash
# monitor_competitors.sh

COMPANIES=("Moderna" "BioNTech" "Pfizer" "AstraZeneca")
DAYS_BACK=7

for company in "${COMPANIES[@]}"; do
  echo "=== $company publications (last $DAYS_BACK days) ==="
  esearch -db pubmed -query "$company [AFFL]" | \
    efilter -days "$DAYS_BACK" | \
    efetch -format abstract | head -300
  echo ""
  sleep 2
done
```

## Quick Reference Examples

### 24. One-Liners for Common Tasks

```bash
# Count papers by year
seq 2010 2023 | xargs -I {} bash -c 'echo -n "{}: "; esearch -db pubmed -query "cancer" | efilter -mindate {} -maxdate {} | xtract -pattern Count -element Count; sleep 0.5'

# Get PMIDs from search
esearch -db pubmed -query "your query" | efetch -format uid > pmids.txt

# Download abstracts in parallel
cat pmids.txt | xargs -P 5 -I {} bash -c 'efetch -db pubmed -id {} -format abstract > {}.txt; sleep 0.3'

# Create author frequency list
cat *.xml | xtract -pattern PubmedArticle -block Author -sep " " -element LastName,Initials | sort | uniq -c | sort -rn
```

### 25. Quality Control Checks

```bash
# Check for retracted articles
esearch -db pubmed -query "retracted publication [PTYP]" | \
  efilter -mindate 2022 | \
  efetch -format abstract | grep -i "retract" | head -10

# Verify data completeness
esearch -db pubmed -query "your query" -retmax 10 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -element MedlineCitation/PMID \
    -if Abstract -exists -lbl "Has abstract" -else -lbl "No abstract"
```

## Tips for Using These Examples

1. **Modify queries** to match your research interests
2. **Adjust retmax values** based on your needs
3. **Add sleep commands** when processing large batches
4. **Save intermediate results** for debugging
5. **Combine examples** to create custom workflows
6. **Test with small samples** before full runs
7. **Check rate limits** and add API keys if needed
8. **Document your modifications** for reproducibility