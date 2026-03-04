#!/usr/bin/env node
const path = require('node:path');

const { loadConfig, parsePrefix, resolveRoute } = require('./router');
const { createLogger } = require('./logger');
const { createOpenClawSessionController } = require('./session-controller');
const { acquireLock } = require('./lock');
const {
  loadSchedule,
  validateSchedule,
  resolveActiveRule,
  detectConflicts,
  addRule,
  removeRule,
  saveSchedule,
  buildCronPreview,
} = require('./scheduler');

function usage() {
  return `
Usage:
  node src/cli.js parse "<message>"
  node src/cli.js route "<message>" [--config <path>] [--json]
  node src/cli.js validate [--config <path>]
  node src/cli.js schedule list [--schedule <path>]
  node src/cli.js schedule add --id <id> --days <mon,tue> --start <HH:MM> --end <HH:MM> --model <model> [--priority N] [--disable]
  node src/cli.js schedule remove --id <id> [--schedule <path>]
  node src/cli.js schedule resolve [--at "2026-02-28T10:00"] [--schedule <path>]
  node src/cli.js schedule apply [--id <ruleId>] [--at "2026-02-28T10:00"] [--schedule <path>] [--config <path>] [--json]
  node src/cli.js schedule end --id <ruleId> [--schedule <path>] [--config <path>] [--json]
  node src/cli.js schedule validate [--schedule <path>]
  node src/cli.js schedule cron [--schedule <path>]
`;
}

function getArgValue(args, key) {
  const idx = args.indexOf(key);
  if (idx === -1) return null;
  return args[idx + 1] || null;
}

function hasFlag(args, flag) {
  return args.includes(flag);
}

function classifyFailure(err) {
  const msg = String((err && err.message) || '').toLowerCase();
  if (msg.includes('auth') || msg.includes('token') || msg.includes('permission')) return 'auth_expired';
  if (msg.includes('rate') || msg.includes('quota')) return 'rate_limit';
  if (msg.includes('verify') || msg.includes('model')) return 'provider_drift';
  return 'unknown';
}

