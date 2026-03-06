---
name: doc-accurate-codegen
version: "1.0.0"
description: "Generate code that references actual documentation, preventing hallucination bugs. ALWAYS loads docs first, validates against API signatures, and verifies correctness. Use for ANY code generation, API usage, or configuration creation."
metadata:
  openclaw:
    emoji: "📚"
    requires:
      bins: ["curl", "jq", "git"]
      env: ["BRAVE_API_KEY"]
    install:
      - id: npm
        kind: node
        package: axios
        bins: ["axios"]
---

# Documentation-Accurate Code Generation

**CRITICAL**: This skill prevents LLM hallucination by enforcing documentation reference.

## When to Use
- **ALWAYS** when generating code
- **ALWAYS** when using APIs
- **ALWAYS** when creating configurations
- **ALWAYS** when implementing features

## Core Philosophy

**NEVER generate code from memory. ALWAYS reference documentation.**

### The Problem
- LLMs hallucinate APIs that don't exist
- Methods get renamed or removed
- Parameters change or get deprecated
- Return types shift unexpectedly
- Configuration formats evolve

### The Solution
1. **Load documentation FIRST** — Before writing any code
2. **Extract API signatures** — Get actual method signatures
3. **Generate from docs** — Use real API data
4. **Validate against docs** — Check generated code matches
5. **Reference tracking** — Document which docs were used

## Workflow

```
1. IDENTIFY → What code/API/tool is needed?
2. LOCATE → Find documentation source
3. LOAD → Fetch and parse documentation
4. EXTRACT → Pull API signatures, parameters, examples
5. GENERATE → Create code using actual docs
6. VALIDATE → Check code matches documentation
7. REFERENCE → Track what docs were used
```

## Documentation Sources

### 1. OpenClaw Internal Docs
- Location: `C:\Users\clipp\AppData\Roaming\npm\node_modules\openclaw\docs`
- Access: `read` tool
- Use: For OpenClaw-specific APIs, tools, skills

### 2. Tool Documentation
- Tool help: `--help` flags
- Man pages: `man <command>`
- Official docs: Use `web_fetch` to get docs

### 3. API Documentation
- Official docs: Use `web_fetch`
- OpenAPI specs: Parse and reference
- Package docs: npm, pip, cargo docs

### 4. Code Examples
- Existing code: Read similar implementations
- Tests: Check test files for usage patterns
- Examples: Find working code samples

## Process for Code Generation

### Step 1: Documentation Discovery
```bash
# For OpenClaw tools
read("openclaw-docs-path/tool-name.md")

# For external tools
web_fetch("https://docs.tool.com/api")

# For local tools
exec("tool --help")
```

### Step 2: API Signature Extraction
```markdown
# Extract:
- Method names
- Parameters (names, types, required/optional)
- Return types
- Error handling
- Examples
- Version information
```

### Step 3: Code Generation
```python
# Generate code using actual API data
def generate_from_docs(api_docs):
    # Use real method names
    # Use real parameter names
    # Use real return types
    # Include error handling from docs
    # Add docstrings from docs
    pass
```

### Step 4: Validation
```python
def validate_against_docs(code, api_docs):
    # Check method names match
    # Check parameter names match
    # Check types match
    # Check return types match
    # Verify no hallucinated methods
    pass
```

## Quick Actions

- `codegen <api>` — Generate code with doc reference
- `validate <code>` — Check code against docs
- `doc-lookup <api>` — Load and display documentation
- `api-extract <tool>` — Extract API signatures

## Usage Examples

```
"Generate code to use the OpenClaw sessions_spawn tool"
# Process: Load docs → Extract API → Generate → Validate

"Create a Python script using the requests library"
# Process: Fetch requests docs → Extract API → Generate → Validate

"Write configuration for OpenClaw channels"
# Process: Load config docs → Extract format → Generate → Validate
```

## Validation Rules

### 1. Method Name Validation
- Check method exists in docs
- Verify spelling matches exactly
- Confirm method is not deprecated

### 2. Parameter Validation
- All required parameters present
- Parameter names match docs exactly
- Parameter types match docs
- Optional parameters marked correctly

### 3. Return Type Validation
- Return type matches docs
- Error types match docs
- Edge cases handled

