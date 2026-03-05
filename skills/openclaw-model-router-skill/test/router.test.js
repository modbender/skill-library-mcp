const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');

const { parsePrefix, resolveRoute, loadConfig, validateConfig } = require('../src/router');
const { resolveActiveRule, detectConflicts } = require('../src/scheduler');
const { routeAndExecute } = require('../src/executor');
const { createLogger } = require('../src/logger');
const { pickModelFromStatus } = require('../src/session-controller');

test('parsePrefix extracts prefix and body', () => {
  const result = parsePrefix('@mini hello world');
  assert.equal(result.prefix, '@mini');
  assert.equal(result.body, 'hello world');
});

test('parsePrefix strips trailing punctuation', () => {
  const result = parsePrefix('@mini: hello');
  assert.equal(result.prefix, '@mini');
  assert.equal(result.body, 'hello');
});

test('resolveRoute returns mapping for supported prefix', () => {
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const route = resolveRoute('@codex', config);
  assert.equal(route.model, 'openai-codex/gpt-5.3-codex');
});

test('resolveRoute supports alias prefixes', () => {
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const route = resolveRoute('@c', config);
  assert.equal(route.model, 'openai-codex/gpt-5.3-codex');
});

test('validateConfig rejects bad retry section', () => {
  assert.throws(() => validateConfig({
    prefixMap: { '@mini': { model: 'minimax/MiniMax-M2.5' } },
    retry: { maxRetries: -1 },
  }), /non-negative integer/);
});

test('loadConfig respects ROUTER_CONFIG_PATH', () => {
  const tmpPath = path.join(__dirname, 'tmp.router.config.json');
  const payload = {
    prefixMap: { '@x': { model: 'm1', fallbackModel: 'm2' } },
    retry: { maxRetries: 0, baseDelayMs: 0 },
  };
  fs.writeFileSync(tmpPath, JSON.stringify(payload, null, 2));
  const prev = process.env.ROUTER_CONFIG_PATH;
  process.env.ROUTER_CONFIG_PATH = tmpPath;
  const cfg = loadConfig();
  assert.equal(cfg.prefixMap['@x'].model, 'm1');
  if (prev === undefined) delete process.env.ROUTER_CONFIG_PATH;
  else process.env.ROUTER_CONFIG_PATH = prev;
  try { fs.unlinkSync(tmpPath); } catch {}
});

test('routeAndExecute switches model then runs body', async () => {
  const logPath = path.join(__dirname, 'tmp.log.jsonl');
  try { fs.unlinkSync(logPath); } catch {}

  let model = 'minimax/MiniMax-M2.5';
  const calls = [];
  const sessionController = {
    async getCurrentModel() { return model; },
    async setModel(next) { model = next; return true; },
  };
  const taskExecutor = {
    async execute(input) { calls.push(input); return `ok:${input}`; },
  };

  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const logger = createLogger(logPath);
  const result = await routeAndExecute({
    message: '@codex build parser',
    config,
    sessionController,
    taskExecutor,
    logger,
  });

  assert.equal(result.targetModel, 'openai-codex/gpt-5.3-codex');
  assert.deepEqual(calls, ['build parser']);
  const lines = fs.readFileSync(logPath, 'utf8').trim().split('\n');
  assert.ok(lines.at(-1).includes('route.success'));
});

test('routeAndExecute falls back when executor throws', async () => {
  let model = 'openai-codex/gpt-5.3-codex';
  let runs = 0;
  const sessionController = {
    async getCurrentModel() { return model; },
    async setModel(next) { model = next; return true; },
  };
  const taskExecutor = {
    async execute() {
      runs += 1;
      if (runs === 1) throw new Error('boom');
      return 'recovered';
    },
  };

  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const logger = { log() {} };

  const result = await routeAndExecute({
    message: '@mini hi',
    config,
    sessionController,
    taskExecutor,
    logger,
  });

  assert.equal(result.fallback, true);
  assert.equal(result.output, 'recovered');
});

test('routeAndExecute raises FALLBACK_EXECUTION_FAILED when fallback run also fails', async () => {
  let model = 'openai-codex/gpt-5.3-codex';
  let runs = 0;
  const events = [];
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));

  await assert.rejects(() => routeAndExecute({
    message: '@mini still broken',
    config,
    sessionController: {
      async getCurrentModel() { return model; },
      async setModel(next) { model = next; return true; },
    },
    taskExecutor: {
      async execute() {
        runs += 1;
        throw new Error(`run-${runs}`);
      },
    },
    logger: { log(event) { events.push(event); } },
  }), /Fallback execution failed/);

  assert.equal(events.at(-1).code, 'FALLBACK_EXECUTION_FAILED');
});

test('routeAndExecute attempts restore on fallback failure', async () => {
  let model = 'openai-codex/gpt-5.3-codex';
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));

  await assert.rejects(() => routeAndExecute({
    message: '@mini fail restore',
    config,
    sessionController: {
      async getCurrentModel() { return model; },
      async setModel(next) { model = next; return true; },
    },
    taskExecutor: {
      async execute() { throw new Error('always fail'); },
    },
    logger: { log() {} },
  }), /Fallback execution failed/);

  assert.equal(model, 'openai-codex/gpt-5.3-codex');
});

