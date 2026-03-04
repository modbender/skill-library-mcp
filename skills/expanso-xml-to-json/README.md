# xml-to-json

Convert XML to JSON format.

## Usage

```bash
echo "<root><item>value</item></root>" | expanso-edge run pipeline-cli.yaml
```

## Output

```json
{
  "json": {"root": {"item": "value"}},
  "valid": true
}
```
