# json-to-csv

Convert JSON array of objects to CSV format.

## Overview

This skill converts a JSON array to CSV with automatic header detection. Runs entirely locally.

## Usage

### CLI Mode

```bash
echo '[{"name":"Alice","age":30},{"name":"Bob","age":25}]' | \
  expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
PORT=8080 expanso-edge run pipeline-mcp.yaml &
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{"data": [{"name":"Alice","age":30},{"name":"Bob","age":25}]}'
```

## Output

```json
{
  "csv": "name,age\nAlice,30\nBob,25",
  "row_count": 2,
  "columns": ["name", "age"],
  "metadata": {...}
}
```

## Use Cases

- Data export
- Spreadsheet generation
- Report creation
- API response formatting
