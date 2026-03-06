# Agent-Weave

Master-Worker Agent Cluster with parallel task execution.

## Quick Start

```bash
npm install -g agent-weave
```

```javascript
const { Loom } = require('agent-weave');

const loom = new Loom();
const master = loom.createMaster('cluster');
const workers = loom.spawnWorkers(master.id, 5, taskFn);
```

## CLI

```bash
weave loom create-master --name my-cluster
weave loom spawn --parent <id> --count 5
```

## License

MIT
