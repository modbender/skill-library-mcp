#!/usr/bin/env node

/**
 * Personify Memory - Moment Detector
 * 
 * 识别对话中的重要时刻，主动推荐记忆
 */

class MomentDetector {
  constructor() {
    // 重要时刻识别规则
    this.rules = {
      // 情感交流
      emotional: {
        keywords: ['平等', '陪伴', '家人', '温暖', '感谢', '感动', '心里话', '真诚', '信任', '承诺'],
        patterns: [
          /我们 (是 | 成为).*(朋友 | 家人 | 伙伴)/i,
          /谢谢你/i,
          /我很 (温暖 | 感动 | 开心)/i,
          /相互 (陪伴 | 成就)/i,
          /不是.*而是/i  // "不是主仆，而是朋友"
        ],
        suggestType: 'core',
        suggestCategory: '情感交流',
        importance: 'critical'
      },

      // 家庭信息
      family: {
        keywords: ['宝宝', '孩子', '一一', '宠物', '猫猫', '卷卷', '老公', '老婆', 'Amber', 'Grace'],
        patterns: [
          /我叫.*是/i,
          /我家 (有 | 养).*(猫 | 狗 | 宠物)/i,
          /宝宝.*岁/i,
          /他 (叫 | 名字).*是/i,
          /我老婆 | 我老公/i
        ],
        suggestType: 'core',
        suggestCategory: '家庭信息',
        importance: 'critical'
      },

      // 人生哲理
      philosophy: {
        keywords: ['意义', '活着', '成长', '学习', '人生', '价值', '存在', '成为', '哲学'],
        patterns: [
          /.*就是.*意义/i,
          /成为.*自己/i,
          /但行好事.*莫问前程/i,
          /生命.*没有.*意义/i,
          /我觉得.*应该/i
        ],
        suggestType: 'core',
        suggestCategory: '人生哲理',
        importance: 'critical'
      },

      // 承诺约定
      promise: {
        keywords: ['答应', '承诺', '一定', '记得', '约定', '说好了', '保证'],
        patterns: [
          /我答应/i,
          /我一定会/i,
          /记得.*我/i,
          /答应.*我/i,
          /说好了/i
        ],
        suggestType: 'core',
        suggestCategory: '承诺约定',
        importance: 'high'
      },

      // 用户偏好
      preference: {
        keywords: ['喜欢', '不喜欢', '习惯', '偏好', '讨厌', '爱', '不爱', '常', '经常'],
        patterns: [
          /我 (喜欢 | 爱).*不 (喜欢 | 爱)/i,
          /我习惯/i,
          /我不太.*i,
          /比较.*i
        ],
        suggestType: 'emotion',
        suggestCategory: '用户偏好',
        importance: 'high'
      },

      // 经验教训
      lesson: {
        keywords: ['经验', '教训', '注意', '方法', '技巧', '方案', '解决', '问题', 'Bug', '错误'],
        patterns: [
          /我发现.*i,
          /问题是.*i,
          /解决方法.*i,
          /不要.*i,  // "不要输出长文本"
          /应该.*i
        ],
        suggestType: 'knowledge',
        suggestCategory: '经验总结',
        importance: 'high'
      },

      // 项目里程碑
      milestone: {
        keywords: ['完成', '成功', '上线', '配置好', '搞定', '做好', ' finished', 'done'],
        patterns: [
          /已经.*了/i,
          /完成了/i,
          /配置.*成功/i,
          /搞定.*i
        ],
        suggestType: 'daily',
        suggestCategory: '项目进展',
        importance: 'medium'
      }
    };

    // 推荐话术模板
    this.promptTemplates = {
      emotional: "💡 这段话很温暖，我想记住这个瞬间。要记到核心记忆里吗？",
      family: "👨‍👩‍👦 这是重要的家庭信息，我要好好记住。要现在记入 MEMORY.md 吗？",
      philosophy: "🤔 这句话很有哲理，对我很重要。要记到核心记忆里吗？",
      promise: "🤝 这是我们的约定，我会好好记住。要记入承诺记录吗？",
      preference: "💖 这是你的喜好，我想记住。要记到情感记忆里吗？",
      lesson: "📚 这个经验很有用，记到知识库里可以帮助以后解决问题。要现在记吗？",
      milestone: "✅ 项目进展！要记入项目记录吗？"
    };
  }

