# Advanced EDirect Techniques

## Complex XML Extraction with xtract

### Nested Exploration

```bash
# Extract authors with their affiliations
efetch -db pubmed -id 1234567 -format xml | \
  xtract -pattern PubmedArticle \
    -block Author \
      -element LastName,Initials \
      -block AffiliationInfo -element Affiliation
```

### Conditional Extraction

```bash
# Extract only corresponding authors
efetch -db pubmed -id 1234567 -format xml | \
  xtract -pattern PubmedArticle \
    -block Author \
    -if "@ValidYN" -equals "Y" \
    -element LastName,Initials
```

### Variable Usage in xtract

```bash
# Store and use variables
efetch -db pubmed -id 1234567 -format xml | \
  xtract -pattern PubmedArticle \
    -YEAR Year \
    -block Author \
    -element "&YEAR" LastName,Initials
```

## Multi-Step Query Pipelines

### Complex Cross-Database Queries

```bash
# Find genes associated with diseases in literature
esearch -db pubmed -query "alzheimer disease" | \
  elink -target gene | \
  efilter -organism human | \
  efetch -format docsum | \
  xtract -pattern DocumentSummary -element Id Name Description
```

### Chaining Multiple Filters

```bash
# Highly specific search
esearch -db pubmed -query "cancer" | \
  efilter -mindate 2020 -maxdate 2023 | \
  efilter -query "review [PTYP]" | \
  efilter -query "english [LANG]" | \
  efilter -query "humans [MESH]" | \
  efetch -format abstract
```

## Advanced Search Techniques

### Using Search History

```bash
# Save search to history server
esearch -db pubmed -query "complex query" -log > search_history.log

# Use WebEnv from history
esearch -db pubmed -query "additional terms" -webenv "$WEBENV" -query_key "$QUERY_KEY"
```

### Combining Multiple Searches

```bash
# Intersection of two searches
search1=$(esearch -db pubmed -query "term1" | efetch -format uid)
search2=$(esearch -db pubmed -query "term2" | efetch -format uid)

# Find common PMIDs
comm -12 <(echo "$search1" | sort) <(echo "$search2" | sort) | \
  efetch -db pubmed -format abstract
```

### Proximity Searching

```bash
# Words near each other (using PubMed syntax)
esearch -db pubmed -query '"machine learning"~10' | efetch -format abstract
```

## Data Transformation Pipelines

### Convert XML to Structured Formats

```bash
# Create CSV with multiple fields
esearch -db pubmed -query "genomics" -retmax 100 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -element MedlineCitation/PMID \
    -block PubDate -sep "-" -element Year,Month,Day \
    -block Author -position first -sep " " -element LastName,Initials \
    -element Article/ArticleTitle \
    -block Abstract -element AbstractText | \
  awk 'BEGIN {FS="\t"; OFS=","} {print $1,$2,$3,$4,$5,$6}' > output.csv
```

### Extract and Analyze Citation Networks

```bash
# Build citation graph for a paper
elink -db pubmed -id 1234567 -cited | \
  efetch -format uid | \
  while read cited_pmid; do
    echo "1234567 -> $cited_pmid"
    # Get papers citing the cited paper
    elink -db pubmed -id "$cited_pmid" -cited | \
      efetch -format uid | \
      while read cited2; do
        echo "$cited_pmid -> $cited2"
      done
    sleep 0.5
  done > citation_network.tsv
```

## Performance Optimization

### Parallel Processing

```bash
# Process multiple PMIDs in parallel
cat pmids.txt | \
  xargs -P 4 -I {} bash -c '
    efetch -db pubmed -id {} -format abstract > abstract_{}.txt
    sleep 0.3
  '
```

### Caching Strategies

```bash
# Cache XML for repeated queries
if [ ! -f "cached_query.xml" ]; then
  esearch -db pubmed -query "expensive query" | \
    efetch -format xml > cached_query.xml
fi

# Use cached data
cat cached_query.xml | \
  xtract -pattern PubmedArticle -element Title
```

### Batch Processing with Error Recovery

```bash
# Process with retry logic
process_pmid() {
  local pmid=$1
  local attempt=1
  local max_attempts=3
  
  while [ $attempt -le $max_attempts ]; do
    if efetch -db pubmed -id "$pmid" -format abstract > "abstract_${pmid}.txt" 2>/dev/null; then
      echo "Processed $pmid"
      return 0
    else
      echo "Attempt $attempt failed for $pmid"
      sleep $((attempt * 2))
      attempt=$((attempt + 1))
    fi
  done
  echo "Failed to process $pmid after $max_attempts attempts" >&2
  return 1
}

export -f process_pmid
cat pmids.txt | xargs -P 2 -I {} bash -c 'process_pmid "$@"' _ {}
```

## Advanced xtract Features

### Pattern Matching with Regular Expressions

