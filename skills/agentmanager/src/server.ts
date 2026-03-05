import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createApp } from './app.js';
import { OrchestratorService } from './services/orchestrator.js';
import { RunStore } from './services/run-store.js';
import { getConfig } from './config.js';

const cfg = getConfig();
const port = cfg.PORT;
const persist = cfg.PERSIST_RUNS;

const base = dirname(fileURLToPath(import.meta.url));
const packagePath = join(base, '../../package.json');
const serviceVersion = (JSON.parse(readFileSync(packagePath, 'utf8')) as { version: string }).version;

const orchestrator = new OrchestratorService(new RunStore(persist), serviceVersion);
const app = createApp(orchestrator);

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`agent-manager listening on :${port}`);
});
