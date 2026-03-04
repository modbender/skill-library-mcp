# json-flatten

Analyze nested JSON structure.

## Usage

```bash
echo '{"user": {"name": "test"}, "active": true}' | expanso-edge run pipeline-cli.yaml
```

## Output

```json
{
  "top_level_keys": ["user", "active"],
  "key_count": 2,
  "has_nested_objects": true
}
```
