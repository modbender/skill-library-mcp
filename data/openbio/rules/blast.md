# BLAST Sequence Similarity Search

Search for similar sequences in NCBI databases using BLAST (Basic Local Alignment Search Tool) via OpenBio API.

## When to Use

Use BLAST tools when:
1. Identifying an unknown protein or nucleotide sequence
2. Finding homologous sequences across species
3. Checking if a designed sequence has known relatives
4. Annotating a sequence by finding similar characterized sequences
5. Validating sequence identity against a reference database

## Decision Tree

```
What type of sequence do you have and what are you searching?
│
├─ Protein sequence → search protein DB?
│   └─ blastp + nr/swissprot/pdb/refseq_protein
│
├─ Nucleotide sequence → search nucleotide DB?
│   └─ blastn + nt/refseq_rna/refseq_genomic
│
├─ Nucleotide sequence → search protein DB?
│   └─ blastx + nr/swissprot/pdb/refseq_protein
│       (translates your nucleotide query in all 6 frames)
│
├─ Protein sequence → search nucleotide DB?
│   └─ tblastn + nt/refseq_rna/refseq_genomic
│       (translates DB sequences in all 6 frames)
│
└─ Nucleotide vs translated nucleotide?
    └─ tblastx + nt/refseq_rna/refseq_genomic
        (translates both query and DB)
```

### Database Selection

| Database | Type | Contents | Best For |
|----------|------|----------|----------|
| nr | Protein | Non-redundant protein sequences | Broadest protein search |
| swissprot | Protein | Curated UniProt entries | High-quality annotated proteins |
| pdb | Protein | Protein Data Bank sequences | Finding structural homologs |
| refseq_protein | Protein | NCBI RefSeq proteins | Reference protein sequences |
| nt | Nucleotide | Non-redundant nucleotide | Broadest nucleotide search |
| refseq_rna | Nucleotide | NCBI RefSeq RNA | Reference transcripts |
| refseq_genomic | Nucleotide | NCBI RefSeq genomes | Reference genomic sequences |

**Important**: Database must be compatible with the BLAST program. Protein programs (blastp, blastx) require protein databases. Nucleotide programs (blastn, tblastx) require nucleotide databases. tblastn uses nucleotide databases but takes a protein query.

## Tools Reference

### submit_blast — Submit a BLAST search

Submits a sequence to NCBI BLAST and returns a Request ID (RID) for polling.

```bash
# Protein BLAST against SwissProt
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_blast" \
  -F 'params={"query": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH", "program": "blastp", "database": "swissprot", "evalue": 0.001, "max_hits": 10}'
```

```bash
# Nucleotide BLAST against nt
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_blast" \
  -F 'params={"query": "ATGGTTCTGTCTAAGCCCGATGACAAAACCAACGTGAAAGCAGCCTGGGGA", "program": "blastn", "database": "nt"}'
```

**Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | — | Raw sequence (10–10,000 characters, no FASTA header) |
| program | string | Yes | — | blastn, blastp, blastx, tblastn, or tblastx |
| database | string | No | nr | Target database (must match program type) |
| evalue | float | No | 10.0 | E-value threshold (lower = more stringent) |
| max_hits | int | No | 10 | Max hits to return (1–50) |

**Returns**: `rid` (Request ID), `program`, `database`, `query_len`

### check_blast_status — Poll for completion

BLAST searches take 10–60+ seconds. Poll this endpoint until status is `READY`.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=check_blast_status" \
  -F 'params={"rid": "YOUR_RID_HERE"}'
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| rid | string | Yes | Request ID from submit_blast |

**Returns**: `status` — one of:
- `WAITING` — still running, poll again in 10–15 seconds
- `READY` — results available, call get_blast_results
- `FAILED` — search failed, resubmit
- `UNKNOWN` — unexpected state

### get_blast_results — Retrieve results

Fetch parsed results once status is `READY`.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=get_blast_results" \
  -F 'params={"rid": "YOUR_RID_HERE", "max_hits": 20}'
```

**Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| rid | string | Yes | — | Request ID (must have READY status) |
| max_hits | int | No | 10 | Max hits to return (1–50) |

**Returns**: `query_title`, `query_len`, `program`, `database`, `total_hits`, `hits` array. Each hit includes:
- `accession`, `title`, `scientific_name`, `taxid`
- `evalue`, `bit_score`, `identity_pct`, `align_len`
- `query_start`, `query_end`, `hit_start`, `hit_end`, `gaps`

## Quality Thresholds

### E-value Interpretation

| E-value | Interpretation |
|---------|----------------|
| < 1e-50 | Excellent match — near-identical or close homolog |
| 1e-50 to 1e-10 | Strong match — likely homologous |
| 1e-10 to 0.01 | Moderate — possible remote homology |
| 0.01 to 10 | Weak — may be spurious, inspect alignment |
| > 10 | Not significant — likely random |

### Identity Percentage

| Identity % | Interpretation |
|------------|----------------|
| > 90% | Very high — same protein/gene or very close ortholog |
| 70–90% | High — clear homolog, likely conserved function |
| 30–70% | Moderate — probable homolog, function may diverge |
| < 30% | Low — remote homology or convergent similarity |

### Bit Score

Higher bit scores indicate better alignments. Bit scores > 50 are generally significant. Unlike e-values, bit scores are independent of database size.

## Common Workflow

```
1. Submit BLAST search
   → submit_blast with sequence, program, database
   → Save the returned RID

2. Poll for completion (wait 10-15 seconds between checks)
   → check_blast_status with RID
   → Repeat until status is READY

3. Retrieve results
   → get_blast_results with RID
   → Parse hits by e-value, identity, bit score

4. Analyze top hits
   → Check species, annotations, and alignment quality
   → Use other OpenBio tools for follow-up:
     - lookup_gene for gene details
     - fetch_pdb_metadata for structural info
     - get_sequence for full sequence retrieval
```

## Common Mistakes

### Wrong: Mismatched program and database
```
❌ submit_blast with program="blastp" and database="nt"
   → Protein program cannot search nucleotide database
```

```
✅ Match program type to database type:
   - blastp/blastx → protein databases (nr, swissprot, pdb)
   - blastn/tblastx → nucleotide databases (nt, refseq_rna)
   - tblastn → nucleotide databases (protein query, translated DB)
```

### Wrong: Not waiting for completion
```
❌ Calling get_blast_results immediately after submit_blast
   → Search hasn't finished yet
```

```
✅ Always check status first:
   → check_blast_status until READY
   → Then get_blast_results
```

### Wrong: Using too permissive e-value
```
❌ submit_blast with evalue=10 for identifying a protein
   → Returns many spurious hits
```

```
✅ Use stringent e-value for identification:
   → evalue=0.001 or lower for confident matches
   → Only use evalue=10 for exhaustive remote homology searches
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Status stays WAITING | Large database or busy server | Wait longer (up to 5 min), poll every 15 seconds |
| Status FAILED | Invalid sequence or server error | Verify sequence is valid, resubmit |
| No hits returned | Sequence too short or novel | Try broader database (nr/nt), increase e-value |
| Too many low-quality hits | Permissive e-value | Lower e-value threshold (e.g., 0.001) |
| Program/database error | Incompatible combination | See database selection table above |
| Sequence rejected | Too short (< 10) or too long (> 10,000) | Trim or split sequence to 10–10,000 characters |

---

**Tip**: For quick protein identification, use `blastp` against `swissprot` with `evalue=0.001`. SwissProt is smaller but curated, giving faster and more annotated results than `nr`.
