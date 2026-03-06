/**
 * 飞书交互式卡片模板库
 * 提供常用的卡片模板生成函数
 */

/**
 * 创建确认卡片
 * @param {string} message - 确认消息
 * @param {object} options - 可选配置
 * @returns {object} 卡片 JSON
 */
function createConfirmationCard(message, options = {}) {
  const {
    title = '⚠️ 确认操作',
    template = 'orange',
    confirmText = '✅ 确认',
    cancelText = '❌ 取消',
    confirmType = 'danger',
    operation = 'confirm',
    data = {}
  } = options;
  
  return {
    config: { wide_screen_mode: true },
    header: {
      title: { content: title, tag: "plain_text" },
      template: template
    },
    elements: [
      {
        tag: "div",
        text: {
          content: message,
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
            text: { content: confirmText, tag: "plain_text" },
            type: confirmType,
            value: { action: operation, ...data }
          },
          {
            tag: "button",
            text: { content: cancelText, tag: "plain_text" },
            type: "default",
            value: { action: "cancel" }
          }
        ]
      }
    ]
  };
}

/**
 * 创建投票卡片
 * @param {string} question - 投票问题
 * @param {array} options - 投票选项数组
 * @param {object} config - 可选配置
 * @returns {object} 卡片 JSON
 */
function createPollCard(question, options = [], config = {}) {
  const {
    title = '📊 投票',
    template = 'purple',
    showResults = true
  } = config;
  
  // 将选项分组，每行最多3个按钮
  const optionRows = [];
  for (let i = 0; i < options.length; i += 3) {
    optionRows.push(options.slice(i, i + 3));
  }
  
  const elements = [
    {
      tag: "div",
      text: {
        content: `**${question}**\n\n请选择：`,
        tag: "lark_md"
      }
    },
    {
      tag: "hr"
    }
  ];
  
  // 添加选项按钮
  optionRows.forEach(row => {
    elements.push({
      tag: "action",
      actions: row.map(option => ({
        tag: "button",
        text: { content: option, tag: "plain_text" },
        type: "default",
        value: { action: "vote", option: option }
      }))
    });
  });
  
  // 添加查看结果按钮
  if (showResults) {
    elements.push({
      tag: "hr"
    });
    elements.push({
      tag: "action",
      actions: [
        {
          tag: "button",
          text: { content: "📊 查看结果", tag: "plain_text" },
          type: "primary",
          value: { action: "view_poll_results" }
        }
      ]
    });
  }
  
  return {
    config: { wide_screen_mode: true },
    header: {
      title: { content: title, tag: "plain_text" },
      template: template
    },
    elements: elements
  };
}

/**
 * 创建 TODO 清单卡片
 * @param {array} todos - TODO 项数组 [{ id, text, completed, priority }]
 * @param {object} config - 可选配置
 * @returns {object} 卡片 JSON
 */
function createTodoCard(todos = [], config = {}) {
  const {
    title = '📋 任务清单',
    showProgress = true,
    showActions = true
  } = config;
  
  // 统计信息
  const total = todos.length;
  const completed = todos.filter(t => t.completed).length;
  const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
  
  // 按优先级分组
  const highPriority = todos.filter(t => t.priority === 'high');
  const mediumPriority = todos.filter(t => t.priority === 'medium');
  const lowPriority = todos.filter(t => t.priority === 'low');
  
  const elements = [];
  
  // 添加进度信息
  if (showProgress) {
    elements.push({
      tag: "div",
      text: {
        content: `**${title}**\n\n进度：${completed}/${total} 已完成 (${progress}%)`,
        tag: "lark_md"
      }
    });
    elements.push({ tag: "hr" });
  }
  
  // 添加高优先级任务
  if (highPriority.length > 0) {
    elements.push({
      tag: "div",
      text: { content: "**🔴 高优先级**", tag: "lark_md" }
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
            value: { action: "toggle_todo", todoId: todo.id, todos: todos }
          }
        ]
      });
    });
    
    elements.push({ tag: "div", text: { content: "", tag: "plain_text" } });
  }
  
  // 添加中优先级任务
  if (mediumPriority.length > 0) {
    elements.push({
      tag: "div",
      text: { content: "**🟡 中优先级**", tag: "lark_md" }
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
            value: { action: "toggle_todo", todoId: todo.id, todos: todos }
          }
        ]
      });
    });
    
    elements.push({ tag: "div", text: { content: "", tag: "plain_text" } });
  }
  
  // 添加低优先级任务
  if (lowPriority.length > 0) {
    elements.push({
      tag: "div",
      text: { content: "**🟢 低优先级**", tag: "lark_md" }
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
            value: { action: "toggle_todo", todoId: todo.id, todos: todos }
          }
        ]
      });
    });
  }
  
  // 添加操作按钮
  if (showActions) {
    elements.push({ tag: "hr" });
    elements.push({
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
    });
    
    elements.push({
      tag: "note",
      elements: [
        { tag: "plain_text", content: "💡 提示：点击任务可以切换完成状态" }
      ]
    });
  }
  
  return {
    config: { wide_screen_mode: true },
    header: {
      title: { content: title, tag: "plain_text" },
      template: completed === total && total > 0 ? "green" : "blue"
    },
    elements: elements
  };
}