```bash
# Extract emails from affiliations
efetch -db pubmed -id 1234567 -format xml | \
  xtract -pattern PubmedArticle \
    -block AffiliationInfo \
    -if Affiliation -matches "@" \
    -element Affiliation
```

### Statistical Operations

```bash
# Calculate average authors per paper
esearch -db pubmed -query "your topic" -retmax 50 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -NUM Author \
    -block Author -last "" | \
  awk '{sum += $1; count++} END {print "Average authors:", sum/count}'
```

### Hierarchical Data Extraction

```bash
# Extract MeSH terms with qualifiers
efetch -db pubmed -id 1234567 -format xml | \
  xtract -pattern PubmedArticle \
    -block MeshHeading \
      -element DescriptorName \
      -subset QualifierName -element QualifierName
```

## Database-Specific Advanced Queries

### Gene Expression Data

```bash
# Link genes to GEO datasets
esearch -db gene -query "TP53 AND human" | \
  elink -target gds | \
  efetch -format docsum | \
  xtract -pattern DocumentSummary -element Id Title Summary
```

### Protein Structure Links

```bash
# Find protein structures for a gene
esearch -db gene -query "INSR AND human" | \
  elink -target structure | \
  efetch -format docsum | \
  xtract -pattern DocumentSummary -element Id PdbAcc Title
```

### Clinical Trial Connections

```bash
# Link publications to clinical trials
esearch -db pubmed -query "clinical trial phase III" | \
  elink -target clinvar | \
  efetch -format docsum | \
  xtract -pattern DocumentSummary -element Id ClinicalSignificance Name
```

## Scripting with EDirect

### Create Reusable Functions

```bash
#!/bin/bash
# pmid_to_authors.sh - Extract authors from PMID

PMID_TO_AUTHORS() {
  local pmid=$1
  efetch -db pubmed -id "$pmid" -format xml | \
    xtract -pattern PubmedArticle \
      -block Author \
      -sep ", " -element LastName,Initials
}

# Usage
PMID_TO_AUTHORS 1234567
```

### Build Custom Analysis Pipelines

```bash
#!/bin/bash
# literature_trends.sh - Analyze publication trends

analyze_trends() {
  local query="$1"
  local start_year="$2"
  local end_year="$3"
  
  for year in $(seq "$start_year" "$end_year"); do
    count=$(esearch -db pubmed -query "$query" | \
      efilter -mindate "$year" -maxdate "$year" | \
      xtract -pattern Count -element Count)
    echo "$year,$count"
    sleep 1
  done
}

analyze_trends "artificial intelligence" 2010 2023 > ai_trends.csv
```

## Integration with Other Tools

### Combine with jq for JSON Processing

```bash
# Convert to JSON and process
esearch -db pubmed -query "test" | \
  efetch -format xml | \
  xml2json | \
  jq '.PubmedArticleSet.PubmedArticle[].MedlineCitation.PMID' 
```

### Use with Python/R for Analysis

```bash
# Export data for Python analysis
esearch -db pubmed -query "cancer biomarkers" -retmax 100 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -element PMID Year Title | \
  awk 'BEGIN {FS="\t"; print "pmid,year,title"} {print $1","$2",\""$3"\""}' > \
  data_for_analysis.csv

# Then in Python:
# import pandas as pd
# df = pd.read_csv('data_for_analysis.csv')
```

### Database Integration

```bash
# Load results into SQLite
esearch -db pubmed -query "your query" -retmax 1000 | \
  efetch -format xml | \
  xtract -pattern PubmedArticle \
    -element PMID Year Title | \
  awk 'BEGIN {FS="\t"; print "BEGIN TRANSACTION;"} 
       {print "INSERT INTO publications VALUES (\"" $1 "\", \"" $2 "\", \"" $3 "\");"} 
       END {print "COMMIT;"}' | \
  sqlite3 literature.db
```

## Monitoring and Debugging

### Query Performance Analysis

```bash
# Time your queries
time esearch -db pubmed -query "complex query" | efetch -format abstract > /dev/null
```

### Debug XML Structure

```bash
# See XML structure of a record
efetch -db pubmed -id 1234567 -format xml | \
  xtract -outline | head -20
```

### Validate Queries

```bash
# Test query without fetching
esearch -db pubmed -query "test query" -retmax 0 | \
  xtract -pattern Count -element Count
```

## Best Practices for Production Use

1. **Always use an API key** for higher rate limits
2. **Implement caching** for repetitive queries
3. **Add error handling** and retry logic
4. **Respect rate limits** with appropriate delays
5. **Log your queries** for reproducibility
6. **Validate results** before processing
7. **Use version control** for analysis scripts
8. **Document your pipelines** for future reference

## Next Steps

- Apply these techniques to your specific research questions
- Combine EDirect with other bioinformatics tools
- Automate repetitive literature review tasks
- Build custom dashboards for monitoring publication trends