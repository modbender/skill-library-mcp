# EDirect Quick Reference

## Command Reference

### Core Commands

| Command | Description | Basic Syntax |
|---------|-------------|--------------|
| `esearch` | Search databases | `esearch -db DATABASE -query "TERMS"` |
| `efetch` | Retrieve records | `efetch -db DATABASE -id ID -format FORMAT` |
| `elink` | Find related records | `elink -db DATABASE -id ID -target TARGET` |
| `efilter` | Filter results | `efilter -mindate DATE -maxdate DATE` |
| `xtract` | Extract XML data | `xtract -pattern PATTERN -element ELEMENT` |
| `einfo` | Database info | `einfo -db DATABASE` |
| `epost` | Post IDs to history | `epost -db DATABASE -id ID1,ID2` |

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `-db` | Database name | `-db pubmed` |
| `-query` | Search terms | `-query "cancer [TIAB]"` |
| `-id` | Record IDs | `-id 1234567,2345678` |
| `-format` | Output format | `-format abstract` |
| `-retmax` | Max results | `-retmax 100` |
| `-retstart` | Start offset | `-retstart 100` |
| `-mindate` | Minimum date | `-mindate 2020` |
| `-maxdate` | Maximum date | `-maxdate 2023` |
| `-days` | Days back | `-days 30` |
| `-target` | Target database | `-target gene` |
| `-log` | Log to history | `-log` |

## PubMed Field Qualifiers

### Content Fields

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[TIAB]` | Title/Abstract | Words in title or abstract |
| `[TITL]` | Title | Words in title only |
| `[AB]` | Abstract | Words in abstract only |
| `[TW]` | Text Word | Words anywhere in citation |
| `[ALL]` | All Fields | All searchable fields |

### Author Fields

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[AUTH]` | Author | Any author |
| `[FAUT]` | First Author | First author only |
| `[LAUT]` | Last Author | Last author only |
| `[AU]` | Author | Alternative to [AUTH] |

### Journal Fields

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[JOUR]` | Journal | Journal name |
| `[TA]` | Journal Title Abbreviation | Abbreviated journal name |
| `[JT]` | Journal Title | Full journal name |

### Date Fields

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[PDAT]` | Publication Date | Date article published |
| `[EDAT]` | Entry Date | Date added to PubMed |
| `[MHDA]` | MeSH Date | Date MeSH terms added |

### MeSH Fields

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[MESH]` | MeSH Terms | Medical Subject Headings |
| `[MAJR]` | MeSH Major Topic | Major MeSH terms |
| `[SH]` | Subheadings | MeSH subheadings |
| `[MH]` | MeSH Terms | Alternative to [MESH] |

### Publication Types

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[PTYP]` | Publication Type | Type of article |
| `[PT]` | Publication Type | Alternative to [PTYP] |

### Other Fields

| Qualifier | Field | Description |
|-----------|-------|-------------|
| `[AFFL]` | Affiliation | Author affiliation |
| `[LANG]` | Language | Article language |
| `[FILT]` | Filter | PubMed filters |
| `[UID]` | PMID | PubMed ID number |

## Common Filters

### Language Filters

| Filter | Description |
|--------|-------------|
| `english [LANG]` | English language articles |
| `chinese [LANG]` | Chinese language articles |
| `german [LANG]` | German language articles |

### Species Filters

| Filter | Description |
|--------|-------------|
| `humans [MESH]` | Human studies |
| `animals [MESH]` | Animal studies |
| `mice [MESH]` | Mouse studies |

### Article Type Filters

| Filter | Description |
|--------|-------------|
| `review [PTYP]` | Review articles |
| `clinical trial [PTYP]` | Clinical trials |
| `randomized controlled trial [PTYP]` | RCTs |
| `meta-analysis [PTYP]` | Meta-analyses |

### Other Filters

| Filter | Description |
|--------|-------------|
| `has abstract [FILT]` | Articles with abstracts |
| `free full text [FILT]` | Free full text available |
| `medline [FILT]` | In MEDLINE database |

## Output Formats

### PubMed Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `abstract` | Human-readable abstract | Reading articles |
| `medline` | MEDLINE format | Reference managers |
| `xml` | Structured XML | Data extraction |
| `uid` | PMIDs only | Getting IDs |
| `docsum` | Document summary | Quick overview |
| `asn.1` | ASN.1 format | Specialized tools |
| `json` | JSON format | Web applications |

### Sequence Formats

| Format | Description | Database |
|--------|-------------|----------|
| `fasta` | FASTA sequence | nuccore, protein |
| `gb` | GenBank flatfile | nuccore |
| `gp` | GenPept flatfile | protein |
| `gff` | GFF3 format | nuccore |

### Special Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `native` | Native format | Database default |
| `acc` | Accession only | Getting accessions |
| `list` | ID list | Simple lists |

## Database Names

### Literature Databases

| Database | Description |
|----------|-------------|
| `pubmed` | Biomedical literature |
| `pmc` | PubMed Central full-text |
| `books` | NCBI Bookshelf |
| `nlmcatalog` | NLM Catalog |

### Sequence Databases

| Database | Description |
|----------|-------------|
| `nuccore` | Nucleotide sequences |
| `protein` | Protein sequences |
| `gene` | Gene records |
| `genome` | Genome assemblies |

