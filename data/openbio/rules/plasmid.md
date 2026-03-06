# Plasmid Tools

Analyze and edit plasmid files (GenBank, SnapGene, FASTA).

> **Note**: `show_plasmid` is a frontend-only visualization tool (not available via the SDK API). Use `parse_plasmid_file` for analysis and `edit_plasmid` for editing.

## When to Use

Use plasmid tools when:
1. Analyzing plasmid contents (sequence length, GC%, feature inventory)
2. Inserting, deleting, or replacing sequence in a plasmid
3. Managing annotations (create, update, delete features)
4. Updating plasmid metadata (name, description, topology)
5. Converting a SnapGene `.dna` file to GenBank `.gbk`

## Decision Tree

```
What plasmid task?
│
├─ Get text summary for analysis?
│   └─ parse_plasmid_file
│       Returns text with length, GC%, features
│
└─ Edit plasmid?
    └─ edit_plasmid
        ├─ Insert DNA → op: "insert_sequence"
        ├─ Delete region → op: "delete_range"
        ├─ Replace region → op: "replace_range"
        ├─ Add annotation → op: "create_annotation"
        ├─ Modify annotation → op: "update_annotation"
        ├─ Remove annotation → op: "delete_annotation"
        └─ Change metadata → op: "set_metadata"
```

**Getting feature IDs**: To get `openbio_id` values needed for `update_annotation` or `delete_annotation`, use `edit_plasmid` with a read-only operation like `set_metadata` — the response includes full feature data with `openbio_id` in qualifiers. Alternatively, `parse_plasmid_file` returns feature coordinates that you can use for `create_annotation`.

## Coordinate System

All sequence coordinates are **0-indexed, end-exclusive** `[start, end)`.

| Convention | Value | Example |
|-----------|-------|---------|
| First base | Position 0 | Base 1 in GenBank = position 0 in API |
| Range `[10, 20)` | Bases at positions 10–19 | 10 bp long |
| Insert at position 5 | New bases appear before current position 5 | |

### GenBank-to-API Conversion

GenBank files use 1-based, inclusive coordinates. Convert:
```
API_start = GenBank_start - 1
API_end   = GenBank_end            (no change — GenBank end is inclusive, API end is exclusive)
```

Example: GenBank feature at `101..500` → API `start: 100, end: 500`.

### Sequential Operations and Coordinate Shifts

Operations in `edit_plasmid` are applied in order. Each operation sees coordinates from the state **after all prior operations**. Insertions and deletions shift downstream coordinates.

```
Example: Insert 10 bp at position 100, then delete [200, 210)
- After insert: sequence is 10 bp longer
- The delete sees the post-insert coordinates
- Original position 200 is now at position 210
- So delete [210, 220) to target the same original region
```

### Operation Ordering Best Practices

1. **Delete annotations before sequence modifications.** Annotation operations use `openbio_id` to find features. Sequence operations (insert, delete, replace) do not change IDs, but if a feature is fully inside a deleted range, it is removed — making subsequent `delete_annotation` or `update_annotation` calls for that ID fail with `annotation_not_found`.

2. **Create annotations after sequence modifications.** After an insert or delete, downstream coordinates shift. Create new annotations using post-edit coordinates (which are the coordinates you see in the response from the sequence operation).

3. **Use `set_metadata` as a read-only probe.** To get current `openbio_id` values without changing anything, call `edit_plasmid` with only a `set_metadata` operation (e.g., just setting the description to its current value). The response includes the full feature list with IDs.

Recommended ordering within a batch:
```
1. delete_annotation (by ID — before sequence changes)
2. delete_range / insert_sequence / replace_range (sequence edits)
3. create_annotation (using post-edit coordinates)
4. update_annotation (for features that survived the edit)
5. set_metadata (order doesn't matter)
```

## Feature Handling Modes

The `feature_handling` parameter controls what happens when a sequence edit overlaps existing feature boundaries.

| Mode | Behavior | When to Use |
|------|----------|-------------|
| `strict` (default) | Raises `ambiguous_feature_overlap` error if edit partially overlaps a feature | Safe default — prevents accidental feature corruption |
| `adjust` | Automatically clips or extends feature bounds to accommodate the edit | When you intentionally want to modify regions that overlap features |

