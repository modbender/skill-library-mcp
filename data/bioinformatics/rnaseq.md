# RNA-seq Pipeline — Bioinformatics

## Overview

```
FASTQ → QC → Trim → Align → Count → Normalize → DE Analysis
```

## Step 1: Quality Control

```bash
# Raw data QC
mkdir -p qc/raw
fastqc -t 8 -o qc/raw/ raw_data/*.fastq.gz

# Aggregate
multiqc qc/raw/ -o qc/raw_multiqc/
```

**Check for:**
- Per-base quality (should stay >Q20)
- Adapter content
- Sequence duplication
- GC content (organism-specific)

## Step 2: Trimming

```bash
mkdir -p trimmed

for sample in sample1 sample2 sample3; do
  fastp \
    -i raw_data/${sample}_R1.fastq.gz \
    -I raw_data/${sample}_R2.fastq.gz \
    -o trimmed/${sample}_R1.fastq.gz \
    -O trimmed/${sample}_R2.fastq.gz \
    -h qc/${sample}_fastp.html \
    -j qc/${sample}_fastp.json \
    --detect_adapter_for_pe \
    --thread 4
done
```

## Step 3: Alignment with STAR

### Build Index (once per genome)

```bash
STAR --runMode genomeGenerate \
  --genomeDir star_index/ \
  --genomeFastaFiles genome.fa \
  --sjdbGTFfile genes.gtf \
  --sjdbOverhang 149 \
  --runThreadN 16
```

Note: `sjdbOverhang` = read length - 1

### Align Samples

```bash
mkdir -p aligned

for sample in sample1 sample2 sample3; do
  STAR \
    --genomeDir star_index/ \
    --readFilesIn trimmed/${sample}_R1.fastq.gz trimmed/${sample}_R2.fastq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --quantMode GeneCounts \
    --runThreadN 8 \
    --outFileNamePrefix aligned/${sample}_
  
  # Index BAM
  samtools index aligned/${sample}_Aligned.sortedByCoord.out.bam
done
```

## Step 4: Gene Counting

**Option A: STAR GeneCounts** (from alignment step)
```bash
# Counts are in aligned/*_ReadsPerGene.out.tab
# Column 1: Gene ID
# Column 2: Unstranded counts
# Column 3: First-strand counts
# Column 4: Second-strand counts
```

**Option B: featureCounts**
```bash
featureCounts \
  -T 8 \
  -p -B -C \
  -t exon \
  -g gene_id \
  -a genes.gtf \
  -o counts/gene_counts.txt \
  aligned/*_Aligned.sortedByCoord.out.bam
```

Flags:
- `-p`: paired-end
- `-B`: both ends mapped
- `-C`: no chimeric reads

## Step 5: Differential Expression (R/DESeq2)

```r
library(DESeq2)

# Load counts matrix
counts <- read.table("counts/gene_counts.txt", header=TRUE, row.names=1)
counts <- counts[, 7:ncol(counts)]  # Remove metadata columns

# Sample info
coldata <- data.frame(
  condition = factor(c("control", "control", "treated", "treated")),
  row.names = colnames(counts)
)

# Create DESeq object
dds <- DESeqDataSetFromMatrix(
  countData = counts,
  colData = coldata,
  design = ~ condition
)

# Filter low counts
dds <- dds[rowSums(counts(dds)) >= 10, ]

# Run DESeq
dds <- DESeq(dds)

# Get results
res <- results(dds, contrast = c("condition", "treated", "control"))
res <- res[order(res$padj), ]

# Export significant genes
sig <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
write.csv(as.data.frame(sig), "results/significant_genes.csv")
```

## Step 6: Visualization

```r
# MA plot
plotMA(res, ylim = c(-5, 5))

# Volcano plot
library(EnhancedVolcano)
EnhancedVolcano(res,
  lab = rownames(res),
  x = 'log2FoldChange',
  y = 'pvalue',
  pCutoff = 0.05,
  FCcutoff = 1
)

# PCA
vsd <- vst(dds, blind = FALSE)
plotPCA(vsd, intgroup = "condition")

# Heatmap of top genes
library(pheatmap)
top_genes <- head(rownames(res[order(res$padj), ]), 50)
pheatmap(assay(vsd)[top_genes, ], scale = "row")
```

## Common Issues

### Low Mapping Rate (<70%)
- Wrong reference genome
- Contamination (rRNA, adapter)
- Check species with BLAST

### High Duplication
- Low library complexity
- Consider deduplication for DNA, but usually keep for RNA-seq

### Batch Effects
- Use `ComBat` or include batch in DESeq2 design
- Always check PCA for batch clustering

### Few Significant Genes
- Increase biological replicates
- Check count distribution
- Verify experimental design

## Resource Requirements

| Step | RAM | Time (6 samples, human) |
|------|-----|-------------------------|
| FastQC | 1 GB | 10 min |
| fastp | 4 GB | 20 min |
| STAR index | 32 GB | 30 min |
| STAR align | 32 GB | 2 hours |
| featureCounts | 4 GB | 10 min |
| DESeq2 | 8 GB | 5 min |