### Specialized Databases

| Database | Description |
|----------|-------------|
| `mesh` | Medical Subject Headings |
| `taxonomy` | Taxonomy database |
| `snp` | Single Nucleotide Polymorphism |
| `structure` | Molecular structures |
| `clinvar` | Clinical variants |
| `gtr` | Genetic testing registry |
| `biosample` | BioSample database |
| `bioproject` | BioProject database |

## xtract Patterns for PubMed

### Common Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `PubmedArticle` | Complete article | `-pattern PubmedArticle` |
| `DocumentSummary` | Summary format | `-pattern DocumentSummary` |
| `Count` | Result count | `-pattern Count` |

### PubMed XML Elements

| Element | Path | Description |
|---------|------|-------------|
| PMID | `MedlineCitation/PMID` | PubMed ID |
| Title | `Article/ArticleTitle` | Article title |
| Abstract | `Abstract/AbstractText` | Abstract text |
| Journal | `Journal/Title` | Journal name |
| Year | `PubDate/Year` | Publication year |
| Author | `AuthorList/Author` | Author information |
| MeSH | `MeshHeadingList/MeshHeading` | MeSH terms |

### xtract Commands

| Command | Description | Example |
|---------|-------------|---------|
| `-pattern` | Main pattern | `-pattern PubmedArticle` |
| `-element` | Extract element | `-element Title` |
| `-block` | Block pattern | `-block Author` |
| `-if` | Conditional | `-if Language -equals eng` |
| `-sep` | Separator | `-sep ", "` |
| `-tab` | Tab replacement | `-tab ","` |
| `-def` | Default value | `-def "N/A"` |

## Date Formats

EDirect accepts multiple date formats:

| Format | Example | Description |
|--------|---------|-------------|
| YYYY | `2023` | Year only |
| YYYY/MM | `2023/06` | Year and month |
| YYYY/MM/DD | `2023/06/15` | Full date |
| Relative | `-days 30` | Days ago |

## Rate Limits

| Configuration | Requests/Second | Daily Limit |
|---------------|----------------|-------------|
| No API key | 3 | 10,000 |
| With API key | 10 | Unlimited |

**Best Practices:**
- Always use API key for production use
- Add delays: `sleep 0.5` between requests
- Cache results when possible
- Use batch operations for many IDs

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Command not found` | EDirect not in PATH | Add `$HOME/edirect` to PATH |
| `403 Forbidden` | Rate limit exceeded | Add API key, add delays |
| `No results found` | Invalid query | Check field qualifiers |
| `XML parsing error` | Malformed XML | Check format, use `-format xml` |
| `Network error` | Connection issue | Check internet, retry |

## Boolean Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `AND` | Both terms required | `cancer AND therapy` |
| `OR` | Either term | `lung OR breast` |
| `NOT` | Exclude term | `cancer NOT review` |
| `()` | Grouping | `(lung OR breast) AND cancer` |

## Special Characters

| Character | Usage | Notes |
|-----------|-------|-------|
| `*` | Truncation | `immun*` finds immune, immunity, etc. |
| `" "` | Phrase search | `"clinical trial"` exact phrase |
| `[ ]` | Field qualifier | `[TIAB]` title/abstract field |
| `~` | Proximity | `"machine learning"~10` within 10 words |

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `NCBI_API_KEY` | API key for rate limits | `export NCBI_API_KEY="your_key"` |
| `NCBI_EMAIL` | Identify to NCBI | `export NCBI_EMAIL="you@example.com"` |
| `PATH` | EDirect location | `export PATH="$HOME/edirect:$PATH"` |
| `EUTILS_TIMEOUT` | Request timeout | `export EUTILS_TIMEOUT=60` |

## Quick Examples Cheat Sheet

```bash
# Basic search
esearch -db pubmed -query "your topic" | efetch -format abstract

# Get PMIDs only
esearch -db pubmed -query "search terms" | efetch -format uid

# Recent articles
esearch -db pubmed -query "topic" | efilter -days 30 | efetch -format abstract

# Specific field search
esearch -db pubmed -query "author [AUTH] AND topic [TIAB]"

# Extract to CSV
esearch -db pubmed -query "topic" | efetch -format xml | \
  xtract -pattern PubmedArticle -tab "," -element PMID,Title,Year

# Find related articles
elink -db pubmed -id 1234567 -related | efetch -format abstract

# Cross-database link
esearch -db pubmed -query "gene name" | elink -target gene | efetch -format docsum
```

## Tips for Effective Searching

1. **Start broad, then narrow** - Begin with general terms, add filters
2. **Use field qualifiers** - Be specific about where to search
3. **Check MeSH terms** - Use controlled vocabulary when possible
4. **Review similar articles** - Use `elink -related` to find more
5. **Save your searches** - Use `-log` option for reproducibility
6. **Validate with small samples** - Test queries with `-retmax 5` first
7. **Combine with other tools** - Pipe to `grep`, `awk`, `sort` for analysis

## Related Resources

- [EDirect Official Documentation](https://www.ncbi.nlm.nih.gov/books/NBK179288/)
- [PubMed Help](https://pubmed.ncbi.nlm.nih.gov/help/)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [MeSH Database](https://www.ncbi.nlm.nih.gov/mesh/)