# OpenClaw Integration Guide ⚠️

**Important Security Reminder**: You must complete secure installation steps (see [INSTALL.md](INSTALL.md)) before using this skill. This skill executes external commands and requires careful auditing.

## Secure Usage Guidelines

### ⚠️ Pre-Execution Checks
Before each use of the `exec` tool, ensure:
1. Understand the commands to be executed
2. Confirm EDirect is properly installed
3. Check network connection security
4. Set appropriate timeout periods

### Command Execution Audit
```bash
# Write complex commands to script files for auditability
# 1. Create script file
echo 'esearch -db pubmed -query "$1" | efetch -format abstract | head -200' > search.sh

# 2. Review script content
cat search.sh

# 3. Set permissions
chmod +x search.sh

# 4. Execute script
exec -c './search.sh "CRISPR"'
```

## Basic Usage in OpenClaw

### Running EDirect Commands

Use OpenClaw's `exec` tool to run EDirect commands:

```bash
# Simple search example
exec -c 'esearch -db pubmed -query "CRISPR [TIAB]" | efetch -format abstract | head -200'
```

### Using the Included Scripts

```bash
# Run the batch fetch script
exec -c 'cd /root/.openclaw/workspace/pubmed-edirect && ./scripts/batch_fetch_abstracts.sh'

# With custom parameters
exec -c 'cd /root/.openclaw/workspace/pubmed-edirect && ./scripts/search_export_csv.sh "machine learning" 50 ml_results.csv'
```

## Common OpenClaw Workflows

### 1. Literature Search and Summary

```bash
# Search and get a summary
exec -c '
  echo "Searching for recent review articles..."
  esearch -db pubmed -query "cancer immunotherapy" | \
    efilter -mindate 2023 -query "review [PTYP]" | \
    efetch -format abstract | head -500
'
```

### 2. Data Extraction to Workspace

```bash
# Extract data and save to workspace
exec -c '
  esearch -db pubmed -query "your topic" -retmax 100 | \
    efetch -format xml | \
    xtract -pattern PubmedArticle \
      -element PMID Title Year | \
    awk "BEGIN {FS=\"\\t\"; print \"PMID,Title,Year\"} {print \$1\",\"\$2\",\"\$3}" > /root/.openclaw/workspace/literature.csv
  echo "Data saved to workspace/literature.csv"
'
```

### 3. Automated Literature Monitoring

Create a cron job in OpenClaw to check for new publications:

```bash
# Check for new papers daily
exec -c '
  cd /root/.openclaw/workspace/pubmed-edirect
  ./scripts/publication_trends.sh "your research area" $(date +%Y -d "1 year ago") $(date +%Y) daily_trend.csv
  # Send notification if significant new publications
'
```

## OpenClaw-Specific Tips

### 1. Managing Large Outputs

```bash
# Pipe to less for long outputs
exec -c 'esearch -db pubmed -query "broad topic" | efetch -format abstract | less -N'

# Save to file and then read
exec -c '
  esearch -db pubmed -query "query" | efetch -format abstract > /tmp/results.txt
  head -100 /tmp/results.txt
'
```

### 2. Error Handling in OpenClaw

```bash
# Use error checking
exec -c '
  if esearch -db pubmed -query "test" > /dev/null 2>&1; then
    echo "EDirect is working correctly"
  else
    echo "Error: EDirect may not be installed or configured"
    echo "Please check INSTALL.md"
  fi
'
```

### 3. Interactive Search Sessions

```bash
# Create an interactive search function
exec -c '
  search_pubmed() {
    local query="$1"
    local max="${2:-20}"
    echo "Searching: $query"
    esearch -db pubmed -query "$query" -retmax "$max" | \
      efetch -format abstract | head -$((max * 10))
  }
  
  # Test it
  search_pubmed "COVID-19 vaccine" 10
'
```

## Integration with Other OpenClaw Skills

### Combine with Text Processing

```bash
# Extract and analyze text
exec -c '
  esearch -db pubmed -query "topic" -retmax 50 | \
    efetch -format abstract | \
    grep -i "keyword" | \
    wc -l | \
    xargs echo "Occurrences of keyword:"
'
```

### Use with File Management

```bash
# Organize results in workspace
exec -c '
  mkdir -p /root/.openclaw/workspace/literature/$(date +%Y-%m-%d)
  esearch -db pubmed -query "daily search" | \
    efetch -format xml > /root/.openclaw/workspace/literature/$(date +%Y-%m-%d)/results.xml
  echo "Results saved to workspace"
'
```

## Creating OpenClaw Commands

You can create aliases or functions in your OpenClaw environment:

```bash
# Add to your shell configuration
alias pubmed-search='esearch -db pubmed'
alias pubmed-fetch='efetch -db pubmed -format abstract'

# Or create functions
pmsearch() {
  esearch -db pubmed -query "$1" ${2:+-retmax $2} | \
    efetch -format abstract | head -${3:-200}
}
```

## Example: Complete Literature Review Workflow

```bash
# 1. Initial search
exec -c '
  echo "=== Initial Broad Search ==="
  esearch -db pubmed -query "main topic" | \
    efilter -mindate 2020 | \
    xtract -pattern Count -element Count
  echo " papers since 2020"
'

# 2. Refine search
exec -c '
  echo "=== Refined Search ==="
  esearch -db pubmed -query "specific aspect [TIAB]" | \
    efilter -query "review [PTYP]" | \
    efetch -format abstract | head -300
'

# 3. Extract data for analysis
exec -c '
  echo "=== Data Extraction ==="
  esearch -db pubmed -query "final query" -retmax 100 | \
    efetch -format xml | \
    xtract -pattern PubmedArticle \
      -element PMID Year Title | \
    sort -k2 > /root/.openclaw/workspace/extracted_data.tsv
  echo "Data extracted to workspace"
'
```

## Troubleshooting in OpenClaw

### Common Issues

1. **EDirect not found**
   ```bash
   exec -c 'export PATH="$HOME/edirect:$PATH" && esearch -help'
   ```

2. **Permission denied on scripts**
   ```bash
   exec -c 'chmod +x /root/.openclaw/workspace/pubmed-edirect/scripts/*.sh'
   ```

3. **Rate limiting errors**
   ```bash
   exec -c 'export NCBI_API_KEY="your_key" && esearch -db pubmed -query "test"'
   ```

### Testing Your Setup

```bash
# Run a complete test
exec -c '
  echo "Testing EDirect installation..."
  if command -v esearch >/dev/null 2>&1; then
    echo "✓ EDirect commands available"
    count=$(esearch -db pubmed -query "test" | xtract -pattern Count -element Count 2>/dev/null || echo "error")
    if [[ "$count" =~ ^[0-9]+$ ]]; then
      echo "✓ NCBI connection working ($count results for 'test')"
      echo "✓ Setup is complete and functional"
    else
      echo "✗ Could not connect to NCBI"
    fi
  else
    echo "✗ EDirect not in PATH"
    echo "Please check INSTALL.md"
  fi
'
```

## Best Practices for OpenClaw Use

1. **Use workspace directory** for storing results
2. **Add delays** in batch operations to respect rate limits
3. **Log your queries** for reproducibility
4. **Combine with other tools** (grep, awk, sort) for processing
5. **Create reusable scripts** for common workflows
6. **Monitor API usage** if using an API key
7. **Backup important results** from workspace

## Getting Help

- Review the skill documentation files
- Check EDirect official documentation
- Test queries in small batches first
- Use the `-help` option with any EDirect command