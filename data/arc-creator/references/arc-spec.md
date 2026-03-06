# ARC Specification Reference (v3.0.0-draft.2)

## Directory Structure

```
<arc-root>/
├── isa.investigation.xlsx          # MUST exist
├── studies/
│   └── <study_name>/
│       ├── isa.study.xlsx          # MUST exist per study
│       ├── isa.datamap.xlsx        # optional
│       ├── resources/              # material/sample files
│       └── protocols/              # optional, additional payload
├── assays/
│   └── <assay_name>/
│       ├── isa.assay.xlsx          # MUST exist per assay
│       ├── isa.datamap.xlsx        # optional
│       ├── dataset/                # assay data files (immutable)
│       └── protocols/              # optional, additional payload
├── workflows/
│   └── <workflow_name>/
│       ├── workflow.cwl            # MUST exist per workflow
│       ├── docker-compose.yml      # optional
│       └── isa.workflow.xlsx       # optional
├── runs/
│   └── <run_name>/
│       ├── run.cwl                 # MUST exist per run
│       ├── run.yml
│       └── [output files]
└── README.md                       # additional payload
```

## ISA-XLSX Files

### Investigation File (isa.investigation.xlsx)

Sheet `isa_investigation` MUST contain:
- ONTOLOGY SOURCE REFERENCE
- INVESTIGATION (Identifier, Title, Description, Submission Date, Public Release Date)
- INVESTIGATION PUBLICATIONS (PubMed ID, DOI, Author List, Title, Status)
- INVESTIGATION CONTACTS (Last Name, First Name, Mid Initials, Email, Phone, Fax, Address, Affiliation, Roles)

MAY contain:
- STUDY sections (one per study): Identifier, Title, Description, Submission Date, Public Release Date
- STUDY DESIGN DESCRIPTORS (Type, Type Term Accession Number, Type Term Source REF)
- STUDY PUBLICATIONS
- STUDY FACTORS (Name, Type, Type Term Accession Number, Type Term Source REF)
- STUDY ASSAYS (Measurement Type, Technology Type, Technology Platform, File Name)
- STUDY PROTOCOLS (Name, Type, Description, URI, Version, Parameters Name, Components Name, Components Type)
- STUDY CONTACTS

### Study File (isa.study.xlsx)

Sheet `isa_study` MUST contain:
- STUDY (Identifier, Title, Description)
- STUDY DESIGN DESCRIPTORS
- STUDY PUBLICATIONS
- STUDY CONTACTS

MAY contain:
- STUDY FACTORS
- STUDY ASSAYS
- STUDY PROTOCOLS

SHOULD contain Annotation Table sheets describing sample provenance:
- Sources → Samples (with Characteristics, Factors, Parameters, Protocols)

### Assay File (isa.assay.xlsx)

Sheet `isa_assay` MUST contain:
- ASSAY (Measurement Type, Technology Type, Technology Platform)
- ASSAY PERFORMERS

SHOULD contain Annotation Table sheets:
- Samples → Data (with Parameters, Protocols, Components)

## Annotation Table Columns

| Column Type | Header Pattern | Description |
|---|---|---|
| Input | `Source Name` or `Sample Name` | Starting material |
| Output | `Sample Name` or `Data File Name` | Resulting material/data |
| Protocol | `Protocol REF` | Reference to a protocol |
| Characteristic | `Characteristic [<term>]` | Sample property (e.g., organism, age) |
| Factor | `Factor [<term>]` | Experimental variable |
| Parameter | `Parameter [<term>]` | Protocol parameter |
| Component | `Component [<term>]` | Protocol component |
| Unit | `Unit` | Unit for preceding value column |
| Term Source REF | `Term Source REF` | Ontology source |
| Term Accession | `Term Accession Number` | Ontology term ID |
| Comment | `Comment [<name>]` | Free-text annotation |

## Key Ontologies

- **NCBITAXON** — Organism taxonomy
- **OBI** — Biomedical investigations
- **EFO** — Experimental factors
- **CHEBI** — Chemical entities
- **PATO** — Phenotype and trait
- **UO** — Units of measurement
- **DPBO** — DataPLANT Biology Ontology

## Naming Conventions

- File names: ASCII only (A-Za-z0-9._!#$%&+,;=@^)
- Avoid spaces and shell metacharacters
- Study/assay identifiers: lowercase-with-hyphens recommended
- Dates: ISO 8601 format (YYYY-MM-DD)

## ARC Representation

- ARCs are Git repositories (Git ≥ 2.26 + Git-LFS ≥ 2.12.0)
- Files > 100 MB should use Git LFS
- All branch heads MUST adhere to ARC schema
- Removing .git invalidates the ARC
