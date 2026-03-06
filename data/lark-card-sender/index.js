/**
 * 飞书卡片发送器主入口
 * Feishu Interactive Card Sender - Main Entry Point
 * 
 * @description 提供完整的飞书交互式卡片发送功能，支持多种格式和模板
 * @author OpenClaw Team
 * @version 1.0.0
 */

const { FeishuCardSender } = require('./src/FeishuCardSender');
const { CardTemplateManager } = require('./src/CardTemplateManager');
const { CardValidator } = require('./src/CardValidator');
const { BatchProcessor } = require('./src/BatchProcessor');
const { StatsTracker } = require('./src/StatsTracker');

// 版本信息
const VERSION = '1.0.0';
const BUILD_DATE = '2026-02-28';

/**
 * 飞书卡片发送器主类
 * 整合所有功能模块，提供统一的API接口
 */
class FeishuCardKit {
  constructor(config = {}) {
    this.config = {
      // 默认配置
      defaultFormat: 'native',
      maxBatchSize: 100,
      retryAttempts: 3,
      retryDelay: 1000,
      enableStats: true,
      enableValidation: true,
      debug: false,
      ...config
    };

    // 初始化各个模块
    this.sender = new FeishuCardSender(this.config);
    this.templates = new CardTemplateManager(this.config);
    this.validator = new CardValidator(this.config);
    this.batchProcessor = new BatchProcessor(this.config);
    this.stats = new StatsTracker(this.config);

    console.log(`🚀 FeishuCardKit v${VERSION} initialized`);
    if (this.config.debug) {
      console.log('📋 Configuration:', JSON.stringify(this.config, null, 2));
    }
  }

  /**
   * 发送单张卡片
   * @param {string} templateType - 模板类型
   * @param {Object} data - 模板数据
   * @param {Object} options - 发送选项
   * @returns {Promise<Object>} 发送结果
   */
  async sendCard(templateType, data, options = {}) {
    try {
      const startTime = Date.now();
      
      // 获取格式配置
      const format = options.format || this.config.defaultFormat;
      const target = options.target || null;

      // 验证输入参数
      if (!templateType || !data) {
        throw new Error('模板类型和数据不能为空');
      }

      // 获取模板
      const template = this.templates.getTemplate(templateType, format);
      if (!template) {
        throw new Error(`未找到${format}格式的${templateType}模板`);
      }

      // 渲染模板
      const renderedCard = this.templates.renderTemplate(template, data);

      // 验证卡片格式（如果启用）
      if (this.config.enableValidation) {
        const validation = this.validator.validateCard(renderedCard.data, format);
        if (!validation.valid) {
          throw new Error(`卡片验证失败: ${validation.errors.join(', ')}`);
        }
      }

      // 发送卡片
      const result = await this.sender.sendCard(renderedCard, target);

      // 记录统计信息
      if (this.config.enableStats) {
        const duration = Date.now() - startTime;
        this.stats.recordSend(templateType, format, result.success, duration);
      }

      return {
        success: true,
        messageId: result.messageId,
        templateType,
        format,
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime
      };

    } catch (error) {
      console.error(`发送卡片失败:`, error);
      
      // 记录失败统计
      if (this.config.enableStats) {
        this.stats.recordSend(templateType, format || this.config.defaultFormat, false, 0);
      }

      return {
        success: false,
        error: error.message,
        templateType,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * 批量发送卡片
   * @param {Array} cards - 卡片配置数组
   * @param {Object} options - 批量发送选项
   * @returns {Promise<Object>} 批量发送结果
   */
  async sendBatch(cards, options = {}) {
    try {
      const startTime = Date.now();
      
      // 验证输入
      if (!Array.isArray(cards) || cards.length === 0) {
        throw new Error('卡片数组不能为空');
      }

      if (cards.length > this.config.maxBatchSize) {
        throw new Error(`批量发送数量超过最大限制(${this.config.maxBatchSize})`);
      }

      console.log(`📦 开始批量发送${cards.length}张卡片...`);

      // 使用批量处理器处理
      const results = await this.batchProcessor.processBatch(cards, async (card) => {
        return await this.sendCard(card.type, card.data, {
          format: card.format,
          target: card.target
        });
      });

      const duration = Date.now() - startTime;
      const successCount = results.filter(r => r.success).length;

      console.log(`✅ 批量发送完成: ${successCount}/${results.length} 成功，耗时${duration}ms`);

      return {
        success: true,
        total: results.length,
        successCount,
        failedCount: results.length - successCount,
        results,
        duration,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error(`批量发送失败:`, error);
      return {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * 验证卡片格式
   * @param {Object} cardData - 卡片数据
   * @param {string} format - 格式类型
   * @returns {Object} 验证结果
   */
  validateCard(cardData, format) {
    return this.validator.validateCard(cardData, format);
  }

  /**
   * 获取发送统计
   * @returns {Object} 统计信息
   */
  getStats() {
    return this.stats.getStats();
  }

  /**
   * 获取可用模板
   * @returns {Array} 模板列表
   */
  getAvailableTemplates() {
    return this.templates.getAvailableTemplates();
  }

  /**
   * 添加自定义模板
   * @param {string} name - 模板名称
   * @param {Object} template - 模板定义
   * @param {string} format - 格式类型
   */
  addTemplate(name, template, format = 'native') {
    return this.templates.addTemplate(name, template, format);
  }

  /**
   * 获取版本信息
   * @returns {Object} 版本信息
   */
  getVersion() {
    return {
      version: VERSION,
      buildDate: BUILD_DATE,
      modules: {
        sender: this.sender.getVersion(),
        templates: this.templates.getVersion(),
        validator: this.validator.getVersion(),
        batchProcessor: this.batchProcessor.getVersion(),
        stats: this.stats.getVersion()
      }
    };
  }

  /**
   * 重置统计信息
   */
  resetStats() {
    return this.stats.reset();
  }
}

// 创建默认实例
const defaultKit = new FeishuCardKit();

// 快速发送函数
async function quickSend(templateType, data, options = {}) {
  return await defaultKit.sendCard(templateType, data, options);
}

// 批量发送函数
async function quickBatch(cards, options = {}) {
  return await defaultKit.sendBatch(cards, options);
}

// 模块导出
module.exports = {
  FeishuCardKit,
  defaultKit,
  quickSend,
  quickBatch,
  VERSION
};

// 如果直接运行此文件，显示版本信息
if (require.main === module) {
  console.log(`🎯 FeishuCardKit v${VERSION}`);
  console.log(`📅 Build Date: ${BUILD_DATE}`);
  console.log('\n📚 Available methods:');
  console.log('- FeishuCardKit: 主类');
  console.log('- quickSend(): 快速发送单张卡片');
  console.log('- quickBatch(): 快速批量发送');
  console.log('\n💡 Run "node examples/demo.js" for a complete demo');
}