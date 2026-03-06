#!/usr/bin/env node
/**
 * 飞书 Skill 全面测试脚本
 * 测试 feishu skill 的核心 API 能力
 */

const path = require('path');
const { pathToFileURL } = require('url');
const FEISHU_APP_ID = process.env.FEISHU_APP_ID;
const FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET;
const CHAT_ID = process.env.FEISHU_CHAT_ID;

if (!FEISHU_APP_ID || !FEISHU_APP_SECRET) {
  console.warn('⚠️  未检测到 FEISHU_APP_ID/FEISHU_APP_SECRET，部分测试可能失败');
}

// 测试结果汇总
const testResults = {
  passed: [],
  failed: [],
  skipped: []
};

function log(title, content = '') {
  console.log(`\n${'='.repeat(60)}`);
  console.log(title);
  if (content) console.log(content);
  console.log('='.repeat(60));
}

const FEISHU_SKILL_PATH = path.join(__dirname, '..', 'dist', 'index.js');
let feishuModule = null;

async function loadFeishu() {
  if (!feishuModule) {
    feishuModule = await import(pathToFileURL(FEISHU_SKILL_PATH).href);
  }
  return feishuModule;
}

async function testFeishuThreads() {
  log('📌 测试 feishu/im (threads)');
  
  try {
    const { replyInThread, listThreadMessages } = await loadFeishu();
    
    // 测试话题回复
    console.log('\n1️⃣ 测试 replyInThread()');
    try {
      const result = await replyInThread(
        'om_x100b576b02de30a4c12251694065fa0',
        '✅ feishu (im/threads) 测试成功！\n🦐 虾宝宝已掌握话题回复能力'
      );
      
      if (result.ok) {
        console.log('✅ 话题回复成功！');
        console.log('  消息ID:', result.data?.message_id);
        console.log('  话题ID:', result.data?.thread_id);
        testResults.passed.push('feishu (im/threads): replyInThread');
      } else {
        throw new Error(result.error || '未知错误');
      }
    } catch (err) {
      console.log('❌ 话题回复失败:', err.message);
      testResults.failed.push(`feishu (im/threads): replyInThread - ${err.message}`);
    }
    
    // 测试获取话题消息列表
    console.log('\n2️⃣ 测试 listThreadMessages()');
    try {
      // 注意：这个函数需要在话题中才能测试
      console.log('⏭️  跳过：需要在已有话题中测试');
      testResults.skipped.push('feishu (im/threads): listThreadMessages');
    } catch (err) {
      console.log('❌ 获取话题消息失败:', err.message);
      testResults.failed.push(`feishu (im/threads): listThreadMessages - ${err.message}`);
    }
    
  } catch (err) {
    console.error('❌ feishu 模块加载失败:', err.message);
    testResults.failed.push(`feishu (im/threads): 模块加载 - ${err.message}`);
  }
}

async function testFeishuMessages() {
  log('📌 测试 feishu/im (messages)');
  
  try {
    const { 
      listMessages, 
      recallMessage, 
      updateMessage, 
      pinMessage, 
      unpinMessage 
    } = await loadFeishu();
    
    // 1. 测试获取消息列表
    console.log('\n1️⃣ 测试 listMessages()');
    try {
      const result = await listMessages({
        container_id: CHAT_ID,
        container_id_type: 'chat',
        page_size: 10
      });
      
      if (result.ok) {
        console.log('✅ 获取消息列表成功！');
        console.log('  消息数量:', result.data?.items?.length || 0);
        testResults.passed.push('feishu (im/messages): listMessages');
      } else {
        throw new Error(result.error || '未知错误');
      }
    } catch (err) {
      console.log('❌ 获取消息列表失败:', err.message);
      if (err.response?.data?.msg?.includes('scope')) {
        console.log('   💡 原因: 缺少必要的权限 scope');
      }
      testResults.failed.push(`feishu (im/messages): listMessages - ${err.message}`);
    }
    
    // 2. 测试撤回消息
    console.log('\n2️⃣ 测试 recallMessage()');
    console.log('⏭️  跳过：需要真实消息ID，避免误删');
    testResults.skipped.push('feishu (im/messages): recallMessage');
    
    // 3. 测试更新消息
    console.log('\n3️⃣ 测试 updateMessage()');
    console.log('⏭️  跳过：需要真实消息ID，避免误改');
    testResults.skipped.push('feishu (im/messages): updateMessage');
    
    // 4. 测试置顶消息
    console.log('\n4️⃣ 测试 pinMessage()');
    console.log('⏭️  跳过：需要真实消息ID，避免误操作');
    testResults.skipped.push('feishu (im/messages): pinMessage');
    
    // 5. 测试取消置顶
    console.log('\n5️⃣ 测试 unpinMessage()');
    console.log('⏭️  跳过：需要真实置顶ID，避免误操作');
    testResults.skipped.push('feishu (im/messages): unpinMessage');
    
  } catch (err) {
    console.error('❌ feishu 模块加载失败:', err.message);
    testResults.failed.push(`feishu (im/messages): 模块加载 - ${err.message}`);
  }
}

async function runAllTests() {
  console.log('\n');
  console.log('🦐 飞书 Skill 全面测试开始');
  console.log('时间:', new Date().toLocaleString());
  console.log('群ID:', CHAT_ID);
  console.log('');
  
  // 运行所有测试
  await testFeishuThreads();
  await testFeishuMessages();
  
  // 输出测试报告
  log('📊 测试报告汇总');
  
  console.log('\n✅ 通过:', testResults.passed.length);
  testResults.passed.forEach(item => console.log('   ✓', item));
  
  console.log('\n❌ 失败:', testResults.failed.length);
  testResults.failed.forEach(item => console.log('   ✗', item));
  
  console.log('\n⏭️  跳过:', testResults.skipped.length);
  testResults.skipped.forEach(item => console.log('   -', item));
  
  console.log('\n');
  console.log('测试完成！🦐');
}

// 运行测试
runAllTests().catch(err => {
  console.error('测试运行失败:', err);
  process.exit(1);
});
