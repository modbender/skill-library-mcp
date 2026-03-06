const { spawnSync } = require('child_process');
const path = require('path');

const runner = path.join(__dirname, 'run-all.mjs');
const result = spawnSync(process.execPath, [runner], { stdio: 'inherit' });

process.exit(result.status ?? 1);
