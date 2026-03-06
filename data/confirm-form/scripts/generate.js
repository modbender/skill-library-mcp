#!/usr/bin/env node
/**
 * 生成确认表单并上传到 Gist
 * 
 * 用法：
 *   node generate.js questions.json
 *   node generate.js --stdin < questions.json
 *   echo '[{...}]' | node generate.js --stdin
 * 
 * 选项：
 *   --auto-notify  使用自动通知模板（v2），提交后自动通知
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const crypto = require('crypto');

const TEMPLATE_V1 = path.join(__dirname, '..', 'assets', 'template.html');
const TEMPLATE_V2 = path.join(__dirname, '..', 'assets', 'template-v2.html');
const OUTPUT_DIR = path.join(__dirname, '..', 'output');
const GITHUB_USER = 'xiaozhuang0127';

async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('readable', () => {
      let chunk;
      while (chunk = process.stdin.read()) {
        data += chunk;
      }
    });
    process.stdin.on('end', () => resolve(data));
  });
}

async function main() {
  const args = process.argv.slice(2);
  const autoNotify = args.includes('--auto-notify');
  const filteredArgs = args.filter(a => !a.startsWith('--'));
  
  let questionsJson;
  
  if (args.includes('--stdin')) {
    questionsJson = await readStdin();
  } else if (filteredArgs[0] && fs.existsSync(filteredArgs[0])) {
    questionsJson = fs.readFileSync(filteredArgs[0], 'utf-8');
  } else if (filteredArgs[0]) {
    questionsJson = filteredArgs[0];
  } else {
    console.error('用法: node generate.js <questions.json | --stdin> [--auto-notify]');
    process.exit(1);
  }
  
  let questions;
  try {
    questions = JSON.parse(questionsJson);
  } catch (e) {
    console.error('JSON 解析失败:', e.message);
    process.exit(1);
  }
  
  if (!Array.isArray(questions) || questions.length === 0) {
    console.error('问题列表必须是非空数组');
    process.exit(1);
  }
  
  // 验证
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    if (!q.title) {
      console.error(`问题 ${i + 1} 缺少 title`);
      process.exit(1);
    }
    if (!q.options || !Array.isArray(q.options) || q.options.length < 2) {
      console.error(`问题 ${i + 1} 的 options 必须是至少包含2个选项的数组`);
      process.exit(1);
    }
  }
  
  // 选择模板
  const templatePath = autoNotify ? TEMPLATE_V2 : TEMPLATE_V1;
  const template = fs.readFileSync(templatePath, 'utf-8');
  
  // 生成 ID
  const now = new Date();
  const formId = `form-${now.toISOString().slice(0, 10).replace(/-/g, '')}-${now.toISOString().slice(11, 19).replace(/:/g, '')}`;
  const timestamp = now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  const notifyTopic = `clawd-form-${crypto.randomBytes(6).toString('hex')}`;
  
  // 替换
  let html = template
    .replace('{{QUESTIONS_JSON}}', JSON.stringify(questions, null, 2))
    .replace('{{TIMESTAMP}}', timestamp)
    .replace('{{QUESTION_COUNT}}', questions.length.toString())
    .replace('{{FORM_ID}}', formId)
    .replace('{{NOTIFY_TOPIC}}', notifyTopic);
  
  // 输出
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
  
  const outputFile = path.join(OUTPUT_DIR, `${formId}.html`);
  fs.writeFileSync(outputFile, html);
  console.log(`本地文件: ${outputFile}`);
  
  // 上传 Gist
  try {
    const gistResult = execSync(
      `gh gist create "${outputFile}" --desc "确认表单 ${formId}" --public`,
      { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    ).trim();
    
    const gistId = gistResult.split('/').pop();
    const filename = path.basename(outputFile);
    const previewUrl = `https://htmlpreview.github.io/?https://gist.githubusercontent.com/${GITHUB_USER}/${gistId}/raw/${filename}`;
    
    console.log(`\nGist: ${gistResult}`);
    console.log(`\n🔗 访问链接:`);
    console.log(previewUrl);
    
    const result = {
      success: true,
      formId: formId,
      localFile: outputFile,
      gistUrl: gistResult,
      gistId: gistId,
      previewUrl: previewUrl,
      questionCount: questions.length,
      autoNotify: autoNotify,
      notifyTopic: autoNotify ? notifyTopic : null,
      checkCommand: autoNotify ? `curl -s "https://ntfy.sh/${notifyTopic}/json?poll=1"` : null
    };
    
    console.log(`\n📋 结果 JSON:`);
    console.log(JSON.stringify(result, null, 2));
    
  } catch (e) {
    console.error('\n上传 Gist 失败:', e.message);
    const result = {
      success: false,
      formId: formId,
      localFile: outputFile,
      error: e.message,
      questionCount: questions.length
    };
    console.log(JSON.stringify(result, null, 2));
  }
}

main();
