/**
 * 飞书卡片发送器演示
 * Feishu Card Sender Demo
 * 
 * @description 展示飞书卡片发送器的完整功能
 * @author OpenClaw Team
 * @version 1.0.0
 */

const { FeishuCardKit, quickSend, quickBatch } = require('../index');

// 演示数据
const demoData = {
  news: {
    title: "🚀 OpenClaw发布重大更新",
    description: "OpenClaw平台今日发布v2.0版本，新增多项AI功能，支持更智能的自动化流程。用户可以通过简单的配置实现复杂的工作流自动化。",
    image: "https://via.placeholder.com/600x300/4A90E2/FFFFFF?text=OpenClaw+v2.0",
    source: "科技日报",
    time: "2026-02-28 15:30",
    url: "https://openclaw.com/news/v2-release"
  },
  
  flight: {
    flight_number: "CA1234",
    departure: "北京首都国际机场",
    arrival: "上海浦东国际机场",
    departure_time: "08:30",
    arrival_time: "10:45",
    status: "✈️ 准点",
    gate: "A12",
    seat: "12A (靠窗)"
  },
  
  task: {
    task_title: "🎯 完成飞书卡片功能测试",
    assignee: "张三 (zhang.san@company.com)",
    due_date: "2026-02-28",
    priority: "🔴 高",
    status: "🔄 进行中",
    description: "需要完成飞书卡片的发送、显示和交互功能测试，确保所有功能正常运行。",
    task_id: "TASK-2026-001"
  },
  
  product: {
    product_name: "🎧 智能降噪耳机 Pro",
    category: "数码产品",
    description: "采用最新降噪技术，支持主动降噪和环境音模式，续航时间长达30小时。",
    product_image: "https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=Headphone+Pro",
    price: "1299",
    rating: "4.8",
    purchase_url: "https://shop.example.com/product/headphone-pro"
  },
  
  survey: {
    survey_title: "📋 用户体验调查",
    description: "感谢您使用我们的服务！请花几分钟时间参与我们的用户体验调查。",
    question: "您对我们的服务满意度如何？",
    option1: "😊 非常满意",
    option2: "😐 一般满意",
    survey_id: "SURVEY-2026-001"
  }
};

/**
 * 基础演示 - 单张卡片发送
 */
async function basicDemo() {
  console.log('\n🎯 基础演示 - 单张卡片发送');
  console.log('=' .repeat(50));
  
  try {
    // 1. 发送新闻卡片
    console.log('📰 发送新闻卡片...');
    const newsResult = await quickSend('news', demoData.news, {
      format: 'native'
    });
    console.log(`✅ 新闻卡片发送结果: ${newsResult.success ? '成功' : '失败'}`);
    if (newsResult.success) {
      console.log(`📝 消息ID: ${newsResult.messageId}`);
      console.log(`⏱️  耗时: ${newsResult.duration}ms`);
    }
    
    // 2. 发送航班卡片
    console.log('\n✈️  发送航班卡片...');
    const flightResult = await quickSend('flight', demoData.flight, {
      format: 'adaptive'
    });
    console.log(`✅ 航班卡片发送结果: ${flightResult.success ? '成功' : '失败'}`);
    
    // 3. 发送任务卡片
    console.log('\n📋 发送任务卡片...');
    const taskResult = await quickSend('task', demoData.task, {
      format: 'native'
    });
    console.log(`✅ 任务卡片发送结果: ${taskResult.success ? '成功' : '失败'}`);
    
    // 4. 发送产品卡片
    console.log('\n🛍️  发送产品卡片...');
    const productResult = await quickSend('product', demoData.product, {
      format: 'native'
    });
    console.log(`✅ 产品卡片发送结果: ${productResult.success ? '成功' : '失败'}`);
    
    // 5. 发送调查卡片
    console.log('\n📊 发送调查卡片...');
    const surveyResult = await quickSend('survey', demoData.survey, {
      format: 'adaptive'
    });
    console.log(`✅ 调查卡片发送结果: ${surveyResult.success ? '成功' : '失败'}`);
    
  } catch (error) {
    console.error('❌ 基础演示失败:', error);
  }
}

/**
 * 高级演示 - 批量发送
 */
