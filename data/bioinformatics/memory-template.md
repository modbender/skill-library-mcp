# Memory Template — Bioinformatics

Create `~/bioinformatics/memory.md` with this structure:

```markdown
# Bioinformatics Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Environment
compute: local | hpc | cloud
cores: 8
memory_gb: 32

## Reference Genomes
<!-- Track which references are downloaded and used -->

## Active Projects
<!-- Current analyses with status -->

## Tool Preferences
<!-- User's explicitly stated tool preferences -->

## Notes
<!-- Notes from user's explicit instructions -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Active use | Work normally |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Work with what you have |

## Example After First Session

```markdown
# Bioinformatics Memory

## Status
status: ongoing
version: 1.0.0
last: 2024-01-15
integration: done

## Environment
compute: local
cores: 8
memory_gb: 32

## Reference Genomes
- Human GRCh38: ~/refs/hg38/
- Mouse GRCm39: ~/refs/mm39/

## Active Projects
- RNA-seq tumor samples: ~/projects/tumor_rnaseq/
  - Status: QC complete, alignment next
  - Samples: 12 tumor, 4 normal

## Tool Preferences
- Alignment: STAR (for RNA-seq), BWA-MEM2 (for DNA)
- QC: fastp over trimmomatic

## Notes
- User prefers MultiQC report after QC
- Separate BAMs per sample before merge

---
*Updated: 2024-01-15*
```

## Key Principles

- **Only save what user explicitly shares** — do not infer preferences
- **Update last on each use**
- **Projects section** — track analyses user mentions to resume context
- **Ask before saving sensitive information**
