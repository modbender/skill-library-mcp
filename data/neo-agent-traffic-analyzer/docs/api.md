# API Documentation

## Analyzer

```js
const { Analyzer } = require('./lib/analyzer');
const analyzer = new Analyzer(messages);
```

### Constructor

- `new Analyzer(messages)` — Creates a new analyzer instance from an array of message objects.

### Message Format

```json
{
  "id": "string",
  "from": "string (required)",
  "to": "string (required)",
  "timestamp": "ISO 8601 string",
  "type": "request | response | broadcast",
  "payload_size": "number (bytes)",
  "latency_ms": "number",
  "status": "delivered | failed | timeout"
}
```

### Methods

- `getAgents()` — Returns sorted array of unique agent names.
- `getAgentStats()` — Returns per-agent statistics (sent, received, bytes, latency, failures).
- `getEdgeStats()` — Returns per-edge statistics for each communication channel.
- `getTimeline()` — Returns messages sorted chronologically.
- `getSummary()` — Returns overall summary statistics.
- `findBottlenecks(options)` — Detects bottlenecks based on configurable thresholds.
- `suggestOptimizations()` — Returns optimization strategies based on detected bottlenecks.

## Visualizer

```js
const { Visualizer } = require('./lib/visualizer');
const visualizer = new Visualizer(analyzer);
```

### Methods

- `generateDot(options)` — Generates Graphviz DOT format network graph.
- `generateTimeline(options)` — Generates ASCII timeline of message flow.
- `generateAsciiNetwork()` — Generates ASCII network topology diagram.

## Reporter

```js
const { Reporter } = require('./lib/reporter');
const reporter = new Reporter(analyzer, visualizer);
```

### Methods

- `generateJSON()` — Full report as JSON string.
- `generateCSV()` — Report as CSV format.
- `generateDot(options)` — Report as DOT graph.
- `generateReport(format, options)` — Generate report in specified format.
- `exportToFile(filepath, format, options)` — Write report to file.
- `generateTextSummary()` — Human-readable text summary.