### strict mode
- Insertions inside a feature body → error
- Deletions that partially overlap a feature → error
- Edits on feature boundaries or outside features → allowed
- Features fully contained within a deleted range → removed silently

### adjust mode
- Insertions inside a feature → feature is extended to encompass insertion
- Deletions that clip feature start → feature start moves to edit boundary
- Deletions that clip feature end → feature end moves to edit start
- Features fully deleted → removed silently

## Validation Modes

The `validation_mode` parameter controls what safety checks are run before applying edits.

| Mode | Checks | When to Use |
|------|--------|-------------|
| `basic` (default) | Coordinate bounds, sequence validity (IUPAC nucleotides), range constraints | General editing |
| `cloning_safe` | All `basic` checks + CDS overlap detection, frameshift warnings, internal stop codon warnings | When editing near or within CDS features |

### cloning_safe details

When `validation_mode: "cloning_safe"`:
- Detects if any sequence operation overlaps a CDS feature
- Warns if insertion/replacement length is not a multiple of 3 (potential frameshift)
- Warns if replacement sequence contains in-frame stop codons (TAA, TAG, TGA)
- Results appear in `validation_summary.warnings` and `validation_summary.affected_features`

When combined with `strict_validation: true`, validation errors block the edit entirely and no changes are saved.

## Circular Plasmid Editing

Circular topology is auto-detected from the plasmid file's metadata. When editing circular plasmids, the engine uses circular-aware coordinate math automatically — no special parameters needed.

### What works automatically

- **Downstream feature shifting**: Insertions, deletions, and replacements shift only downstream features (features at or after the edit position). Upstream features are untouched.
- **Origin-crossing features**: Features that span the origin (e.g., a promoter from position 4900 to position 200 on a 5000 bp plasmid) are represented as compound locations and handled correctly during edits.
- **Wrap-around after shift**: If a feature is shifted past the end of the sequence, its coordinates wrap around the origin automatically.

### Coordinates are still linear

Even on circular plasmids, coordinates are 0-based and end-exclusive `[start, end)` within the sequence length. You do not need to handle wrap-around yourself — the engine does it. Position 0 is the origin; position `length` is after the last base (same as position 0 on a circle).

### Editing near the origin

Insertions at position 0 push all features downstream. Insertions at the end of the sequence (position = sequence length) append without shifting any features. Both work correctly on circular plasmids.

## Supported File Formats

| Format | Extensions | Read | Edit | Notes |
|--------|-----------|------|------|-------|
| GenBank | `.gb`, `.gbk` | Yes | Yes | In-place edit by default |
| SnapGene | `.dna` | Yes | Yes (input only) | Output saved as `.gbk` (original `.dna` unchanged) |
| FASTA | `.fasta`, `.fa` | Yes | No | No annotations; view/parse only |

## Tools Reference

### show_plasmid — Interactive plasmid map (frontend only)

> **Not available via the SDK API.** This tool renders an interactive plasmid map in the OpenBio web frontend. It is not callable from external SDK clients.

### parse_plasmid_file — Text summary

Returns a human-readable text summary with sequence length, GC%, topology, and feature list grouped by type.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=parse_plasmid_file" \
  -F 'params={"filesystem_path": "plasmids/pUC19.gb"}'
```

Returns: Plain text with plasmid name, length, topology, GC%, and features listed as `name: start..end (+/-, N bp)`.

### edit_plasmid — Sequence and annotation editing

Applies one or more operations transactionally. All operations succeed or none are saved. The response includes the full updated feature list with `openbio_id` values in qualifiers — use these IDs for subsequent `update_annotation` or `delete_annotation` calls.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filesystem_path` | string | required | Path to plasmid file (`.gb`, `.gbk`, `.dna`) |
| `operations` | array | required | Ordered list of edit operations |
| `output_path` | string | null | Output file path (`.gb`/`.gbk`). Defaults to in-place for GenBank, `<name>.edited.gbk` for `.dna` |
| `validation_mode` | string | `"basic"` | `"basic"` or `"cloning_safe"` |
| `strict_validation` | bool | false | When true, validation errors block persistence |
| `feature_handling` | string | `"strict"` | `"strict"` or `"adjust"` |
| `preserve_semantic_feature_type` | bool | true | Map non-standard feature types to `misc_feature` while preserving original in qualifiers |

