/**
 * BridgeRateLimiter.js — 5 层 Bridge 频率控制
 *
 * 防止 burst flooding 导致写锁争用卡死（曾出现 274次/小时）。
 *
 * 5 层防护：
 *   1) 滑动窗口硬上限：60 分钟内最多投递 10 次
 *   2) 最小间隔：两次投递至少间隔 120 秒
 *   3) 队列缓冲：被拦截的脉冲入队（上限 3），满时丢弃最旧
 *   4) 计数器持久化：时间戳写入文件，崩溃重启后不归零
 *   5) 锁感知：检测 main session 写锁状态，锁存在时暂缓投递
 */

const fs = require('fs');
const path = require('path');

const BRIDGE_MAX_PER_HOUR = 10;
const BRIDGE_MIN_INTERVAL_SEC = 120;
const BRIDGE_QUEUE_MAX = 3;
const BRIDGE_STATE_FILE = 'bridge_rate_state.json';

// --- 锁感知配置 ---
const MAIN_SESSION_LOCK_PATH = process.env.OPENCLAW_MAIN_SESSION_LOCK
    || path.resolve(process.env.HOME || '/root', '.openclaw/qmd/sessions/main.jsonl.lock');
const LOCK_CHECK_INTERVAL_MS = 10 * 1000;
const LOCK_TIMEOUT_MS = 5 * 60 * 1000;

class BridgeRateLimiter {
    constructor(dataDir) {
        this.dataDir = dataDir || path.resolve(__dirname, '../data');
        this.stateFilePath = path.join(this.dataDir, BRIDGE_STATE_FILE);
        this.deliveryTimestamps = [];
        this.queue = [];
        this._drainTimer = null;
        this._lockWaitQueue = [];
        this._lockPollTimer = null;
        this._lockDetectedAt = null;
        this._deliverFn = null;  // W1: 当前投递函数（实例属性）
        this._loadState();
    }

    // W4: 依赖 Node.js 单线程事件循环模型，如改为异步持久化需加互斥锁
    attempt(message, deliverFn) {
        const now = Date.now();

        // W1: 更新实例属性上的 deliverFn
        this._deliverFn = deliverFn;

        // --- 层 5: 锁感知（最高优先级） ---
        if (this._isMainSessionLocked()) {
            console.log(`[RateLimiter] 🔒 检测到 main session 写锁，脉冲暂缓投递`);
            // W2: lockWaitQueue 每个 item 存储各自的 deliverFn
            this._lockWaitEnqueue(message, deliverFn);
            return { allowed: false, reason: 'main_session_locked' };
        }

        // --- 层 1: 滑动窗口硬上限 ---
        this._pruneOldTimestamps(now);
        if (this.deliveryTimestamps.length >= BRIDGE_MAX_PER_HOUR) {
            console.log(`[RateLimiter] ⛔ 滑动窗口已满 (${this.deliveryTimestamps.length}/${BRIDGE_MAX_PER_HOUR}/h)，入队`);
            this._enqueue(message);
            return { allowed: false, reason: 'window_full' };
        }

        // --- 层 2: 最小间隔 ---
        const last = this.deliveryTimestamps[this.deliveryTimestamps.length - 1] || 0;
        const elapsed = (now - last) / 1000;
        if (elapsed < BRIDGE_MIN_INTERVAL_SEC) {
            console.log(`[RateLimiter] ⏳ 间隔不足 (${elapsed.toFixed(0)}s < ${BRIDGE_MIN_INTERVAL_SEC}s)，入队`);
            this._enqueue(message);
            return { allowed: false, reason: 'interval_too_short' };
        }

        // --- 通过所有检查 ---
        // W3: 不立即 _recordDelivery，返回 confirm() 让调用方在投递成功后确认
        const confirm = () => {
            this._recordDelivery(now);
        };
        deliverFn(message, confirm);
        this._scheduleDrain();
        return { allowed: true };
    }

    /**
     * W3: 将消息重新入队（投递失败时由 OpenClawBridge 调用）
     */
    requeue(message) {
        console.log(`[RateLimiter] 🔄 投递失败，消息重新入队`);
        this._enqueue(message);
        this._scheduleDrain();
    }

    getStatus() {
        const now = Date.now();
        this._pruneOldTimestamps(now);
        const last = this.deliveryTimestamps[this.deliveryTimestamps.length - 1] || 0;
        const locked = this._isMainSessionLocked();
        return {
            deliveriesInWindow: this.deliveryTimestamps.length,
            maxPerHour: BRIDGE_MAX_PER_HOUR,
            secondsSinceLast: last ? ((now - last) / 1000).toFixed(0) : 'never',
            minIntervalSec: BRIDGE_MIN_INTERVAL_SEC,
            queueLength: this.queue.length,
            queueMax: BRIDGE_QUEUE_MAX,
            mainSessionLocked: locked,
            lockWaitQueueLength: this._lockWaitQueue.length,
            lockDurationSec: this._lockDetectedAt
                ? ((now - this._lockDetectedAt) / 1000).toFixed(0) : null,
        };
    }

    shutdown() {
        if (this._drainTimer) {
            clearTimeout(this._drainTimer);
            this._drainTimer = null;
        }
        if (this._lockPollTimer) {
            clearInterval(this._lockPollTimer);
            this._lockPollTimer = null;
        }
        this._saveState();
    }

    // --- 锁感知方法 ---

    _isMainSessionLocked() {
        try {
            return fs.existsSync(MAIN_SESSION_LOCK_PATH);
        } catch (e) {
            console.warn('[RateLimiter] ⚠️ 锁文件检测异常:', e.message);
            return false;
        }
    }

