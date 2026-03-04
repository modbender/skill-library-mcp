# json-to-yaml

Convert JSON to YAML format.

## Usage

```bash
echo '{"name": "test", "value": 123}' | expanso-edge run pipeline-cli.yaml
```

## Output

```json
{
  "yaml": "name: test\nvalue: 123\n",
  "valid": true
}
```
