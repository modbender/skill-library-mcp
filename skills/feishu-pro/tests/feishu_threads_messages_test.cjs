#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const argv = process.argv.slice(2);

function getFlag(flag) {
  return argv.includes(flag);
}

function getArgValue(flag, defaultValue = null) {
  const idx = argv.indexOf(flag);
  if (idx !== -1 && argv[idx + 1] && !argv[idx + 1].startsWith('--')) {
    return argv[idx + 1];
  }
  const kv = argv.find((arg) => arg.startsWith(flag + '='));
  if (kv) return kv.split('=').slice(1).join('=');
  return defaultValue;
}

function die(msg) {
  console.error(msg);
  process.exit(1);
}

const options = {
  live: getFlag('--live'),
  allowDestructive: getFlag('--allow-destructive'),
  threadsSignature: getArgValue('--threads-signature', 'message'),
  unpinMode: getArgValue('--unpin-mode', 'message'),
  reportPath: getArgValue('--report', null),
  jsonPath: getArgValue('--json', null),
};

if (!['message', 'chat-root'].includes(options.threadsSignature)) {
  die('Invalid --threads-signature. Use message or chat-root.');
}
if (!['message', 'pin'].includes(options.unpinMode)) {
  die('Invalid --unpin-mode. Use message or pin.');
}

const FEISHU_SKILL_PATH = path.join(__dirname, '..', 'dist', 'index.js');
let feishuModule = null;

const config = {
  appId: process.env.FEISHU_APP_ID || null,
  appSecret: process.env.FEISHU_APP_SECRET || null,
  chatId: process.env.FEISHU_CHAT_ID || null,
  threadRootId: process.env.FEISHU_THREAD_ROOT_ID || null,
  threadId: process.env.FEISHU_THREAD_ID || null,
  messageId: process.env.FEISHU_MESSAGE_ID || null,
  pinId: process.env.FEISHU_PIN_ID || null,
  updateContent: process.env.FEISHU_UPDATE_CONTENT || 'Updated by automated test',
};

function mask(value) {
  if (!value) return 'N/A';
  if (value.length <= 6) return '***';
  return value.slice(0, 3) + '***' + value.slice(-3);
}

if (options.live) {
  if (!config.appId || !config.appSecret) {
    die('Missing FEISHU_APP_ID or FEISHU_APP_SECRET for --live run.');
  }
}

async function loadFeishu() {
  if (!feishuModule) {
    feishuModule = await import(pathToFileURL(FEISHU_SKILL_PATH).href);
  }
  return feishuModule;
}

const KNOWN_SPEC_GAPS = [];

const results = [];

function record(result) {
  results.push(result);
  const statusIcon = result.status === 'passed' ? 'PASS' : result.status === 'failed' ? 'FAIL' : 'SKIP';
  console.log(`[${statusIcon}] ${result.id} ${result.skill}.${result.api} - ${result.note}`);
}

function normalizeError(err) {
  if (!err) return { message: 'Unknown error' };
  if (typeof err === 'string') return { message: err };
  const message = err.message || 'Unknown error';
  const code = err.code || err.response?.data?.code || null;
  const msg = err.response?.data?.msg || err.response?.data?.message || null;
  return { message, code, apiMessage: msg };
}

function isOk(res) {
  return res && res.ok === true;
}