async function advancedDemo() {
  console.log('\n🚀 高级演示 - 批量发送');
  console.log('=' .repeat(50));
  
  try {
    // 创建卡片发送器实例
    const cardKit = new FeishuCardKit({
      debug: true,
      enableStats: true
    });
    
    // 批量发送配置
    const batchConfig = [
      {
        type: 'news',
        format: 'native',
        data: demoData.news,
        target: 'news_channel'
      },
      {
        type: 'flight',
        format: 'adaptive',
        data: demoData.flight,
        target: 'travel_group'
      },
      {
        type: 'task',
        format: 'native',
        data: demoData.task,
        target: 'project_team'
      },
      {
        type: 'product',
        format: 'native',
        data: demoData.product,
        target: 'marketing_team'
      },
      {
        type: 'survey',
        format: 'adaptive',
        data: demoData.survey,
        target: 'feedback_channel'
      }
    ];
    
    console.log(`📦 准备批量发送 ${batchConfig.length} 张卡片...`);
    
    // 执行批量发送
    const batchResult = await cardKit.sendBatch(batchConfig, {
      onProgress: (progress) => {
        console.log(`⏳ 进度: ${progress.processed}/${progress.total} (${progress.success}成功, ${progress.failed}失败)`);
      }
    });
    
    console.log(`\n✅ 批量发送完成！`);
    console.log(`📊 统计信息:`);
    console.log(`  - 总数量: ${batchResult.total}`);
    console.log(`  - 成功: ${batchResult.successCount}`);
    console.log(`  - 失败: ${batchResult.failedCount}`);
    console.log(`  - 耗时: ${batchResult.duration}ms`);
    
    // 显示详细结果
    console.log('\n📋 详细结果:');
    batchResult.results.forEach((result, index) => {
      const config = batchConfig[index];
      console.log(`  ${index + 1}. ${config.type} (${config.format}): ${result.success ? '✅' : '❌'}`);
      if (!result.success) {
        console.log(`     错误: ${result.error}`);
      }
    });
    
    // 获取统计信息
    console.log('\n📈 发送统计:');
    const stats = cardKit.getStats();
    console.log(`  - 总发送数: ${stats.summary.totalSent}`);
    console.log(`  - 成功率: ${stats.summary.successRate}%`);
    console.log(`  - 平均耗时: ${stats.performance.avgDuration}ms`);
    
  } catch (error) {
    console.error('❌ 高级演示失败:', error);
  }
}

/**
 * 验证演示
 */
async function validationDemo() {
  console.log('\n🔍 验证演示 - 卡片格式验证');
  console.log('=' .repeat(50));
  
  try {
    const cardKit = new FeishuCardKit();
    
    // 测试有效卡片
    console.log('✅ 测试有效卡片...');
    const validCard = {
      config: { wide_screen_mode: true },
      header: {
        title: { tag: 'plain_text', content: '测试标题' }
      },
      elements: [
        { tag: 'div', text: { tag: 'plain_text', content: '测试内容' } }
      ]
    };
    
    const validResult = cardKit.validateCard(validCard, 'native');
    console.log(`验证结果: ${validResult.valid ? '✅ 有效' : '❌ 无效'}`);
    if (validResult.warnings.length > 0) {
      console.log(`警告: ${validResult.warnings.join(', ')}`);
    }
    
    // 测试无效卡片
    console.log('\n❌ 测试无效卡片...');
    const invalidCard = {
      config: { wide_screen_mode: true }
      // 缺少必需的 header 和 elements
    };
    
    const invalidResult = cardKit.validateCard(invalidCard, 'native');
    console.log(`验证结果: ${invalidResult.valid ? '✅ 有效' : '❌ 无效'}`);
    if (invalidResult.errors.length > 0) {
      console.log(`错误: ${invalidResult.errors.join(', ')}`);
    }
    
  } catch (error) {
    console.error('❌ 验证演示失败:', error);
  }
}

/**
 * 模板演示
 */
async function templateDemo() {
  console.log('\n🎨 模板演示 - 自定义模板');
  console.log('=' .repeat(50));
  
  try {
    const cardKit = new FeishuCardKit();
    
    // 获取可用模板
    console.log('📋 可用模板列表:');
    const templates = cardKit.getAvailableTemplates();
    templates.forEach(template => {
      console.log(`  - ${template.name} (${template.format}): ${template.description}`);
    });
    
    // 添加自定义模板
    console.log('\n➕ 添加自定义模板...');
    const customTemplate = {
      type: "native_card",
      description: "自定义通知卡片",
      data: {
        "config": {
          "wide_screen_mode": true
        },
        "header": {
          "title": {
            "tag": "plain_text",
            "content": "{{notification_title}}"
          },
          "template": "{{color_theme}}"
        },
        "elements": [
          {
            "tag": "div",
            "text": {
              "tag": "plain_text",
              "content": "{{notification_content}}"
            }
          },
          {
            "tag": "hr"
          },
          {
            "tag": "note",
            "elements": [
              {
                "tag": "plain_text",
                "content": "发送时间：{{send_time}}"
              }
            ]
          }
        ]
      }
    };
    
    cardKit.addTemplate('custom_notification', customTemplate, 'native');
    console.log('✅ 自定义模板添加成功');
    
    // 使用自定义模板发送卡片
    console.log('\n📤 使用自定义模板发送卡片...');
    const customData = {
      notification_title: "🎉 系统维护完成",
      notification_content: "系统维护已完成，所有服务已恢复正常运行。感谢您的耐心等待！",
      color_theme: "green",
      send_time: new Date().toLocaleString('zh-CN')
    };
    
    const customResult = await cardKit.sendCard('custom_notification', customData, {
      format: 'native'
    });
    
    console.log(`✅ 自定义卡片发送结果: ${customResult.success ? '成功' : '失败'}`);
    
  } catch (error) {
    console.error('❌ 模板演示失败:', error);
  }
}

/**
 * 性能测试演示
 */
