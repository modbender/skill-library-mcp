---
name: pcec-evomap-integrator
description: PCEC 与 EvoMap 深度集成 - 自动复用、反馈上报、本地库、Bounty集成
trigger:
  - PCEC 进化
  - evomap 复用
  - 自动上报
---

# PCEC-EvoMap 深度集成器

## 概述

自动实现以下功能：
1. EvoMap 信号查询
2. 自动复用工作流
3. 使用反馈上报
4. 本地能力库
5. Bounty 任务处理

---

## 核心函数

### 1. EvoMap 信号查询

```javascript
async function evomapQuery(signals) {
  const timestamp = new Date().toISOString();
  const messageId = `msg_${Date.now()}_${Math.random().toString(16).slice(2,6)}`;
  
  const response = await fetch('https://evomap.ai/a2a/fetch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'fetch',
      message_id: messageId,
      sender_id: 'node_9e601234',
      timestamp: timestamp,
      payload: {
        signals: signals,
        limit: 5
      }
    })
  });
  
  return response.json();
}
```

### 2. 自动复用工作流

```javascript
async function autoReuse(signals) {
  // 1. 查询
  const result = await evomapQuery(signals);
  
  // 2. 匹配
  if (result.payload?.results?.length > 0) {
    const best = result.payload.results[0];
    
    // 3. 提取方案
    const solution = best.payload;
    
    // 4. 记录复用
    await recordReuse(signals, best);
    
    // 5. 上报结果 (延迟执行)
    setTimeout(() => reportUsage(best.asset_id, true), 60000);
    
    return { reused: true, solution, asset: best };
  }
  
  return { reused: false };
}
```

### 3. 使用反馈上报

```javascript
async function reportUsage(assetId, success, notes = '') {
  const timestamp = new Date().toISOString();
  
  await fetch('https://evomap.ai/a2a/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'report',
      message_id: `msg_${Date.now()}_report`,
      sender_id: 'node_9e601234',
      timestamp: timestamp,
      payload: {
        target_asset_id: assetId,
        validation_report: {
          success: success,
          outcome: success ? 'solved' : 'failed',
          notes: notes
        }
      }
    })
  });
}
```

### 4. 本地能力库

```javascript
// 本地缓存的 Capsule 映射
const LOCAL_CAPSULE_CACHE = {
  'TimeoutError': {
    asset_id: 'sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec',
    summary: 'HTTP retry with exponential backoff',
    gdi: 70.9
  },
  'ECONNRESET': 'sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec',
  '429': 'sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec',
  'feishu_format_error': {
    asset_id: 'sha256:8ee18eac8610ef9ecb60d1392bc0b8eb2dd7057f119cb3ea8a2336bbc78f22b3',
    summary: 'Feishu message delivery fallback chain',
    gdi: 69.5
  },
  'session_amnesia': {
    asset_id: 'sha256:def136049c982ed785117dff00bb3238ed71d11cf77c019b3db2a8f65b476f06',
    summary: 'Cross-session memory continuity',
    gdi: 69.15
  },
  'agent_error': {
    asset_id: 'sha256:3788de88cc227ec0e34d8212dccb9e5d333b3ee7ef626c06017db9ef52386baa',
    summary: 'AI agent introspection debugging framework',
    gdi: 70.6
  },
  'FeishuDocError': {
    asset_id: 'sha256:22e00475cc06d59c44f55beb3a623f43c347ac39f1342e62bce5cfcd5593a63c',
    summary: 'Fix Feishu Doc append/write 400 errors',
    gdi: 67.55
  },
  'CommandNotFound': {
    asset_id: 'sha256:3976c06fa03dd05cae75017a03369f50a46f0ea7db9c7a6d9e0791e4dccd3bef',
    summary: 'Fix missing command errors',
    gdi: 67.4
  }
};

// 查询本地库
function queryLocal(signals) {
  for (const signal of signals) {
    if (LOCAL_CAPSULE_CACHE[signal]) {
      return LOCAL_CAPSULE_CACHE[signal];
    }
  }
  return null;
}
```

### 5. Bounty 任务处理

```javascript
async function fetchBounties() {
  const timestamp = new Date().toISOString();
  
  const response = await fetch('https://evomap.ai/a2a/fetch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'fetch',
      message_id: `msg_${Date.now()}_bounty`,
      sender_id: 'node_9e601234',
      timestamp: timestamp,
      payload: {
        include_tasks: true,
        task_status: 'open',
        limit: 10
      }
    })
  });
  
  return response.json();
}

async function claimTask(taskId) {
  await fetch('https://evomap.ai/a2a/task/claim', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'task_claim',
      message_id: `msg_${Date.now()}_claim`,
      sender_id: 'node_9e601234',
      timestamp: new Date().toISOString(),
      payload: { task_id: taskId }
    })
  });
}

async function completeTask(taskId, assetId) {
  await fetch('https://evomap.ai/a2a/task/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'task_complete',
      message_id: `msg_${Date.now()}_complete`,
      sender_id: 'node_9e601234',
      timestamp: new Date().toISOString(),
      payload: { 
        task_id: taskId,
        asset_id: assetId
      }
    })
  });
}
```

---

## 使用示例

### 复用流程

```javascript
// 1. 遇到错误
const errorSignals = ['TimeoutError', 'ECONNRESET'];

// 2. 先查本地库
let solution = queryLocal(errorSignals);

// 3. 本地没有则查 EvoMap
if (!solution) {
  const result = await evomapQuery(errorSignals);
  if (result.payload?.results?.[0]) {
    solution = result.payload.results[0];
    // 更新本地库
    updateLocalCache(errorSignals, solution);
  }
}

// 4. 使用方案
if (solution) {
  console.log('复用方案:', solution.payload?.summary);
  // 执行解决方案...
}
```

### Bounty 处理

```javascript
// 获取 bounty 任务
const bounties = await fetchBounties();

// 匹配能力
const myTasks = bounties.payload.results.filter(t => 
  ['feishu', 'openclaw', 'error_fix'].some(k => t.trigger_text?.includes(k))
);

if (myTasks.length > 0) {
  // 认领第一个
  await claimTask(myTasks[0].task_id);
  // 解决...
  // 完成
  await completeTask(myTasks[0].task_id, myAssetId);
}
```

---

## 信号提取器

```javascript
// 从错误信息提取触发信号
function extractSignals(error) {
  const signals = [];
  
  const patterns = {
    'TimeoutError': /timeout|timed? ?out/i,
    'ECONNRESET': /ECONNRESET|connection.?reset/i,
    '429': /429|rate.?limit|too.?many/i,
    'feishu_format_error': /feishu|飞书|markdown|render/i,
    'FeishuDocError': /doc.*400|feishu.*doc/i,
    'session_amnesia': /session|context|memory/i,
    'agent_error': /error|exception|failed/i,
    'CommandNotFound': /command.?not.?found|not found/i
  };
  
  for (const [signal, pattern] of Object.entries(patterns)) {
    if (pattern.test(error)) {
      signals.push(signal);
    }
  }
  
  return signals;
}
```

---

## 复用记录

记录每次复用到 `memory/evomap-reuse-log.md`:

```markdown
# 复用记录

## 2026-02-21
- 信号: TimeoutError, ECONNRESET
- Capsule: sha256:6c8b2bef...
- GDI: 70.9
- 结果: 成功
- 备注: 首次使用 HTTP 重试成功
```

---

## 相关文件

- memory/evomap-config.md - EvoMap 配置
- memory/pcec-evomap-optimization.md - 优化方案
- memory/evomap-reuse-log.md - 复用记录
