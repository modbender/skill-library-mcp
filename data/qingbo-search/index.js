const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const fetch = require('node-fetch');

// 配置文件路径
const configPath = path.join(__dirname, 'config.json');

// 读取配置
function readConfig() {
  try {
    const configData = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(configData);
  } catch (error) {
    console.error('读取配置文件失败:', error);
    return null;
  }
}

// 生成MD5签名
function generateSign(params, appSecret) {
  // 按参数名排序
  const sortedParams = Object.keys(params).sort().reduce((result, key) => {
    result[key] = params[key];
    return result;
  }, {});

  // 构造字符串A
  let stringA = '_';
  for (const [key, value] of Object.entries(sortedParams)) {
    stringA += key + value;
  }
  stringA += '_';

  // 构造字符串B
  const stringB = appSecret + stringA + appSecret;

  // 计算MD5哈希值
  const sign = crypto.createHash('md5').update(stringB).digest('hex');
  return sign;
}

// 生成access-token
function generateAccessToken(appKey, sign, router) {
  const tokenContent = `${appKey}:${sign}:${router}`;
  return Buffer.from(tokenContent).toString('base64');
}

// 调用关键词检索文章接口
async function searchArticles(params) {
  const config = readConfig();
  if (!config || !config.app_key || !config.app_secret) {
    throw new Error('请先在config.json中配置app_key和app_secret');
  }

  const router = '/pubsent/full-search/index';
  const baseUrl = 'http://databus.gsdata.cn:8888/api/service';

  // 生成签名
  const sign = generateSign(params, config.app_secret);

  // 生成access-token
  const accessToken = generateAccessToken(config.app_key, sign, router);

  // 构造查询字符串
  const queryString = new URLSearchParams(params).toString();
  const url = `${baseUrl}?${queryString}`;

  // 发送请求
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'access-token': accessToken
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP错误! 状态: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API调用失败:', error);
    throw new Error('无法连接到清博开放平台API');
  }
}