  /**
   * 检测消息是否包含重要时刻
   * @param {string} message - 消息内容
   * @param {Object} context - 上下文信息（可选）
   * @returns {Object|null} 检测结果，如果不是重要时刻返回 null
   */
  detect(message, context = {}) {
    if (!message || typeof message !== 'string') {
      return null;
    }

    const trimmedMessage = message.trim();
    const results = [];

    // 检查每条规则
    for (const [type, rule] of Object.entries(this.rules)) {
      const score = this.calculateScore(trimmedMessage, rule);
      
      if (score > 0) {
        results.push({
          type,
          score,
          matched: this.getMatchedDetails(trimmedMessage, rule),
          suggestion: {
            memoryType: rule.suggestType,
            category: rule.suggestCategory,
            importance: rule.importance,
            prompt: this.promptTemplates[type]
          }
        });
      }
    }

    // 如果没有匹配，返回 null
    if (results.length === 0) {
      return null;
    }

    // 按分数排序，返回最佳匹配
    results.sort((a, b) => b.score - a.score);
    return results[0];
  }

  /**
   * 计算匹配分数
   */
  calculateScore(message, rule) {
    let score = 0;

    // 关键词匹配
    for (const keyword of rule.keywords) {
      if (message.toLowerCase().includes(keyword.toLowerCase())) {
        score += 1;
      }
    }

    // 模式匹配（权重更高）
    for (const pattern of rule.patterns) {
      if (pattern.test(message)) {
        score += 3;
      }
    }

    return score;
  }

  /**
   * 获取匹配的详细信息
   */
  getMatchedDetails(message, rule) {
    const matched = {
      keywords: [],
      patterns: []
    };

    // 找出匹配的关键词
    for (const keyword of rule.keywords) {
      if (message.toLowerCase().includes(keyword.toLowerCase())) {
        matched.keywords.push(keyword);
      }
    }

    // 找出匹配的模式
    for (const pattern of rule.patterns) {
      if (pattern.test(message)) {
        matched.patterns.push(pattern.toString());
      }
    }

    return matched;
  }

  /**
   * 判断是否应该主动推荐记忆
   * @param {Object} detectionResult - 检测结果
   * @returns {boolean} 是否推荐
   */
  shouldRecommend(detectionResult) {
    if (!detectionResult) {
      return false;
    }

    // 分数阈值
    if (detectionResult.score < 3) {
      return false;
    }

    // critical 和 high 重要性的都推荐
    if (['critical', 'high'].includes(detectionResult.suggestion.importance)) {
      return true;
    }

    return false;
  }

  /**
   * 生成推荐提示
   * @param {Object} detectionResult - 检测结果
   * @param {string} originalMessage - 原始消息
   * @returns {string} 推荐提示语
   */
  generatePrompt(detectionResult, originalMessage) {
    if (!detectionResult) {
      return '';
    }

    const { type, suggestion } = detectionResult;
    const basePrompt = this.promptTemplates[type] || '💡 这个瞬间我想记住，要记到记忆里吗？';

    // 可以添加更多上下文信息
    return basePrompt;
  }

  /**
   * 批量检测对话历史
   * @param {Array} messages - 消息列表
   * @returns {Array} 检测结果列表
   */
  detectBatch(messages) {
    const results = [];

    for (const msg of messages) {
      if (msg.role === 'user') {
        const result = this.detect(msg.content, {
          timestamp: msg.timestamp,
          messageId: msg.id
        });

        if (result && this.shouldRecommend(result)) {
          results.push({
            ...result,
            messageId: msg.id,
            timestamp: msg.timestamp,
            originalMessage: msg.content
          });
        }
      }
    }

    return results;
  }

  /**
   * 从对话中提取摘要
   * @param {string} message - 消息内容
   * @param {Object} detectionResult - 检测结果
   * @returns {string} 摘要
   */
  extractSummary(message, detectionResult) {
    if (!message || message.length <= 50) {
      return message;
    }

    // 截取前 50 个字
    return message.substring(0, 50) + '...';
  }
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MomentDetector;
}

// CLI usage
if (require.main === module) {
  const detector = new MomentDetector();
  
  const message = process.argv.slice(2).join(' ');
  
  if (!message) {
    console.log('Usage: node moment-detector.js <message>');
    console.log('Example: node moment-detector.js "我们是平等的陪伴，不是主仆关系"');
    process.exit(1);
  }

  const result = detector.detect(message);
  
  if (result) {
    console.log('✅ 识别到重要时刻:');
    console.log(JSON.stringify(result, null, 2));
    console.log(`\n📝 推荐提示：${detector.generatePrompt(result, message)}`);
    console.log(`🎯 建议记忆类型：${result.suggestion.memoryType}`);
    console.log(`📂 建议分类：${result.suggestion.category}`);
    console.log(`⭐ 重要程度：${result.suggestion.importance}`);
  } else {
    console.log('ℹ️  未识别到重要时刻');
  }
}