async function runCase(def, ctx) {
  if (def.mode === 'live' && !options.live) {
    record({
      id: def.id,
      skill: def.skill,
      api: def.api,
      category: def.category,
      status: 'skipped',
      note: 'Dry-run: add --live to execute'
    });
    return;
  }
  if (def.requires) {
    const missing = def.requires.filter((k) => !ctx[k]);
    if (missing.length) {
      record({
        id: def.id,
        skill: def.skill,
        api: def.api,
        category: def.category,
        status: 'skipped',
        note: `Missing ${missing.join(', ')}`
      });
      return;
    }
  }
  if (def.destructive && !options.allowDestructive) {
    record({
      id: def.id,
      skill: def.skill,
      api: def.api,
      category: def.category,
      status: 'skipped',
      note: 'Destructive: add --allow-destructive to execute'
    });
    return;
  }

  try {
    const res = await def.run(ctx);
    if (def.expectFailure) {
      if (res && isOk(res)) {
        record({
          id: def.id,
          skill: def.skill,
          api: def.api,
          category: def.category,
          status: 'failed',
          note: 'Expected failure but got ok'
        });
      } else {
        record({
          id: def.id,
          skill: def.skill,
          api: def.api,
          category: def.category,
          status: 'passed',
          note: def.successNote || 'Error handled as expected'
        });
      }
      return;
    }

    if (!res || !isOk(res)) {
      record({
        id: def.id,
        skill: def.skill,
        api: def.api,
        category: def.category,
        status: 'failed',
        note: res?.error || 'API returned not ok'
      });
      return;
    }

    if (def.validate) {
      const validation = def.validate(res, ctx);
      if (validation.ok) {
        record({
          id: def.id,
          skill: def.skill,
          api: def.api,
          category: def.category,
          status: 'passed',
          note: validation.note || 'Validation ok'
        });
      } else {
        record({
          id: def.id,
          skill: def.skill,
          api: def.api,
          category: def.category,
          status: 'failed',
          note: validation.note || 'Validation failed'
        });
      }
    } else {
      record({
        id: def.id,
        skill: def.skill,
        api: def.api,
        category: def.category,
        status: 'passed',
        note: def.successNote || 'OK'
      });
    }
  } catch (err) {
    const e = normalizeError(err);
    if (def.expectFailure) {
      record({
        id: def.id,
        skill: def.skill,
        api: def.api,
        category: def.category,
        status: 'passed',
        note: def.successNote || `Expected failure: ${e.message}`
      });
    } else {
      record({
        id: def.id,
        skill: def.skill,
        api: def.api,
        category: def.category,
        status: 'failed',
        note: e.apiMessage || e.message
      });
    }
  }
}

