# Variant Calling Pipeline — Bioinformatics

## Overview

```
FASTQ → Align → Mark Duplicates → Call Variants → Filter → Annotate
```

## Quick Pipeline (bcftools)

Fastest approach for simple SNV/indel calling:

```bash
# Align
bwa mem -t 8 -R '@RG\tID:sample\tSM:sample\tPL:ILLUMINA' \
  reference.fa R1.fq.gz R2.fq.gz | \
  samtools sort -o aligned.bam -

samtools index aligned.bam

# Call variants
bcftools mpileup -Ou -f reference.fa aligned.bam | \
  bcftools call -mv -Oz -o variants.vcf.gz

bcftools index variants.vcf.gz

# Filter
bcftools filter -s LowQual -e 'QUAL<20 || DP<10' variants.vcf.gz \
  -Oz -o variants.filtered.vcf.gz
```

## Full GATK Pipeline

For clinical/publication-grade variant calling.

### Step 1: Align with Read Groups

```bash
bwa mem -t 8 \
  -R "@RG\tID:${sample}\tSM:${sample}\tPL:ILLUMINA\tLB:lib1" \
  reference.fa R1.fq.gz R2.fq.gz | \
  samtools sort -o ${sample}.bam -

samtools index ${sample}.bam
```

### Step 2: Mark Duplicates

```bash
gatk MarkDuplicates \
  -I ${sample}.bam \
  -O ${sample}.dedup.bam \
  -M ${sample}.dup_metrics.txt \
  --CREATE_INDEX true
```

### Step 3: Base Quality Recalibration (BQSR)

```bash
# Build recalibration model
gatk BaseRecalibrator \
  -R reference.fa \
  -I ${sample}.dedup.bam \
  --known-sites dbsnp.vcf.gz \
  --known-sites known_indels.vcf.gz \
  -O ${sample}.recal_data.table

# Apply recalibration
gatk ApplyBQSR \
  -R reference.fa \
  -I ${sample}.dedup.bam \
  --bqsr-recal-file ${sample}.recal_data.table \
  -O ${sample}.recal.bam
```

### Step 4: Call Variants (HaplotypeCaller)

```bash
# Single sample
gatk HaplotypeCaller \
  -R reference.fa \
  -I ${sample}.recal.bam \
  -O ${sample}.g.vcf.gz \
  -ERC GVCF

# Joint genotyping (multiple samples)
gatk CombineGVCFs \
  -R reference.fa \
  --variant sample1.g.vcf.gz \
  --variant sample2.g.vcf.gz \
  -O combined.g.vcf.gz

gatk GenotypeGVCFs \
  -R reference.fa \
  -V combined.g.vcf.gz \
  -O joint.vcf.gz
```

### Step 5: Variant Quality Score Recalibration (VQSR)

```bash
# SNPs
gatk VariantRecalibrator \
  -R reference.fa \
  -V joint.vcf.gz \
  --resource:hapmap,known=false,training=true,truth=true,prior=15.0 hapmap.vcf.gz \
  --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
  -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
  -mode SNP \
  -O snps.recal \
  --tranches-file snps.tranches

gatk ApplyVQSR \
  -R reference.fa \
  -V joint.vcf.gz \
  --recal-file snps.recal \
  --tranches-file snps.tranches \
  -mode SNP \
  -O joint.snps.vcf.gz

# Indels (similar process)
```

### Step 6: Hard Filtering (Alternative to VQSR)

For small sample sizes where VQSR doesn't work:

```bash
# SNPs
gatk VariantFiltration \
  -R reference.fa \
  -V joint.vcf.gz \
  --filter-expression "QD < 2.0" --filter-name "QD2" \
  --filter-expression "FS > 60.0" --filter-name "FS60" \
  --filter-expression "MQ < 40.0" --filter-name "MQ40" \
  --filter-expression "MQRankSum < -12.5" --filter-name "MQRankSum-12.5" \
  --filter-expression "ReadPosRankSum < -8.0" --filter-name "ReadPosRankSum-8" \
  -O filtered.vcf.gz
```

## Annotation

### ANNOVAR

```bash
# Download databases
annotate_variation.pl -buildver hg38 -downdb -webfrom annovar refGene humandb/
annotate_variation.pl -buildver hg38 -downdb -webfrom annovar clinvar_20230416 humandb/

# Annotate
table_annovar.pl variants.vcf.gz humandb/ \
  -buildver hg38 \
  -out annotated \
  -protocol refGene,clinvar_20230416,gnomad_genome \
  -operation g,f,f \
  -vcfinput
```

### SnpEff

```bash
# Download database
snpEff download -v GRCh38.99

# Annotate
snpEff -Xmx8g GRCh38.99 variants.vcf.gz > variants.annotated.vcf
```

### VEP (Ensembl)

```bash
vep -i variants.vcf.gz \
  -o variants.vep.vcf \
  --cache --offline \
  --assembly GRCh38 \
  --vcf \
  --everything
```

## Filtering Examples

```bash
# PASS variants only
bcftools view -f PASS variants.vcf.gz

# High quality SNPs
bcftools view -v snps -i 'QUAL>30 && DP>20 && AF>0.2' variants.vcf.gz

# Rare variants (gnomAD AF < 0.01)
bcftools view -i 'gnomAD_AF<0.01 || gnomAD_AF="."' annotated.vcf.gz

# Coding variants
bcftools view -i 'ANN ~ "missense" || ANN ~ "nonsense" || ANN ~ "frameshift"' annotated.vcf.gz

# Extract specific samples
bcftools view -s sample1,sample2 joint.vcf.gz
```

## Somatic Variant Calling

For tumor-normal pairs:

```bash
# Mutect2
gatk Mutect2 \
  -R reference.fa \
  -I tumor.bam \
  -I normal.bam \
  -normal normal_sample \
  --germline-resource gnomad.vcf.gz \
  --panel-of-normals pon.vcf.gz \
  -O somatic.vcf.gz

# Filter
gatk FilterMutectCalls \
  -R reference.fa \
  -V somatic.vcf.gz \
  -O somatic.filtered.vcf.gz
```

## Common Issues

### No Variants Called
- Check BAM alignment rate
- Verify reference matches
- Check chromosome naming (chr1 vs 1)

### Too Many Variants
- Relax BQSR (or skip for non-human)
- Check sample contamination

### Annotation Fails
- Version mismatch (genome vs annotation)
- Chromosome naming inconsistency

## Resource Requirements

| Step | RAM | Time (30x Human WGS) |
|------|-----|----------------------|
| BWA alignment | 6 GB | 10-20 hours |
| Mark duplicates | 16 GB | 2-3 hours |
| BQSR | 8 GB | 4-6 hours |
| HaplotypeCaller | 8 GB | 20+ hours |
| Joint genotyping | 16 GB | 2-4 hours |
| VQSR | 8 GB | 1 hour |
