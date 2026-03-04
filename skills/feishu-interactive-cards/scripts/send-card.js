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
    console.error('⚠️ 无法读取 OpenClaw 配置:', error.message);
  }
  
  return null;
}

// 获取租户访问令牌
async function getTenantAccessToken(appId, appSecret) {
  const response = await axios.post(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    { app_id: appId, app_secret: appSecret }
  );
  return response.data.tenant_access_token;
}

// 发送卡片到指定 chat_id
async function sendCardToChatId(appId, appSecret, chatId, card) {
  const token = await getTenantAccessToken(appId, appSecret);
  const response = await axios.post(
    'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
    {
      receive_id: chatId,
      msg_type: 'interactive',
      content: JSON.stringify(card)
    },
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8'
      }
    }
  );
  return response.data;
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  // 解析命令行参数
  let cardType = 'confirmation';
  let message = '';
  let chatId = '';
  let templatePath = '';
  let options = [];
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--chat-id') {
      chatId = args[++i];
    } else if (args[i] === '--template') {
      templatePath = args[++i];
    } else if (args[i] === '--options') {
      options = args[++i].split(',');
    } else if (!cardType || cardType === 'confirmation') {
      if (i === 0) {
        cardType = args[i];
      } else {
        message = args[i];
      }
    } else {
      message = args[i];
    }
  }
  
  // 验证必填参数
  if (!chatId) {
    console.error('❌ 缺少必填参数: --chat-id');
    console.log('\n用法:');
    console.log('  node send-card.js confirmation "消息内容" --chat-id oc_xxx');
    console.log('  node send-card.js todo --chat-id oc_xxx');
    console.log('  node send-card.js poll "投票标题" --options "选项1,选项2,选项3" --chat-id oc_xxx');
    console.log('  node send-card.js custom --template path/to/card.json --chat-id oc_xxx');
    process.exit(1);
  }
  
  // 加载配置
  const config = loadFeishuConfig();
  if (!config) {
    console.error('❌ 无法加载飞书配置，请检查 ~/.openclaw/openclaw.json');
    process.exit(1);
  }
  
  let card;
  
  // 根据类型生成卡片
  if (cardType === 'custom' && templatePath) {
    // 自定义卡片 - 安全验证
    // ⚠️ SECURITY: 防止任意文件读取攻击
    
    // 1. 规范化路径
    const resolvedPath = path.resolve(templatePath);
    
    // 2. 定义允许的模板目录
    const skillRoot = path.resolve(__dirname, '..');
    const allowedDirs = [
      path.join(skillRoot, 'examples'),
      path.join(skillRoot, 'templates'),
      path.join(process.cwd(), 'templates'),
      path.join(process.cwd(), 'examples')
    ];
    
    // 3. 检查路径是否在允许的目录内
    const isAllowed = allowedDirs.some(dir => resolvedPath.startsWith(dir));
    
    if (!isAllowed) {
      console.error('❌ 安全错误: 模板文件必须位于以下目录之一:');
      allowedDirs.forEach(dir => console.error(`  - ${dir}`));
      console.error(`\n尝试访问: ${resolvedPath}`);
      process.exit(1);
    }
    
    // 4. 检查文件扩展名
    const ext = path.extname(resolvedPath).toLowerCase();
    if (ext !== '.json') {
      console.error('❌ 安全错误: 模板文件必须是 .json 格式');
      process.exit(1);
    }
    
    // 5. 检查文件是否存在
    if (!fs.existsSync(resolvedPath)) {
      console.error('❌ 文件不存在:', resolvedPath);
      process.exit(1);
    }
    
    // 6. 读取并验证 JSON 格式
    try {
      const content = fs.readFileSync(resolvedPath, 'utf8');
      card = JSON.parse(content);
      
      // 验证是否是有效的飞书卡片格式
      if (!card.elements && !card.header) {
        console.error('❌ 无效的卡片格式: 缺少 elements 或 header 字段');
        process.exit(1);
      }
    } catch (error) {
      console.error('❌ 无效的 JSON 格式:', error.message);
      process.exit(1);
    }
  } else if (cardType === 'confirmation') {
    // 确认卡片
    const CardTemplates = require('./card-templates');
    card = CardTemplates.createConfirmationCard(message || '确认此操作？');
  } else if (cardType === 'todo') {
    // TODO 卡片
    const examplePath = path.join(__dirname, '..', 'examples', 'todo-card.json');
    card = JSON.parse(fs.readFileSync(examplePath, 'utf8'));
  } else if (cardType === 'poll') {
    // 投票卡片
    const CardTemplates = require('./card-templates');
    card = CardTemplates.createPollCard(message || '请投票', options);
  } else if (cardType === 'form') {
    // 表单卡片
    const examplePath = path.join(__dirname, '..', 'examples', 'form-card.json');
    card = JSON.parse(fs.readFileSync(examplePath, 'utf8'));
  } else {
    console.error('❌ 未知的卡片类型:', cardType);
    console.log('支持的类型: confirmation, todo, poll, form, custom');
    process.exit(1);
  }
  
  // 发送卡片
  try {
    const result = await sendCardToChatId(config.appId, config.appSecret, chatId, card);
    console.log('✅ 卡片发送成功！');
    console.log('Message ID:', result.data?.message_id);
    console.log('Chat ID:', chatId);
  } catch (error) {
    console.error('❌ 发送失败:', error.response?.data || error.message);
    process.exit(1);
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 错误:', error);
    process.exit(1);
  });
}

module.exports = { sendCardToChatId, getTenantAccessToken };
