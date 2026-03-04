# Tool Reference — Bioinformatics

## Installation

### Conda (Recommended)
```bash
# Create bioinformatics environment
conda create -n bioinfo -c bioconda -c conda-forge \
  samtools bcftools bedtools bwa star fastqc fastp multiqc

conda activate bioinfo
```

### Homebrew (macOS)
```bash
brew install samtools bcftools bedtools bwa
```

## Core Tools

### samtools — BAM/SAM Manipulation
```bash
# View
samtools view -h file.bam              # With header
samtools view file.bam chr1:1000-2000  # Region

# Sort
samtools sort -o sorted.bam file.bam
samtools sort -n -o namesorted.bam file.bam  # By name

# Index
samtools index file.bam  # Creates .bai

# Merge
samtools merge out.bam in1.bam in2.bam

# Stats
samtools flagstat file.bam
samtools coverage file.bam
samtools depth file.bam > depth.txt

# Convert
samtools fastq -1 R1.fq -2 R2.fq file.bam
samtools fasta file.bam > reads.fa
```

### bcftools — VCF/BCF Manipulation
```bash
# View
bcftools view file.vcf.gz
bcftools view -H file.vcf.gz           # No header
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\n' file.vcf.gz

# Filter
bcftools filter -e 'QUAL<20' file.vcf.gz
bcftools view -f PASS file.vcf.gz
bcftools view -i 'INFO/DP>10' file.vcf.gz

# Call variants
bcftools mpileup -Ou -f ref.fa aln.bam | bcftools call -mv -Oz -o out.vcf.gz

# Normalize
bcftools norm -f ref.fa -m -any file.vcf.gz

# Merge
bcftools merge -Oz -o merged.vcf.gz sample1.vcf.gz sample2.vcf.gz

# Stats
bcftools stats file.vcf.gz > stats.txt
```

### bedtools — Interval Operations
```bash
# Intersect
bedtools intersect -a a.bed -b b.bed
bedtools intersect -a a.bam -b regions.bed -wa

# Subtract
bedtools subtract -a a.bed -b b.bed

# Merge
bedtools merge -i sorted.bed
bedtools merge -i sorted.bed -d 100  # Merge within 100bp

# Coverage
bedtools coverage -a regions.bed -b aligned.bam
bedtools genomecov -ibam file.bam -bg > coverage.bedgraph

# Get FASTA
bedtools getfasta -fi ref.fa -bed regions.bed -fo out.fa
```

## Aligners

### BWA — DNA Alignment
```bash
# Index (once)
bwa index reference.fa

# Align
bwa mem -t 8 reference.fa R1.fq.gz R2.fq.gz > aligned.sam

# With read groups (required for GATK)
bwa mem -t 8 -R '@RG\tID:sample\tSM:sample\tPL:ILLUMINA' \
  reference.fa R1.fq.gz R2.fq.gz | samtools sort -o aligned.bam
```

### STAR — RNA-seq Alignment
```bash
# Generate index (once, needs ~30GB RAM for human)
STAR --runMode genomeGenerate \
  --genomeDir star_index/ \
  --genomeFastaFiles genome.fa \
  --sjdbGTFfile genes.gtf \
  --runThreadN 8

# Align
STAR --genomeDir star_index/ \
  --readFilesIn R1.fq.gz R2.fq.gz \
  --readFilesCommand zcat \
  --outSAMtype BAM SortedByCoordinate \
  --runThreadN 8 \
  --outFileNamePrefix sample_
```

### Bowtie2 — Fast Short Read Alignment
```bash
# Index
bowtie2-build reference.fa reference

# Align
bowtie2 -x reference -1 R1.fq.gz -2 R2.fq.gz -p 8 | samtools sort -o aligned.bam
```

## QC Tools

### FastQC
```bash
fastqc -t 4 -o qc_output/ *.fastq.gz
```

### fastp — Trimming + QC
```bash
fastp -i R1.fq.gz -I R2.fq.gz \
  -o R1.clean.fq.gz -O R2.clean.fq.gz \
  -h report.html -j report.json \
  --detect_adapter_for_pe \
  --thread 4
```

### MultiQC — Aggregate Reports
```bash
multiqc qc_output/ -o multiqc_report/
```

## Quantification

### featureCounts — Gene Counts
```bash
featureCounts -T 8 -p -t exon -g gene_id \
  -a genes.gtf \
  -o counts.txt \
  aligned.bam
```

### Salmon — Fast Quantification
```bash
# Index
salmon index -t transcripts.fa -i salmon_index

# Quantify
salmon quant -i salmon_index -l A \
  -1 R1.fq.gz -2 R2.fq.gz \
  -o salmon_output/
```

## Resource Requirements

| Tool | RAM (Human) | Time (30x WGS) |
|------|-------------|----------------|
| BWA index | ~6 GB | 1 hour |
| BWA mem | ~6 GB | 10-20 hours |
| STAR index | ~32 GB | 30 min |
| STAR align | ~32 GB | 30 min/sample |
| GATK HaplotypeCaller | ~8 GB | 20+ hours |
| bcftools mpileup | ~2 GB | 2-4 hours |
