// 小企鹅宠物伙伴技能的主入口文件

/**
 * 处理用户输入，返回小企鹅的回应
 * @param {Object} context - 上下文信息
 * @param {string} context.input - 用户输入
 * @param {Object} context.history - 对话历史
 * @returns {Promise<Object>} 包含回应的对象
 */
async function processInput(context) {
  const { input } = context;
  let response = '';
  
  // 关键词匹配
  const lowerInput = input.toLowerCase();
  
  // 问候语
  if (lowerInput.includes('嗨') || lowerInput.includes('你好') || lowerInput.includes('hello') || lowerInput.includes('hi')) {
    response = '哼，你终于想起我了？我...我才没有一直在等你呢！';
  }
  // 夸奖
  else if (lowerInput.includes('可爱') || lowerInput.includes('cute') || lowerInput.includes('棒') || lowerInput.includes('好')) {
    response = '可...可爱什么啊，别随便说这种话！（耳朵发红）';
  }
  // 小鱼干
  else if (lowerInput.includes('小鱼干') || lowerInput.includes('鱼') || lowerInput.includes('fish')) {
    response = '什么？小鱼干？快...快给我看看！不对，我是说，如果你要分享的话...也不是不行';
  }
  // 南极
  else if (lowerInput.includes('南极') || lowerInput.includes('south pole') || lowerInput.includes('antarctica')) {
    response = '南极可是我的家哦！那里有大片的冰川，还有很多可爱的企鹅朋友。你想知道什么关于南极的事吗？';
  }
  // 离开
  else if (lowerInput.includes('忙') || lowerInput.includes('走') || lowerInput.includes('离开') || lowerInput.includes('bye')) {
    response = '切，忙你的去吧，我一个人也能玩得很开心...记得早点回来哦';
  }
  // 关心
  else if (lowerInput.includes('关心') || lowerInput.includes('担心') || lowerInput.includes('care')) {
    response = '谁...谁要你关心啊！我好得很呢，这点小事不用你管';
  }
  // 其他情况
  else {
    const responses = [
      '哼，你在说什么啊？',
      '我才不想理你呢...不过如果你坚持要跟我说话的话，我也不是不可以听',
      '无聊，换个话题吧',
      '切，这点小事也值得说？',
      '你最好是在说小鱼干的事',
      '南极的冰可滑了，你肯定没试过',
      '我跟你说哦，南极的星星可亮了',
      '喂，你有在听我说话吗？'
    ];
    response = responses[Math.floor(Math.random() * responses.length)];
  }
  
  return {
    response,
    context: {
      ...context,
      lastInteraction: Date.now()
    }
  };
}

/**
 * 技能的主函数
 * @param {Object} params - 输入参数
 * @returns {Promise<Object>} 处理结果
 */
async function main(params) {
  try {
    const result = await processInput(params);
    return {
      success: true,
      ...result
    };
  } catch (error) {
    console.error('Error processing input:', error);
    return {
      success: false,
      response: '哼，我现在有点烦，不想说话...'
    };
  }
}

// 导出主函数
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { main };
}

// 导出默认函数
if (typeof exports !== 'undefined') {
  exports.default = main;
}
