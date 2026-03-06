---
name: batch-processing-patterns
version: 1.0.0
description: 批量处理与长时任务编排模式。涵盖队列管理、并发调度、中断恢复、熔断器、远程任务轮询、进度报告和反风控策略。适用于批量文件处理、AI API 调用、爬虫和后台任务场景。
---

# 批量处理与长时任务指南

来自生产级桌面应用的实战经验，覆盖批量文件处理、远程 API 轮询、并发控制和错误恢复。

## 适用场景

- 批量文件处理（转码、压缩、水印）
- 远程 AI 任务轮询（视频生成、语音合成）
- 爬虫/批量 HTTP 请求
- 后台队列任务

---

## 1. 批处理架构

```
任务队列
├── 并发调度器（动态调整并发数）
│   ├── Worker 1 → processItem()
│   ├── Worker 2 → processItem()
│   └── Worker N → processItem()
├── 中止控制器（shouldStop + 子进程清理）
├── 熔断器（连续失败 N 次暂停）
├── 跳过检查（断点续传 / 前置过滤）
└── 进度报告（per-item + overall）
```

### 核心原则

1. **逐项处理，逐项报告** — 不等全部完成
2. **中断即停** — 每个 item 之间检查 abort 信号
3. **失败不中断** — 单项失败标记 `failed`，继续处理其他
4. **熔断保护** — 连续失败超阈值暂停整个队列

---

## 2. 并发调度

### 自适应并发池

根据每个 item 的处理耗时动态调整并发数：

```typescript
class AdaptiveScheduler {
  private concurrency: number;
  private running = 0;
  private queue: (() => void)[] = [];

  constructor(
    private min: number,
    private max: number,
    private slowThresholdMs: number
  ) {
    this.concurrency = Math.ceil((min + max) / 2);
  }

  async run<T>(fn: () => Promise<T>): Promise<T> {
    if (this.running >= this.concurrency) {
      await new Promise<void>((resolve) => this.queue.push(resolve));
    }
    this.running++;
    const start = Date.now();

    try {
      return await fn();
    } finally {
      const elapsed = Date.now() - start;
      this.running--;

      // 自适应调整
      if (elapsed > this.slowThresholdMs && this.concurrency > this.min) {
        this.concurrency--;
      } else if (elapsed < this.slowThresholdMs / 2 && this.concurrency < this.max) {
        this.concurrency++;
      }

      if (this.queue.length > 0) {
        this.queue.shift()!();
      }
    }
  }
}
```

### 预设配置

| 场景 | 初始 | 最小 | 最大 | 慢阈值 |
|------|------|------|------|--------|
| CPU 密集（FFmpeg 转码） | 4 | 1 | CPU 核数 | 3s |
| API 调用（AI 服务） | 3 | 1 | 5 | 8s |
| 文件 I/O | 2 | 1 | 3 | 30s |
| 串行（必须顺序） | 1 | 1 | 1 | - |

### 简易并发池（不需要自适应时）

```typescript
async function runPool<T>(
  items: T[],
  fn: (item: T) => Promise<void>,
  concurrency: number,
  signal?: AbortSignal
): Promise<{ completed: number; failed: number }> {
  let completed = 0, failed = 0;
  const running = new Set<Promise<void>>();

  for (const item of items) {
    if (signal?.aborted) break;

    const p = fn(item)
      .then(() => { completed++; })
      .catch(() => { failed++; });

    running.add(p.then(() => { running.delete(p); }));

    if (running.size >= concurrency) {
      await Promise.race(running);
    }
  }
  await Promise.all(running);
  return { completed, failed };
}
```

---

## 3. 中断与恢复

### AbortController 模式

```typescript
class BatchAbortController {
  private _aborted = false;
  private callbacks: (() => void)[] = [];

  get aborted() { return this._aborted; }

  abort() {
    if (this._aborted) return; // 幂等
    this._aborted = true;
    this.callbacks.forEach((cb) => cb());
  }

  onAbort(cb: () => void) {
    if (this._aborted) { cb(); return; }
    this.callbacks.push(cb);
  }

  reset() {
    this._aborted = false;
    this.callbacks = [];
  }
}
```

### 断点续传（shouldSkip）

```typescript
const completedSet = new Set(loadCompletedFromDisk());

function shouldSkip(item: FileItem): string | null {
  if (completedSet.has(item.path)) return '已完成（断点续传）';
  if (item.size <= targetSize) return '已满足目标条件';
  return null; // 正常处理
}

// 在批处理循环中
for (const item of items) {
  if (abortController.aborted) break;

  const skipReason = shouldSkip(item);
  if (skipReason) {
    onItemSkip(item, skipReason);
    continue;
  }

  try {
    await processItem(item);
    completedSet.add(item.path);
    saveCompletedToDisk(completedSet); // 持久化进度
    onItemComplete(item);
  } catch (err) {
    onItemError(item, err);
  }
}
```

---

## 4. 熔断器

连续失败过多时自动暂停，避免无意义的重试浪费资源。

```typescript
class CircuitBreaker {
  private consecutiveFailures = 0;

  constructor(
    private maxFailures: number = 5,
    private onTrip?: (failures: number) => void
  ) {}

  recordSuccess() {
    this.consecutiveFailures = 0;
  }

  recordFailure(): boolean {
    this.consecutiveFailures++;
    if (this.consecutiveFailures >= this.maxFailures) {
      this.onTrip?.(this.consecutiveFailures);
      return true; // tripped
    }
    return false;
  }

  get isTripped() {
    return this.consecutiveFailures >= this.maxFailures;
  }

  reset() {
    this.consecutiveFailures = 0;
  }
}
```

