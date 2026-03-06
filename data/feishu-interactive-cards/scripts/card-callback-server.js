const lark = require('@larksuiteoapi/node-sdk');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');

// 从 OpenClaw 配置文件读取飞书配置
function loadFeishuConfig() {
  try {
    const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      
      const feishuConfig = config.channels?.feishu?.accounts?.main;
      if (feishuConfig) {
        return {
          appId: feishuConfig.appId,
          appSecret: feishuConfig.appSecret
        };
      }
    }
  } catch (error) {
    console.error('⚠️ 无法读取飞书配置:', error.message);
  }
  
  // 如果配置文件不存在，尝试从环境变量读取
  return {
    appId: process.env.FEISHU_APP_ID || '',
    appSecret: process.env.FEISHU_APP_SECRET || ''
  };
}

// 从 OpenClaw 配置文件读取 Gateway 配置
function loadGatewayConfig() {
  try {
    const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      
      return {
        url: process.env.OPENCLAW_GATEWAY_URL || config.gateway?.url || `http://localhost:${config.gateway?.port || 18789}`,
        token: process.env.OPENCLAW_GATEWAY_TOKEN || config.gateway?.token || '',
        enabled: config.gateway?.enabled !== false // 默认启用
      };
    }
  } catch (error) {
    console.log('⚠️ 无法读取 OpenClaw 配置:', error.message);
  }
  
  // 返回默认配置
  return {
    url: process.env.OPENCLAW_GATEWAY_URL || 'http://localhost:18789',
    token: process.env.OPENCLAW_GATEWAY_TOKEN || '',
    enabled: false
  };
}

// OpenClaw Gateway 配置
const GATEWAY_CONFIG = loadGatewayConfig();
const GATEWAY_URL = GATEWAY_CONFIG.url;
const GATEWAY_TOKEN = GATEWAY_CONFIG.token;
const GATEWAY_ENABLED = GATEWAY_CONFIG.enabled && GATEWAY_TOKEN;

console.log('🔧 初始化飞书卡片回调服务器...\n');
console.log('📡 Gateway URL:', GATEWAY_URL);
console.log('🔑 Gateway Token:', GATEWAY_TOKEN ? '已配置 ✅' : '未配置 ⚠️');
console.log('🔌 Gateway 集成:', GATEWAY_ENABLED ? '已启用 ✅' : '已禁用 ⚠️');
console.log('');

// 向 OpenClaw Gateway 发送回调信息
async function sendToGateway(callbackData) {
  if (!GATEWAY_ENABLED) {
    return; // 静默跳过
  }

  try {
    const payload = {
      type: 'feishu_card_callback',
      timestamp: new Date().toISOString(),
      data: callbackData
    };

    await axios.post(`${GATEWAY_URL}/api/callback`, payload, {
      headers: {
        'Authorization': `Bearer ${GATEWAY_TOKEN}`,
        'Content-Type': 'application/json'
      },
      timeout: 3000 // 3秒超时
    });

    console.log('✅ 已发送到 Gateway');
  } catch (error) {
    // 静默失败，不影响主流程
    if (error.code === 'ECONNREFUSED') {
      console.log('⚠️ Gateway 未运行');
    } else if (error.response?.status === 401) {
      console.log('⚠️ Gateway Token 验证失败');
    } else {
      console.log('⚠️ 发送到 Gateway 失败:', error.message);
    }
  }
}


// 请求去重 - 防止快速重复点击
const requestCache = new Map();
const REQUEST_CACHE_TTL = 3000; // 3秒内的重复请求将被忽略

function isDuplicateRequest(eventId, actionValue) {
  const key = `${eventId}_${JSON.stringify(actionValue)}`;
  const now = Date.now();
  
  if (requestCache.has(key)) {
    const timestamp = requestCache.get(key);
    if (now - timestamp < REQUEST_CACHE_TTL) {
      return true; // 重复请求
    }
  }
  
  requestCache.set(key, now);
  
  // 清理过期的缓存
  for (const [k, v] of requestCache.entries()) {
    if (now - v > REQUEST_CACHE_TTL) {
      requestCache.delete(k);
    }
  }
  
  return false;
}

