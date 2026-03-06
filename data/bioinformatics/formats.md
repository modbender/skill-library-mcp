# File Formats — Bioinformatics

## Sequence Formats

### FASTA
Reference sequences, assembled genomes, protein sequences.

```
>chr1 description
ATCGATCGATCGATCG...
>chr2 description
GCTAGCTAGCTAGCTA...
```

**Operations:**
```bash
# Index for random access
samtools faidx reference.fa

# Extract sequence
samtools faidx reference.fa chr1:1000-2000

# Get sequence lengths
awk '/^>/ {if(name) print name, len; name=$1; len=0; next} {len+=length}' file.fa
```

### FASTQ
Raw sequencing reads with quality scores.

```
@read_id
ATCGATCGATCG
+
IIIIIIIIIII
```

Quality: Phred+33 (Illumina 1.8+). `I` = Q40 = 0.0001 error rate.

**Operations:**
```bash
# Count reads
echo $(($(zcat file.fastq.gz | wc -l) / 4))

# Check encoding
head -100 file.fastq | awk 'NR%4==0' | od -c | head

# Convert to FASTA
seqtk seq -a file.fastq > file.fasta
```

## Alignment Formats

### SAM/BAM/CRAM
Aligned reads. BAM = compressed binary. CRAM = reference-compressed.

**FLAG field (critical):**
| Bit | Meaning |
|-----|---------|
| 1 | Paired |
| 2 | Proper pair |
| 4 | Unmapped |
| 8 | Mate unmapped |
| 16 | Reverse strand |
| 256 | Secondary |
| 1024 | Duplicate |
| 2048 | Supplementary |

**Operations:**
```bash
# BAM info
samtools view -H file.bam  # Header
samtools flagstat file.bam  # Mapping stats
samtools idxstats file.bam  # Per-chromosome counts

# Filter by FLAG
samtools view -f 2 file.bam     # Proper pairs only
samtools view -F 1024 file.bam  # No duplicates

# Convert
samtools view -bS file.sam > file.bam
samtools view -h file.bam > file.sam
```

## Variant Formats

### VCF/BCF
Variant calls. BCF = binary compressed.

```
#CHROM POS ID REF ALT QUAL FILTER INFO FORMAT SAMPLE
chr1   100 .  A   G   30   PASS   DP=20  GT:DP  0/1:20
```

**INFO field tags:**
| Tag | Meaning |
|-----|---------|
| DP | Read depth |
| AF | Allele frequency |
| MQ | Mapping quality |
| FS | Fisher strand bias |

**Operations:**
```bash
# Stats
bcftools stats file.vcf.gz

# Filter
bcftools view -f PASS file.vcf.gz            # PASS only
bcftools view -i 'QUAL>30 && DP>10' file.vcf.gz
bcftools view -v snps file.vcf.gz            # SNPs only

# Extract samples
bcftools view -s sample1,sample2 file.vcf.gz

# Annotate
bcftools annotate -a annotations.bed.gz -c CHROM,FROM,TO,GENE file.vcf.gz
```

## Interval Formats

### BED
Genomic intervals. **0-based, half-open** coordinates.

```
chr1    1000    2000    region1    100    +
```

Columns: chrom, start (0-based), end (exclusive), name, score, strand.

**Operations:**
```bash
# Intersect
bedtools intersect -a regions.bed -b features.bed

# Merge overlapping
bedtools merge -i sorted.bed

# Get flanks
bedtools flank -i regions.bed -g genome.sizes -b 100

# Coverage
bedtools coverage -a regions.bed -b aligned.bam
```

### GFF/GTF
Gene annotations. **1-based, closed** coordinates.

```
chr1  source  gene   1000  2000  .  +  .  gene_id "ABC"; gene_name "ABC"
chr1  source  exon   1000  1200  .  +  .  gene_id "ABC"; transcript_id "ABC.1"
```

**Operations:**
```bash
# Extract features
awk '$3=="exon"' file.gtf

# Convert GTF to BED
awk 'OFS="\t" {print $1,$4-1,$5,$10,$6,$7}' file.gtf | tr -d '";'

# Get gene lengths
gffread -T file.gff -o- | awk -F'\t' '{print $1, $5-$4}'
```

## Coordinate Systems Summary

| Format | Start | End | Example chr1:100-200 |
|--------|-------|-----|---------------------|
| BED | 0-based | Exclusive | 99, 200 |
| VCF | 1-based | Inclusive | 100, 200 |
| GFF/GTF | 1-based | Inclusive | 100, 200 |
| SAM/BAM | 1-based | Inclusive | 100, 200 |

**Convert BED → 1-based:** `start + 1`  
**Convert 1-based → BED:** `start - 1`