---

## 5. 远程任务轮询

### 递归 setTimeout 模式（推荐）

```typescript
function startPolling(taskId: string, interval = 5000) {
  const poll = async () => {
    try {
      const result = await queryTaskStatus(taskId);

      if (result.status === 'completed') {
        onComplete(result);
        return; // 停止轮询
      }
      if (result.status === 'failed') {
        onFailed(result);
        return;
      }

      // 超时检查
      if (Date.now() - startTime > MAX_POLL_TIME) {
        onTimeout(taskId);
        return;
      }

      setTimeout(poll, interval); // 继续
    } catch (err) {
      if (isCriticalError(err)) return; // 停止
      setTimeout(poll, interval); // 瞬态错误继续
    }
  };

  poll();
}
```

### 关键要点

- **用 `setTimeout` 而非 `setInterval`** — 确保前一次完成后再调度下一次
- **超时保护** — 总轮询时间有上限，避免永久轮询
- **错误分类** — 瞬态错误继续轮询，致命错误立即停止
- **去重** — 用 Set 防止同一任务重复轮询

### 批量轮询（多任务顺序轮询）

```typescript
// 多任务并发轮询可能触发限流，改为顺序轮询
const pollAll = async () => {
  const activeTasks = getActiveTasks();

  for (const task of activeTasks) {
    if (aborted) return;
    await pollOne(task.id);
    // 任务间延迟，尊重 QPS
    if (activeTasks.length > 1) {
      await sleep(2000);
    }
  }

  if (getActiveTasks().length > 0) {
    setTimeout(pollAll, POLL_INTERVAL);
  }
};
```

---

## 6. 错误分类与处理

| 错误类型 | 行为 | 示例 |
|---------|------|------|
| 瞬态网络错误 | 重试 | timeout, ECONNRESET |
| 401 Unauthorized | **停止** | API Key 无效 |
| 403 / 余额不足 | **停止** | 账户问题 |
| 429 Too Many Requests | **退避重试** | 限流 |
| 500+ Server Error | 有限重试（3 次） | 服务端异常 |
| 文件不存在 | 跳过此项 | 输入文件被删 |
| 磁盘空间不足 | **停止全部** | ENOSPC |

### 指数退避重试

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 2000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxRetries) throw err;
      if (isFatalError(err)) throw err; // 不重试

      const delay = baseDelay * Math.pow(2, attempt)
        + Math.random() * 1000; // 抖动
      await sleep(delay);
    }
  }
  throw new Error('unreachable');
}
```

---

## 7. 进度报告

### 双层进度

```typescript
interface BatchProgress {
  // 整体进度
  current: number;       // 已处理项数
  total: number;         // 总项数
  percentage: number;    // 0-100

  // 当前项进度（可选）
  currentItem?: {
    name: string;
    itemProgress: number; // 0-100
  };
}

// 报告整体进度
function reportProgress(done: number, total: number) {
  send({ current: done, total, percentage: Math.round(done / total * 100) });
}
```

### 进度节流

```typescript
// GUI 场景必须节流，否则高频更新会卡 UI
const throttledProgress = throttle(reportProgress, 100); // 10fps
```

---

## 8. 反风控策略（批量 HTTP 请求）

### 三层防护

```
请求节流（同域名限速）→ 风控检测（响应分析）→ 指数退避重试
```

### 请求节流

```typescript
const lastRequest = new Map<string, number>();

async function throttleByDomain(domain: string) {
  const last = lastRequest.get(domain) || 0;
  const minInterval = 1500 + Math.random() * 1500; // 1.5-3s 随机
  const wait = minInterval - (Date.now() - last);
  if (wait > 0) await sleep(wait);
  lastRequest.set(domain, Date.now());
}
```

### 风控检测

即使 HTTP 200 也要检查响应内容：
- 验证码页面关键词（captcha, 滑块验证）
- 空壳页面（body < 500 字节）
- 重定向到登录页

### UA 轮换

```typescript
const USER_AGENTS = [
  'Mozilla/5.0 (Macintosh; ...) Chrome/...',
  'Mozilla/5.0 (Windows NT ...) Chrome/...',
  'Mozilla/5.0 (iPhone; ...) Safari/...',
];

function randomUA(): string {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}
```

---

## 9. Checklist

### 新增批处理功能
- [ ] 有 AbortController 中止机制
- [ ] 有并发控制（不超过 CPU 核数）
- [ ] 单项失败不中断整体
- [ ] 有熔断器（连续失败 5 次暂停）
- [ ] 进度通过节流后的回调报告
- [ ] 错误分类处理（瞬态 vs 致命）
- [ ] 临时文件在 finally 中清理

### 远程任务轮询
- [ ] 用 setTimeout 而非 setInterval
- [ ] 有超时上限
- [ ] 有去重机制
- [ ] 401/403 立即停止轮询
- [ ] 429 指数退避

### 批量 HTTP 请求
- [ ] 同域名请求间隔 ≥ 1.5s
- [ ] 检测风控响应（captcha/空页面）
- [ ] 退避重试（2s → 4s → 8s）

---

## 来源

提炼自生产级 Electron 桌面应用，覆盖 6+ 个批处理模块和 3 个远程轮询场景的实战经验。
