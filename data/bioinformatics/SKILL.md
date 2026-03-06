---
name: Bioinformatics
slug: bioinformatics
version: 1.0.0
homepage: https://clawic.com/skills/bioinformatics
description: Analyze DNA, RNA, and protein sequences with alignment, variant calling, and expression analysis pipelines.
metadata: {"clawdbot":{"emoji":"🧬","requires":{"bins":["samtools","bcftools","bedtools","bwa","fastqc","fastp"],"config":["~/bioinformatics/"]},"os":["linux","darwin"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. Create `~/bioinformatics/` with user consent to store project context and preferences.

## When to Use

User needs to analyze biological sequences, run genomic pipelines, or interpret sequencing data. Agent handles sequence alignment, variant calling, expression analysis, and format conversions.

## Architecture

Memory lives in `~/bioinformatics/`. See `memory-template.md` for structure.

```
~/bioinformatics/
├── memory.md         # Projects, preferences, reference genomes
├── pipelines/        # Saved pipeline configurations
└── results/          # Analysis outputs and logs
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| File formats | `formats.md` |
| Tool commands | `tools.md` |
| RNA-seq pipeline | `rnaseq.md` |
| Variant calling | `variants.md` |

## Core Rules

### 1. Verify Input Quality First
Before any analysis, check input data quality:
- FASTQ: Run FastQC, check per-base quality, adapter content
- BAM: Verify sorted, indexed (`samtools quickcheck`)
- VCF: Validate format (`bcftools view -h`)

Bad input → garbage output. Always QC first.

### 2. Use Reference Genome Consistently
Track which reference is used per project:
- Human: GRCh38/hg38 (prefer) or GRCh37/hg19
- Mouse: GRCm39/mm39 or GRCm38/mm10
- Mixing references = invalid results

Store reference info in `~/bioinformatics/memory.md` per project.

### 3. Preserve Raw Data
**NEVER** modify original FASTQ/BAM files:
- Work on copies
- Keep originals read-only
- Log every transformation step

### 4. Resource Awareness
Bioinformatics commands can consume massive resources:
- Check file sizes before operations
- Use streaming when possible (`samtools view | ...`)
- Estimate memory needs (BWA: ~6GB for human genome)
- Warn before operations >10 minutes

### 5. Reproducibility
Every analysis must be reproducible:
- Log exact tool versions (`samtools --version`)
- Save command parameters
- Record input file checksums for critical analyses

## Common Traps

- **Wrong chromosome naming** — `chr1` vs `1` causes silent failures. Check and convert with `sed 's/^chr//'`
- **Unsorted BAM** — Most tools expect sorted input. Symptoms: errors or wrong results with no warning
- **Index missing** — BAM needs `.bai`, VCF needs `.tbi`. Commands fail cryptically without them
- **Memory exhaustion** — Large BAM operations kill the session. Stream or use `--threads` wisely
- **Stale indices** — After modifying BAM/VCF, regenerate index. Old index = corrupt reads
- **0-based vs 1-based coordinates** — BED is 0-based, VCF/GFF is 1-based. Off-by-one bugs are common

## File Formats Quick Reference

| Format | Purpose | Key Tool |
|--------|---------|----------|
| FASTA | Reference sequences | `samtools faidx` |
| FASTQ | Raw reads + quality | `seqtk`, `fastp` |
| SAM/BAM | Aligned reads | `samtools` |
| VCF/BCF | Variants | `bcftools` |
| BED | Genomic intervals | `bedtools` |
| GFF/GTF | Gene annotations | `gffread` |
| BigWig | Coverage tracks | `deepTools` |

## Essential Commands

### Quality Control
```bash
# FASTQ quality report
fastqc sample.fastq.gz -o qc_reports/

# Trim adapters + low quality
fastp -i R1.fq.gz -I R2.fq.gz -o R1.clean.fq.gz -O R2.clean.fq.gz

# BAM statistics
samtools flagstat aligned.bam
samtools stats aligned.bam > stats.txt
```

### Alignment
```bash
# Index reference (once)
bwa index reference.fa

# Align paired-end reads
bwa mem -t 8 reference.fa R1.fq.gz R2.fq.gz | \
  samtools sort -o aligned.bam -

# Index BAM
samtools index aligned.bam
```

### Variant Calling
```bash
# Call variants
bcftools mpileup -Ou -f reference.fa aligned.bam | \
  bcftools call -mv -Oz -o variants.vcf.gz

# Index VCF
bcftools index variants.vcf.gz

# Filter variants
bcftools filter -s LowQual -e 'QUAL<20' variants.vcf.gz
```

### Data Manipulation
```bash
# Extract region
samtools view -b aligned.bam chr1:1000000-2000000 > region.bam

# Convert BAM to FASTQ
samtools fastq -1 R1.fq.gz -2 R2.fq.gz aligned.bam

# Merge BAMs
samtools merge merged.bam sample1.bam sample2.bam

# Subset VCF by region
bcftools view -r chr1:1000-2000 variants.vcf.gz
```

## Security & Privacy

**Data access:**
- Only reads files user explicitly provides as input
- Writes outputs to directories user specifies
- Stores preferences in ~/bioinformatics/ (with consent)

**Data that stays local:**
- All sequence data processed locally
- No external API calls for analysis
- Pipeline configs in ~/bioinformatics/

**This skill does NOT:**
- Upload sequence data anywhere
- Access files without explicit user instruction
- Infer or collect data beyond explicit inputs
- Make network requests during analysis

**Note:** Installing tools (conda, brew) and downloading reference genomes requires internet access. These are user-initiated actions.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `data-analysis` — statistical interpretation
- `statistics` — hypothesis testing
- `science` — research methodology

## Feedback

- If useful: `clawhub star bioinformatics`
- Stay updated: `clawhub sync`
