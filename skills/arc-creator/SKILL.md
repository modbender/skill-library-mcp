---
name: arc-creator
description: Create and populate Annotated Research Contexts (ARCs) following the nfdi4plants ARC specification. Use when creating a new ARC, adding studies/assays/workflows/runs, annotating ISA metadata, organizing research data into ARC structure, or pushing ARCs to a DataHUB. Guides the user interactively through all required and optional metadata fields.
---

# ARC Creator

Create FAIR Digital Objects following the nfdi4plants ARC specification v3.0.0.

## Prerequisites

- `git` and `git-lfs` installed
- ARC Commander CLI at `~/bin/arc` (optional but recommended)
- For DataHUB sync: Personal Access Token for git.nfdi4plants.org or datahub.hhu.de

## Interactive ARC Creation Workflow

Guide the user through these phases in order. Ask questions conversationally — don't dump all questions at once. Batch 2-4 related questions per message.

### Phase 1: Investigation Setup

Ask the user:
1. **Investigation identifier** (short, lowercase-hyphenated, e.g. `cold-stress-arabidopsis`)
2. **Title** (concise name for the investigation)
3. **Description** (textual description of the research goals)
4. **Where to store the ARC locally** (suggest `/home/uranus/arc-projects/<identifier>/`)

Then run `scripts/create_arc.sh <path> <identifier>` and set investigation metadata via:
```bash
arc investigation update -i "<id>" --title "<title>" --description "<desc>"
```

### Phase 2: Studies

For each study, ask:
1. **Study identifier** (e.g. `plant-growth`)
2. **Title and description**
3. **Organism** (for Characteristic [Organism])
4. **Growth conditions** (temperature, light, medium, etc.)
5. **Source materials** (what goes in — seeds, cell lines, etc.)
6. **Sample materials** (what comes out — leaves, roots, extracts, etc.)
7. **Protocols** — does the user have protocol documents to include?
8. **Factors** — what experimental variables are being tested? (e.g., temperature, genotype, treatment)

Create with:
```bash
arc study init --studyidentifier "<id>"
arc study update --studyidentifier "<id>" --title "<title>" --description "<desc>"
```

Copy protocol files to `studies/<id>/protocols/`.
Copy resource files to `studies/<id>/resources/`.

### Phase 3: Assays

For each assay, ask:
1. **Assay identifier** (e.g. `proteomics-ms`, `rnaseq`, `sugar-measurement`)
2. **Measurement type** (e.g., protein expression profiling, transcription profiling, metabolite profiling)
3. **Technology type** (e.g., mass spectrometry, nucleotide sequencing, plate reader)
4. **Technology platform** (e.g., Illumina NovaSeq, Bruker timsTOF)
5. **Data files** — where are the raw data files? (will go into `assays/<id>/dataset/`)
6. **Processed data** — any processed output files?
7. **Protocols** — assay-specific protocols?
8. **Performers** — who performed this assay? (name, affiliation, role)

Create with:
```bash
arc assay init -a "<id>" --measurementtype "<type>" --technologytype "<tech>"
```

Copy data to `assays/<id>/dataset/`, protocols to `assays/<id>/protocols/`.

### Phase 4: Workflows (optional)

Ask if there are computational analysis steps. For each:
1. **Workflow identifier** (e.g. `deseq2-analysis`, `heatmap-generation`)
2. **Description** of what it does
3. **Code files** (scripts, notebooks)
4. **Dependencies** (Python packages, R libraries, Docker image)

Place code in `workflows/<id>/`.
Note: `workflow.cwl` is REQUIRED by spec but often created later. Inform user.

### Phase 5: Runs (optional)

Ask if there are computation outputs. For each:
1. **Run identifier**
2. **Which workflow produced it**
3. **Output files** (figures, tables, processed data)

Place outputs in `runs/<id>/`.

### Phase 6: Contacts & Publications

Ask:
1. **Investigation contacts** (name, email, affiliation, role — at minimum the PI)
2. **Publications** (if any — DOI, PubMed ID, title, authors)

Add via:
```bash
arc investigation person register --lastname "<last>" --firstname "<first>" --email "<email>" --affiliation "<aff>"
```

### Phase 7: Git Commit & DataHUB Sync

1. Configure git user:
```bash
git config user.name "<name>"
git config user.email "<email>"
```

2. Commit:
```bash
git add -A
git commit -m "Initial ARC: <investigation title>"
```

3. Ask if the user wants to push to a DataHUB. If yes:
   - Ask which host (git.nfdi4plants.org, datahub.hhu.de, etc.)
   - Create remote repo (via browser or API)
   - Set remote and push

## ISA Metadata Reference

For detailed ISA-XLSX fields, annotation table columns, and ontology references, read `references/arc-spec.md`.

## Key Reminders

- **Assay data is immutable** — never modify files in `assays/<id>/dataset/` after initial placement
- **Studies describe materials**, assays describe measurements
- **Workflows are code**, runs are outputs
- **Git LFS** for files > 100 MB: `git lfs track "*.fastq.gz" "*.bam" "*.raw"`
- **Don't store ARCs on OneDrive/Dropbox** — Git + cloud sync causes conflicts
- ARC Commander CLI reference: `arc <subcommand> --help`
