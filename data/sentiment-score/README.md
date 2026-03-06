# sentiment-score

Score text sentiment from -1 (negative) to +1 (positive).

## Usage

```bash
echo "I love this product!" | expanso-edge run pipeline-cli.yaml
echo "This is terrible" | expanso-edge run pipeline-cli.yaml
```

## Output

```json
{"score": 0.85, "label": "positive", "confidence": 0.92}
```
