# API Design Reviewer

A comprehensive toolkit for analyzing, reviewing, and scoring REST API designs. This skill provides automated linting, breaking change detection, and quality assessment to help engineering teams build better APIs.

## Overview

The API Design Reviewer includes three main tools:

1. **API Linter** (`api_linter.py`) - Analyzes API specifications for REST conventions and best practices
2. **Breaking Change Detector** (`breaking_change_detector.py`) - Compares API versions to identify breaking changes  
3. **API Scorecard** (`api_scorecard.py`) - Generates comprehensive quality scores across multiple dimensions

## Features

### 🔍 API Linting
- **Naming Conventions**: Enforces kebab-case resources, camelCase fields
- **HTTP Method Usage**: Validates proper REST method patterns
- **URL Structure**: Analyzes endpoint design and hierarchy
- **Error Handling**: Checks response format consistency
- **Documentation Coverage**: Identifies missing descriptions and examples
- **Security Analysis**: Reviews authentication and authorization patterns

### 🔄 Breaking Change Detection
- **Endpoint Changes**: Detects removed or modified endpoints
- **Schema Evolution**: Tracks field additions, removals, and type changes
- **Parameter Changes**: Identifies new required parameters
- **Response Modifications**: Catches breaking response format changes
- **Migration Guides**: Provides actionable guidance for each breaking change

### 📊 API Scoring
- **Consistency (30%)**: Naming conventions, response patterns, structural consistency
- **Documentation (20%)**: Completeness and clarity of API documentation
- **Security (20%)**: Authentication, authorization, and security best practices  
- **Usability (15%)**: Ease of use, discoverability, developer experience
- **Performance (15%)**: Caching, pagination, efficiency patterns

## Installation

All tools are standalone Python scripts with **zero external dependencies** - only Python standard library is used.

```bash
# Clone or download the scripts
cd engineering/api-design-reviewer/scripts/

# Make scripts executable (optional)
chmod +x *.py
```

## Usage

### API Linter

Analyze an OpenAPI specification for design issues:

```bash
# Basic linting
python3 api_linter.py openapi.json

# JSON output
python3 api_linter.py --format json openapi.json

# Save to file
python3 api_linter.py --output report.txt openapi.json

# Lint raw endpoint definitions
python3 api_linter.py --raw-endpoints endpoints.json
```

**Input Format**: OpenAPI 3.0+ JSON or raw endpoint definitions

**Sample Output**:
```
API LINTING REPORT
═══════════════════════════════════════════════════════════════
Total Endpoints: 4
Overall Score: 93.0/100.0
🔴 Errors: 0  🟡 Warnings: 2  ℹ️ Info: 1

🏆 Excellent! Your API design follows best practices.
```

### Breaking Change Detector

Compare two API specification versions:

```bash
# Compare specifications
python3 breaking_change_detector.py api-v1.json api-v2.json

# JSON output for CI/CD integration
python3 breaking_change_detector.py --format json api-v1.json api-v2.json

# Exit with error if breaking changes found
python3 breaking_change_detector.py --exit-on-breaking api-v1.json api-v2.json
```

**Sample Output**:
```
BREAKING CHANGE ANALYSIS REPORT
═══════════════════════════════════════════════════════════════
🔴 Breaking Changes: 3
🟡 Potentially Breaking: 1
🟢 Non-Breaking Changes: 5

⛔ MAJOR VERSION BUMP REQUIRED
   This version contains breaking changes that will affect existing clients.
```

### API Scorecard

Generate comprehensive quality assessment:

```bash
# Generate scorecard
python3 api_scorecard.py openapi.json

# JSON format for automated processing
python3 api_scorecard.py --format json openapi.json

# Require minimum grade
python3 api_scorecard.py --min-grade B openapi.json
```

**Sample Output**:
```
API DESIGN SCORECARD
═══════════════════════════════════════════════════════════════
🏆 OVERALL GRADE: A (88.5/100.0)

📊 CONSISTENCY - Grade: A (92.0/100) | Weight: 30%
📊 DOCUMENTATION - Grade: A (90.0/100) | Weight: 20% 
📊 SECURITY - Grade: B (85.0/100) | Weight: 20%
📊 USABILITY - Grade: B (82.0/100) | Weight: 15%
📊 PERFORMANCE - Grade: A (90.0/100) | Weight: 15%
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: API Design Review
on: [pull_request]
jobs:
  api-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint API
        run: python3 scripts/api_linter.py openapi.json
      - name: Check Breaking Changes
        run: python3 scripts/breaking_change_detector.py --exit-on-breaking openapi-v1.json openapi-v2.json
      - name: Generate Scorecard
        run: python3 scripts/api_scorecard.py --min-grade B openapi.json
```