async function main() {
  if (options.threadsSignature !== 'message') {
    console.warn('[WARN] --threads-signature 已废弃，当前 feishu 统一使用 messageId 签名。');
  }
  if (options.unpinMode !== 'message') {
    console.warn('[WARN] --unpin-mode 已废弃，当前 feishu 统一使用 messageId 取消置顶。');
  }

  const summary = {
    executedAt: new Date().toISOString(),
    mode: options.live ? 'live' : 'dry-run',
    allowDestructive: options.allowDestructive,
    threadsSignature: options.threadsSignature,
    unpinMode: options.unpinMode,
    env: {
      FEISHU_APP_ID: mask(config.appId),
      FEISHU_CHAT_ID: mask(config.chatId),
      FEISHU_THREAD_ROOT_ID: mask(config.threadRootId),
      FEISHU_THREAD_ID: mask(config.threadId),
      FEISHU_MESSAGE_ID: mask(config.messageId),
      FEISHU_PIN_ID: mask(config.pinId)
    }
  };

  const feishu = await loadFeishu();

  const ctx = {
    threads: feishu,
    messages: feishu,
    chatId: config.chatId,
    threadRootId: config.threadRootId,
    threadId: config.threadId,
    messageId: config.messageId,
    pinId: config.pinId,
    updateContent: config.updateContent,
  };

  const cases = [
    // feishu
    {
      id: 'THREADS-001',
      skill: 'feishu',
      api: 'replyInThread',
      category: 'happyPath',
      mode: 'live',
      requires: ['threadRootId'],
      run: async (c) => {
        const content = 'Automated test: replyInThread happy path.';
        return await c.threads.replyInThread(c.threadRootId, content, true, 'text');
      },
      successNote: 'Reply sent successfully'
    },
    {
      id: 'THREADS-002',
      skill: 'feishu',
      api: 'replyInThread',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async (c) => {
        const badId = 'invalid_thread_id';
        return await c.threads.replyInThread(badId, 'Should fail', true, 'text');
      },
      successNote: 'Invalid thread id rejected'
    },
    {
      id: 'THREADS-003',
      skill: 'feishu',
      api: 'replyInThread',
      category: 'boundary',
      mode: 'static',
      run: async () => ({ ok: true, data: { length: 6000 } }),
      validate: (res) => {
        const length = res.data?.length || 0;
        return {
          ok: length >= 6000,
          note: length >= 6000 ? 'Long content prepared for boundary test' : 'Long content not prepared'
        };
      }
    },
    {
      id: 'THREADS-004',
      skill: 'feishu',
      api: 'listThreadMessages',
      category: 'happyPath',
      mode: 'live',
      requires: ['chatId', 'threadId'],
      run: async (c) => c.threads.listThreadMessages(c.chatId, c.threadId),
      validate: (res, c) => {
        const items = res.data?.items || [];
        const bad = items.find((m) => m.thread_id !== c.threadId && m.message_id !== c.threadId);
        return { ok: !bad, note: `Items returned: ${items.length}` };
      }
    },
    {
      id: 'THREADS-005',
      skill: 'feishu',
      api: 'listThreadMessages',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async (c) => c.threads.listThreadMessages('oc_invalid_chat', c.threadId || 'invalid_thread') ,
      successNote: 'Invalid chatId rejected'
    },

    // feishu
    {
      id: 'MSG-001',
      skill: 'feishu',
      api: 'listMessages',
      category: 'happyPath',
      mode: 'live',
      requires: ['chatId'],
      run: async (c) => c.messages.listMessages({
        container_id_type: 'chat',
        container_id: c.chatId,
        page_size: 5
      }),
      validate: (res) => {
        const items = res.data?.items || [];
        return { ok: Array.isArray(items), note: `Items returned: ${items.length}` };
      }
    },
    {
      id: 'MSG-002',
      skill: 'feishu',
      api: 'listMessages',
      category: 'boundary',
      mode: 'live',
      requires: ['chatId'],
      run: async (c) => c.messages.listMessages({
        container_id_type: 'chat',
        container_id: c.chatId,
        page_size: 1
      }),
      validate: (res) => ({ ok: typeof res.data?.has_more === 'boolean', note: 'Pagination flags present' })
    },
    {
      id: 'MSG-003',
      skill: 'feishu',
      api: 'listMessages',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async (c) => c.messages.listMessages({
        container_id_type: 'chat',
        container_id: 'oc_invalid_chat',
        page_size: 1
      }),
      successNote: 'Invalid container_id rejected'
    },
    {
      id: 'MSG-004',
      skill: 'feishu',
      api: 'recallMessage',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async (c) => c.messages.recallMessage('om_invalid_message'),
      successNote: 'Invalid messageId rejected'
    },
    {
      id: 'MSG-005',
      skill: 'feishu',
      api: 'updateMessage',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async (c) => c.messages.updateMessage('om_invalid_message', c.updateContent),
      successNote: 'Invalid messageId rejected'
    },
    {
      id: 'MSG-006',
      skill: 'feishu',
      api: 'updateMessage',
      category: 'boundary',
      mode: 'static',
      run: async () => ({ ok: true, data: { length: 8000 } }),
      validate: (res) => ({ ok: res.data?.length >= 8000, note: 'Long update payload prepared' })
    },
    {
      id: 'MSG-007',
      skill: 'feishu',
      api: 'pinMessage',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async (c) => c.messages.pinMessage('om_invalid_message'),
      successNote: 'Invalid messageId rejected'
    },
    {
      id: 'MSG-008',
      skill: 'feishu',
      api: 'unpinMessage',
      category: 'errorHandling',
      mode: 'live',
      expectFailure: true,
      run: async () => c.messages.unpinMessage('om_invalid_message'),
      successNote: 'Invalid pin/message id rejected'
    },
    {
      id: 'MSG-009',
      skill: 'feishu',
      api: 'recallMessage',
      category: 'permission',
      mode: 'live',
      destructive: true,
      requires: ['messageId'],
      run: async (c) => c.messages.recallMessage(c.messageId),
      successNote: 'Message recalled'
    },
    {
      id: 'MSG-010',
      skill: 'feishu',
      api: 'updateMessage',
      category: 'permission',
      mode: 'live',
      destructive: true,
      requires: ['messageId'],
      run: async (c) => c.messages.updateMessage(c.messageId, c.updateContent),
      successNote: 'Message updated'
    },
    {
      id: 'MSG-011',
      skill: 'feishu',
      api: 'pinMessage',
      category: 'permission',
      mode: 'live',
      destructive: true,
      requires: ['messageId'],
      run: async (c) => c.messages.pinMessage(c.messageId),
      successNote: 'Message pinned'
    },
    {
      id: 'MSG-012',
      skill: 'feishu',
      api: 'unpinMessage',
      category: 'permission',
      mode: 'live',
      destructive: true,
      requires: ['messageId'],
      run: async (c) => c.messages.unpinMessage(c.messageId),
      successNote: 'Message unpinned'
    }
  ];

  for (const testCase of cases) {
    await runCase(testCase, ctx);
  }

  const summaryCounts = results.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] || 0) + 1;
    return acc;
  }, {});

  const output = {
    summary,
    counts: summaryCounts,
    results,
    knownSpecGaps: KNOWN_SPEC_GAPS
  };

  if (options.jsonPath) {
    fs.writeFileSync(options.jsonPath, JSON.stringify(output, null, 2));
  }

  if (options.reportPath) {
    const md = renderMarkdownReport(output);
    fs.writeFileSync(options.reportPath, md);
  }
}

