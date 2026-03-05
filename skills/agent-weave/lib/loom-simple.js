const { randomUUID } = require('crypto');
const EventEmitter = require('events');

/**
 * Agent 基础类
 */
class Agent extends EventEmitter {
  constructor({ name, type, parentId = null }) {
    super();
    this.id = randomUUID();
    this.name = name;
    this.type = type;
    this.parentId = parentId;
    this.status = 'active';
    this.createdAt = Date.now();
  }

  destroy() {
    this.status = 'destroyed';
    this.removeAllListeners();
  }
}

/**
 * Master Agent - 管理 Worker 集群
 */
class Master extends Agent {
  constructor(name, loom, options = {}) {
    super({ name, type: 'master' });
    this.loom = loom;
    this.workers = new Map();
    this.results = [];
    this.options = options;
    this.capabilities = options.capabilities || [];
  }

  get identity() {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      capabilities: this.capabilities
    };
  }

  get identity() {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      capabilities: this.options.capabilities || []
    };
  }

  get identity() {
    return {
      id: this.id,
      name: this.name,
      type: this.type
    };
  }

  spawn(count, taskFn, options = {}) {
    console.log(`[Master:${this.name}] 创建 ${count} 个 Worker...`);

    for (let i = 0; i < count; i++) {
      const worker = new Worker(
        `${this.name}-worker-${i}`,
        this.id,
        taskFn
      );

      this.workers.set(worker.id, worker);

      worker.on('complete', (result) => {
        this.results.push({ workerId: worker.id, result });
      });

      worker.on('error', (error) => {
        console.error(`[Master] Worker ${worker.id} 错误:`, error);
      });
    }

    console.log(`[Master] 已创建 ${this.workers.size} 个 Worker`);
    return this;
  }

  async dispatch(inputs) {
    console.log(`[Master] 分发 ${inputs.length} 个任务到 ${this.workers.size} 个 Worker...`);

    const workerList = Array.from(this.workers.values());
    const promises = [];

    for (let i = 0; i < inputs.length; i++) {
      const input = inputs[i];
      const worker = workerList[i % workerList.length];

      const promise = worker.execute(input).then(result => {
        this.results[i] = result;
        return result;
      });

      promises.push(promise);
    }

    await Promise.all(promises);
    return this.aggregate();
  }

  aggregate() {
    const success = this.results.filter(r => r && r.success).length;
    const failed = this.results.length - success;

    console.log(`[Master] 任务完成: ${success} 成功, ${failed} 失败`);

    return {
      master: this.name,
      workers: this.workers.size,
      results: this.results,
      summary: { total: this.results.length, success, failed }
    };
  }

  destroy() {
    console.log(`[Master] 销毁 ${this.workers.size} 个 Worker...`);
    for (const [id, worker] of this.workers) {
      worker.destroy();
    }
    this.workers.clear();
    this.results = [];
    super.destroy();
  }
}

/**
 * Worker Agent - 执行具体任务
 */
class Worker extends Agent {
  constructor(name, masterId, taskFn) {
    super({ name, type: 'worker', parentId: masterId });
    this.masterId = masterId;
    this.taskFn = taskFn;
    this.status = 'idle';
  }

  async execute(input) {
    this.status = 'running';
    this.emit('start', { input, worker: this.id });

    const startTime = Date.now();

    try {
      const result = await this.taskFn(input, this);
      const duration = Date.now() - startTime;

      this.status = 'completed';
      const output = {
        success: true,
        result,
        duration,
        worker: this.name
      };

      this.emit('complete', output);
      return output;

    } catch (error) {
      this.status = 'error';
      const output = {
        success: false,
        error: error.message,
        worker: this.name
      };

      this.emit('error', output);
      return output;
    }
  }
}

/**
 * Loom - Agent 工厂
 */
class Loom {
  constructor() {
    this.agents = new Map();
    this.masters = new Map();
    this.workers = new Map();
  }

  createMaster(name, options = {}) {
    const master = new Master(name, this, options);
    this.agents.set(master.id, master);
    this.masters.set(master.id, master);
    console.log(`[Loom] 创建 Master: ${name} (${master.id.slice(0, 8)})`);
    return master;
  }

  createWorker(parentId, name, taskFn, capabilities = []) {
    const parent = this.getAgent(parentId);
    if (!parent || parent.type !== 'master') {
      throw new Error(`Invalid parent: ${parentId}`);
    }

    const worker = new Worker(name, parentId, taskFn);
    worker.capabilities = capabilities;

    this.agents.set(worker.id, worker);
    this.workers.set(worker.id, worker);

    return worker.id;
  }

  getAgent(id) {
    return this.agents.get(id);
  }

  spawnWorkers(parentId, count, taskFn, options = {}) {
    const workers = [];
    for (let i = 0; i < count; i++) {
      const workerId = this.createWorker(
        parentId,
        `worker-${i}`,
        taskFn,
        options.capabilities || []
      );
      workers.push(this.getAgent(workerId));
    }
    return workers;
  }

  getStats() {
    return {
      total: this.agents.size,
      masters: this.masters.size,
      workers: this.workers.size
    };
  }

  createWorker(parentId, name, taskFn, capabilities = []) {
    const parent = this.agents.get(parentId);
    if (!parent || parent.type !== 'master') {
      throw new Error(`Invalid parent: ${parentId}`);
    }

    const worker = new Worker(name, parentId, taskFn);
    worker.capabilities = capabilities;

    this.agents.set(worker.id, worker);
    this.workers.set(worker.id, worker);

    return worker.id;
  }

  getAgent(id) {
    return this.agents.get(id);
  }
}

module.exports = {
  Loom,
  Master,
  Worker,
  Agent
};
