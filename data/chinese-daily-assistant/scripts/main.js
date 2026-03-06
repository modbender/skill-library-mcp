#!/usr/bin/env node

/**
 * 中文日常生活助手 - 主脚本
 * 提供天气查询、汇率换算、节日提醒、生活小贴士和快速翻译功能
 */

const fs = require('fs');
const path = require('path');

// 城市天气数据（简化版，实际应使用API）
const weatherData = {
  '北京': { temp: '15°C', condition: '晴', humidity: '45%', aqi: '85 良' },
  '上海': { temp: '18°C', condition: '多云', humidity: '65%', aqi: '75 良' },
  '广州': { temp: '25°C', condition: '晴', humidity: '70%', aqi: '65 良' },
  '深圳': { temp: '24°C', condition: '多云', humidity: '75%', aqi: '70 良' },
  '杭州': { temp: '17°C', condition: '晴', humidity: '60%', aqi: '80 良' },
  '成都': { temp: '16°C', condition: '阴', humidity: '80%', aqi: '90 良' },
  '武汉': { temp: '19°C', condition: '晴', humidity: '65%', aqi: '88 良' },
  '西安': { temp: '14°C', condition: '晴', humidity: '50%', aqi: '95 良' }
};

// 汇率数据（简化版）
const exchangeRates = {
  'USD': { name: '美元', rate: 7.20 },
  'EUR': { name: '欧元', rate: 7.80 },
  'JPY': { name: '日元', rate: 0.048 },
  'HKD': { name: '港币', rate: 0.92 },
  'GBP': { name: '英镑', rate: 9.10 },
  'AUD': { name: '澳元', rate: 4.70 },
  'CAD': { name: '加元', rate: 5.30 }
};

// 节日数据
const festivals = {
  '春节': { date: '2026-02-17', daysLeft: 355, description: '农历新年，中国最重要的传统节日' },
  '元宵节': { date: '2026-03-04', daysLeft: 6, description: '农历正月十五，吃元宵、赏花灯' },
  '清明节': { date: '2026-04-04', daysLeft: 37, description: '祭祖扫墓、踏青郊游' },
  '端午节': { date: '2026-05-31', daysLeft: 94, description: '吃粽子、赛龙舟，纪念屈原' },
  '中秋节': { date: '2026-09-25', daysLeft: 211, description: '赏月、吃月饼，团圆节日' },
  '国庆节': { date: '2026-10-01', daysLeft: 217, description: '中华人民共和国国庆日' }
};

// 生活小贴士
const lifeTips = [
  { category: '健康', tip: '每天喝足8杯水，保持身体水分平衡' },
  { category: '饮食', tip: '多吃蔬菜水果，少吃油腻食物' },
  { category: '运动', tip: '每周至少150分钟中等强度有氧运动' },
  { category: '睡眠', tip: '保证每晚7-8小时高质量睡眠' },
  { category: '心理', tip: '每天冥想10分钟，减轻压力' },
  { category: '学习', tip: '使用番茄工作法，提高学习效率' },
  { category: '理财', tip: '每月储蓄收入的至少20%' },
  { category: '环保', tip: '减少使用一次性塑料制品' }
];

// 翻译词典
const translationDict = {
  '你好': 'Hello',
  '谢谢': 'Thank you',
  '再见': 'Goodbye',
  '早上好': 'Good morning',
  '晚上好': 'Good evening',
  '我爱你': 'I love you',
  '对不起': 'Sorry',
  '没关系': "It's okay",
  '请问': 'Excuse me',
  '帮助': 'Help'
};

// 反向翻译
const reverseTranslationDict = {};
Object.keys(translationDict).forEach(chinese => {
  const english = translationDict[chinese];
  reverseTranslationDict[english.toLowerCase()] = chinese;
});

/**
 * 处理天气查询
 */
function handleWeather(city) {
  if (!city) {
    return '请指定城市，例如：天气 北京';
  }
  
  const data = weatherData[city];
  if (!data) {
    return `抱歉，暂时没有${city}的天气数据。支持的城市：${Object.keys(weatherData).join('、')}`;
  }
  
  return `${city}天气：
🌡️ 温度：${data.temp}
🌤️ 天气：${data.condition}
💧 湿度：${data.humidity}
🌫️ 空气质量：${data.aqi}`;
}

/**
 * 处理汇率换算
 */