// 验证响应格式
function validateResponse(response) {
  if (!response) return false;
  
  // toast 是可选的
  if (response.toast) {
    if (!response.toast.type || !response.toast.content) {
      console.error('❌ Toast 格式错误');
      return false;
    }
  }
  
  // card 是可选的，但如果存在必须格式正确
  if (response.card) {
    if (response.card.type !== 'raw' || !response.card.data) {
      console.error('❌ Card 格式错误');
      return false;
    }
  }
  
  return true;
}

// 创建安全的响应包装器
function createSafeResponse(response) {
  try {
    if (!validateResponse(response)) {
      console.error('❌ 响应验证失败，返回默认响应');
      return {
        toast: {
          type: 'info',
          content: '操作成功'
        }
      };
    }
    return response;
  } catch (error) {
    console.error('❌ 创建响应时出错:', error);
    return {
      toast: {
        type: 'error',
        content: '操作失败，请重试'
      }
    };
  }
}


// 辅助函数：格式化满意度文本
function getSatisfactionText(value) {
  const map = {
    'very_satisfied': '😄 非常满意',
    'satisfied': '🙂 满意',
    'neutral': '😐 一般',
    'dissatisfied': '😞 不满意',
    'very_dissatisfied': '😡 非常不满意'
  };
  return map[value] || '未选择';
}

// 辅助函数：格式化功能列表
function getFeaturesText(features) {
  if (!features) return '未选择';
  
  const map = {
    'analytics': '📊 数据分析',
    'recommendation': '🤖 智能推荐',
    'chat': '💬 即时通讯',
    'file_management': '📁 文件管理',
    'notifications': '🔔 消息提醒',
    'ui_design': '🎨 界面设计'
  };
  
  // 如果是数组（多选）
  if (Array.isArray(features)) {
    return features.map(f => map[f] || f).join('、');
  }
  
  // 如果是字符串（单选）
  return map[features] || features;
}

// 辅助函数：格式化投票选项
function getVoteOptionText(option) {
  const map = {
    'bowling': '🎳 保龄球',
    'movie': '🎬 看电影',
    'dinner': '🍕 聚餐',
    'outdoor': '🏃 户外运动',
    'gaming': '🎮 电竞'
  };
  return map[option] || option;
}

// 辅助函数：格式化会议室
function getRoomText(room) {
  const map = {
    'A301': '🏢 A座301（10人）',
    'A302': '🏢 A座302（20人）',
    'B201': '🏢 B座201（50人）',
    'B202': '🏢 B座202（100人）'
  };
  return map[room] || room;
}

// 辅助函数：格式化推荐意愿
function getRecommendText(value) {
  const map = {
    'very_likely': '👍 非常愿意',
    'likely': '🙂 愿意',
    'neutral': '😐 不确定',
    'unlikely': '😞 不太愿意',
    'very_unlikely': '👎 完全不愿意'
  };
  return map[value] || '未选择';
}

// 辅助函数：创建标准卡片结构
function createCard(header, elements) {
  return {
    type: 'raw',
    data: {
      config: { wide_screen_mode: true },
      header: {
        title: { content: header.title, tag: "plain_text" },
        template: header.template || "blue"
      },
      elements: elements
    }
  };
}

// 辅助函数：创建标准响应
function createResponse(toast, card) {
  const response = {};
  
  if (toast) {
    response.toast = {
      type: toast.type || 'info',
      content: toast.content
    };
  }
  
  if (card) {
    response.card = card;
  }
  
  return response;
}

