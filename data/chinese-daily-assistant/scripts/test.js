#!/usr/bin/env node

/**
 * 测试脚本 - 验证所有功能
 */

const { 
  handleWeather, 
  handleExchange, 
  handleFestival, 
  handleLifeTip, 
  handleTranslation 
} = require('./main.js');

console.log('🧪 中文日常生活助手 - 功能测试\n');

// 测试天气查询
console.log('1. 天气查询测试:');
console.log(handleWeather('北京'));
console.log(handleWeather('上海'));
console.log(handleWeather('未知城市'));
console.log();

// 测试汇率换算
console.log('2. 汇率换算测试:');
console.log(handleExchange(''));
console.log(handleExchange('USD CNY 100'));
console.log(handleExchange('CNY USD 720'));
console.log();

// 测试节日查询
console.log('3. 节日查询测试:');
console.log(handleFestival(''));
console.log(handleFestival('春节'));
console.log(handleFestival('未知节日'));
console.log();

// 测试生活小贴士
console.log('4. 生活小贴士测试:');
console.log(handleLifeTip(''));
console.log(handleLifeTip('健康'));
console.log(handleLifeTip('未知类别'));
console.log();

// 测试翻译
console.log('5. 翻译测试:');
console.log(handleTranslation('你好'));
console.log(handleTranslation('Hello'));
console.log(handleTranslation('未知词汇'));
console.log();

console.log('✅ 所有功能测试完成！');