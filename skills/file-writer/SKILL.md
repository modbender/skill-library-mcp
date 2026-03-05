---
name: file-writer
description: Safe file writing strategy for large files. Use when you need to write or update large files (over 5000 bytes) to avoid truncation. Provides step-by-step approach: (1) Read current state, (2) Use edit tool for precise modifications, (3) Verify results, (4) Repeat until complete. Also provides fallback strategies and error recovery.
---

# File Writer

Safe file writing strategy for large files to avoid truncation issues.

## When to Use

- Writing files larger than 5000 bytes
- Updating existing files with significant changes
- Modifying specific sections of large files
- Previous write operations were truncated
- Need to ensure file integrity

## Problem Analysis

### Why Files Get Truncated

Large file writes can fail due to:

1. **Tool limitations** - `write` tool may have byte limits per operation
2. **Network limits** - Large file transfers may be truncated during transmission
3. **System limits** - OpenClaw may have size limits on single operations

### Safe Size Thresholds

| Operation | Safe Size | Risk Level |
|-----------|------------|-------------|
| `write` new file | < 2000 bytes | ✅ Safe |
| `write` new file | 2000-5000 bytes | ⚠️ Moderate |
| `write` new file | > 5000 bytes | ❌ High risk |
| `edit` modification | < 500 bytes | ✅ Safe |
| `edit` modification | 500-1000 bytes | ⚠️ Moderate |
| `edit` modification | > 1000 bytes | ❌ High risk |

## Safe Writing Strategy

### Step 1: Read Current State

Before making changes, read the current file state:

```bash
# Read the file to understand current structure
read /path/to/file.md

# For large files, read specific sections
read /path/to/file.md --offset 100 --limit 50
```

**Purpose:**
- Understand file structure
- Identify exact text to replace
`- Determine modification points

### Step 2: Use Edit Tool for Precise Modifications

For small to medium changes, use `edit` tool:

```markdown
Use `edit` tool with:
- `oldText`: Exact text to replace (must match exactly)
- `newText`: New text to replace with
- `file_path`: Path to the file
```

**Best Practices:**
- Keep modifications under 500 bytes
- Match `oldText` exactly (including whitespace)
- Use unique text markers for large sections
- Verify `oldText` exists before editing

### Step 3: Verify Results

After each modification, verify the result:

```bash
# Check file line count
wc -l /path/to/file.md

# Read modified section
read /path/to/file.md --offset <start> --limit <lines>

# Verify file ends correctly
read /path/to/file.md --offset -10
```

**Success Criteria:**
- File size increased as expected
- Modified section contains new content
- File ends correctly (not truncated)
- No syntax errors (for code files)

### Step 4: Repeat Until Complete

For large multi-section updates:

1. Modify one section at a time
2. Verify each modification
3. Proceed to next section
4. Repeat until all changes complete

## Fallback Strategies

### Strategy 1: Split Large Writes

If `write` tool fails for large content:

```markdown
Split content into chunks:

1. Write first chunk (header + section 1)
2. Verify and append section 2
3. Verify and append section 3
4. Continue until complete
```

### Strategy 2: Use Unique Markers

For complex modifications, use unique markers:

```markdown
In source file:
<!-- SECTION_START: configuration -->
[existing content]
<!-- SECTION_END: configuration -->

Edit operation:
oldText: "<!-- SECTION_START: configuration -->\n[existing content]\n<!-- SECTION_END: configuration -->"
newText: "<!-- SECTION_START: configuration -->\n[new content]\n<!-- SECTION_END: configuration -->"
```

### Strategy 3: Incremental Build

For creating new large files:

```markdown
1. Create file with basic structure
2. Add sections one by one using edit
3. Verify after each addition
4. Final verification
```

### Strategy 4: Backup and Restore

For critical file modifications:

```bash
# Create backup before modification
cp /path/to/file.md /path/to/file.md.backup

# Attempt modification
# ... (write or edit operation)

# If modification fails, restore
cp /path/to/file.md.backup /path/to/file.md
```

## Error Recovery

### Edit Tool Fails

**Symptom:** "Could not find exact text in file"

**Causes:**
- `oldText` doesn't match exactly
- Whitespace differences (spaces vs tabs)
- File already modified
- Text doesn't exist in file

**Solutions:**

1. **Re-read the file** to get exact content
2. **Use unique markers** for large sections
3. **Match whitespace exactly** (copy from file read)
4. **Use smaller `oldText`** for more precise matching

### Write Tool Truncates

**Symptom:** File ends abruptly or is incomplete

**Solutions:**

1. **Use edit tool** instead of write
2. **Split content** into smaller chunks
3. **Write incrementally** (section by section)
4. **Verify file size** after each operation

### File Corruption

**Symptom:** File has syntax errors or invalid content

**Solutions:**

1. **Restore from backup**
2. **Re-read and re-verify**
3. **Use incremental build** strategy
4. **Validate syntax** after each modification

## Examples

### Example 1: Adding Section to Large File

```markdown
Step 1: Read file to find insertion point
read /path/to/large-file.md --offset 50 --limit 10

Step 2: Use edit to add new section
edit:
  file_path: /path/to/large-file.md
  oldText: "## Existing Section\n\nContent here"
  newText: "## Existing Section\n\nContent here\n\n## New Section\n\nNew content"

Step 3: Verify
read /path/to/large-file.md --offset 50 --limit 20
```

### Example 2: Creating Large New File

```markdown
Step 1: Create basic structure
write:
  file_path: /path/to/new-file.md
  content: "# Title\n\n## Section 1\n\nContent 1"

Step 2: Add sections incrementally
edit:
  file_path: /path/to/new-file.md
  oldText: "Content 1"
  newText: "Content 1\n\n## Section 2\n\nContent 2"

Step 3: Verify
wc -l /path/to/new-file.md
```

### Example 3: Replacing Large Section

```markdown
Step 1: Read file to find exact text
read /path/to/file.md

Step 2: Use unique markers
edit:
  file_path: /path/to/file.md
  oldText: "<!-- START: old-section -->\n[old content]\n<!-- END: old-section -->"
  newText: "<!-- START: old-section -->\n[new content]\n<!-- END: old-section -->"

Step 3: Verify
read /path/to/file.md | grep "new content"
```

## Best Practices

1. **Always read before editing** - Understand current state
2. **Use edit for modifications** - More precise than write
3. **Keep changes small** - Under 500 bytes per edit
4. **Verify after each operation** - Don't batch operations
5. **Use unique markers** - For complex modifications
6. **Create backups** - For critical files
7. **Handle errors gracefully** - Provide recovery strategies
8. **Test incrementally** - Verify each step

## Decision Tree

```
Need to write/update file?
├─ New file?
│  ├─ < 2000 bytes?
│  │  └─ Use write tool
│  └─ > 2000 bytes?
│     └─ Use incremental build strategy
└─ Existing file?
   ├─ Small change (< 500 bytes)?
   │  └─ Use edit tool
   ├─ Medium change (500-1000 bytes)?
   │  └─ Use edit with unique markers
   └─ Large change (> 1000 bytes)?
      └─ Use incremental edit strategy
```

## Quick Reference

| Task | Tool | Strategy |
|------|------|----------|
| Create small file | write | Direct write |
| Create large file | write + edit | Incremental build |
| Small modification | edit | Direct edit |
| Medium modification | edit | Edit with markers |
| Large modification | edit | Incremental edit |
| Replace section | edit | Unique markers |
| Append content | edit | Edit end of file |
