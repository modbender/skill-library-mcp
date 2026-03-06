/**
 * 批量处理器
 * Batch Processor
 * 
 * @description 处理批量卡片发送，支持并发控制和错误处理
 * @author OpenClaw Team
 * @version 1.0.0
 */

class BatchProcessor {
  constructor(config = {}) {
    this.config = {
      maxConcurrent: 5,
      retryAttempts: 3,
      retryDelay: 1000,
      batchDelay: 100,
      enableProgressCallback: false,
      ...config
    };
    
    this.activeBatches = new Map();
    this.batchStats = {
      totalProcessed: 0,
      totalSuccess: 0,
      totalFailed: 0,
      averageTime: 0
    };
    
    console.log('📦 BatchProcessor initialized');
  }

  /**
   * 处理批量任务
   * @param {Array} items - 要处理的项
   * @param {Function} processor - 处理函数
   * @param {Object} options - 处理选项
   * @returns {Promise<Array>} 处理结果
   */
  async processBatch(items, processor, options = {}) {
    const batchId = this.generateBatchId();
    const startTime = Date.now();
    
    console.log(`📋 开始批量处理 [${batchId}]: ${items.length} 项`);
    
    const batchInfo = {
      id: batchId,
      startTime,
      totalItems: items.length,
      processedItems: 0,
      successItems: 0,
      failedItems: 0,
      status: 'processing'
    };
    
    this.activeBatches.set(batchId, batchInfo);
    
    try {
      // 分批处理
      const results = await this.processInBatches(items, processor, batchInfo, options);
      
      // 更新批次状态
      batchInfo.status = 'completed';
      batchInfo.endTime = Date.now();
      batchInfo.duration = batchInfo.endTime - startTime;
      
      // 更新统计
      this.updateBatchStats(batchInfo);
      
      console.log(`✅ 批量处理完成 [${batchId}]: ${batchInfo.successItems}/${batchInfo.totalItems} 成功，耗时${batchInfo.duration}ms`);
      
      return results;
      
    } catch (error) {
      batchInfo.status = 'failed';
      batchInfo.endTime = Date.now();
      batchInfo.duration = batchInfo.endTime - startTime;
      batchInfo.error = error.message;
      
      console.error(`❌ 批量处理失败 [${batchId}]:`, error);
      
      throw error;
      
    } finally {
      // 清理批次信息
      setTimeout(() => {
        this.activeBatches.delete(batchId);
      }, 60000); // 1分钟后清理
    }
  }

  /**
   * 分批处理
   */
  async processInBatches(items, processor, batchInfo, options) {
    const results = [];
    const chunks = this.createChunks(items, this.config.maxConcurrent);
    
    for (let chunkIndex = 0; chunkIndex < chunks.length; chunkIndex++) {
      const chunk = chunks[chunkIndex];
      console.log(`🔄 处理批次 ${chunkIndex + 1}/${chunks.length}: ${chunk.length} 项`);
      
      // 处理当前批次
      const chunkResults = await Promise.allSettled(
        chunk.map(async (item, index) => {
          const itemIndex = chunkIndex * this.config.maxConcurrent + index;
          
          try {
            // 重试机制
            const result = await this.processWithRetry(
              item,
              processor,
              itemIndex
            );
            
            // 更新进度
            batchInfo.processedItems++;
            batchInfo.successItems++;
            
            if (this.config.enableProgressCallback && options.onProgress) {
              options.onProgress({
                batchId: batchInfo.id,
                processed: batchInfo.processedItems,
                total: batchInfo.totalItems,
                success: batchInfo.successItems,
                failed: batchInfo.failedItems
              });
            }
            
            return {
              success: true,
              index: itemIndex,
              data: result,
              timestamp: new Date().toISOString()
            };
            
          } catch (error) {
            // 更新进度
            batchInfo.processedItems++;
            batchInfo.failedItems++;
            
            if (this.config.enableProgressCallback && options.onProgress) {
              options.onProgress({
                batchId: batchInfo.id,
                processed: batchInfo.processedItems,
                total: batchInfo.totalItems,
                success: batchInfo.successItems,
                failed: batchInfo.failedItems
              });
            }
            
            return {
              success: false,
              index: itemIndex,
              error: error.message,
              timestamp: new Date().toISOString()
            };
          }
        })
      );
      
      // 处理结果
      const processedResults = chunkResults.map(result => {
        if (result.status === 'fulfilled') {
          return result.value;
        } else {
          return {
            success: false,
            error: result.reason.message,
            timestamp: new Date().toISOString()
          };
        }
      });
      
      results.push(...processedResults);
      
      // 批次间延迟
      if (chunkIndex < chunks.length - 1) {
        await this.delay(this.config.batchDelay);
      }
    }
    
    return results;
  }

