# yaml-to-json

Convert YAML to JSON format.

## Usage

```bash
echo "name: test
value: 123" | expanso-edge run pipeline-cli.yaml
```

## Output

```json
{
  "json": {"name": "test", "value": 123},
  "valid": true
}
```