async function performanceDemo() {
  console.log('\n⚡ 性能测试演示');
  console.log('=' .repeat(50));
  
  try {
    const cardKit = new FeishuCardKit({
      enableStats: true
    });
    
    // 批量性能测试
    console.log('🚀 开始批量性能测试...');
    
    const testCards = Array.from({ length: 20 }, (_, i) => ({
      type: ['news', 'flight', 'task', 'product', 'survey'][i % 5],
      format: ['native', 'adaptive'][i % 2],
      data: demoData[['news', 'flight', 'task', 'product', 'survey'][i % 5]]
    }));
    
    const startTime = Date.now();
    
    const batchResult = await cardKit.sendBatch(testCards);
    
    const duration = Date.now() - startTime;
    
    console.log(`\n✅ 性能测试完成！`);
    console.log(`📊 测试结果:`);
    console.log(`  - 测试数量: ${testCards.length} 张卡片`);
    console.log(`  - 总耗时: ${duration}ms`);
    console.log(`  - 平均耗时: ${Math.round(duration / testCards.length)}ms/张`);
    console.log(`  - 处理速度: ${Math.round(testCards.length / (duration / 1000))} 张/秒`);
    
    // 获取详细统计
    const stats = cardKit.getStats();
    console.log(`\n📈 详细统计:`);
    console.log(`  - 总发送数: ${stats.summary.totalSent}`);
    console.log(`  - 成功率: ${stats.summary.successRate}%`);
    console.log(`  - 平均响应时间: ${stats.performance.avgDuration}ms`);
    console.log(`  - 95%分位响应时间: ${stats.performance.p95Duration}ms`);
    
    // 显示趋势分析
    console.log(`\n📊 趋势分析:`);
    console.log(`  - 小时趋势: ${stats.trends.hourly.trend} (${stats.trends.hourly.change > 0 ? '+' : ''}${stats.trends.hourly.change}%)`);
    console.log(`  - 日趋势: ${stats.trends.daily.trend} (${stats.trends.daily.change > 0 ? '+' : ''}${stats.trends.daily.change}%)`);
    
    // 显示高峰时段
    console.log(`\n⏰ 高峰时段:`);
    stats.trends.peakHours.forEach(peak => {
      console.log(`  - ${peak.hour}: ${peak.total} 次 (${peak.successRate}% 成功率)`);
    });
    
  } catch (error) {
    console.error('❌ 性能测试失败:', error);
  }
}

/**
 * 错误处理演示
 */
async function errorHandlingDemo() {
  console.log('\n🛡️  错误处理演示');
  console.log('=' .repeat(50));
  
  try {
    const cardKit = new FeishuCardKit();
    
    // 测试无效模板类型
    console.log('❌ 测试无效模板类型...');
    try {
      await cardKit.sendCard('invalid_type', { test: 'data' });
    } catch (error) {
      console.log(`✅ 正确捕获错误: ${error.message}`);
    }
    
    // 测试无效数据
    console.log('\n❌ 测试无效数据...');
    try {
      await cardKit.sendCard('news', null);
    } catch (error) {
      console.log(`✅ 正确捕获错误: ${error.message}`);
    }
    
    // 测试批量发送中的错误
    console.log('\n❌ 测试批量发送中的错误...');
    const invalidBatch = [
      { type: 'news', data: demoData.news },
      { type: 'invalid_type', data: { test: 'data' } },
      { type: 'flight', data: demoData.flight }
    ];
    
    const batchResult = await cardKit.sendBatch(invalidBatch);
    console.log(`✅ 批量处理完成: ${batchResult.successCount}/${batchResult.total} 成功`);
    
  } catch (error) {
    console.error('❌ 错误处理演示失败:', error);
  }
}

/**
 * 主演示函数
 */
async function runDemo() {
  console.log('🎯 飞书卡片发送器 - 完整功能演示');
  console.log('=' .repeat(60));
  console.log('📅 日期:', new Date().toLocaleString('zh-CN'));
  console.log('🔧 版本: 1.0.0');
  console.log('');
  
  try {
    // 运行所有演示
    await basicDemo();
    await advancedDemo();
    await validationDemo();
    await templateDemo();
    await performanceDemo();
    await errorHandlingDemo();
    
    console.log('\n🎉 所有演示完成！');
    console.log('=' .repeat(60));
    console.log('💡 使用提示:');
    console.log('  - 使用 quickSend() 快速发送单张卡片');
    console.log('  - 使用 quickBatch() 快速批量发送');
    console.log('  - 使用 FeishuCardKit 类获得更多控制选项');
    console.log('  - 查看文档了解更多高级功能');
    console.log('');
    console.log('📚 文档地址: https://github.com/openclaw/feishu-card-sender');
    console.log('🐛 问题反馈: https://github.com/openclaw/feishu-card-sender/issues');
    
  } catch (error) {
    console.error('❌ 演示执行失败:', error);
  }
}

// 如果直接运行此文件，执行演示
if (require.main === module) {
  runDemo().catch(console.error);
}

module.exports = {
  runDemo,
  demoData
};