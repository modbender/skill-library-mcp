const { randomUUID: uuid } = require('crypto');
const EventEmitter = require('events');

/**
 * PartitionStrategies - 任务分片策略
 */
const PartitionStrategies = {
  // 轮询
  roundRobin: (items, numPartitions) => {
    const partitions = Array(numPartitions).fill().map(() => []);
    items.forEach((item, i) => {
      partitions[i % numPartitions].push(item);
    });
    return partitions;
  },

  // 哈希
  hash: (items, numPartitions) => {
    const partitions = Array(numPartitions).fill().map(() => []);
    items.forEach(item => {
      const hash = require('crypto').createHash('md5')
        .update(String(item)).digest('hex');
      const idx = parseInt(hash.slice(0, 8), 16) % numPartitions;
      partitions[idx].push(item);
    });
    return partitions;
  },

  // 范围
  range: (items, numPartitions) => {
    const sorted = [...items].sort();
    const partitionSize = Math.ceil(sorted.length / numPartitions);
    return Array(numPartitions).fill().map((_, i) => 
      sorted.slice(i * partitionSize, (i + 1) * partitionSize)
    );
  }
};

/**
 * Tapestry - 任务编排引擎
 */
class Tapestry extends EventEmitter {
  constructor(loom, thread, options = {}) {
    super();
    this.loom = loom;
    this.thread = thread;
    this.options = {
      defaultTimeout: options.defaultTimeout || 300000, // 5分钟
      maxRetries: options.maxRetries || 3,
      retryDelay: options.retryDelay || 1000,
      ...options
    };
    this.runningJobs = new Map();
  }

  /**
   * MapReduce 工作流
   * @param {Object} config - 配置
   * @param {Array} config.input - 输入数据
   * @param {number} config.numWorkers - Worker数量
   * @param {Function} config.mapFunction - 映射函数
   * @param {Function} config.reduceFunction - 归约函数
   * @param {string} config.partitionStrategy - 分片策略
   * @param {Object} options - 额外选项
   * @returns {Promise<Object>} 执行结果
   */
  async mapReduce(config, options = {}) {
    const jobId = `job:${uuid()}`;
    const startTime = Date.now();
    
    this.emit('job:start', { jobId, type: 'mapreduce' });
    
    try {
      // 1. 创建 Master
      const master = this.loom.createMaster({
        name: `mapreduce-${jobId.slice(0, 8)}`,
        capabilities: ['orchestration', 'aggregation']
      });

      // 2. 数据分片
      const strategy = PartitionStrategies[config.partitionStrategy] || PartitionStrategies.roundRobin;
      const partitions = strategy(config.input, config.numWorkers);
      
      this.emit('job:partition', { jobId, partitions: partitions.length });

      // 3. 创建 Workers
      const workerIds = [];
      for (let i = 0; i < config.numWorkers; i++) {
        const workerId = this.loom.createWorker(
          master.id,
          `${master.identity.name}-worker-${i}`,
          config.mapFunction,
          { partitionIndex: i }
        );
        workerIds.push(workerId);
      }

      // 4. 并行执行 Map 任务
      this.emit('job:map:start', { jobId, workers: workerIds.length });
      
      const mapPromises = workerIds.map((workerId, i) => {
        const worker = this.loom.getAgent(workerId);
        const input = partitions[i] || [];
        
        return this.executeWithRetry(
          () => worker.execute(input),
          this.options.maxRetries
        ).catch(error => ({
          success: false,
          error: error.message,
          worker: workerId
        }));
      });

      const mapResults = await Promise.all(mapPromises);
      
      this.emit('job:map:complete', { jobId, results: mapResults.length });

      // 5. 检查失败
      const failures = mapResults.filter(r => !r.success);
      if (failures.length > 0 && options.failOnError !== false) {
        throw new Error(`Map phase failed: ${failures.length} workers failed`);
      }

      // 6. 执行 Reduce
      this.emit('job:reduce:start', { jobId });
      
      const successfulResults = mapResults
        .filter(r => r.success)
        .map(r => r.result);
      
      const finalResult = await config.reduceFunction(successfulResults);
      
      this.emit('job:reduce:complete', { jobId });

      // 7. 清理
      this.cleanup(master, workerIds);

      const duration = Date.now() - startTime;
      
      const result = {
        jobId,
        success: true,
        duration,
        master: master.identity.name,
        workers: workerIds.length,
        mapResults: successfulResults.length,
        failures: failures.length,
        result: finalResult
      };

      this.emit('job:complete', result);
      return result;

    } catch (error) {
      this.emit('job:error', { jobId, error: error.message });
      throw error;
    }
  }

  /**
   * 带重试的执行
   */
  async executeWithRetry(fn, maxRetries) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        
        if (attempt < maxRetries) {
          const delay = this.options.retryDelay * attempt;
          console.log(`  重试 ${attempt}/${maxRetries}，等待 ${delay}ms...`);
          await new Promise(r => setTimeout(r, delay));
        }
      }
    }
    
    throw lastError;
  }

  /**
   * 清理资源
   */
  cleanup(master, workerIds) {
    // 销毁 Workers
    for (const workerId of workerIds) {
      const worker = this.loom.getAgent(workerId);
      if (worker) {
        worker.destroy();
      }
    }
    
    // 销毁 Master
    if (master) {
      master.destroy();
    }
  }
}

module.exports = { Tapestry, PartitionStrategies };