// 辅助函数：创建 TODO 卡片响应
function createTodoCardResponse(todos) {
  // 统计信息
  const total = todos.length;
  const completed = todos.filter(t => t.completed).length;
  const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
  
  // 按优先级分组
  const highPriority = todos.filter(t => t.priority === 'high');
  const mediumPriority = todos.filter(t => t.priority === 'medium');
  const lowPriority = todos.filter(t => t.priority === 'low');
  
  const elements = [
    {
      tag: "div",
      text: {
        content: `**今日任务清单** 📋\n\n进度：${completed}/${total} 已完成 (${progress}%)`,
        tag: "lark_md"
      }
    },
    {
      tag: "hr"
    }
  ];
  
  // 添加高优先级任务
  if (highPriority.length > 0) {
    elements.push({
      tag: "div",
      text: {
        content: "**🔴 高优先级**",
        tag: "lark_md"
      }
    });
    
    highPriority.forEach(todo => {
      elements.push({
        tag: "action",
        actions: [
          {
            tag: "button",
            text: { 
              content: todo.completed ? `✅ ${todo.text}` : `⬜ ${todo.text}`, 
              tag: "plain_text" 
            },
            type: todo.completed ? "default" : "primary",
            value: { 
              action: "toggle_todo", 
              todoId: todo.id,
              todos: todos
            }
          }
        ]
      });
    });
    
    elements.push({
      tag: "div",
      text: { content: "", tag: "plain_text" }
    });
  }
  
  // 添加中优先级任务
  if (mediumPriority.length > 0) {
    elements.push({
      tag: "div",
      text: {
        content: "**🟡 中优先级**",
        tag: "lark_md"
      }
    });
    
    mediumPriority.forEach(todo => {
      elements.push({
        tag: "action",
        actions: [
          {
            tag: "button",
            text: { 
              content: todo.completed ? `✅ ${todo.text}` : `⬜ ${todo.text}`, 
              tag: "plain_text" 
            },
            type: todo.completed ? "default" : "primary",
            value: { 
              action: "toggle_todo", 
              todoId: todo.id,
              todos: todos
            }
          }
        ]
      });
    });
    
    elements.push({
      tag: "div",
      text: { content: "", tag: "plain_text" }
    });
  }
  
  // 添加低优先级任务
  if (lowPriority.length > 0) {
    elements.push({
      tag: "div",
      text: {
        content: "**🟢 低优先级**",
        tag: "lark_md"
      }
    });
    
    lowPriority.forEach(todo => {
      elements.push({
        tag: "action",
        actions: [
          {
            tag: "button",
            text: { 
              content: todo.completed ? `✅ ${todo.text}` : `⬜ ${todo.text}`, 
              tag: "plain_text" 
            },
            type: todo.completed ? "default" : "primary",
            value: { 
              action: "toggle_todo", 
              todoId: todo.id,
              todos: todos
            }
          }
        ]
      });
    });
  }
  
  // 添加操作按钮
  elements.push(
    {
      tag: "hr"
    },
    {
      tag: "action",
      actions: [
        {
          tag: "button",
          text: { content: "✅ 全部完成", tag: "plain_text" },
          type: "primary",
          value: { action: "complete_all_todos", todos: todos }
        },
        {
          tag: "button",
          text: { content: "🔄 重置全部", tag: "plain_text" },
          type: "default",
          value: { action: "reset_all_todos", todos: todos }
        },
        {
          tag: "button",
          text: { content: "🗑️ 清除已完成", tag: "plain_text" },
          type: "danger",
          value: { action: "clear_completed_todos", todos: todos }
        }
      ]
    },
    {
      tag: "note",
      elements: [
        {
          tag: "plain_text",
          content: "💡 提示：点击任务可以切换完成状态"
        }
      ]
    }
  );
  
  return {
    type: 'raw',
    data: {
      config: { wide_screen_mode: true },
      header: {
        title: { content: "📋 今日任务清单", tag: "plain_text" },
        template: completed === total && total > 0 ? "green" : "blue"
      },
      elements: elements
    }
  };
}