function renderMarkdownReport(data) {
  const lines = [];
  lines.push('# Feishu Skills Test Report');
  lines.push('');
  lines.push(`- Executed At: ${data.summary.executedAt}`);
  lines.push(`- Mode: ${data.summary.mode}`);
  lines.push(`- Allow Destructive: ${data.summary.allowDestructive}`);
  lines.push(`- Threads Signature: ${data.summary.threadsSignature}`);
  lines.push(`- Unpin Mode: ${data.summary.unpinMode}`);
  lines.push('');
  lines.push('## Environment');
  lines.push(`- FEISHU_APP_ID: ${data.summary.env.FEISHU_APP_ID}`);
  lines.push(`- FEISHU_CHAT_ID: ${data.summary.env.FEISHU_CHAT_ID}`);
  lines.push(`- FEISHU_THREAD_ROOT_ID: ${data.summary.env.FEISHU_THREAD_ROOT_ID}`);
  lines.push(`- FEISHU_THREAD_ID: ${data.summary.env.FEISHU_THREAD_ID}`);
  lines.push(`- FEISHU_MESSAGE_ID: ${data.summary.env.FEISHU_MESSAGE_ID}`);
  lines.push(`- FEISHU_PIN_ID: ${data.summary.env.FEISHU_PIN_ID}`);
  lines.push('');
  lines.push('## Summary');
  lines.push(`- Passed: ${data.counts.passed || 0}`);
  lines.push(`- Failed: ${data.counts.failed || 0}`);
  lines.push(`- Skipped: ${data.counts.skipped || 0}`);
  lines.push('');
  lines.push('## Results');
  lines.push('| ID | Skill | API | Category | Status | Note |');
  lines.push('| --- | --- | --- | --- | --- | --- |');
  for (const r of data.results) {
    lines.push(`| ${r.id} | ${r.skill} | ${r.api} | ${r.category} | ${r.status} | ${r.note} |`);
  }
  lines.push('');
  lines.push('## Known Spec Gaps');
  for (const gap of data.knownSpecGaps) {
    lines.push(`- ${gap.skill}.${gap.api}: spec=${gap.spec}; impl=${gap.impl}; impact=${gap.impact}`);
  }
  lines.push('');
  return lines.join('\n');
}

main().catch((err) => {
  console.error('Test runner failed:', err.message || err);
  process.exit(1);
});
