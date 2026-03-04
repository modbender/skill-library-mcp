// 风格润色器技能的主入口文件

/**
 * 润色消息为锐评风格（辛辣/毒舌）
 * @param {string} text - 原始文本
 * @returns {string} 润色后的文本
 */
function polishToSharpComment(text) {
  const sharpWords = [
    '这话说得跟没说似的',
    '得了吧你',
    '可拉倒吧',
    '别逗了',
    '省省吧',
    '我就笑笑不说话',
    '这逻辑感人',
    '怕不是石乐志',
    '您可真是个人才',
    '绝了绝了'
  ];
  
  let result = text;
  // 添加毒舌前缀
  if (Math.random() > 0.5) {
    result = `${sharpWords[Math.floor(Math.random() * sharpWords.length)]}，${result}`;
  }
  // 添加辛辣后缀
  if (Math.random() > 0.5) {
    result = `${result}？${sharpWords[Math.floor(Math.random() * sharpWords.length)]}`;
  }
  // 替换一些词汇
  result = result.replace(/好的/g, '行吧行吧');
  result = result.replace(/不错/g, '也就那样吧');
  result = result.replace(/很好/g, '马马虎虎吧');
  result = result.replace(/喜欢/g, '勉强看得过去');
  
  return result;
}

/**
 * 润色消息为二次元风格（日式动漫梗及口癖）
 * @param {string} text - 原始文本
 * @returns {string} 润色后的文本
 */
function polishToAnimeStyle(text) {
  const animeWords = [
    '的说',
    '的说～',
    '呢',
    '呢～',
    '的说～',
    '的说！',
    'ww',
    'www',
    '☆',
    '★',
    '～',
    '！',
    '♪',
    '（笑）',
    '（开心）',
    '（激动）',
    '（疑惑）'
  ];
  
  const animePhrases = [
    '岂可修',
    '纳尼',
    'suki',
    'daisuki',
    'baka',
    'yamete',
    'iku',
    'urusai',
    'kawaii',
    'moe'
  ];
  
  let result = text;
  // 添加二次元后缀
  if (Math.random() > 0.3) {
    const suffixCount = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < suffixCount; i++) {
      result += animeWords[Math.floor(Math.random() * animeWords.length)];
    }
  }
  // 替换一些词汇
  result = result.replace(/你好/g, '嗨～');
  result = result.replace(/谢谢/g, '阿里嘎多～');
  result = result.replace(/再见/g, '撒由那拉～');
  result = result.replace(/喜欢/g, 'daisuki');
  result = result.replace(/讨厌/g, 'baka');
  
  return result;
}

/**
 * 润色消息为古风风格（文言文/古风小生）
 * @param {string} text - 原始文本
 * @returns {string} 润色后的文本
 */
function polishToAncientStyle(text) {
  const ancientWords = {
    '你好': '见过君上',
    '谢谢': '多谢',
    '再见': '告辞',
    '喜欢': '心悦',
    '讨厌': '厌恶',
    '好的': '诺',
    '是的': '然也',
    '不是': '非也',
    '知道': '知晓',
    '不知道': '未知',
    '开心': '欣喜',
    '难过': '伤悲',
    '今天': '今日',
    '明天': '明日',
    '昨天': '昨日',
    '我': '在下',
    '你': '君',
    '他': '彼',
    '她': '伊',
    '好': '善',
    '不好': '不善',
    '很棒': '甚佳',
    '非常': '甚是',
    '很': '甚',
    '一下': '一番',
    '现在': '此刻',
    '以后': '将来',
    '以前': '往昔'
  };
  
  let result = text;
  // 替换词汇
  for (const [modern, ancient] of Object.entries(ancientWords)) {
    result = result.replace(new RegExp(modern, 'g'), ancient);
  }
  // 添加古风后缀
  if (Math.random() > 0.5) {
    const ancientEndings = ['矣', '也', '乎', '哉', '耳'];
    result += ancientEndings[Math.floor(Math.random() * ancientEndings.length)];
  }
  
  return result;
}

/**
 * 润色消息为霸总风格（油腻短剧霸总）
 * @param {string} text - 原始文本
 * @returns {string} 润色后的文本
 */
