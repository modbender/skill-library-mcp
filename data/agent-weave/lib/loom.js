const { randomUUID: uuid } = require('crypto');
const EventEmitter = require('events');

/**
 * Agent 身份标识
 */
class AgentIdentity {
  constructor({ name, type, parentId = null, capabilities = [] }) {
    this.id = `agent:${uuid()}`;
    this.name = name || `agent-${Date.now()}`;
    this.type = type; // 'master' | 'worker'
    this.parentId = parentId;
    this.generation = parentId ? 1 : 0;
    this.capabilities = new Set(capabilities);
    this.createdAt = new Date();
    this.lastHeartbeat = new Date();
    this.status = 'active';
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      parentId: this.parentId,
      generation: this.generation,
      capabilities: Array.from(this.capabilities),
      createdAt: this.createdAt,
      status: this.status
    };
  }
}

/**
 * Master Agent - 管理 Worker 集群
 */
class Master extends EventEmitter {
  constructor(identity, loom) {
    super();
    this.identity = identity;
    this.loom = loom;
    this.workers = new Map();
    this.results = [];
    this.taskQueue = [];
  }

  /**
   * 批量创建 Worker
   */
  spawn(count, taskFn, options = {}) {
    console.log(`[Master:${this.identity.name}] 创建 ${count} 个 Worker...`);
    
    for (let i = 0; i < count; i++) {
      const workerId = this.loom.createWorker(
        this.identity.id,
        `${this.identity.name}-worker-${i}`,
        taskFn,
        options.capabilities || []
      );
      
      const worker = this.loom.getAgent(workerId);
      this.workers.set(workerId, worker);
      
      // 监听 Worker 完成事件
      worker.on('complete', (result) => {
        this.results.push({ workerId, result });
      });
      
      worker.on('error', (error) => {
        console.error(`[Master] Worker ${workerId} 错误:`, error);
      });
    }
    
    console.log(`[Master] 已创建 ${this.workers.size} 个 Worker`);
    return this;
  }

  /**
   * 并行分发任务
   */
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

  /**
   * 汇总结果（子类可覆盖）
   */
  aggregate() {
    const success = this.results.filter(r => r && r.success).length;
    const failed = this.results.length - success;
    
    console.log(`[Master] 任务完成: ${success} 成功, ${failed} 失败`);
    
    return {
      master: this.identity.name,
      workers: this.workers.size,
      results: this.results,
      summary: { total: this.results.length, success, failed }
    };
  }

  /**
   * 销毁所有 Worker
   */
  destroy() {
    console.log(`[Master] 销毁 ${this.workers.size} 个 Worker...`);
    for (const [id, worker] of this.workers) {
      worker.destroy();
    }
    this.workers.clear();
    this.results = [];
  }
}

/**
 * Worker Agent - 执行具体任务
 */
class Worker extends EventEmitter {
  constructor(identity, masterId, taskFn) {
    super();
    this.identity = identity;
    this.masterId = masterId;
    this.taskFn = taskFn;
    this.status = 'idle';
  }

  /**
   * 执行任务
   */
  async execute(input) {
    this.status = 'running';
    this.emit('start', { input, worker: this.identity.id });
    
    const startTime = Date.now();
    
    try {
      const result = await this.taskFn(input, this);
      const duration = Date.now() - startTime;
      
      this.status = 'completed';
      const output = { 
        success: true, 
        result, 
        duration,
        worker: this.identity.name 
      };
      
      this.emit('complete', output);
      return output;
      
    } catch (error) {
      this.status = 'error';
      const output = { 
        success: false, 
        error: error.message, 
        worker: this.identity.name 
      };
      
      this.emit('error', output);
      return output;
    }
  }

  /**
   * 销毁 Worker
   */
  destroy() {
    this.status = 'destroyed';
    this.removeAllListeners();
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

  /**
   * 创建 Master
   */
  createMaster(name, capabilities = []) {
    const identity = new AgentIdentity({
      name,
      type: 'master',
      capabilities: ['orchestration', 'aggregation', ...capabilities]
    });

    const master = new Master(identity, this);
    
    this.agents.set(identity.id, master);
    this.masters.set(identity.id, master);
    
    console.log(`[Loom] 创建 Master: ${name} (${identity.id.slice(0, 8)})`);
    return master;
  }

  /**
   * 创建 Worker
   */
  createWorker(parentId, name, taskFn, capabilities = []) {
    const parent = this.getAgent(parentId);
    if (!parent || parent.identity.type !== 'master') {
      throw new Error(`Invalid parent: ${parentId}`);
    }

    const identity = new AgentIdentity({
      name,
      type: 'worker',
      parentId,
      capabilities: ['execution', ...capabilities]
    });

    const worker = new Worker(identity, parentId, taskFn);
    
    this.agents.set(identity.id, worker);
    this.workers.set(identity.id, worker);
    
    return identity.id;
  }

  getAgent(id) {
    return this.agents.get(id);
  }

  spawnWorkers(parentId, count, taskFn, options = {}) {
    const workerIds = [];
    for (let i = 0; i < count; i++) {
      const workerId = this.createWorker(
        parentId,
        `worker-${i}`,
        taskFn,
        options.capabilities || []
      );
      workerIds.push(workerId);
    }
    return workerIds.map(id => this.getAgent(id));
  }

  getMaster(id) {
    return this.masters.get(id);
  }

  getWorker(id) {
    return this.workers.get(id);
  }

  list() {
    return {
      total: this.agents.size,
      masters: this.masters.size,
      workers: this.workers.size
    };
  }
}

module.exports = {
  Loom,
  Master,
  Worker,
  AgentIdentity
};