test('routeAndExecute logs failure for invalid prefix', async () => {
  const events = [];
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const logger = { log(event) { events.push(event); } };

  await assert.rejects(() => routeAndExecute({
    message: '@unknown hello',
    config,
    sessionController: {
      async getCurrentModel() { return 'minimax/MiniMax-M2.5'; },
      async setModel() { return true; },
    },
    taskExecutor: { async execute() { return 'ok'; } },
    logger,
  }), /Unsupported prefix/);

  assert.equal(events.at(-1).type, 'route.failure');
  assert.equal(events.at(-1).code, 'INVALID_PREFIX');
});

test('routeAndExecute throws when fallback switch cannot verify', async () => {
  let model = 'minimax/MiniMax-M2.5';
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));

  await assert.rejects(() => routeAndExecute({
    message: '@mini retry me',
    config,
    sessionController: {
      async getCurrentModel() { return model; },
      async setModel(next) {
        if (next === 'openai-codex/gpt-5.3-codex') {
          model = 'unexpected/model';
          return true;
        }
        model = next;
        return true;
      },
    },
    taskExecutor: {
      async execute() { throw new Error('first run fails'); },
    },
    logger: { log() {} },
  }), /Model verification failed/);
});

test('routeAndExecute retries transient setModel failure', async () => {
  let model = 'minimax/MiniMax-M2.5';
  let attempts = 0;
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));

  const result = await routeAndExecute({
    message: '@codex quick task',
    config,
    sessionController: {
      async getCurrentModel() { return model; },
      async setModel(next) {
        attempts += 1;
        if (attempts === 1) return false;
        model = next;
        return true;
      },
    },
    taskExecutor: {
      async execute(input) { return `ok:${input}`; },
    },
    logger: { log() {} },
  });

  assert.equal(result.output, 'ok:quick task');
  assert.ok(attempts >= 2);
});

test('routeAndExecute handles prefix-only message as switch confirmation', async () => {
  let model = 'minimax/MiniMax-M2.5';
  const calls = [];
  const events = [];
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));

  const result = await routeAndExecute({
    message: '@codex',
    config,
    sessionController: {
      async getCurrentModel() { return model; },
      async setModel(next) { model = next; return true; },
    },
    taskExecutor: {
      async execute(input) { calls.push(input); return `ok:${input}`; },
    },
    logger: { log(event) { events.push(event); } },
  });

  assert.equal(result.switchOnly, true);
  assert.equal(result.targetModel, 'openai-codex/gpt-5.3-codex');
  assert.deepEqual(calls, []);
  assert.equal(events.at(-1).type, 'route.switch_only');
});

test('routeAndExecute reports already-on-model for prefix-only', async () => {
  let model = 'openai-codex/gpt-5.3-codex';
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const result = await routeAndExecute({
    message: '@codex',
    config,
    sessionController: {
      async getCurrentModel() { return model; },
      async setModel(next) { model = next; return true; },
    },
    taskExecutor: { async execute() { return 'ok'; } },
    logger: { log() {} },
  });
  assert.equal(result.alreadyOnModel, true);
  assert.equal(result.output, 'already_on:openai-codex/gpt-5.3-codex');
});


test('routeAndExecute passes through non-prefix input', async () => {
  const config = loadConfig(path.join(__dirname, '..', 'router.config.json'));
  const outputs = [];
  const result = await routeAndExecute({
    message: '   hello router  ',
    config,
    sessionController: {
      async getCurrentModel() { return 'minimax/MiniMax-M2.5'; },
      async setModel() { return true; },
    },
    taskExecutor: {
      async execute(input) { outputs.push(input); return 'ok'; },
    },
    logger: { log() {} },
  });

  assert.equal(result.switched, false);
  assert.deepEqual(outputs, ['   hello router  ']);
});

test('scheduler resolves active rule by time and priority', () => {
  const schedule = {
    rules: [
      { id: 'a', days: ['sat'], start: '09:00', end: '18:00', model: 'm1', priority: 1, enabled: true },
      { id: 'b', days: ['sat'], start: '09:00', end: '18:00', model: 'm2', priority: 5, enabled: true },
    ],
  };
  const at = new Date('2026-02-28T10:00:00');
  const rule = resolveActiveRule(schedule, at);
  assert.equal(rule.id, 'b');
});

test('scheduler detects overlapping conflicts with same priority', () => {
  const schedule = {
    rules: [
      { id: 'a', days: ['sat'], start: '09:00', end: '18:00', model: 'm1', priority: 1, enabled: true },
      { id: 'b', days: ['sat'], start: '12:00', end: '20:00', model: 'm2', priority: 1, enabled: true },
    ],
  };
  const conflicts = detectConflicts(schedule);
  assert.equal(conflicts.length, 1);
});

test('scheduler resolve respects configured timezone', () => {
  const schedule = {
    timezone: 'Europe/Rome',
    rules: [
      { id: 'rome_day', days: ['mon'], start: '09:00', end: '18:00', model: 'm1', priority: 1, enabled: true },
    ],
  };
  const atUtc = new Date('2026-03-02T08:30:00Z'); // 09:30 in Europe/Rome
  const rule = resolveActiveRule(schedule, atUtc);
  assert.equal(rule.id, 'rome_day');
});

test('pickModelFromStatus prefers activeModel over defaultModel', () => {
  const picked = pickModelFromStatus({ activeModel: 'm_active', defaultModel: 'm_default' });
  assert.equal(picked, 'm_active');
});
