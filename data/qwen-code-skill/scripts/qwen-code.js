#!/usr/bin/env node

/**
 * Qwen Code CLI - OpenClaw Skill 工具
 * 基于官方文档：https://qwenlm.github.io/qwen-code-docs/zh/
 * 
 * @version 1.1.0-dev
 * @author UserB1ank
 * @repository https://github.com/UserB1ank/qwen-code-skill
 * 
 * 安装：npm install -g @qwen-code/qwen-code@latest
 * 认证：Qwen OAuth (免费) - 运行 qwen 后按提示登录
 */

const VERSION = '1.1.0-dev';

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const QWEN_DIR = path.join(process.env.HOME, '.qwen');
const SETTINGS_FILE = path.join(QWEN_DIR, 'settings.json');
const PROJECTS_DIR = path.join(QWEN_DIR, 'projects');

function qwenExists() {
  try {
    execSync('which qwen', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function checkNodeVersion() {
  try {
    const version = execSync('node -v', { encoding: 'utf8' }).trim();
    const major = parseInt(version.slice(1));
    return { ok: major >= 20, version };
  } catch {
    return { ok: false, version: '未安装' };
  }
}

function readSettings() {
  if (!fs.existsSync(SETTINGS_FILE)) return null;
  return JSON.parse(fs.readFileSync(SETTINGS_FILE, 'utf8'));
}

function isAuthenticated() {
  // Qwen Code 有两种认证方式：
  // 1. OAuth 认证（交互式登录）
  // 2. API Key（百炼 API，通过 BAILIAN_CODING_PLAN_API_KEY）
  
  const settings = readSettings();
  
  // 检查 OAuth 认证
  if (settings && (settings.auth || settings.accessToken)) {
    return { type: 'oauth', status: true };
  }
  
  // 检查 API Key 认证（百炼）
  if (settings && settings.env?.BAILIAN_CODING_PLAN_API_KEY) {
    const apiKey = settings.env.BAILIAN_CODING_PLAN_API_KEY;
    if (apiKey && apiKey.startsWith('sk-')) {
      return { type: 'apikey', status: true, prefix: apiKey.slice(0, 8) + '...' };
    }
  }
  
  return { type: 'none', status: false };
}

function getAvailableModels() {
  const settings = readSettings();
  if (!settings?.modelProviders?.openai) return [];
  return settings.modelProviders.openai.map(m => ({
    id: m.id,
    name: m.name,
    baseUrl: m.baseUrl
  }));
}

function getRecentSessions() {
  const cwd = process.cwd();
  const sanitizedCwd = cwd.replace(/[^a-zA-Z0-9]/g, '_');
  const chatsDir = path.join(PROJECTS_DIR, sanitizedCwd, 'chats');
  
  if (!fs.existsSync(chatsDir)) return [];
  
  try {
    const sessions = fs.readdirSync(chatsDir)
      .filter(f => f.endsWith('.json'))
      .map(f => {
        const stat = fs.statSync(path.join(chatsDir, f));
        return { name: f.replace('.json', ''), modified: stat.mtime };
      })
      .sort((a, b) => b.modified - a.modified);
    return sessions.slice(0, 5);
  } catch {
    return [];
  }
}

function showStatus() {
  console.log('📊 Qwen Code 状态检查\n');
  
  const nodeCheck = checkNodeVersion();
  console.log(`${nodeCheck.ok ? '✅' : '⚠️'} Node.js: ${nodeCheck.version}${!nodeCheck.ok ? ' (需要 20+)' : ''}`);
  
  const cliExists = qwenExists();
  console.log(`${cliExists ? '✅' : '❌'} Qwen Code CLI: ${cliExists ? '已安装' : '未安装'}`);
  
  const authResult = isAuthenticated();
  if (authResult.status) {
    if (authResult.type === 'oauth') {
      console.log('✅ 认证状态：已登录 (OAuth)');
    } else if (authResult.type === 'apikey') {
      console.log(`✅ 认证状态：已配置 (百炼 API Key: ${authResult.prefix})`);
    }
  } else {
    console.log('⚠️ 认证状态：未认证');
  }
  
  const models = getAvailableModels();
  if (models.length > 0) {
    console.log(`\n📦 已配置模型 (${models.length} 个):`);
    models.forEach(m => console.log(`   - ${m.id} (${m.name})`));
  }
  
  try {
    const extensions = execSync('qwen extensions list', { encoding: 'utf8', timeout: 5000 }).trim();
    console.log(`\n🔌 扩展：${extensions || '无'}`);
  } catch {
    console.log('\n🔌 扩展：无法获取');
  }
  
  const sessions = getRecentSessions();
  if (sessions.length > 0) {
    console.log(`\n💬 最近会话 (${sessions.length} 个):`);
    sessions.forEach(s => console.log(`   - ${s.name}`));
  }
  
  console.log('\n💡 提示:');
  if (!nodeCheck.ok) console.log('   升级 Node.js: https://nodejs.org/zh-cn/download');
  if (!cliExists) console.log('   安装：npm install -g @qwen-code/qwen-code@latest');
  if (!authResult.status && cliExists) {
    console.log('   认证方式 1: 运行 qwen 并按提示完成 OAuth 认证');
    console.log('   认证方式 2: 在 ~/.qwen/settings.json 中配置 BAILIAN_CODING_PLAN_API_KEY');
  }
  console.log('   VS Code 扩展：https://marketplace.visualstudio.com/items?itemName=qwenlm.qwen-code-vscode-ide-companion');
}

function runTask(task, options = {}) {
  if (!qwenExists()) {
    console.error('❌ Qwen Code CLI 未安装');
    console.error('   安装：npm install -g @qwen-code/qwen-code@latest');
    process.exit(1);
  }
  
  const authResult = isAuthenticated();
  if (!authResult.status) {
    console.error('❌ 未认证');
    console.error('   方式 1: 运行 qwen 完成 OAuth 认证');
    console.error('   方式 2: 在 ~/.qwen/settings.json 中配置 BAILIAN_CODING_PLAN_API_KEY');
    process.exit(1);
  }
  
  const args = [];
  if (options.model) args.push('-m', options.model);
  if (options.yolo) args.push('-y');
  if (options.sandbox) args.push('-s');
  if (options.approvalMode) args.push('--approval-mode', options.approvalMode);
  if (options.outputFormat) args.push('--output-format', options.outputFormat);
  if (options.debug) args.push('-d');
  if (options.continue) args.push('--continue');
  if (options.resume) args.push('--resume', options.resume);
  if (options.prompt) args.push('--prompt', task);
  else args.push(task);
  
  console.log(`🤖 运行 Qwen Code: qwen ${args.join(' ')}\n`);
  
  const proc = spawn('qwen', args, { stdio: 'inherit', env: { ...process.env } });
  proc.on('close', (code) => process.exit(code || 0));
}

function reviewFile(filePath, options = {}) {
  if (!fs.existsSync(filePath)) {
    console.error(`❌ 文件不存在：${filePath}`);
    process.exit(1);
  }
  
  const task = `请审查这个代码文件，指出：
- 潜在 bug
- 性能问题
- 代码风格问题
- 安全漏洞
- 改进建议

文件内容：
\`\`\`
${fs.readFileSync(filePath, 'utf8')}
\`\`\``;
  
  runTask(task, { ...options, model: options.model || 'qwen3-coder-plus' });
}

function mcpCommand(command, args = []) {
  if (!qwenExists()) {
    console.error('❌ Qwen Code CLI 未安装');
    process.exit(1);
  }
  
  const mcpArgs = ['mcp', command, ...args];
  console.log(`🔗 执行 MCP 命令：qwen ${mcpArgs.join(' ')}\n`);
  
  try {
    execSync(`qwen ${mcpArgs.join(' ')}`, { stdio: 'inherit' });
  } catch (error) {
    console.error('❌ 命令执行失败:', error.message);
    process.exit(1);
  }
}

function extensionsCommand(command, args = []) {
  if (!qwenExists()) {
    console.error('❌ Qwen Code CLI 未安装');
    process.exit(1);
  }
  
  const extArgs = ['extensions', command, ...args];
  console.log(`🔌 执行扩展命令：qwen ${extArgs.join(' ')}\n`);
  
  try {
    execSync(`qwen ${extArgs.join(' ')}`, { stdio: 'inherit' });
  } catch (error) {
    console.error('❌ 命令执行失败:', error.message);
    process.exit(1);
  }
}

function headlessMode(task, options = {}) {
  if (!qwenExists()) {
    console.error('❌ Qwen Code CLI 未安装');
    console.error('   安装：npm install -g @qwen-code/qwen-code@latest');
    process.exit(1);
  }
  
  const args = [];
  if (options.model) args.push('-m', options.model);
  if (options.outputFormat) args.push('--output-format', options.outputFormat);
  if (options.yolo) args.push('-y');
  if (options.approvalMode) args.push('--approval-mode', options.approvalMode);
  if (options.continue) args.push('--continue');
  if (options.resume) args.push('--resume', options.resume);
  args.push('--prompt', task);
  
  console.log(`📝 Headless 模式：qwen ${args.join(' ')}\n`);
  
  const proc = spawn('qwen', args, { stdio: 'inherit', env: { ...process.env } });
  proc.on('close', (code) => process.exit(code || 0));
}

function agentCommand(action, args = []) {
  if (!qwenExists()) {
    console.error('❌ Qwen Code CLI 未安装');
    process.exit(1);
  }
  
  let agentArgs = [];
  if (action === 'spawn' || action === 'create') {
    const agentName = args[0];
    const task = args.slice(1).join(' ');
    agentArgs = ['-i', `/agent spawn ${agentName} ${task}`];
  } else if (action === 'list') {
    agentArgs = ['-i', '/agents list'];
  } else {
    agentArgs = ['-i', `/agent ${action} ${args.join(' ')}`];
  }
  
  console.log(`🤖 执行 Agent 命令\n`);
  const proc = spawn('qwen', agentArgs, { stdio: 'inherit', env: { ...process.env } });
  proc.on('close', (code) => process.exit(code || 0));
}

function skillCommand(action, args = []) {
  const SKILLS_DIR = path.join(process.env.HOME, '.qwen/skills');
  
  if (action === 'list') {
    console.log('📚 已安装 Skills:\n');
    try {
      const skills = fs.readdirSync(SKILLS_DIR);
      if (skills.length === 0) {
        console.log('  暂无已安装的 skills');
      } else {
        skills.forEach(skill => console.log(`  - ${skill}`));
      }
    } catch {
      console.log('  Skills 目录不存在');
    }
  } else if (action === 'create') {
    const skillName = args[0];
    if (!skillName) {
      console.error('❌ 请提供 skill 名称');
      process.exit(1);
    }
    const skillDir = path.join(SKILLS_DIR, skillName);
    fs.mkdirSync(skillDir, { recursive: true });
    fs.writeFileSync(path.join(skillDir, 'README.md'), `# ${skillName} Skill\n\n描述：${skillName} 技能\n`);
    fs.writeFileSync(path.join(skillDir, 'index.js'), `// ${skillName} Skill\nmodule.exports = { name: '${skillName}', execute: async (ctx) => {} };\n`);
    console.log(`✅ Skill "${skillName}" 已创建在 ${skillDir}`);
  } else if (action === 'open') {
    const skillDir = path.join(SKILLS_DIR, args[0] || '.');
    console.log(`📂 ${skillDir}`);
  } else {
    console.error(`❌ 未知动作：${action}`);
    process.exit(1);
  }
}

function showVersion() {
  console.log(`qwen-code v${VERSION}`);
  console.log('');
  console.log('🦌 Qwen Code CLI - OpenClaw Skill');
  console.log('Repository: https://github.com/UserB1ank/qwen-code-skill');
  console.log('License: MIT');
}

function showHelp() {
  console.log(`
🦌 Qwen Code v${VERSION} - 官方 Qwen Code CLI 集成
文档：https://qwenlm.github.io/qwen-code-docs/zh/

安装:
  npm install -g @qwen-code/qwen-code@latest
  brew install qwen-code  # macOS/Linux

用法：qwen-code <command> [options]

命令:
  status              检查状态和配置
  version             显示版本信息
  run <task>          运行 Qwen Code 任务
  review <file>       代码审查
  headless <task>     Headless 模式（脚本化/自动化）
  agent <action>      Sub-Agent 管理
  skill <action>      Skills 管理
  mcp <cmd>           MCP 服务器管理
  extensions <cmd>    扩展管理
  sessions            列出最近会话
  help                显示帮助

选项:
  -m, --model         指定模型 (默认：qwen3-coder-plus)
  -y, --yolo          YOLO 模式（自动批准所有操作）
  -s, --sandbox       沙盒模式
  --approval-mode     审批模式 (plan|default|auto-edit|yolo)
  -o, --output-format 输出格式 (text|json|stream-json)
  -d, --debug         调试模式
  --continue          恢复当前项目的最近会话
  --resume <id>       恢复指定会话 ID
  -p, --prompt        提示词模式（headless 模式）

示例:
  # 基本用法
  qwen-code status
  qwen-code run "创建一个 Python Flask API"
  qwen-code run "创建 API" -m qwen3-coder-next
  
  # Headless 模式（自动化/CI/CD）
  qwen-code headless "分析代码" -o json
  qwen-code headless "生成 commit message" --continue
  git diff | qwen -p "生成 commit message"
  
  # 代码审查
  qwen-code review src/app.ts
  
  # Sub-Agents
  qwen-code agent spawn "代码审查员" 请审查这个模块
  qwen-code agent list
  
  # Skills
  qwen-code skill list
  qwen-code skill create "python-expert"
  
  # MCP (连接外部数据源)
  qwen-code mcp list
  qwen-code mcp add google-drive

  # 扩展管理
  qwen-code extensions list
  qwen-code extensions install <git-url>

可用模型:
  - qwen3.5-plus         通用编程
  - qwen3-coder-plus     复杂代码任务
  - qwen3-coder-next     轻量代码生成
  - qwen3-max            最强能力

自动化用例:
  git diff | qwen -p "生成 commit message"
  gh pr diff | qwen -p "审查此 PR"
  cat logs/app.log | qwen -p "分析错误原因"
  tail -f app.log | qwen -p "如果发现异常，Slack 通知我"

配置文件：~/.qwen/settings.json
会话数据：~/.qwen/projects/<cwd>/chats
VS Code 扩展：https://marketplace.visualstudio.com/items?itemName=qwenlm.qwen-code-vscode-ide-companion
`);
}

// 主程序
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'version':
  case '-v':
  case '--version':
    showVersion();
    break;
  case 'status':
    showStatus();
    break;
  case 'run':
    if (!args[1]) {
      console.error('❌ 请提供任务描述');
      process.exit(1);
    }
    runTask(args.slice(1).join(' '), {
      model: args.includes('-m') ? args[args.indexOf('-m') + 1] : null,
      yolo: args.includes('-y') || args.includes('--yolo'),
      sandbox: args.includes('-s') || args.includes('--sandbox'),
      debug: args.includes('-d') || args.includes('--debug'),
      approvalMode: args.includes('--approval-mode') ? args[args.indexOf('--approval-mode') + 1] : null,
      outputFormat: args.includes('-o') ? args[args.indexOf('-o') + 1] : (args.includes('--output-format') ? args[args.indexOf('--output-format') + 1] : null),
      continue: args.includes('--continue'),
      resume: args.includes('--resume') ? args[args.indexOf('--resume') + 1] : null
    });
    break;
  case 'review':
    if (!args[1]) {
      console.error('❌ 请提供文件路径');
      process.exit(1);
    }
    reviewFile(args[1], {
      model: args.includes('-m') ? args[args.indexOf('-m') + 1] : 'qwen3-coder-plus'
    });
    break;
  case 'headless':
    if (!args[1]) {
      console.error('❌ 请提供任务描述');
      process.exit(1);
    }
    headlessMode(args.slice(1).join(' '), {
      model: args.includes('-m') ? args[args.indexOf('-m') + 1] : null,
      outputFormat: args.includes('-o') ? args[args.indexOf('-o') + 1] : (args.includes('--output-format') ? args[args.indexOf('--output-format') + 1] : null),
      yolo: args.includes('-y'),
      approvalMode: args.includes('--approval-mode') ? args[args.indexOf('--approval-mode') + 1] : null,
      continue: args.includes('--continue'),
      resume: args.includes('--resume') ? args[args.indexOf('--resume') + 1] : null
    });
    break;
  case 'agent':
    if (!args[1]) {
      console.error('❌ 请提供 agent 动作');
      process.exit(1);
    }
    agentCommand(args[1], args.slice(2));
    break;
  case 'skill':
    if (!args[1]) {
      console.error('❌ 请提供 skill 动作');
      process.exit(1);
    }
    skillCommand(args[1], args.slice(2));
    break;
  case 'mcp':
    if (!args[1]) {
      console.error('❌ 请提供 MCP 命令');
      process.exit(1);
    }
    mcpCommand(args[1], args.slice(2));
    break;
  case 'extensions':
    if (!args[1]) {
      console.error('❌ 请提供扩展命令');
      process.exit(1);
    }
    extensionsCommand(args[1], args.slice(2));
    break;
  case 'sessions':
    showStatus(); // 复用 status 显示会话列表
    break;
  case 'help':
  case '--help':
  case '-h':
  default:
    showHelp();
}
