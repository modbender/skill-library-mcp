# language-detect

Detect the language of text using AI.

## Usage

```bash
export OPENAI_API_KEY=sk-...
echo "Bonjour le monde" | expanso-edge run pipeline-cli.yaml
```

## Output

```json
{
  "language": "French",
  "code": "fr",
  "confidence": 0.98
}
```
