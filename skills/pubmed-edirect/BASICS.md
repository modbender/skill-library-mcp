# Basic EDirect Usage

## Core Command Overview

EDirect consists of several commands that work together through Unix pipes:

| Command | Purpose | Common Use |
|---------|---------|------------|
| `esearch` | Search databases | `esearch -db pubmed -query "cancer"` |
| `efetch` | Retrieve records | `efetch -format abstract` |
| `elink` | Find related records | `elink -related` |
| `efilter` | Filter results | `efilter -mindate 2020` |
| `xtract` | Extract data from XML | `xtract -pattern PubmedArticle -element Title` |
| `einfo` | Database information | `einfo -db pubmed` |

## Basic Search Workflow

### 1. Simple Search and Retrieve

```bash
# Search and get abstracts
esearch -db pubmed -query "alzheimer disease" | efetch -format abstract
```

### 2. Search with Results Limit

```bash
# Get first 10 results
esearch -db pubmed -query "diabetes" -retmax 10 | efetch -format abstract
```

### 3. Search in Specific Field

```bash
# Search in title/abstract only
esearch -db pubmed -query "CRISPR [TIAB]" | efetch -format medline
```

## Fetching Records

### By Search Results

```bash
# Standard pipeline
esearch -db pubmed -query "machine learning" | efetch -format xml
```

### By Direct PMIDs

```bash
# Single PMID
efetch -db pubmed -id 1234567 -format abstract

# Multiple PMIDs
efetch -db pubmed -id 1234567,2345678,3456789 -format medline

# From a file
cat pmids.txt | efetch -db pubmed -format abstract
```

### Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `abstract` | Human-readable abstract | Reading articles |
| `medline` | MEDLINE format | Reference managers |
| `xml` | Structured XML | Data extraction |
| `uid` | PMIDs only | Getting IDs |
| `docsum` | Document summary | Quick overview |

## Linking Between Records

### Find Related Articles

```bash
# Articles related to search results
esearch -db pubmed -query "parkinson disease" | elink -related | efetch -format abstract
```

### Citation Tracking

```bash
# Articles citing a specific paper
elink -db pubmed -id 1234567 -cited | efetch -format abstract

# Articles cited by a paper
elink -db pubmed -id 1234567 -cites | efetch -format abstract
```

### Cross-Database Links

```bash
# Link PubMed articles to PMC (full text)
esearch -db pubmed -query "nature 2023" | elink -target pmc | efetch -format xml
```

## Filtering Results

### By Date

```bash
# Articles from specific period
esearch -db pubmed -query "cancer" | \
  efilter -mindate 2020 -maxdate 2023 | \
  efetch -format abstract
```

### By Publication Type

```bash
# Review articles only
esearch -db pubmed -query "immunotherapy" | \
  efilter -query "review [PTYP]" | \
  efetch -format abstract
```

### By Language

```bash
# English articles only
esearch -db pubmed -query "genomics" | \
  efilter -query "english [LANG]" | \
  efetch -format abstract
```

## Basic Data Extraction with xtract

### Extract Simple Fields

```bash
# Get titles and PMIDs
esearch -db pubmed -query "COVID-19" | \
  efetch -format xml | \
  xtract -pattern PubmedArticle -element MedlineCitation/PMID Article/ArticleTitle
```

### Extract Authors

```bash
# Get author lists
efetch -db pubmed -id 1234567 -format xml | \
  xtract -pattern PubmedArticle -block Author -sep " " -element LastName,Initials
```

### Count Results

```bash
# Count search results
esearch -db pubmed -query "vaccine" | \
  xtract -pattern Count -element Count
```

## Working with Different Databases

### PubMed (Literature)

```bash
# Standard PubMed search
esearch -db pubmed -query "your query" | efetch -format abstract
```

### PubMed Central (Full Text)

```bash
# Search full-text articles
esearch -db pmc -query "open access" | efetch -format xml
```

### Gene Database

```bash
# Search for genes
esearch -db gene -query "BRCA1 AND human" | efetch -format docsum
```

### Nucleotide Sequences

```bash
# Search nucleotide database
esearch -db nuccore -query "insulin [PROT]" | efetch -format fasta
```

## Common Query Patterns

### Boolean Operators

```bash
# AND operator
esearch -db pubmed -query "cancer AND therapy"

# OR operator  
esearch -db pubmed -query "(lung OR breast) AND cancer"

# NOT operator
esearch -db pubmed -query "cancer NOT review"
```

### Phrase Searching

```bash
# Exact phrase
esearch -db pubmed -query '"clinical trial"'

# With field qualifier
esearch -db pubmed -query '"randomized controlled trial" [TIAB]'
```

### Truncation/Wildcards

```bash
# Word stem searching
esearch -db pubmed -query "immun*"  # Finds immune, immunity, immunization, etc.
```

## Managing Output

### Save to Files

```bash
# Save abstracts to file
esearch -db pubmed -query "neuroscience" | \
  efetch -format abstract > abstracts.txt

# Save PMIDs to file
esearch -db pubmed -query "genetics" | \
  efetch -format uid > pmids.txt
```

### Format Output

```bash
# Pretty print XML
esearch -db pubmed -query "test" | \
  efetch -format xml | xmllint --format -

# Convert to CSV
esearch -db pubmed -query "test" | \
  efetch -format xml | \
  xtract -pattern PubmedArticle -tab "," -element PMID,Title | \
  sort -t, -k2 > output.csv
```

## Error Handling

### Check for Errors

```bash
# Add -log option to see details
esearch -db pubmed -query "test" -log | efetch -format abstract
```

### Handle Empty Results

```bash
# Check count first
count=$(esearch -db pubmed -query "very specific term" | \
  xtract -pattern Count -element Count)
if [ "$count" -gt 0 ]; then
  # Process results
  esearch -db pubmed -query "very specific term" | efetch -format abstract
else
  echo "No results found"
fi
```

## Performance Tips

### Use Appropriate Limits

```bash
# Don't fetch more than needed
esearch -db pubmed -query "broad topic" -retmax 50 | efetch -format abstract
```

### Add Delays for Batch Processing

```bash
# Process list with delay
while read pmid; do
  efetch -db pubmed -id "$pmid" -format abstract
  sleep 0.5  # Respect rate limits
done < pmids.txt
```

### Cache Results

```bash
# Save intermediate results
esearch -db pubmed -query "complex query" -retmax 100 > search_results.xml
cat search_results.xml | efetch -format abstract
```

## Next Steps

- See [EXAMPLES.md](EXAMPLES.md) for practical use cases
- Explore [ADVANCED.md](ADVANCED.md) for complex queries
- Refer to [REFERENCE.md](REFERENCE.md) for field qualifiers and formats