### 4. Configuration Validation
- Keys match documentation
- Value types match schema
- Required fields present
- Format matches specification

## Error Prevention

### Common Hallucination Patterns
1. **Non-existent methods** — Methods that don't exist
2. **Wrong parameter names** — Hallucinated parameter names
3. **Wrong types** — Incorrect parameter/return types
4. **Missing error handling** — Ignoring documented errors
5. **Wrong configuration format** — Incorrect config structure

### Prevention Strategies
1. **Always load docs first** — Never generate from memory
2. **Extract actual signatures** — Don't guess API shape
3. **Validate everything** — Check against real docs
4. **Reference tracking** — Know which docs were used
5. **Test with real APIs** — Verify code actually works

## Integration Points

### With Other Skills
- **Coding skill**: Use this for doc-accurate code
- **Self-evolution**: Update skills with doc validation
- **Content generation**: Generate accurate code examples
- **Research**: Research APIs from actual docs

### With OpenClaw Tools
- **read**: Load internal documentation
- **web_fetch**: Fetch external documentation
- **exec**: Run tools with `--help` for docs
- **edit/write**: Create validated code

## Reference Tracking

### Format
```markdown
# Code Generation Reference

## Generated Code
- File: path/to/file.py
- Generated: 2026-02-23
- Tool: doc-accurate-codegen

## Documentation Sources
1. OpenClaw Tool Docs: /docs/tools/exec.md
2. API Reference: https://docs.example.com/api
3. Examples: /examples/exec-usage.py

## Validation
- ✅ Method names validated
- ✅ Parameters validated
- ✅ Return types validated
- ✅ Error handling validated

## Notes
- Using exec tool with sandbox mode
- All parameters from official docs
- Error handling from API reference
```

## Output Template

When generating code, always include:

```python
# Code generated with documentation reference
# Source: [documentation URL or path]
# Validated: [timestamp]
# API Version: [version if available]

def function_name():
    """
    [Docstring from actual documentation]
    
    Source: [link to docs]
    Parameters: [from docs]
    Returns: [from docs]
    """
    # Implementation using actual API
    pass
```

## Best Practices

1. **Docs First, Always** — Never generate without loading docs
2. **Exact Matches** — Use exact names, types, formats from docs
3. **Validate Everything** — Check all generated code
4. **Track References** — Document which docs were used
5. **Test Real APIs** — Actually run the code to verify
6. **Update Regularly** — Re-check docs as APIs evolve
7. **Error Handling** — Include all documented errors
8. **Examples** — Reference working examples from docs

## Common Pitfalls

1. **Assuming API stability** — APIs change, always re-check docs
2. **Memory over docs** — Trust docs, not memory
3. **Partial loading** — Load complete documentation
4. **No validation** — Always validate generated code
5. **Missing references** — Always track doc sources

## Success Metrics

- **Hallucination rate**: 0% (all code references actual docs)
- **Validation rate**: 100% (all code validated)
- **Reference tracking**: 100% (all code has doc sources)
- **Error rate**: 0% (no API misuse)
- **Test pass rate**: 100% (all generated code works)

## Advanced Features

### 1. Automatic Doc Loading
- Detect what APIs are needed
- Automatically fetch relevant docs
- Cache for future use

### 2. API Change Detection
- Monitor docs for changes
- Alert when APIs change
- Suggest code updates

### 3. Multi-Source Validation
- Cross-reference multiple doc sources
- Detect conflicts between sources
- Use most authoritative source

### 4. Example Extraction
- Extract working examples from docs
- Adapt examples to specific needs
- Test examples before using

## Integration with OpenClaw

### Tool Documentation
```bash
# Get tool help
exec("tool --help")

# Read tool docs
read("openclaw/docs/tools/tool-name.md")

# Check tool examples
read("openclaw/examples/tool-usage.md")
```

### Skill Documentation
```bash
# Read skill docs
read("skills/skill-name/SKILL.md")

# Check skill examples
read("skills/skill-name/examples/")
```

### Configuration Documentation
```bash
# Read config docs
read("openclaw/docs/configuration.md")

# Check config examples
read("openclaw/examples/config/")
```

---

**Remember**: This skill exists because LLMs hallucinate. ALWAYS use it for code generation. The only way to prevent bugs is to reference actual documentation.