# Troubleshooting

## Common Issues

### "File not found" error

Ensure the path to your JSON log file is correct. Use absolute paths or paths relative to your current working directory.

```bash
agent-traffic-analyzer analyze ./logs/communication.json
```

### "Invalid JSON" error

The input file must contain valid JSON. Verify with:

```bash
node -e "JSON.parse(require('fs').readFileSync('your-file.json','utf8'))"
```

### "Expected an array of messages" error

The root element of the JSON file must be an array `[...]`, not an object `{...}`.

### "Missing required from or to field" error

Every message object must have at minimum `from` and `to` string fields identifying the sender and receiver agents.

### No bottlenecks detected

The default thresholds may be too lenient for your data. Try lowering them:

```bash
agent-traffic-analyzer bottlenecks data.json --latency-threshold 50 --traffic-threshold 0.2
```

### DOT output not rendering

The DOT output is plain text in Graphviz format. To render it as an image:

```bash
agent-traffic-analyzer visualize data.json -f dot -o network.dot
dot -Tpng network.dot -o network.png
```

Requires Graphviz to be installed (`apt install graphviz` or `brew install graphviz`).

## Performance

The analyzer processes messages in-memory. For very large datasets (100k+ messages), consider splitting the log file or increasing Node.js memory:

```bash
node --max-old-space-size=4096 bin/agent-traffic-analyzer analyze large-file.json
```