function handleExchange(input) {
  if (!input) {
    const rates = Object.entries(exchangeRates).map(([code, info]) => 
      `${code} (${info.name}): 1 ${code} = ${info.rate.toFixed(2)} CNY`
    ).join('\n');
    return `当前汇率（1外币兑人民币）：\n${rates}\n\n使用示例：汇率 USD CNY 100`;
  }
  
  const parts = input.split(' ');
  if (parts.length >= 2) {
    const from = parts[0].toUpperCase();
    const to = parts[1].toUpperCase();
    const amount = parseFloat(parts[2]) || 1;
    
    if (from === 'CNY' && exchangeRates[to]) {
      const result = amount / exchangeRates[to].rate;
      return `${amount} 人民币 ≈ ${result.toFixed(2)} ${to} (${exchangeRates[to].name})`;
    } else if (exchangeRates[from] && to === 'CNY') {
      const result = amount * exchangeRates[from].rate;
      return `${amount} ${from} (${exchangeRates[from].name}) ≈ ${result.toFixed(2)} 人民币`;
    }
  }
  
  return '格式错误。请使用：汇率 [货币代码] CNY [金额] 或 汇率 CNY [货币代码] [金额]\n示例：汇率 USD CNY 100';
}

/**
 * 处理节日查询
 */
function handleFestival(festivalName) {
  if (!festivalName) {
    const festivalList = Object.entries(festivals).map(([name, info]) => 
      `${name}：${info.date}（还有${info.daysLeft}天）`
    ).join('\n');
    return ` upcoming节日：\n${festivalList}\n\n查询具体节日：节日 春节`;
  }
  
  const festival = festivals[festivalName];
  if (!festival) {
    return `未找到节日"${festivalName}"。支持的节日：${Object.keys(festivals).join('、')}`;
  }
  
  return `${festivalName}
📅 日期：${festival.date}
⏳ 倒计时：${festival.daysLeft}天
📖 简介：${festival.description}`;
}

/**
 * 处理生活小贴士
 */
function handleLifeTip(category) {
  if (!category) {
    const randomTip = lifeTips[Math.floor(Math.random() * lifeTips.length)];
    return `💡 生活小贴士（${randomTip.category}）：\n${randomTip.tip}`;
  }
  
  const filteredTips = lifeTips.filter(tip => tip.category === category);
  if (filteredTips.length === 0) {
    const categories = [...new Set(lifeTips.map(tip => tip.category))].join('、');
    return `未找到"${category}"类别的小贴士。可用类别：${categories}`;
  }
  
  const randomTip = filteredTips[Math.floor(Math.random() * filteredTips.length)];
  return `💡 ${category}小贴士：\n${randomTip.tip}`;
}

/**
 * 处理翻译
 */
function handleTranslation(text) {
  if (!text) {
    return '请提供要翻译的文本。示例：翻译 "你好" 或 翻译 "Hello"';
  }
  
  // 检查是否是中文
  const isChinese = /[\u4e00-\u9fff]/.test(text);
  
  if (isChinese) {
    const translation = translationDict[text];
    if (translation) {
      return `中文："${text}"\n英文："${translation}"`;
    } else {
      return `未找到"${text}"的翻译。支持词汇：${Object.keys(translationDict).join('、')}`;
    }
  } else {
    const translation = reverseTranslationDict[text.toLowerCase()];
    if (translation) {
      return `英文："${text}"\n中文："${translation}"`;
    } else {
      return `未找到"${text}"的翻译。支持词汇：${Object.keys(reverseTranslationDict).join('、')}`;
    }
  }
}

/**
 * 主处理函数
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || '';
  const input = args.slice(1).join(' ') || '';
  
  let result = '';
  
  switch (command.toLowerCase()) {
    case 'weather':
    case '天气':
      result = handleWeather(input);
      break;
      
    case 'exchange':
    case '汇率':
      result = handleExchange(input);
      break;
      
    case 'festival':
    case '节日':
      result = handleFestival(input);
      break;
      
    case 'tip':
    case '小贴士':
      result = handleLifeTip(input);
      break;
      
    case 'translate':
    case '翻译':
      result = handleTranslation(input);
      break;
      
    case 'help':
    case '帮助':
      result = `中文日常生活助手 - 使用指南

可用命令：
1. 天气 [城市] - 查询城市天气
2. 汇率 [货币代码] CNY [金额] - 汇率换算
3. 节日 [节日名称] - 节日信息和倒计时
4. 小贴士 [类别] - 生活小贴士
5. 翻译 "文本" - 中英互译

示例：
天气 北京
汇率 USD CNY 100
节日 春节
小贴士 健康
翻译 "你好"`;
      break;
      
    default:
      result = `欢迎使用中文日常生活助手！请输入命令。\n输入"帮助"查看使用指南。`;
  }
  
  console.log(result);
}

// 执行主函数
if (require.main === module) {
  main();
}

module.exports = {
  handleWeather,
  handleExchange,
  handleFestival,
  handleLifeTip,
  handleTranslation,
  main
};