// 创建事件分发器，注册卡片回调事件
const eventDispatcher = new lark.EventDispatcher({
  loggerLevel: lark.LoggerLevel.info,
}).register({
  // 注册卡片回传交互事件
  'card.action.trigger': async (data) => {
    try {
      // 长连接模式下，数据结构是扁平的，action、operator 等直接在顶层
      const { action, operator, event_id, context } = data;
      const actionValue = action?.value;

      console.log(`\n📨 收到卡片回调 | 操作者: ${operator?.open_id} | 操作: ${actionValue?.action}`);

      // 发送原始回调数据到 Gateway（异步，不阻塞主流程）
      sendToGateway({
        event_id: event_id,
        operator: operator,
        action: action,
        context: context,
        raw_data: data
      }).catch(err => {
        // 静默处理错误
      });

      // 检查是否为重复请求
      if (isDuplicateRequest(event_id, actionValue)) {
        console.log('⚠️ 检测到重复请求，忽略');
        return {
          toast: {
            type: 'info',
            content: '请勿重复点击'
          }
        };
      }

      // 根据不同的操作返回不同的响应
      let response;

    switch (actionValue?.action) {
      case 'great':
        response = {
          toast: {
            type: 'success',
            content: '谢谢你的鼓励！',
            i18n: {
              zh_cn: '谢谢你的鼓励！',
              en_us: 'Thank you for your encouragement!'
            }
          },
          // 返回原卡片，保持不变
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "🎉 交互式卡片测试", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**老板你好！** 🐑\n\n这是我发送的第一张真正的飞书交互式卡片！\n\n你可以点击下面的按钮进行交互：",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "✅ 很棒！", tag: "plain_text" },
                      type: "primary",
                      value: { action: "great" }
                    },
                    {
                      tag: "button",
                      text: { content: "📋 查看 TODO", tag: "plain_text" },
                      type: "default",
                      value: { action: "view_todo" }
                    },
                    {
                      tag: "button",
                      text: { content: "🌤️ 查看天气", tag: "plain_text" },
                      type: "default",
                      value: { action: "view_weather" }
                    }
                  ]
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "💡 **提示**：点击按钮后，我会收到你的操作通知（需要配置回调）",
                    tag: "lark_md"
                  }
                }
              ]
            }
          }
        };
        break;

      case 'view_todo':
        response = {
          toast: {
            type: 'info',
            content: '正在加载 TODO 列表...'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "📋 今日 TODO 清单", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**THE Thing（必做）**\n✅ 完成项目报告\n\n**Would Be Nice（次要）**\n⏰ 回复邮件\n📝 整理文档",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "✅ 全部完成", tag: "plain_text" },
                      type: "primary",
                      value: { action: "complete_all" }
                    },
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'view_weather':
        response = {
          toast: {
            type: 'info',
            content: '正在获取天气信息...'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "🌤️ 今日天气", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**北京**\n\n🌡️ 温度：22°C\n💧 湿度：45%\n🌬️ 风力：3级\n☀️ 天气：晴朗",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'complete_all':
        response = {
          toast: {
            type: 'success',
            content: '🎉 太棒了！所有任务已完成！'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "✅ 任务已完成", tag: "plain_text" },
                template: "green"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**恭喜！** 🎉\n\n所有任务都已完成！\n\n继续保持这个节奏！",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'answer_q1':
        // 第一题回答后，显示第二题
        const q1Answer = actionValue?.answer;
        console.log('📊 问题1回答:', q1Answer);
        
        response = {
          toast: {
            type: 'success',
            content: '✅ 已记录您的回答'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "📋 用户满意度调查 (2/3)", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: `✅ **问题1已回答**：${getSatisfactionText(q1Answer)}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "**2. 您最喜欢我们的哪些功能？**（可多选）",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "📊 数据分析", tag: "plain_text" },
                      type: "default",
                      value: { action: "toggle_feature", feature: "analytics", q1: q1Answer, selected: [] }
                    },
                    {
                      tag: "button",
                      text: { content: "🤖 智能推荐", tag: "plain_text" },
                      type: "default",
                      value: { action: "toggle_feature", feature: "recommendation", q1: q1Answer, selected: [] }
                    },
                    {
                      tag: "button",
                      text: { content: "💬 即时通讯", tag: "plain_text" },
                      type: "default",
                      value: { action: "toggle_feature", feature: "chat", q1: q1Answer, selected: [] }
                    }
                  ]
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "📁 文件管理", tag: "plain_text" },
                      type: "default",
                      value: { action: "toggle_feature", feature: "file_management", q1: q1Answer, selected: [] }
                    },
                    {
                      tag: "button",
                      text: { content: "🔔 消息提醒", tag: "plain_text" },
                      type: "default",
                      value: { action: "toggle_feature", feature: "notifications", q1: q1Answer, selected: [] }
                    },
                    {
                      tag: "button",
                      text: { content: "🎨 界面设计", tag: "plain_text" },
                      type: "default",
                      value: { action: "toggle_feature", feature: "ui_design", q1: q1Answer, selected: [] }
                    }
                  ]
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "**已选择**：无",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "➡️ 下一题", tag: "plain_text" },
                      type: "primary",
                      value: { action: "answer_q2", q1: q1Answer, features: [] }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'toggle_feature':
        // 切换功能选择
        const feature = actionValue?.feature;
        const q1Ans = actionValue?.q1;
        
        // 安全地获取当前选择列表
        let selected = [];
        if (actionValue?.selected) {
          if (Array.isArray(actionValue.selected)) {
            selected = actionValue.selected.filter(item => typeof item === 'string');
          } else if (typeof actionValue.selected === 'string') {
            selected = [actionValue.selected];
          }
        }
        
        // 安全地切换选择状态
        const index = selected.indexOf(feature);
        if (index > -1) {
          // 已选中，取消选择
          selected = selected.filter(f => f !== feature);
        } else {
          // 未选中，添加选择
          if (!selected.includes(feature)) {
            selected = [...selected, feature];
          }
        }
        
        console.log('🔄 切换功能选择:', feature, '当前选择:', selected);
        
        // 定义所有功能按钮
        const allFeatures = [
          { id: "analytics", text: "📊 数据分析" },
          { id: "recommendation", text: "🤖 智能推荐" },
          { id: "chat", text: "💬 即时通讯" },
          { id: "file_management", text: "📁 文件管理" },
          { id: "notifications", text: "🔔 消息提醒" },
          { id: "ui_design", text: "🎨 界面设计" }
        ];
        
        // 构建按钮 - 第一行
        const row1Actions = allFeatures.slice(0, 3).map(f => ({
          tag: "button",
          text: { content: f.text, tag: "plain_text" },
          type: selected.includes(f.id) ? "primary" : "default",
          value: { 
            action: "toggle_feature", 
            feature: f.id, 
            q1: q1Ans, 
            selected: selected 
          }
        }));
        
        // 构建按钮 - 第二行
        const row2Actions = allFeatures.slice(3, 6).map(f => ({
          tag: "button",
          text: { content: f.text, tag: "plain_text" },
          type: selected.includes(f.id) ? "primary" : "default",
          value: { 
            action: "toggle_feature", 
            feature: f.id, 
            q1: q1Ans, 
            selected: selected 
          }
        }));
        
        response = {
          toast: {
            type: 'info',
            content: index > -1 ? '❌ 已取消' : '✅ 已选择'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "📋 用户满意度调查 (2/3)", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: `✅ **问题1已回答**：${getSatisfactionText(q1Ans)}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "**2. 您最喜欢我们的哪些功能？**（可多选）",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "action",
                  actions: row1Actions
                },
                {
                  tag: "action",
                  actions: row2Actions
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: `**已选择 (${selected.length})**：${selected.length > 0 ? getFeaturesText(selected) : '无'}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "➡️ 下一题", tag: "plain_text" },
                      type: "primary",
                      value: { action: "answer_q2", q1: q1Ans, features: selected }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'answer_q2':
        // 第二题回答后，显示第三题
        const q2Features = actionValue?.features || [];
        const q1Prev = actionValue?.q1;
        console.log('📊 问题2回答:', q2Features);
        
        response = {
          toast: {
            type: 'success',
            content: '✅ 已记录您的回答'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "📋 用户满意度调查 (3/3)", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: `✅ **问题1已回答**：${getSatisfactionText(q1Prev)}\n\n` +
                             `✅ **问题2已回答**：${q2Features.length > 0 ? getFeaturesText(q2Features) : '无'}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "**3. 您是否愿意推荐我们的产品给朋友？**",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "👍 非常愿意", tag: "plain_text" },
                      type: "primary",
                      value: { action: "submit_survey", q1: q1Prev, q2: q2Features, q3: "very_likely" }
                    },
                    {
                      tag: "button",
                      text: { content: "🙂 愿意", tag: "plain_text" },
                      type: "default",
                      value: { action: "submit_survey", q1: q1Prev, q2: q2Features, q3: "likely" }
                    },
                    {
                      tag: "button",
                      text: { content: "😐 不确定", tag: "plain_text" },
                      type: "default",
                      value: { action: "submit_survey", q1: q1Prev, q2: q2Features, q3: "neutral" }
                    }
                  ]
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "😞 不太愿意", tag: "plain_text" },
                      type: "default",
                      value: { action: "submit_survey", q1: q1Prev, q2: q2Features, q3: "unlikely" }
                    },
                    {
                      tag: "button",
                      text: { content: "👎 完全不愿意", tag: "plain_text" },
                      type: "default",
                      value: { action: "submit_survey", q1: q1Prev, q2: q2Features, q3: "very_unlikely" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'submit_survey':
        // 处理问卷提交
        const surveyQ1 = actionValue?.q1;
        const surveyQ2 = actionValue?.q2 || [];
        const surveyQ3 = actionValue?.q3;
        
        console.log('📊 完整问卷数据:', JSON.stringify({ q1: surveyQ1, q2: surveyQ2, q3: surveyQ3 }, null, 2));
        
        response = {
          toast: {
            type: 'success',
            content: '✅ 问卷提交成功！感谢您的反馈！'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "✅ 提交成功", tag: "plain_text" },
                template: "green"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**感谢您的反馈！** 🎉\n\n您的意见对我们非常重要，我们会认真考虑您的建议。",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "**您的回答总结：**\n\n" +
                             `📊 **满意度**：${getSatisfactionText(surveyQ1)}\n\n` +
                             `💡 **喜欢的功能**：${surveyQ2.length > 0 ? getFeaturesText(surveyQ2) : '无'}\n\n` +
                             `👥 **推荐意愿**：${getRecommendText(surveyQ3)}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "note",
                  elements: [
                    {
                      tag: "plain_text",
                      content: "💝 再次感谢您的参与！"
                    }
                  ]
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'vote':
        // 处理投票
        const voteOption = actionValue?.option;
        console.log('🗳️ 投票选项:', voteOption);
        
        response = {
          toast: {
            type: 'success',
            content: '✅ 投票成功！'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "✅ 投票成功", tag: "plain_text" },
                template: "green"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: `**感谢您的投票！** 🎉\n\n您选择了：${getVoteOptionText(voteOption)}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "📊 查看结果", tag: "plain_text" },
                      type: "primary",
                      value: { action: "view_poll_results" }
                    },
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'view_poll_results':
        response = {
          toast: {
            type: 'info',
            content: '查看投票结果'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "📊 投票结果", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**本周团建活动投票结果**\n\n" +
                             "🎳 保龄球：3票 (30%)\n" +
                             "🎬 看电影：2票 (20%)\n" +
                             "🍕 聚餐：4票 (40%)\n" +
                             "🏃 户外运动：1票 (10%)\n" +
                             "🎮 电竞：0票 (0%)\n\n" +
                             "总投票数：10票",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'submit_appointment':
        // 处理会议室预约
        const appointmentData = action?.form_value || {};
        console.log('📅 预约数据:', JSON.stringify(appointmentData, null, 2));
        
        response = {
          toast: {
            type: 'success',
            content: '✅ 预约成功！'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "✅ 预约成功", tag: "plain_text" },
                template: "green"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**会议室预约成功！** 🎉\n\n**预约信息：**",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: `🏢 **会议室**：${getRoomText(appointmentData.room)}\n\n` +
                             `📋 **会议主题**：${appointmentData.title || '未填写'}\n\n` +
                             `👥 **预计人数**：${appointmentData.attendees || '未填写'}人\n\n` +
                             `📝 **备注**：${appointmentData.notes || '无'}`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "note",
                  elements: [
                    {
                      tag: "plain_text",
                      content: "💡 预约确认邮件已发送到您的邮箱"
                    }
                  ]
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'toggle_todo':
        // 切换 TODO 完成状态
        const todoId = actionValue?.todoId;
        let todos = actionValue?.todos || [];
        
        // 安全地处理 todos 数组
        if (!Array.isArray(todos)) {
          console.error('❌ todos 不是数组');
          todos = [];
        }
        
        // 切换指定 TODO 的完成状态
        todos = todos.map(todo => {
          if (todo.id === todoId) {
            return { ...todo, completed: !todo.completed };
          }
          return todo;
        });
        
        const toggledTodo = todos.find(t => t.id === todoId);
        console.log('✅ 切换 TODO:', todoId, '状态:', toggledTodo?.completed);
        
        // 重新生成卡片
        response = {
          toast: {
            type: 'success',
            content: toggledTodo?.completed ? '✅ 任务已完成' : '⬜ 任务已取消完成'
          },
          card: createTodoCardResponse(todos)
        };
        break;

      case 'complete_all_todos':
        // 全部标记为完成
        let allTodos = actionValue?.todos || [];
        allTodos = allTodos.map(todo => ({ ...todo, completed: true }));
        
        console.log('✅ 全部任务标记为完成');
        
        response = {
          toast: {
            type: 'success',
            content: '🎉 所有任务已完成！'
          },
          card: createTodoCardResponse(allTodos)
        };
        break;

      case 'reset_all_todos':
        // 重置全部任务
        let resetTodos = actionValue?.todos || [];
        resetTodos = resetTodos.map(todo => ({ ...todo, completed: false }));
        
        console.log('🔄 重置所有任务');
        
        response = {
          toast: {
            type: 'info',
            content: '🔄 已重置所有任务'
          },
          card: createTodoCardResponse(resetTodos)
        };
        break;

      case 'clear_completed_todos':
        // 清除已完成的任务
        let remainingTodos = actionValue?.todos || [];
        const beforeCount = remainingTodos.length;
        remainingTodos = remainingTodos.filter(todo => !todo.completed);
        const clearedCount = beforeCount - remainingTodos.length;
        
        console.log('🗑️ 清除已完成任务:', clearedCount, '个');
        
        if (remainingTodos.length === 0) {
          // 如果没有剩余任务，显示空状态
          response = {
            toast: {
              type: 'success',
              content: `🗑️ 已清除 ${clearedCount} 个已完成任务`
            },
            card: {
              type: 'raw',
              data: {
                config: { wide_screen_mode: true },
                header: {
                  title: { content: "🎉 所有任务已完成", tag: "plain_text" },
                  template: "green"
                },
                elements: [
                  {
                    tag: "div",
                    text: {
                      content: "**太棒了！** 🎉\n\n所有任务都已完成并清除！\n\n继续保持这个节奏！",
                      tag: "lark_md"
                    }
                  },
                  {
                    tag: "hr"
                  },
                  {
                    tag: "action",
                    actions: [
                      {
                        tag: "button",
                        text: { content: "🔙 返回", tag: "plain_text" },
                        type: "default",
                        value: { action: "back" }
                      }
                    ]
                  }
                ]
              }
            }
          };
        } else {
          response = {
            toast: {
              type: 'success',
              content: `🗑️ 已清除 ${clearedCount} 个已完成任务`
            },
            card: createTodoCardResponse(remainingTodos)
          };
        }
        break;

      case 'rate':
        // 处理评分
        const stars = actionValue?.stars || 0;
        console.log('⭐ 评分:', stars);
        
        response = {
          toast: {
            type: 'success',
            content: `感谢您的${stars}星评价！`
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "✅ 评价成功", tag: "plain_text" },
                template: "green"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: `**感谢您的评价！** 🎉\n\n您给出了 ${'⭐'.repeat(stars)} 的评分`,
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "🔙 返回", tag: "plain_text" },
                      type: "default",
                      value: { action: "back" }
                    }
                  ]
                }
              ]
            }
          }
        };
        break;

      case 'cancel':
        response = {
          toast: {
            type: 'info',
            content: '已取消问卷'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "🎉 交互式卡片测试", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**老板你好！** 🐑\n\n这是我发送的第一张真正的飞书交互式卡片！\n\n你可以点击下面的按钮进行交互：",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "✅ 很棒！", tag: "plain_text" },
                      type: "primary",
                      value: { action: "great" }
                    },
                    {
                      tag: "button",
                      text: { content: "📋 查看 TODO", tag: "plain_text" },
                      type: "default",
                      value: { action: "view_todo" }
                    },
                    {
                      tag: "button",
                      text: { content: "🌤️ 查看天气", tag: "plain_text" },
                      type: "default",
                      value: { action: "view_weather" }
                    }
                  ]
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "💡 **提示**：点击按钮后，我会收到你的操作通知（需要配置回调）",
                    tag: "lark_md"
                  }
                }
              ]
            }
          }
        };
        break;

      case 'back':
        response = {
          toast: {
            type: 'info',
            content: '返回主页'
          },
          card: {
            type: 'raw',
            data: {
              config: { wide_screen_mode: true },
              header: {
                title: { content: "🎉 交互式卡片测试", tag: "plain_text" },
                template: "blue"
              },
              elements: [
                {
                  tag: "div",
                  text: {
                    content: "**老板你好！** 🐑\n\n这是我发送的第一张真正的飞书交互式卡片！\n\n你可以点击下面的按钮进行交互：",
                    tag: "lark_md"
                  }
                },
                {
                  tag: "hr"
                },
                {
                  tag: "action",
                  actions: [
                    {
                      tag: "button",
                      text: { content: "✅ 很棒！", tag: "plain_text" },
                      type: "primary",
                      value: { action: "great" }
                    },
                    {
                      tag: "button",
                      text: { content: "📋 查看 TODO", tag: "plain_text" },
                      type: "default",
                      value: { action: "view_todo" }
                    },
                    {
                      tag: "button",
                      text: { content: "🌤️ 查看天气", tag: "plain_text" },
                      type: "default",
                      value: { action: "view_weather" }
                    }
                  ]
                },
                {
                  tag: "hr"
                },
                {
                  tag: "div",
                  text: {
                    content: "💡 **提示**：点击按钮后，我会收到你的操作通知（需要配置回调）",
                    tag: "lark_md"
                  }
                }
              ]
            }
          }
        };
        break;

      default:
        console.log(`⚠️ 未知操作: ${JSON.stringify(actionValue)}`);
        response = {
          toast: {
            type: 'info',
            content: '操作成功'
          }
        };
    }

    console.log(`✅ 响应成功\n`);
    return createSafeResponse(response);
    
  } catch (error) {
    console.error('❌ 处理回调时出错:', error);
    console.error('错误堆栈:', error.stack);
    
    // 返回安全的错误响应
    return {
      toast: {
        type: 'error',
        content: '处理失败，请稍后重试'
      }
    };
  }
}
});