async function applyRule({ rule, config, schedulePath, scheduleTimezone, outputJson }) {
  const lockPath = (config.safety && config.safety.lockPath) || path.join(path.resolve(__dirname, '..'), '.router-switch.lock');
  const lock = acquireLock(lockPath, { staleMs: (config.safety && config.safety.lockStaleMs) || 5 * 60 * 1000 });
  if (lock.busy) {
    const payload = { ok: false, code: 'LOCK_BUSY', lockPath };
    if (outputJson) console.log(JSON.stringify(payload, null, 2));
    else console.error('schedule apply skipped: lock busy');
    process.exit(3);
  }

  const logger = createLogger((config.logging && config.logging.path) || path.join(path.resolve(__dirname, '..'), 'router.log.jsonl'));
  const controller = createOpenClawSessionController({
    ...(config.sessionController || {}),
    auth: config.auth || {},
  });

  const startedAt = Date.now();
  let previousModel = null;
  try {
    previousModel = await controller.getCurrentModel();
    const switched = await controller.setModel(rule.model);
    if (!switched) throw new Error(`setModel failed for ${rule.model}`);
    const verified = await controller.getCurrentModel();
    if (verified !== rule.model) {
      throw new Error(`verify failed expected=${rule.model} actual=${verified}`);
    }

    logger.log({
      type: 'schedule.switch.success',
      ruleId: rule.id,
      timezone: scheduleTimezone,
      fromModel: previousModel,
      toModel: rule.model,
      schedulePath,
      latencyMs: Date.now() - startedAt,
    });

    const payload = {
      ok: true,
      ruleId: rule.id,
      fromModel: previousModel,
      toModel: rule.model,
      latencyMs: Date.now() - startedAt,
    };
    if (outputJson) console.log(JSON.stringify(payload, null, 2));
    else console.log(`switched ${previousModel} -> ${rule.model}`);
    return;
  } catch (err) {
    const failureKind = classifyFailure(err);
    let rollback = null;
    if ((config.safety && config.safety.rollbackOnFailure) !== false && previousModel) {
      try {
        const restored = await controller.setModel(previousModel);
        rollback = restored ? 'restored' : 'restore_failed';
      } catch {
        rollback = 'restore_failed';
      }
    }

    logger.log({
      type: 'schedule.switch.failure',
      ruleId: rule.id,
      timezone: scheduleTimezone,
      toModel: rule.model,
      fromModel: previousModel,
      reason: err.message,
      failureKind,
      rollback,
      schedulePath,
      latencyMs: Date.now() - startedAt,
    });

    const payload = {
      ok: false,
      ruleId: rule.id,
      reason: err.message,
      failureKind,
      rollback,
    };
    if (outputJson) console.log(JSON.stringify(payload, null, 2));
    else console.error(`switch failed: ${err.message}`);
    process.exit(2);
  } finally {
    lock.release();
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(usage());
    process.exit(1);
  }

  const cmd = args[0];
  const configPath = getArgValue(args, '--config') || null;
  const outputJson = hasFlag(args, '--json');
  const schedulePath = getArgValue(args, '--schedule') || null;

  if (cmd === 'parse') {
    const message = args.slice(1).join(' ').trim();
    if (!message) {
      console.error('parse requires a message');
      process.exit(2);
    }
    const parsed = parsePrefix(message);
    const out = outputJson ? JSON.stringify(parsed, null, 2) : `${parsed.prefix || ''}\n${parsed.body || ''}`;
    console.log(out);
    return;
  }

  if (cmd === 'validate') {
    try {
      loadConfig(configPath || undefined);
      console.log('config ok');
    } catch (err) {
      console.error(`config invalid: ${err.message}`);
      process.exit(2);
    }
    return;
  }

  if (cmd === 'route') {
    const message = args.slice(1).filter(a => a !== '--config' && a !== configPath && a !== '--json').join(' ').trim();
    if (!message) {
      console.error('route requires a message');
      process.exit(2);
    }
    const config = loadConfig(configPath || undefined);
    const parsed = parsePrefix(message);
    const route = parsed.prefix ? resolveRoute(parsed.prefix, config) : null;
    const payload = {
      prefix: parsed.prefix,
      body: parsed.body,
      route: route ? { model: route.model, fallbackModel: route.fallbackModel || null } : null,
    };
    console.log(outputJson ? JSON.stringify(payload, null, 2) : `${payload.route ? payload.route.model : 'no_route'}`);
    return;
  }

  if (cmd === 'schedule') {
    const sub = args[1] || '';
    if (!sub) {
      console.log(usage());
      process.exit(1);
    }

    if (sub === 'list') {
      const sched = loadSchedule(schedulePath || undefined);
      console.log(outputJson ? JSON.stringify(sched, null, 2) : (sched.rules || []).map(r => r.id).join('\n'));
      return;
    }

    if (sub === 'validate') {
      try {
        const sched = loadSchedule(schedulePath || undefined);
        const conflicts = detectConflicts(sched);
        if (conflicts.length > 0) {
          console.error(`schedule conflicts: ${JSON.stringify(conflicts)}`);
          process.exit(2);
        }
        console.log('schedule ok');
      } catch (err) {
        console.error(`schedule invalid: ${err.message}`);
        process.exit(2);
      }
      return;
    }

    if (sub === 'resolve') {
      const at = getArgValue(args, '--at');
      const when = at ? new Date(at) : new Date();
      const sched = loadSchedule(schedulePath || undefined);
      try {
        const rule = resolveActiveRule(sched, when);
        const payload = { at: when.toISOString(), rule: rule || null };
        console.log(outputJson ? JSON.stringify(payload, null, 2) : (rule ? rule.model : 'no_rule'));
      } catch (err) {
        console.error(`resolve failed: ${err.message}`);
        process.exit(2);
      }
      return;
    }

    if (sub === 'apply') {
      const at = getArgValue(args, '--at');
      const when = at ? new Date(at) : new Date();
      const ruleId = getArgValue(args, '--id');
      const sched = loadSchedule(schedulePath || undefined);
      const config = loadConfig(configPath || undefined);

      let rule = null;
      if (ruleId) {
        rule = (sched.rules || []).find((r) => r.id === ruleId) || null;
      } else {
        rule = resolveActiveRule(sched, when);
      }

      if (!rule) {
        const payload = { ok: false, code: 'NO_ACTIVE_RULE', at: when.toISOString(), ruleId: ruleId || null };
        if (outputJson) console.log(JSON.stringify(payload, null, 2));
        else console.log('no_rule');
        process.exit(4);
      }

      await applyRule({
        rule,
        config,
        schedulePath: schedulePath || null,
        scheduleTimezone: sched.timezone || 'local',
        outputJson,
      });
      return;
    }

    if (sub === 'end') {
      const ruleId = getArgValue(args, '--id');
      if (!ruleId) {
        console.error('schedule end requires --id');
        process.exit(2);
      }
      const sched = loadSchedule(schedulePath || undefined);
      const rule = (sched.rules || []).find((r) => r.id === ruleId) || null;
      if (!rule) {
        console.error(`rule not found: ${ruleId}`);
        process.exit(2);
      }
      const config = loadConfig(configPath || undefined);
      const fallbackModel = config.defaultModel || null;
      if (!fallbackModel) {
        console.error('defaultModel missing in router config; cannot perform schedule end');
        process.exit(2);
      }
      await applyRule({
        rule: { ...rule, id: `${rule.id}:end`, model: fallbackModel },
        config,
        schedulePath: schedulePath || null,
        scheduleTimezone: sched.timezone || 'local',
        outputJson,
      });
      return;
    }

    if (sub === 'cron') {
      const sched = loadSchedule(schedulePath || undefined);
      console.log(buildCronPreview(sched));
      return;
    }

    if (sub === 'add') {
      const id = getArgValue(args, '--id');
      const days = getArgValue(args, '--days');
      const start = getArgValue(args, '--start');
      const end = getArgValue(args, '--end');
      const model = getArgValue(args, '--model');
      const priority = getArgValue(args, '--priority');
      const disable = hasFlag(args, '--disable');
      if (!id || !days || !start || !end || !model) {
        console.error('missing required fields for schedule add');
        process.exit(2);
      }
      const sched = loadSchedule(schedulePath || undefined);
      const next = addRule(sched, {
        id,
        days,
        start,
        end,
        model,
        priority: priority ? Number(priority) : 0,
        enabled: !disable,
      });
      saveSchedule(next, schedulePath || undefined);
      console.log('schedule updated');
      return;
    }

    if (sub === 'remove') {
      const id = getArgValue(args, '--id');
      if (!id) {
        console.error('schedule remove requires --id');
        process.exit(2);
      }
      const sched = loadSchedule(schedulePath || undefined);
      const next = removeRule(sched, id);
      saveSchedule(next, schedulePath || undefined);
      console.log('schedule updated');
      return;
    }

    console.log(usage());
    process.exit(1);
  }

  console.log(usage());
  process.exit(1);
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err && err.message ? err.message : String(err));
    process.exit(1);
  });
}