  /**
   * 带重试的处理
   */
  async processWithRetry(item, processor, index) {
    let lastError;
    
    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const result = await processor(item, index);
        
        if (attempt > 1) {
          console.log(`✅ 重试成功 [${index}] (尝试 ${attempt})`);
        }
        
        return result;
        
      } catch (error) {
        lastError = error;
        
        if (attempt < this.config.retryAttempts) {
          console.log(`⚠️ 处理失败 [${index}] (尝试 ${attempt}/${this.config.retryAttempts}): ${error.message}`);
          await this.delay(this.config.retryDelay * attempt); // 指数退避
        }
      }
    }
    
    throw lastError;
  }

  /**
   * 创建批次
   */
  createChunks(array, chunkSize) {
    const chunks = [];
    for (let i = 0; i < array.length; i += chunkSize) {
      chunks.push(array.slice(i, i + chunkSize));
    }
    return chunks;
  }

  /**
   * 延迟函数
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 生成批次ID
   */
  generateBatchId() {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `batch_${timestamp}_${random}`;
  }

  /**
   * 更新批次统计
   */
  updateBatchStats(batchInfo) {
    this.batchStats.totalProcessed += batchInfo.processedItems;
    this.batchStats.totalSuccess += batchInfo.successItems;
    this.batchStats.totalFailed += batchInfo.failedItems;
    
    // 更新平均时间
    if (this.batchStats.averageTime === 0) {
      this.batchStats.averageTime = batchInfo.duration;
    } else {
      this.batchStats.averageTime = 
        (this.batchStats.averageTime + batchInfo.duration) / 2;
    }
  }

  /**
   * 获取活跃的批次
   */
  getActiveBatches() {
    const batches = [];
    for (const [id, info] of this.activeBatches) {
      batches.push({
        id,
        status: info.status,
        progress: {
          processed: info.processedItems,
          total: info.totalItems,
          percentage: Math.round((info.processedItems / info.totalItems) * 100)
        },
        duration: info.duration || (Date.now() - info.startTime),
        startTime: new Date(info.startTime).toISOString()
      });
    }
    return batches;
  }

  /**
   * 获取批次统计
   */
  getBatchStats() {
    return {
      ...this.batchStats,
      activeBatches: this.activeBatches.size,
      successRate: this.batchStats.totalProcessed > 0 
        ? Math.round((this.batchStats.totalSuccess / this.batchStats.totalProcessed) * 100)
        : 0
    };
  }

  /**
   * 获取批次详情
   */
  getBatchDetails(batchId) {
    const batch = this.activeBatches.get(batchId);
    if (!batch) {
      return null;
    }
    
    return {
      id: batch.id,
      status: batch.status,
      progress: {
        processed: batch.processedItems,
        total: batch.totalItems,
        success: batch.successItems,
        failed: batch.failedItems,
        percentage: Math.round((batch.processedItems / batch.totalItems) * 100)
      },
      timing: {
        startTime: new Date(batch.startTime).toISOString(),
        duration: batch.duration || (Date.now() - batch.startTime),
        estimatedEndTime: batch.status === 'processing' 
          ? new Date(batch.startTime + (batch.duration || 0) * (batch.totalItems / batch.processedItems)).toISOString()
          : new Date(batch.endTime).toISOString()
      },
      error: batch.error
    };
  }

  /**
   * 取消批次
   */
  cancelBatch(batchId) {
    const batch = this.activeBatches.get(batchId);
    if (batch) {
      batch.status = 'cancelled';
      batch.endTime = Date.now();
      batch.duration = batch.endTime - batch.startTime;
      
      console.log(`🛑 批次已取消 [${batchId}]`);
      return true;
    }
    
    return false;
  }

  /**
   * 重置统计
   */
  resetStats() {
    this.batchStats = {
      totalProcessed: 0,
      totalSuccess: 0,
      totalFailed: 0,
      averageTime: 0
    };
    
    console.log('📊 批次统计已重置');
  }

  /**
   * 获取版本信息
   */
  getVersion() {
    return {
      version: '1.0.0',
      buildDate: '2026-02-28',
      module: 'BatchProcessor'
    };
  }

  /**
   * 性能测试
   */
  async performanceTest(itemCount = 100, processor = null) {
    console.log(`🚀 开始性能测试: ${itemCount} 项`);
    
    // 创建测试数据
    const testItems = Array.from({ length: itemCount }, (_, i) => ({
      id: i,
      data: `测试数据 ${i}`,
      timestamp: Date.now()
    }));
    
    // 默认处理器
    const defaultProcessor = processor || (async (item) => {
      // 模拟处理时间
      await this.delay(Math.random() * 100);
      return {
        success: true,
        processed: item.id,
        timestamp: Date.now()
      };
    });
    
    const startTime = Date.now();
    
    try {
      const results = await this.processBatch(testItems, defaultProcessor);
      
      const duration = Date.now() - startTime;
      const successCount = results.filter(r => r.success).length;
      
      console.log(`✅ 性能测试完成`);
      console.log(`📊 统计信息:`);
      console.log(`  - 总项数: ${itemCount}`);
      console.log(`  - 成功: ${successCount}`);
      console.log(`  - 失败: ${itemCount - successCount}`);
      console.log(`  - 总耗时: ${duration}ms`);
      console.log(`  - 平均耗时: ${Math.round(duration / itemCount)}ms/项`);
      console.log(`  - 处理速度: ${Math.round(itemCount / (duration / 1000))} 项/秒`);
      
      return {
        totalItems: itemCount,
        successCount,
        failedCount: itemCount - successCount,
        duration,
        averageTime: Math.round(duration / itemCount),
        speed: Math.round(itemCount / (duration / 1000))
      };
      
    } catch (error) {
      console.error(`❌ 性能测试失败:`, error);
      throw error;
    }
  }
}

module.exports = {
  BatchProcessor
};