#### insert_sequence

Insert a nucleotide sequence at a specific position.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "insert_sequence", "position": 100, "sequence": "ATGCGATCGATCG"}
    ]
  }'
```

#### delete_range

Delete a range of sequence `[start, end)`.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "delete_range", "start": 100, "end": 200}
    ]
  }'
```

#### replace_range

Replace sequence in `[start, end)` with new sequence.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "replace_range", "start": 100, "end": 200, "sequence": "ATGCGATCG"}
    ]
  }'
```

#### create_annotation

Add a new annotation feature.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {
        "op": "create_annotation",
        "name": "GFP",
        "type": "CDS",
        "start": 100,
        "end": 820,
        "strand": 1,
        "color": "#4B82DB"
      }
    ]
  }'
```

#### update_annotation

Modify an existing annotation by its `openbio_id`. Get the ID from a prior `edit_plasmid` response (the `features` array includes `openbio_id` in qualifiers).

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {
        "op": "update_annotation",
        "annotation_id": "abc-123-def",
        "name": "eGFP",
        "color": "#00FF00"
      }
    ]
  }'
```

Only the fields you include are updated; omitted fields keep their current values.

#### delete_annotation

Remove an annotation by its `openbio_id`.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "delete_annotation", "annotation_id": "abc-123-def"}
    ]
  }'
```

#### set_metadata

Update plasmid metadata (name, description, topology).

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "set_metadata", "name": "pUC19-GFP", "topology": "circular"}
    ]
  }'
```

#### Multi-operation batch

Operations are applied sequentially. Coordinates in later operations refer to the state after prior operations.

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "insert_sequence", "position": 100, "sequence": "ATGCGATCG"},
      {"op": "create_annotation", "name": "insert_tag", "type": "misc_feature", "start": 100, "end": 109, "strand": 1},
      {"op": "set_metadata", "name": "pUC19-tagged"}
    ]
  }'
```

#### cloning_safe validation example

```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=edit_plasmid" \
  -F 'params={
    "filesystem_path": "plasmids/pUC19.gb",
    "operations": [
      {"op": "replace_range", "start": 100, "end": 106, "sequence": "ATGATG"}
    ],
    "validation_mode": "cloning_safe",
    "strict_validation": true,
    "feature_handling": "adjust"
  }'
```

## Common Mistakes

### 1. Using 1-indexed coordinates

```
Wrong:  {"op": "insert_sequence", "position": 1, "sequence": "ATG"}
        → Inserts BEFORE position 1, i.e., after the first base

Right:  {"op": "insert_sequence", "position": 0, "sequence": "ATG"}
        → Inserts at the very start of the sequence
```

GenBank position 1 = API position 0. Always subtract 1 from GenBank start coordinates.

### 2. Forgetting coordinate shifts after prior operations

```
Wrong:  Insert 10 bp at pos 50, then delete [100, 110)
        → Actually deletes positions 100-109 in the NEW sequence,
          which were originally at positions 90-99

Right:  Insert 10 bp at pos 50, then delete [110, 120)
        → Accounts for the 10 bp shift from the prior insert
```

### 3. Using strict mode when edit overlaps features

```
Wrong:  Delete a region that partially overlaps a feature with default feature_handling
        → Raises "ambiguous_feature_overlap" error

Right:  Set feature_handling: "adjust" when you intend to edit through features
        → Features are automatically clipped/extended
```

### 4. Not using cloning_safe for CDS edits

```
Wrong:  Replace 5 bp inside a CDS with basic validation
        → No warning about frameshift (5 is not a multiple of 3)

Right:  Set validation_mode: "cloning_safe"
        → Warning: "non-triplet length change (5 bp) affecting CDS"
```

### 5. Trying to edit FASTA files

```
Wrong:  edit_plasmid with filesystem_path: "seq.fasta"
        → Error: "Unsupported edit format '.fasta'"

Right:  Use .gb, .gbk, or .dna files for editing
        FASTA files are read-only (no annotation support)
```

