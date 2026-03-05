# Scholar Research - API References

## Data Sources

### 1. arXiv
- **Base URL**: `http://export.arxiv.org/api/query`
- **Documentation**: https://arxiv.org/help/api
- **Rate Limit**: 1 request per 3 seconds
- **Fields**: Physics, Math, CS, q-bio, q-fin

### 2. PubMed/PMC
- **Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **Endpoints**:
  - Search: `/esearch.fcgi`
  - Summary: `/esummary.fcgi`
  - Fetch: `/efetch.fcgi`
- **Documentation**: https://www.ncbi.nlm.nih.gov/books/NBK25497/
- **Rate Limit**: 3 requests per second

### 3. OpenAlex
- **Base URL**: `https://api.openalex.org/`
- **Endpoints**:
  - Works: `/works`
  - Authors: `/authors`
  - Institutions: `/institutions`
  - Journals: `/journals`
- **Documentation**: https://docs.openalex.org/
- **Rate Limit**: 100,000 requests/day (free)
- **Note**: Requires email for API token (faster)

### 4. DOAJ (Directory of Open Access Journals)
- **Base URL**: `https://doaj.org/api/v2/`
- **Documentation**: https://doaj.org/api/v2/docs
- **Rate Limit**: 60 requests/minute

### 5. CrossRef
- **Base URL**: `https://api.crossref.org/`
- **Documentation**: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- **Rate Limit**: Polite pool (include email)
- **Note**: Requires email for "polite" usage

### 6. Semantic Scholar
- **Base URL**: `https://api.semanticscholar.org/`
- **Graph API**: `https://api.semanticscholar.org/graph/v1/`
- **Documentation**: https://api.semanticscholar.org/api-docs/
- **Rate Limit**: 100 requests/day (free tier)

### 7. Unpaywall
- **Base URL**: `https://api.unpaywall.org/v2/`
- **Documentation**: https://unpaywall.org/products/api
- **Rate Limit**: 100,000 requests/day
- **Note**: Requires email

### 8. CORE
- **Base URL**: `https://api.core.ac.uk/v3/`
- **Documentation**: https://core.ac.uk/services/api/
- **Rate Limit**: 100 requests/5 minutes (anonymous)

### 9. bioRxiv / medRxiv
- **Base URL**: `https://api.biorxiv.org/details/biorxiv/`
- **Documentation**: https://www.biorxiv.org/aboutbiorxiv
- **Rate Limit**: 10 requests/second

### 10. Zenodo
- **Base URL**: `https://zenodo.org/api/`
- **Documentation**: https://developers.zenodo.org/
- **Rate Limit**: Fair use policy

## Scoring Data Sources

### Author Metrics
- **OpenAlex**: Author h-index, citation count
- **Semantic Scholar**: Author metrics

### Journal Metrics
- **SCImago**: Journal Rank (SJR), CiteScore
- **CrossRef**: Impact factor (some)
- **Scopus**: CiteScore

### Retraction Tracking
- **Retraction Watch**: Database of retractions
- **URL**: https://retractionwatch.org/

## Figure Extraction Tools

### pdftotext (Poppler)
```bash
# Install
sudo apt install poppler-utils

# Extract text
pdftotext paper.pdf -

# Extract images
pdfimages -list -png paper.pdf fig
```

### pdfimages (Poppler)
```bash
pdfimages -png paper.pdf output_prefix
```

### PyPDF2
```python
import PyPDF2
with open('paper.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = reader.pages[0].extract_text()
```

## PDF Download Sources

### arXiv
```
https://arxiv.org/pdf/{arxiv_id}.pdf
```

### DOI
```
https://doi.org/{doi}
```

### PubMed Central
```
https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/
```

## API Key Registration

1. **OpenAlex**: https://openalex.org/
2. **Semantic Scholar**: https://www.semanticscholar.org/
3. **CrossRef**: Use email in requests
4. **Unpaywall**: https://unpaywall.org/products/api (free)