### Pre-commit Hook
```bash
#!/bin/bash
python3 engineering/api-design-reviewer/scripts/api_linter.py api/openapi.json
if [ $? -ne 0 ]; then
  echo "API linting failed. Please fix issues before committing."
  exit 1
fi
```

## Sample Data

The `assets/` directory contains example API specifications:

- **`good_api_example.json`** - Well-designed API following best practices
- **`bad_api_example.json`** - API with common anti-patterns and issues

Use these for testing and learning:

```bash
# Test with good example (should score highly)
python3 api_linter.py assets/good_api_example.json

# Test with bad example (should find many issues)  
python3 api_linter.py assets/bad_api_example.json
```

## Best Practices Enforced

### URL Design
```
✅ Good: GET /users/{id}/orders
❌ Bad: GET /getOrdersForUser/{id}
```

### Response Consistency
```json
✅ Good: Consistent response wrapper
{
  "data": { ... },
  "pagination": { "page": 1, "total": 100 }
}

❌ Bad: Inconsistent responses
{ "user": { ... } }  // Sometimes
{ "result": { ... } } // Other times
```

### Error Handling
```json
✅ Good: Structured error responses
{
  "error": {
    "code": "VALIDATION_ERROR", 
    "message": "Invalid input",
    "requestId": "req-123"
  }
}
```

## Common Issues Detected

### Anti-Patterns
- Verb-based URLs (`/getUsers` instead of `/users`)
- Wrong HTTP methods (`POST /users/{id}/get`)
- Over-nested resources (`/a/b/c/d/e/f`)
- Inconsistent naming conventions
- Missing pagination on list endpoints
- Vague error messages
- No security schemes defined

### Breaking Changes
- Removed endpoints or fields
- Changed field types or requirements  
- Modified URL structures
- New required parameters
- Changed authentication methods

### Quality Issues
- Missing documentation
- Inconsistent response formats
- No caching headers
- Poor error handling
- Security vulnerabilities

## Troubleshooting

### Common Errors

**"Invalid JSON"**: Ensure your API spec is valid JSON
```bash
python3 -m json.tool openapi.json  # Validate JSON syntax
```

**"No paths defined"**: OpenAPI spec needs a `paths` section
```json
{
  "openapi": "3.0.3",
  "paths": {
    "/users": { ... }
  }
}
```

**"Unsupported version"**: Use OpenAPI 3.0+ (not Swagger 2.0)

### Exit Codes

All tools use standard exit codes:
- **0**: Success (no errors found)
- **1**: Errors found or breaking changes detected
- **2**: Invalid input or tool error

Perfect for CI/CD pipeline integration!

## References

### Reference Documents
- **REST Design Rules** (`references/rest_design_rules.md`) - Comprehensive REST API design guidelines
- **API Anti-Patterns** (`references/api_antipatterns.md`) - Common mistakes and how to avoid them
- **Versioning Strategies** (`references/versioning_strategies.md`) - Complete guide to API versioning approaches

### Key Principles
1. **Resources over Actions**: Use nouns in URLs, let HTTP methods define actions
2. **Consistency**: Maintain consistent naming, response formats, and error handling
3. **Documentation**: Comprehensive descriptions, examples, and error scenarios
4. **Security**: Authentication, authorization, and secure data handling from day one
5. **Versioning**: Plan for API evolution with clear versioning and deprecation strategies

## Contributing

### Adding New Rules
1. Extend linting logic in respective Python scripts
2. Add test cases with sample APIs
3. Update reference documentation
4. Test against real-world APIs

### Quality Standards
- Scripts use only Python standard library
- Dual output formats (JSON + human-readable)
- Comprehensive error handling
- Clear migration guidance for breaking changes

## License

MIT License - Built for engineering teams who care about API quality 🚀

---

**Ready to improve your API designs?** Start with the sample assets and see what the tools find!