    _lockWaitEnqueue(message, deliverFn) {
        if (!this._lockDetectedAt) {
            this._lockDetectedAt = Date.now();
        }

        // W2: 入队时存储各自的 deliverFn
        this._lockWaitQueue.push({ message, deliverFn, enqueuedAt: Date.now() });
        while (this._lockWaitQueue.length > BRIDGE_QUEUE_MAX) {
            const dropped = this._lockWaitQueue.shift();
            console.log(`[RateLimiter] 🗑️  锁等待队列已满，丢弃最旧脉冲 (入队于 ${new Date(dropped.enqueuedAt).toISOString()})`);
        }

        // 启动轮询定时器（如果尚未启动）— W1: 不再传参
        this._startLockPoll();
    }

    // W1: 使用 this._deliverFn / item.deliverFn 而非参数传递
    _startLockPoll() {
        if (this._lockPollTimer) return;

        this._lockPollTimer = setInterval(() => {
            if (this._lockDetectedAt) {
                const lockDuration = Date.now() - this._lockDetectedAt;
                if (lockDuration > LOCK_TIMEOUT_MS) {
                    console.warn(`[RateLimiter] ⚠️ 写锁已持续 ${(lockDuration / 1000 / 60).toFixed(1)} 分钟，超过 ${LOCK_TIMEOUT_MS / 1000 / 60} 分钟阈值。不强行投递，继续等待。`);
                }
            }

            if (this._isMainSessionLocked()) return;

            console.log('[RateLimiter] 🔓 写锁已释放，开始排出锁等待队列');
            this._lockDetectedAt = null;
            clearInterval(this._lockPollTimer);
            this._lockPollTimer = null;

            // W2: 逐条投递，使用各 item 自己存储的 deliverFn
            while (this._lockWaitQueue.length > 0) {
                const item = this._lockWaitQueue.shift();
                const fn = item.deliverFn || this._deliverFn;
                console.log(`[RateLimiter] 📤 锁释放后投递脉冲 (锁等待队列剩余 ${this._lockWaitQueue.length})`);
                const result = this.attempt(item.message, fn);
                if (!result.allowed) {
                    break;
                }
            }
        }, LOCK_CHECK_INTERVAL_MS);
    }

    _enqueue(message) {
        this.queue.push({ message, enqueuedAt: Date.now() });
        while (this.queue.length > BRIDGE_QUEUE_MAX) {
            const dropped = this.queue.shift();
            console.log(`[RateLimiter] 🗑️  队列已满，丢弃最旧脉冲 (入队于 ${new Date(dropped.enqueuedAt).toISOString()})`);
        }
    }

    // W1: 使用 this._deliverFn 而非参数传递
    _scheduleDrain() {
        if (this._drainTimer) return;
        if (this.queue.length === 0) return;

        const now = Date.now();
        const last = this.deliveryTimestamps[this.deliveryTimestamps.length - 1] || 0;
        const waitMs = Math.max(0, BRIDGE_MIN_INTERVAL_SEC * 1000 - (now - last)) + 500;

        this._drainTimer = setTimeout(() => {
            this._drainTimer = null;
            if (this.queue.length === 0) return;

            const drainNow = Date.now();
            this._pruneOldTimestamps(drainNow);

            const lastTs = this.deliveryTimestamps[this.deliveryTimestamps.length - 1] || 0;
            const elapsedSec = (drainNow - lastTs) / 1000;

            if (this.deliveryTimestamps.length < BRIDGE_MAX_PER_HOUR && elapsedSec >= BRIDGE_MIN_INTERVAL_SEC) {
                const item = this.queue.shift();
                console.log(`[RateLimiter] 📤 从队列排出一条脉冲 (队列剩余 ${this.queue.length})`);
                // W3: drain 也使用 confirm 模式
                const confirm = () => {
                    this._recordDelivery(drainNow);
                };
                this._deliverFn(item.message, confirm);
            }

            if (this.queue.length > 0) {
                this._scheduleDrain();
            }
        }, waitMs);
    }

    // M1: ts > cutoff 改为 ts >= cutoff
    _pruneOldTimestamps(now) {
        const cutoff = now - 60 * 60 * 1000;
        this.deliveryTimestamps = this.deliveryTimestamps.filter(ts => ts >= cutoff);
    }

    _recordDelivery(now) {
        this.deliveryTimestamps.push(now);
        this._saveState();
    }

    _saveState() {
        try {
            if (!fs.existsSync(this.dataDir)) {
                fs.mkdirSync(this.dataDir, { recursive: true });
            }
            const state = { deliveryTimestamps: this.deliveryTimestamps };
            const tmpPath = this.stateFilePath + '.tmp';
            fs.writeFileSync(tmpPath, JSON.stringify(state, null, 2), 'utf8');
            fs.renameSync(tmpPath, this.stateFilePath);
        } catch (e) {
            console.error('[RateLimiter] ❌ 持久化失败:', e.message);
        }
    }

    _loadState() {
        try {
            if (fs.existsSync(this.stateFilePath)) {
                const raw = fs.readFileSync(this.stateFilePath, 'utf8');
                const state = JSON.parse(raw);
                if (Array.isArray(state.deliveryTimestamps)) {
                    this.deliveryTimestamps = state.deliveryTimestamps;
                    this._pruneOldTimestamps(Date.now());
                    console.log(`[RateLimiter] 📂 已恢复 ${this.deliveryTimestamps.length} 条投递记录`);
                }
            }
        } catch (e) {
            console.warn('[RateLimiter] ⚠️ 读取持久化状态失败，从零开始:', e.message);
            this.deliveryTimestamps = [];
        }
    }
}

module.exports = BridgeRateLimiter;