// 加载飞书配置
const FEISHU_CONFIG = loadFeishuConfig();

if (!FEISHU_CONFIG.appId || !FEISHU_CONFIG.appSecret) {
  console.error('❌ 错误：未找到飞书应用配置');
  console.error('请确保以下任一配置存在：');
  console.error('1. ~/.openclaw/openclaw.json 中配置 channels.feishu.accounts.main');
  console.error('2. 设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET');
  process.exit(1);
}

// 启动长连接客户端
const wsClient = new lark.WSClient({
  appId: FEISHU_CONFIG.appId,
  appSecret: FEISHU_CONFIG.appSecret,
  loggerLevel: lark.LoggerLevel.info,
});

// 启动长连接，注册事件分发器
wsClient.start({
  eventDispatcher: eventDispatcher,
}).then(() => {
  console.log('\n🚀 飞书卡片回调服务器启动成功！');
  console.log('📡 使用长连接模式接收回调');
  console.log('✅ 无需配置公网域名或回调地址');
  console.log('✅ 已注册 card.action.trigger 事件处理器');
  console.log('📋 App ID:', FEISHU_CONFIG.appId);
  console.log('\n💡 提示：');
  console.log('1. 长连接已建立，可以接收卡片交互回调');
  console.log('2. 发送测试卡片: node send-card.js confirmation "测试" --chat-id oc_xxx');
  console.log('3. 点击卡片按钮即可看到回调处理');
  console.log('\n⚠️  如果点击按钮后没有收到回调，请检查：');
  console.log('   - 飞书开发者后台是否选择了"长连接"模式');
  console.log('   - 是否已订阅 card.action.trigger 事件');
  console.log('   - App ID 和 App Secret 是否正确\n');
}).catch((error) => {
  console.error('❌ 启动失败:', error);
  console.error('错误详情:', error.stack);
  process.exit(1);
});

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n\n👋 正在关闭服务器...');
  process.exit(0);
});