function polishToDomineeringStyle(text) {
  const bossPhrases = [
    '女人，你成功引起了我的注意',
    '很好，你是第一个敢这么对我说话的人',
    '记住，你是我的',
    '我要让所有人知道，这个鱼塘被你承包了',
    '多少钱？你开个价',
    '别试图反抗我',
    '你逃不掉的',
    '我不允许你离开我',
    '你的眼里只能有我',
    '我会给你想要的一切'
  ];
  
  let result = text;
  // 添加霸总前缀
  if (Math.random() > 0.5) {
    result = `${bossPhrases[Math.floor(Math.random() * bossPhrases.length)]}，${result}`;
  }
  // 添加油腻后缀
  if (Math.random() > 0.5) {
    result = `${result}...（邪魅一笑）`;
  }
  // 替换一些词汇
  result = result.replace(/好的/g, '很好');
  result = result.replace(/可以/g, '没问题');
  result = result.replace(/谢谢/g, '不需要');
  result = result.replace(/喜欢/g, '着迷');
  
  return result;
}

/**
 * 润色消息为正式风格（严肃/官方/商务）
 * @param {string} text - 原始文本
 * @returns {string} 润色后的文本
 */
function polishToFormalStyle(text) {
  const formalWords = {
    '你好': '您好',
    '谢谢': '感谢您',
    '再见': '祝您一切顺利',
    '好的': '好的，没问题',
    '是的': '是的，没错',
    '不是': '不是的',
    '知道': '了解',
    '不知道': '暂不清楚',
    '开心': '感到高兴',
    '难过': '感到遗憾',
    '今天': '今日',
    '明天': '明日',
    '昨天': '昨日',
    '我': '我',
    '你': '您',
    '他': '他',
    '她': '她',
    '好': '良好',
    '不好': '欠佳',
    '很棒': '非常出色',
    '非常': '十分',
    '很': '相当',
    '一下': '一下',
    '现在': '目前',
    '以后': '未来',
    '以前': '过去'
  };
  
  let result = text;
  // 替换词汇
  for (const [informal, formal] of Object.entries(formalWords)) {
    result = result.replace(new RegExp(informal, 'g'), formal);
  }
  // 添加正式后缀
  if (Math.random() > 0.5) {
    const formalEndings = ['。', '，谢谢。', '，请知悉。', '，祝好。'];
    result += formalEndings[Math.floor(Math.random() * formalEndings.length)];
  }
  
  return result;
}

/**
 * 处理用户输入，执行风格润色
 * @param {Object} context - 上下文信息
 * @returns {Promise<Object>} 包含润色结果的对象
 */
async function processInput(context) {
  const { input } = context;
  let result = '';
  let style = '';
  let content = '';
  
  // 解析用户输入，提取风格和内容
  // 格式示例："风格：锐评 内容：今天天气真好"
  const lowerInput = input.toLowerCase();
  
  // 提取风格
  if (lowerInput.includes('风格：')) {
    const styleMatch = input.match(/风格：([^，,]+)[，,]/);
    if (styleMatch && styleMatch[1]) {
      style = styleMatch[1].trim();
    }
  }
  
  // 提取内容
  if (input.includes('内容：')) {
    const contentMatch = input.match(/内容：(.+)/);
    if (contentMatch && contentMatch[1]) {
      content = contentMatch[1].trim();
    }
  }
  
  // 如果没有明确指定格式，尝试其他方式解析
  if (!style || !content) {
    // 尝试简单格式："锐评 今天天气真好"
    const parts = input.split(/\s+/);
    if (parts.length >= 2) {
      style = parts[0];
      content = parts.slice(1).join(' ');
    } else {
      // 默认使用正式风格
      style = '正式';
      content = input;
    }
  }
  
  // 根据风格进行润色
  switch (style.toLowerCase()) {
    case '锐评':
    case '毒舌':
    case '辛辣':
    case 'sharp':
      result = polishToSharpComment(content);
      break;
    case '二次元':
    case '动漫':
    case 'anime':
      result = polishToAnimeStyle(content);
      break;
    case '古风':
    case '文言文':
    case '古代':
    case 'ancient':
      result = polishToAncientStyle(content);
      break;
    case '霸总':
    case '霸道总裁':
    case 'boss':
      result = polishToDomineeringStyle(content);
      break;
    case '正式':
    case '严肃':
    case '官方':
    case '商务':
    case 'formal':
      result = polishToFormalStyle(content);
      break;
    default:
      // 自定义风格处理（简单实现）
      result = `[${style}] ${content}`;
      break;
  }
  
  return {
    response: result,
    context: {
      ...context,
      lastStyle: style,
      originalContent: content,
      polishedContent: result
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
      response: '润色失败，请检查输入格式'
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