// 分析用户输入并提取参数
function analyzeInput(input) {
  const params = {};

  // 提取关键词
  const keywordPattern1 = /(?:搜索|查找|查询)?\s*(?:关于|有关)?\s*([^\s，。]+?)(?:的文章|的新闻|相关内容|的舆情|的信息)/;
  let keywordMatch = input.match(keywordPattern1);
  
  if (!keywordMatch) {
    const keywordPattern2 = /(?:最近|近|过去)?\s*(?:一周|一个星期|两周|一个月|三个月|半年|一年)\s*(?:的)?\s*([^\s，。]+?)(?:的|相关)/;
    keywordMatch = input.match(keywordPattern2);
  }
  
  if (!keywordMatch) {
    const keywordPattern3 = /([^\s，。]+?)(?:的|相关)(?:文章|新闻|内容|舆情|信息)/;
    keywordMatch = input.match(keywordPattern3);
  }
  
  if (!keywordMatch) {
    // 简单匹配：提取主要名词
    const nounPattern = /(?:小米|华为|苹果|腾讯|阿里|百度|字节跳动|京东|网易|拼多多|美团|滴滴|快手|抖音|微博|微信|B站|小红书|爱奇艺|腾讯视频|今日头条|抖音火山版|西瓜视频|淘宝|天猫|拼多多|京东|苏宁易购|唯品会|网易严选|小红书|美团外卖|饿了么|滴滴出行|高德地图|百度地图|携程旅游|同程旅行|飞猪旅行|去哪儿网|马蜂窝|途牛旅游|驴妈妈旅游|汽车之家|懂车帝|易车网|瓜子二手车|优信二手车|人人车|毛豆新车|坦克|蔚来|小鹏|理想|特斯拉|比亚迪|奇瑞|吉利|长安|长城|广汽|上汽|一汽|东风|北汽|江淮|华晨|东南|海马|众泰|力帆|陆风|北汽幻速|北汽绅宝|昌河|金杯|福田|解放|东风柳汽|重汽|陕汽|红岩|北奔|华菱|大运|徐工|临工|柳工|龙工|厦工|山推|卡特彼勒|小松|日立|神钢|住友|加藤|沃尔沃|斗山|现代|利勃海尔|特雷克斯|杰西博|约翰迪尔|久保田|洋马|石川岛|竹内|卡特彼勒|小松|日立|神钢|住友|加藤|沃尔沃|斗山|现代|利勃海尔|特雷克斯|杰西博|约翰迪尔|久保田|洋马|石川岛|竹内|三一|徐工|中联重科|柳工|龙工|厦工|山推|玉柴|潍柴|上柴|锡柴|大柴|朝柴|扬柴|云内|全柴|莱动|常柴|江铃|庆铃|福田康明斯|东风康明斯|西安康明斯|重庆康明斯|潍柴动力|玉柴机器|上柴动力|锡柴动力|大柴动力|朝柴动力|扬柴动力|云内动力|全柴动力|莱动动力|常柴动力|江铃动力|庆铃动力|福田康明斯动力|东风康明斯动力|西安康明斯动力|重庆康明斯动力|)汽车/;
    keywordMatch = input.match(nounPattern);
  }
  
  if (keywordMatch) {
    params.keywords_include = keywordMatch[1];
  }

  // 提取时间范围
  if (input.includes('最近一周') || input.includes('近一周') || input.includes('过去一周')) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
    params.posttime_start = formatDate(startDate);
    params.posttime_end = formatDate(endDate);
  } else if (input.includes('最近两周') || input.includes('近两周') || input.includes('过去两周')) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 14 * 24 * 60 * 60 * 1000);
    params.posttime_start = formatDate(startDate);
    params.posttime_end = formatDate(endDate);
  } else if (input.includes('最近一个月') || input.includes('近一个月') || input.includes('过去一个月')) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
    params.posttime_start = formatDate(startDate);
    params.posttime_end = formatDate(endDate);
  } else if (input.includes('最近三个月') || input.includes('近三个月') || input.includes('过去三个月')) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 90 * 24 * 60 * 60 * 1000);
    params.posttime_start = formatDate(startDate);
    params.posttime_end = formatDate(endDate);
  } else if (input.includes('最近半年') || input.includes('近半年') || input.includes('过去半年')) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 180 * 24 * 60 * 60 * 1000);
    params.posttime_start = formatDate(startDate);
    params.posttime_end = formatDate(endDate);
  } else if (input.includes('最近一年') || input.includes('近一年') || input.includes('过去一年')) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 365 * 24 * 60 * 60 * 1000);
    params.posttime_start = formatDate(startDate);
    params.posttime_end = formatDate(endDate);
  } else {
    const timePattern = /(\d{4}年)?(\d{1,2}月)?(\d{1,2}日)?/g;
    const timeMatches = [...input.matchAll(timePattern)].filter(match => match[0]);
    if (timeMatches.length > 0) {
      // 处理时间范围
      if (timeMatches.length === 2) {
        // 有开始和结束时间
        params.posttime_start = formatTime(timeMatches[0][0]);
        params.posttime_end = formatTime(timeMatches[1][0]);
      } else if (timeMatches.length === 1) {
        // 只有一个时间
        const timeStr = timeMatches[0][0];
        if (timeStr.includes('年') && timeStr.includes('月')) {
          // 年月格式
          params.posttime_start = timeStr + '01日';
          params.posttime_end = timeStr + getDaysInMonth(parseInt(timeStr.match(/\d{4}年/)[0]), parseInt(timeStr.match(/\d{1,2}月/)[0])) + '日';
        } else if (timeStr.includes('年')) {
          // 年份格式
          params.posttime_start = timeStr + '01月01日';
          params.posttime_end = timeStr + '12月31日';
        }
      }
    }
  }

  // 提取媒体平台
  if (input.includes('微信')) params.media_type = 'wx';
  if (input.includes('微博')) params.media_type = 'weibo'; // 注意：清博接口中的微博类型为weibo
  if (input.includes('新闻网站')) params.media_type = 'web';
  if (input.includes('新闻客户端')) params.media_type = 'app';
  if (input.includes('报刊')) params.media_type = 'journal';
  if (input.includes('论坛')) params.media_type = 'forum';
  if (input.includes('头条') || input.includes('今日头条')) params.media_type = 'toutiao';

  // 提取情感属性
  if (input.includes('正面') || input.includes('积极')) params.news_emotion = 'positive';
  if (input.includes('负面') || input.includes('消极')) params.news_emotion = 'negative';
  if (input.includes('中性')) params.news_emotion = 'neutral';
  if (input.includes('敏感')) params.news_emotion = 'sensitive';

  return params;
}

