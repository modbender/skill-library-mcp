# Pinal: De Novo Protein Design from Natural Language

## Overview

Pinal is a multi-stage neural architecture that transforms natural language descriptions into protein sequences through intermediate structural representations. It supports both de novo design (creating new proteins from text) and structure-based redesign (modifying existing proteins).

### When to Use Pinal
- De novo protein design from functional descriptions
- Redesign existing proteins for new functions
- Generate proteins from natural language prompts
- Initial exploration before detailed design

### When NOT to Use
- Need precise backbone control → Use BoltzGen
- Need ligand-aware design → Use LigandMPNN
- Need stability optimization → Use ThermoMPNN
- Need structure from sequence → Use Boltz/Chai

## Design Modes

### 1. Text-Based De Novo Design

Create entirely new proteins from functional descriptions.

**Tool**: `submit_pinal_text_design`

**Good Descriptions**:
- "Design an enzyme that binds ATP and catalyzes phosphorylation"
- "Membrane protein with seven transmembrane helices for GPCR signaling"
- "Antibody that binds to SARS-CoV-2 spike protein"
- "Create a protein that catalyzes the hydrolysis of cellulose"

**Description Best Practices**:
- Specify biochemical activity: "catalyzes phosphorylation"
- Include binding partners: "binds ATP"
- Describe structural features: "seven transmembrane helices"
- Mention cellular context: "membrane protein"
- Be specific about function: "hydrolysis of cellulose" not just "enzyme"
- Keep it concise (not too long)

### 2. Structure-Based Redesign

Modify existing proteins using structure + description.

**Tool**: `submit_pinal_structure_design`

**Example Goals**:
- "Redesign this protein to bind calcium ions with high affinity"
- "Modify the active site to improve thermal stability"
- "Change surface residues to improve solubility"
- "Enhance binding affinity for the current ligand"

## Parameters

### Text-Based Design

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `description` | string | 10-1000 chars | required | Functional description |
| `num_sequences` | int | 1-10 | 5 | Sequences to generate |
| `output_directory` | string | - | auto | Output path |

### Structure-Based Redesign

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_file_path` | string | required | PDB file path |
| `redesign_description` | string | required | Redesign goal (10-1000 chars) |
| `chain_id` | string | "A" | Chain to redesign (single char) |
| `output_directory` | string | auto | Output path |

## Output

### Generated Files
```
protein_design/{job_id}/
├── sequences.txt        # Generated sequences
├── metadata.json       # Job parameters, summary
└── design_details.txt  # Additional info
```

### Sequence Format
```
>Sequence_1_Highest_Confidence
DFQKAKFAVQQLLKAWEAAPLLVLVVSVQLSCLAVVVQQKDKDALVVSCV...

>Sequence_2_Second_Best
NFQKTKFTVQELLKAWEAAPLLVLVVSVQLSCLAVVVQQKDKDALVVSCV...
```

## API Usage

### De Novo Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_pinal_text_design" \
  -F 'params={
    "description": "Design an enzyme that binds ATP and catalyzes phosphorylation reactions with high specificity",
    "num_sequences": 3
  }'
```

### Membrane Protein Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_pinal_text_design" \
  -F 'params={
    "description": "Create a membrane protein with seven transmembrane helices for GPCR-like signaling",
    "num_sequences": 5
  }'
```

### Structure-Based Redesign
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_pinal_structure_design" \
  -F 'params={
    "input_file_path": "structures/existing_enzyme.pdb",
    "redesign_description": "Redesign the active site to improve binding affinity for substrate by 5-fold",
    "chain_id": "A"
  }'
```

### Get Tool Info
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=get_pinal_tool_info" \
  -F 'params={}'
```

## Expected Runtime

| Mode | Sequences | Time |
|------|-----------|------|
| De Novo | 5 | 10-20 min |
| Structure Redesign | 1 | 5-15 min |

## Rate Limits

- **Per minute**: 2 jobs
- **Per day**: 10 jobs
- **Description**: 10-1000 characters
- **Sequences**: 1-10 per job

## Common Mistakes

### Wrong: Vague description
```
❌ "Design an enzyme"
   → Too generic, poor results
```
```
✅ "Design an enzyme that binds ATP and catalyzes phosphorylation of serine residues"
   → Specific function, binding, mechanism
```

### Wrong: Description too long
```
❌ Very long paragraph with excessive detail
   → May confuse the model
```
```
✅ Concise 1-2 sentence description
   → Clear, focused intent
```

### Wrong: Multi-chain redesign
```
❌ chain_id: "AB" or chain_id: "A,B"
```
```
✅ chain_id: "A"  # Single character only
   → Redesign one chain at a time
```

## Quality Assessment

### What to Check
- **Sequence diversity**: Are generated sequences different?
- **Length**: Reasonable for intended function?
- **Composition**: Unusual amino acid patterns?

### Validation Steps
1. **Structure prediction**: Run Boltz/Chai on designed sequences
2. **Sequence analysis**: Check for unusual patterns
3. **Similarity search**: Compare to known proteins

## Workflow: Validate Pinal Designs

```
1. Generate sequences
   → submit_pinal_text_design

2. Predict structures
   → submit_boltz_prediction for each sequence
   → Check pLDDT > 0.7

3. Analyze confidence
   → Keep sequences with good predicted folds

4. Compare sequences
   → Check diversity
   → Identify common features

5. Select for experimental testing
   → Top candidates by confidence
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Poor sequences | Vague description | Be more specific |
| Timeout | Long description | Shorten, focus on key features |
| Chain error | Multi-character chain | Use single letter (A, B, C) |
| Short sequences | Description doesn't imply length | Mention size if needed |

## Best Practices

1. **Be specific**: Detailed function > generic terms
2. **Include context**: Binding partners, cellular location
3. **Start with 3-5 sequences**: Balance exploration and cost
4. **Validate with Boltz**: Predict structures of designed sequences
5. **Iterate**: Refine description based on results
6. **Combine approaches**: Use Pinal for initial design, ProteinMPNN for optimization

## Sample Output

### Job Response
```json
{
  "success": true,
  "job_id": "pinal_text_abc123",
  "message": "Job submitted successfully",
  "estimated_runtime": "10-20 minutes"
}
```

### Output Sequences
```
>Sequence_1_Highest_Confidence
DFQKAKFAVQQLLKAWEAAPLLVLVVSVQLSCLAVVVQQKDKDALVVSCV...

>Sequence_2_Second_Best
NFQKTKFTVQELLKAWEAAPLLVLVVSVQLSCLAVVVQQKDKDALVVSCV...
```

### What Good Output Looks Like
- **Diverse sequences**: Not all identical
- **Reasonable length**: 100-400 aa typical for enzymes
- **Standard amino acids**: Only 20 standard AAs

## Typical Performance

| Mode | Time |
|------|------|
| De novo (5 seqs) | 10-20 min |
| Structure redesign | 5-15 min |

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# Count generated sequences
grep -c "^>" sequences.txt
```

## Pinal vs Other Design Tools

| Feature | Pinal | BoltzGen | ProteinMPNN |
|---------|-------|----------|-------------|
| Input | Text description | YAML + structure | Backbone PDB |
| De novo | **Yes** | **Yes** | No |
| Structure control | Low | **High** | **High** |
| Binding site | Text-guided | **Precise** | Backbone-derived |
| Complexity | **Low** | High | Low |
| Use case | **Exploration** | Precision design | Fixed backbone |

---

**Next**: Validate designed sequences with `Boltz/Chai` structure prediction → Optimize with `ProteinMPNN`.