/**
 * 创建通知卡片
 * @param {string} message - 通知消息
 * @param {object} options - 可选配置
 * @returns {object} 卡片 JSON
 */
function createNotificationCard(message, options = {}) {
  const {
    title = '📢 通知',
    template = 'blue',
    type = 'info', // info, success, warning, error
    showButton = false,
    buttonText = '知道了',
    buttonAction = 'acknowledge'
  } = options;
  
  const icons = {
    info: 'ℹ️',
    success: '✅',
    warning: '⚠️',
    error: '❌'
  };
  
  const templates = {
    info: 'blue',
    success: 'green',
    warning: 'orange',
    error: 'red'
  };
  
  const elements = [
    {
      tag: "div",
      text: {
        content: `${icons[type]} ${message}`,
        tag: "lark_md"
      }
    }
  ];
  
  if (showButton) {
    elements.push({ tag: "hr" });
    elements.push({
      tag: "action",
      actions: [
        {
          tag: "button",
          text: { content: buttonText, tag: "plain_text" },
          type: "primary",
          value: { action: buttonAction }
        }
      ]
    });
  }
  
  return {
    config: { wide_screen_mode: true },
    header: {
      title: { content: title, tag: "plain_text" },
      template: template || templates[type]
    },
    elements: elements
  };
}

/**
 * 创建选择卡片（单选或多选）
 * @param {string} question - 问题
 * @param {array} choices - 选项数组
 * @param {object} options - 可选配置
 * @returns {object} 卡片 JSON
 */
function createChoiceCard(question, choices = [], options = {}) {
  const {
    title = '❓ 请选择',
    template = 'blue',
    multiSelect = false
  } = options;
  
  const elements = [
    {
      tag: "div",
      text: {
        content: `**${question}**${multiSelect ? '\n\n（可多选）' : ''}`,
        tag: "lark_md"
      }
    },
    {
      tag: "hr"
    }
  ];
  
  // 将选项分组，每行最多2个按钮
  const choiceRows = [];
  for (let i = 0; i < choices.length; i += 2) {
    choiceRows.push(choices.slice(i, i + 2));
  }
  
  choiceRows.forEach(row => {
    elements.push({
      tag: "action",
      actions: row.map(choice => ({
        tag: "button",
        text: { content: choice, tag: "plain_text" },
        type: "default",
        value: { 
          action: multiSelect ? "toggle_choice" : "select_choice", 
          choice: choice 
        }
      }))
    });
  });
  
  if (multiSelect) {
    elements.push({ tag: "hr" });
    elements.push({
      tag: "action",
      actions: [
        {
          tag: "button",
          text: { content: "✅ 确认选择", tag: "plain_text" },
          type: "primary",
          value: { action: "confirm_choices" }
        }
      ]
    });
  }
  
  return {
    config: { wide_screen_mode: true },
    header: {
      title: { content: title, tag: "plain_text" },
      template: template
    },
    elements: elements
  };
}

module.exports = {
  createConfirmationCard,
  createPollCard,
  createTodoCard,
  createNotificationCard,
  createChoiceCard
};
