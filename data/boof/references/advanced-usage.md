# Boof — Advanced Usage

## Section-by-Section Summarization

For full-document summaries that don't miss content, use chunk-then-merge:

1. Boof the document (converts + indexes)
2. Read the markdown and identify section headers
3. Summarize each section individually (small context, focused attention)
4. Merge section summaries into a cohesive overview

This avoids the "lost in the middle" problem where LLMs skip content in the middle of long documents.

## Batch Processing

Boof multiple documents into the same collection:

```bash
# Process all PDFs in a folder
for pdf in /path/to/papers/*.pdf; do
  ./scripts/boof.sh "$pdf" --collection "research-papers" --output-dir ./boofed
done

# Now query across all papers at once
qmd query "lithium extraction methods" -c research-papers
```

## Custom Collections

Organize documents by project:

```bash
# Battery VIP conference materials
boof.sh deck.pdf --collection battery-vip
boof.sh speaker-bios.pdf --collection battery-vip

# DOE grant materials
boof.sh nofo-2026.pdf --collection doe-grants
boof.sh technical-volume.pdf --collection doe-grants

# Query within a specific project
qmd query "eligibility requirements" -c doe-grants
```

## Query Patterns for Agents

When an agent needs to analyze a boofed document:

```bash
# Targeted retrieval (5 most relevant chunks)
qmd query "what are the key findings about membrane durability" -c paper-name -n 5

# Full-text search (exact matches)
qmd search "LiFePO4" -c paper-name

# Get more results for comprehensive analysis
qmd query "experimental results" -c paper-name -n 15

# Output as JSON (for programmatic use)
qmd query "cost analysis" -c paper-name --json
```

## Token Efficiency Comparison

| Approach | Tokens per query | Full doc coverage |
|----------|-----------------|-------------------|
| Full PDF in context | 50,000-150,000 | ⚠️ Lost in middle |
| RAG (top 5 chunks) | 2,000-5,000 | ✅ Targeted |
| RAG (top 15 chunks) | 6,000-15,000 | ✅ Broader |
| Section summaries | 15,000-25,000 | ✅ Complete |

## Re-indexing

After updating or adding documents:

```bash
# Re-index all collections
qmd update

# Rebuild embeddings
qmd embed -f
```
