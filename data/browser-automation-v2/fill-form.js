#!/usr/bin/env node

/**
 * 表单填写自动化：支持通用表单（自动清理）- v2
 * 用法: node fill-form.js "https://example.com/form" '{"username":"test","email":"test@example.com"}'
 */

const BrowserManager = require('./browser-manager.v2');

const [url, fieldsJson] = process.argv.slice(2);

if (!url || !fieldsJson) {
  console.error('❌ 参数错误');
  console.log('用法: node fill-form.js "https://example.com/form" \'{"username":"test","email":"test@example.com"}\'');
  process.exit(1);
}

let fields;
try {
  fields = JSON.parse(fieldsJson);
} catch (e) {
  console.error('❌ JSON 格式错误:', e.message);
  process.exit(1);
}

async function main() {
  const browser = new BrowserManager();
  
  try {
    console.log(`📝 填写表单: ${url}`);
    console.log('字段:', fields);
    
    await browser.start();
    await browser.open(url);
    await browser.waitForLoadState('domcontentloaded', 10000);
    
    // 获取快照寻找输入框
    const snapshot = await browser.snapshot('ai', 200);
    const lines = snapshot.split('\n');
    const refs = {};
    
    // 解析所有 textbox 和对应 ref
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const textboxMatch = line.match(/textbox[^\n]*\[ref=(e\d+)\]/i);
      if (textboxMatch) {
        const ref = textboxMatch[1];
        const context = line + (lines[i+1] || '');
        for (const [fieldName, value] of Object.entries(fields)) {
          const keywords = [fieldName.toLowerCase(), fieldName.toUpperCase()];
          if (keywords.some(kw => context.toLowerCase().includes(kw))) {
            refs[fieldName] = ref;
            break;
          }
        }
      }
    }
    
    console.log('🔍 识别到字段映射:', refs);
    
    // 填充字段
    let completed = 0;
    const total = Object.keys(fields).length;
    
    for (const [fieldName, value] of Object.entries(fields)) {
      const ref = refs[fieldName];
      if (!ref) {
        console.warn(`⚠️ 未找到字段 "${fieldName}" 的输入框`);
        completed++;
        if (completed === total) finish();
        continue;
      }
      
      await browser.type(ref, value);
      // 使用智能等待确保输入完成
      await browser.waitForSelector(ref, 2000);
      completed++;
      if (completed === total) finish();
    }
    
    function finish() {
      console.log('\n🎉 表单填写完成！');
      console.log('💡 提示: 可能需要手动点击提交按钮，或使用 browser click <ref> 自动提交');
      browser.cleanup();
    }
    
  } catch (e) {
    browser.logger.error('表单填写失败', { error: e.message });
    await browser.cleanup();
    process.exit(1);
  }
}

main();
