# csv-to-json

Convert CSV data to JSON array of objects.

## Overview

This skill parses CSV with headers and converts to JSON objects. Runs entirely locally.

## Usage

### CLI Mode

```bash
echo "name,age,city
Alice,30,NYC
Bob,25,LA" | expanso-edge run pipeline-cli.yaml

# Custom delimiter
DELIMITER=";" cat data.csv | expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
PORT=8080 expanso-edge run pipeline-mcp.yaml &
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{"csv": "name,age\nAlice,30\nBob,25"}'
```

## Output

```json
{
  "data": [
    {"name": "Alice", "age": "30", "city": "NYC"},
    {"name": "Bob", "age": "25", "city": "LA"}
  ],
  "row_count": 2,
  "columns": ["name", "age", "city"],
  "metadata": {...}
}
```

## Use Cases

- Data import/export
- API data transformation
- Spreadsheet processing
- Log parsing