### 6. Editing in-place during testing

```
Risky:  edit_plasmid with only filesystem_path (overwrites original)
        → If the edit is wrong, the original file is gone

Safe:   Set output_path to a separate file during testing
        → Original is preserved; inspect the output before committing
```

Use `output_path` when experimenting. Once you've confirmed the edit is correct, you can either repeat without `output_path` (for in-place) or keep the output file.

## Common Workflows

### Workflow 1: Insert gene into plasmid

```
1. Analyze the plasmid
   → parse_plasmid_file to see features and find insertion site

2. Find restriction sites (using molecular biology tools)
   → restriction_find_sites to locate unique cutters near target site

3. Insert the gene sequence
   → edit_plasmid with insert_sequence at the chosen position

4. Annotate the new gene
   → edit_plasmid with create_annotation covering the inserted region

5. Verify the result
   → parse_plasmid_file to confirm the updated features and sequence
```

### Workflow 2: Swap a promoter

```
1. Identify the promoter to replace
   → parse_plasmid_file to find promoter coordinates

2. Replace the sequence
   → edit_plasmid with replace_range + feature_handling: "adjust"
     (adjust mode clips overlapping features instead of erroring)
     The response includes features with openbio_id values

3. Update the annotation
   → edit_plasmid with update_annotation using the openbio_id from step 2

4. Verify
   → parse_plasmid_file to confirm the swap
```

### Workflow 3: Annotate an unannotated region

```
1. Inspect the plasmid
   → parse_plasmid_file to see existing annotations and find gaps

2. Create the annotation
   → edit_plasmid with create_annotation specifying name, type, start, end, strand

3. View the result
   → parse_plasmid_file to confirm the new annotation appears
```

## Integration with Molecular Biology Tools

| Task | Plasmid Tool | Molecular Biology Tool |
|------|-------------|----------------------|
| Find insertion site | parse_plasmid_file | restriction_find_sites, restriction_suggest_cutters |
| Design primers for insert | — | design_primers, evaluate_primers |
| Simulate PCR on plasmid | parse_plasmid_file (get sequence) | run_pcr |
| Insert gene + annotate | edit_plasmid | — |
| Verify digest pattern | parse_plasmid_file (get sequence) | restriction_digest, simulate_gel |
| Gibson into vector | edit_plasmid (linearize) | assemble_gibson |

## Troubleshooting

| Error Code | Cause | Fix |
|------------|-------|-----|
| `position_out_of_bounds` | Insert position > sequence length | Check sequence length with `parse_plasmid_file` first |
| `range_out_of_bounds` | Delete/replace end > sequence length | Use valid `[start, end)` within bounds |
| `ambiguous_feature_overlap` | Edit partially overlaps a feature in strict mode | Use `feature_handling: "adjust"` or choose coordinates that don't overlap features |
| `annotation_not_found` | `annotation_id` doesn't match any feature | Get current `openbio_id` values from a prior `edit_plasmid` response |
| `annotation_out_of_bounds` | Annotation end > sequence length | Ensure annotation range fits within the current sequence |
| `invalid_annotation_range` | Annotation end <= start | Ensure `end > start` for annotations |
| `invalid_sequence` | Sequence contains non-IUPAC characters | Use only valid DNA symbols: A, C, G, T, R, Y, S, W, K, M, B, D, H, V, N |
| `invalid_metadata` | Empty name in set_metadata | Provide a non-empty string for name |
| `frame_shift` (warning) | Insertion/replacement in CDS is not a multiple of 3 bp | Use `cloning_safe` validation to detect; adjust sequence length to preserve reading frame |
| `internal_stop` (warning) | Replacement sequence contains a stop codon affecting a CDS | Check replacement sequence for TAA, TAG, TGA in the reading frame |
| `operation_failed` | Unexpected error during operation | Check error message for details; verify all parameters |

---

**Tip**: The `edit_plasmid` response always includes the full feature list with `openbio_id` values in qualifiers. Use these IDs for subsequent `update_annotation` and `delete_annotation` calls.