// 格式化时间字符串
function formatTime(timeStr) {
  let formattedTime = timeStr;
  // 补充完整日期格式
  if (formattedTime.includes('年') && !formattedTime.includes('月')) {
    formattedTime += '01月01日';
  } else if (formattedTime.includes('年') && formattedTime.includes('月') && !formattedTime.includes('日')) {
    formattedTime += '01日';
  }

  // 转换为YYYY-MM-DD格式
  const year = formattedTime.match(/(\d{4})年/);
  const month = formattedTime.match(/(\d{1,2})月/);
  const day = formattedTime.match(/(\d{1,2})日/);

  if (year && month && day) {
    return `${year[1]}-${month[1].padStart(2, '0')}-${day[1].padStart(2, '0')} 00:00:00`;
  } else if (year && month) {
    return `${year[1]}-${month[1].padStart(2, '0')}-01 00:00:00`;
  } else if (year) {
    return `${year[1]}-01-01 00:00:00`;
  }

  return null;
}

// 格式化日期为 YYYY-MM-DD HH:MM:SS 格式
function formatDate(date) {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 获取指定月份的天数
function getDaysInMonth(yearStr, monthStr) {
  const year = parseInt(yearStr.replace('年', ''));
  const month = parseInt(monthStr.replace('月', ''));
  return new Date(year, month, 0).getDate();
}

// 处理查询结果
function processResult(data, input) {
  if (!data.success) {
    return `查询失败: ${data.msg}`;
  }

  if (data.data && data.data.newsList && data.data.newsList.length > 0) {
    // 判断用户是否需要统计信息
    if (input.includes('统计') || input.includes('数量') || input.includes('分析')) {
      return `共找到 ${data.data.numFound} 篇相关文章。`;
    } else {
      // 返回文章列表
      let result = '';
      data.data.newsList.forEach((news, index) => {
        result += `${index + 1}. ${news.news_title}\n`;
        result += `   发布时间: ${news.news_posttime}\n`;
        result += `   媒体平台: ${getMediaTypeLabel(news.media_type)}\n`;
        result += `   文章链接: ${news.news_url}\n`;
        result += `   情感属性: ${getEmotionLabel(news.news_emotion)}\n\n`;
      });
      return result;
    }
  } else {
    return '未找到相关文章。';
  }
}

// 获取媒体类型标签
function getMediaTypeLabel(mediaType) {
  const mediaLabels = {
    'wx': '微信',
    'weibo': '微博',
    'web': '新闻网站',
    'app': '新闻客户端',
    'journal': '报刊',
    'forum': '论坛',
    'toutiao': '今日头条'
  };
  return mediaLabels[mediaType] || mediaType;
}

// 获取情感属性标签
function getEmotionLabel(emotion) {
  const emotionLabels = {
    'positive': '正面',
    'negative': '负面',
    'neutral': '中性',
    'sensitive': '敏感'
  };
  return emotionLabels[emotion] || emotion;
}

// 主函数
async function main(input) {
  try {
    // 分析用户输入
    const params = analyzeInput(input);
    console.log('提取到的查询参数:', params);

    if (!params.keywords_include) {
      return '您没有提供查询关键词，请包含关键词后再尝试。';
    }

    // 调用搜索接口
    const response = await searchArticles(params);
    console.log('API响应:', response);

    // 处理结果
    const result = processResult(response, input);
    return result;
  } catch (error) {
    console.error('处理查询失败:', error);
    return `查询处理失败: ${error.message}`;
  }
}

// 导出
module.exports = {
  main,
  analyzeInput,
  searchArticles,
  processResult
};
