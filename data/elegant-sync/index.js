#!/usr/bin/env node
/**
 * Elegant Sync - 优雅安全的 OpenClaw 同步工具
 * 
 * 功能:
 * - 版本化备份
 * - .gitignore 规则
 * - 选择性同步
 * - 灾难恢复
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const os = require('os');

// 配置
const HOME = os.homedir();
const OPENCLAW_DIR = path.join(HOME, '.openclaw');
const WORKSPACE_DIR = path.join(OPENCLAW_DIR, 'workspace');
const STAGING_DIR = path.join(OPENCLAW_DIR, '.elegant-sync-staging');
const LOCAL_BACKUP_DIR = path.join(OPENCLAW_DIR, '.local-backup');

// 获取 Instance ID（用于多实例备份）
function getInstanceId() {
  // 优先使用配置的 INSTANCE_ID
  const envFile = path.join(OPENCLAW_DIR, '.backup.env');
  if (fs.existsSync(envFile)) {
    const content = fs.readFileSync(envFile, 'utf8');
    const match = content.match(/INSTANCE_ID=(.+)/);
    if (match) return match[1].trim();
  }
  // 默认使用主机名
  return os.hostname();
}

// 颜色
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(msg, color = 'reset') {
  console.log(`${colors[color]}${msg}${colors.reset}`);
}

function error(msg) {
  console.error(`${colors.red}❌ ${msg}${colors.reset}`);
  process.exit(1);
}

// 加载配置
function loadConfig() {
  const envFile = path.join(OPENCLAW_DIR, '.backup.env');
  if (!fs.existsSync(envFile)) {
    // 首次配置：提示用户输入
    const hostname = os.hostname();
    log('🔧 首次配置 Elegant Sync', 'cyan');
    log(`当前主机名: ${hostname}`);
    log('');
    log('请在 ~/.openclaw/.backup.env 中配置:');
    log('  BACKUP_REPO=https://github.com/你的用户名/仓库名');
    log('  BACKUP_TOKEN=ghp_你的token');
    log('  INSTANCE_ID=' + hostname + '  # 或自定义名称');
    log('');
    error('配置文件不存在: ' + envFile);
  }
  
  const content = fs.readFileSync(envFile, 'utf8');
  const config = {};
  content.split(/\r?\n/).forEach(line => {
    line = line.trim();
    const match = line.match(/^([A-Z_]+)=(.+)$/);
    if (match) {
      config[match[1]] = match[2].trim();
    }
  });
  
  if (!config.BACKUP_REPO || !config.BACKUP_TOKEN) {
    error('配置文件缺少 BACKUP_REPO 或 BACKUP_TOKEN');
  }
  
  return config;
}

// 验证 URL
function validateUrl(url) {
  try {
    const parsed = new URL(url);
    if (!['github.com', 'gitlab.com', 'bitbucket.org'].includes(parsed.hostname)) {
      error('只支持 GitHub/GitLab/Bitbucket');
    }
    return true;
  } catch {
    error('无效的仓库 URL');
  }
}

// 读取 .gitignore
function loadGitignore(dir) {
  const gitignorePath = path.join(dir, '.gitignore');
  if (fs.existsSync(gitignorePath)) {
    return fs.readFileSync(gitignorePath, 'utf8')
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'));
  }
  return [];
}

// 检查是否应该忽略
function shouldIgnore(filePath, ignorePatterns) {
  const relativePath = filePath.replace(WORKSPACE_DIR + '/', '');
  for (const pattern of ignorePatterns) {
    if (relativePath.includes(pattern)) return true;
    if (pattern.endsWith('/') && relativePath.startsWith(pattern)) return true;
    if (relativePath === pattern) return true;
  }
  return false;
}

// 安全的 git 执行
function safeExec(cmd, options = {}) {
  try {
    return execSync(cmd, { ...options, encoding: 'utf8', stdio: 'pipe' });
  } catch (err) {
    const config = loadConfig();
    const token = config.BACKUP_TOKEN;
    let msg = err.message;
    if (token) msg = msg.replace(token, '***TOKEN***');
    error(`Git 错误: ${msg}`);
  }
}

// 生成 tag 名称
function generateTag() {
  const now = new Date();
  return `backup-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}`;
}

// 同步
async function sync(args) {
  const config = loadConfig();
  validateUrl(config.BACKUP_REPO);
  
  const dryRun = args.includes('--dry-run');
  const target = args.find(a => !a.startsWith('--')) || 'all';
  const instanceId = getInstanceId();  // 获取 Instance ID
  
  log(`🔄 Elegant Sync${dryRun ? ' (预览)' : ''}`, 'cyan');
  log(`📦 目标: ${target}`);
  log(`🖥️  实例: ${instanceId}\n`);
  
  // 清理暂存区
  if (!dryRun && fs.existsSync(STAGING_DIR)) {
    fs.rmSync(STAGING_DIR, { recursive: true });
  }
  fs.mkdirSync(STAGING_DIR, { recursive: true });
  
  // 加载忽略规则
  const ignorePatterns = [
    '.git', '.gitignore',
    'benchmarks/', 'logs/', 'media/',
    'canvas/', 'completions/', 'delivery-queue/',
    'memory/daily/', 'memory/sessions/',
    'elegant-sync/',  // 排除自身
    '.elegant-sync-staging/'
  ];
  
  // 读取自定义 .gitignore
  const customIgnore = loadGitignore(WORKSPACE_DIR);
  ignorePatterns.push(...customIgnore);
  
  // 复制文件
  const files = [];
  
  const copyIfExists = (src, dest, name) => {
    if (!fs.existsSync(src)) return false;
    if (shouldIgnore(src, ignorePatterns)) return false;
    
    if (dryRun) {
      log(`  📄 ${name}`, 'blue');
    } else {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      if (fs.statSync(src).isDirectory()) {
        fs.cpSync(src, dest, { recursive: true });
      } else {
        fs.copyFileSync(src, dest);
      }
      log(`  ✅ ${name}`, 'green');
    }
    files.push(name);
    return true;
  };
  
  const instanceDir = instanceId;
  
  // 核心文件
  const coreFiles = ['AGENTS.md', 'IDENTITY.md', 'USER.md', 'SOUL.md', 'TOOLS.md', 'HEARTBEAT.md'];
  log('📝 核心文件:');
  for (const file of coreFiles) {
    if (target === 'all' || target === 'config') {
      copyIfExists(
        path.join(WORKSPACE_DIR, file),
        path.join(STAGING_DIR, instanceDir, file),
        file
      );
    }
  }
  
  // Memory
  const memoryDir = path.join(WORKSPACE_DIR, 'memory');
  if (fs.existsSync(memoryDir) && (target === 'all' || target === 'memory')) {
    log('\n🧠 Memory:');
    
    // 递归查找所有 .md 文件
    function findMdFiles(dir, prefix = '') {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          findMdFiles(fullPath, prefix + item + '/');
        } else if (item.endsWith('.md')) {
          const destPath = path.join(STAGING_DIR, instanceDir, 'memory', prefix + item);
          const srcPath = fullPath;
          copyIfExists(srcPath, destPath, `memory/${prefix}${item}`);
        }
      }
    }
    findMdFiles(memoryDir);
  }
  
  // Skills
  const skillsDir = path.join(WORKSPACE_DIR, 'skills');
  if (fs.existsSync(skillsDir) && (target === 'all' || target === 'skills')) {
    log('\n🔧 Skills:');
    fs.mkdirSync(path.join(STAGING_DIR, instanceDir, 'skills'), { recursive: true });
    for (const skill of fs.readdirSync(skillsDir)) {
      const skillPath = path.join(skillsDir, skill);
      if (fs.statSync(skillPath).isDirectory()) {
        copyIfExists(
          skillPath,
          path.join(STAGING_DIR, instanceDir, 'skills', skill),
          `skills/${skill}`
        );
      }
    }
  }
  
  if (dryRun) {
    log(`\n✅ 预览完成，共 ${files.length} 个文件`, 'yellow');
    return;
  }
  
  // 写入元数据
  fs.writeFileSync(
    path.join(STAGING_DIR, instanceDir, 'SYNC_METADATA.json'),
    JSON.stringify({
      timestamp: new Date().toISOString(),
      tag: generateTag(),
      instance: instanceId,
      files: files.length
    }, null, 2)
  );
  
  // Git 操作
  log('\n📤 推送到远程...', 'cyan');
  const repoUrl = config.BACKUP_REPO.replace('https://', `https://${config.BACKUP_TOKEN}@`);
  
  process.chdir(STAGING_DIR);
  safeExec('git init');
  safeExec('git config user.email "sync@elegant.local"');
  safeExec('git config user.name "Elegant Sync"');
  safeExec('git add -A');
  safeExec('git commit -m "Sync: ' + new Date().toISOString() + '"');
  
  const tag = generateTag();
  const branch = getInstanceId();
  safeExec(`git push ${repoUrl} HEAD:${branch}`);
  safeExec(`git tag ${tag}`);
  safeExec(`git push ${repoUrl} ${tag}`);
  
  // 清理
  process.chdir(HOME);
  fs.rmSync(STAGING_DIR, { recursive: true });
  
  log(`\n✅ 同步完成!`, 'green');
  log(`🏷️  版本: ${tag}`, 'blue');
}

// 恢复
async function restore(args) {
  const config = loadConfig();
  const force = args.includes('--force');
  const version = args.find(a => !a.startsWith('--') && a !== 'restore') || 'latest';
  
  log('🔄 恢复中...', 'cyan');
  
  // 创建本地备份
  const backupDir = path.join(LOCAL_BACKUP_DIR, new Date().toISOString().replace(/:/g, '-'));
  fs.mkdirSync(backupDir, { recursive: true });
  
  // 备份现有文件
  if (fs.existsSync(WORKSPACE_DIR)) {
    fs.cpSync(WORKSPACE_DIR, path.join(backupDir, 'workspace'), { recursive: true });
    log(`📦 本地备份: ${backupDir}`, 'yellow');
  }
  
  // TODO: 实现从远程恢复
  error('恢复功能暂未实现，请手动从 GitHub 克隆');
}

// 状态
function status() {
  const configPath = path.join(OPENCLAW_DIR, '.backup.env');
  
  log('📊 Elegant Sync 状态', 'cyan');
  log(`配置文件: ${fs.existsSync(configPath) ? '✅ 已配置' : '❌ 未配置'}`);
  
  if (fs.existsSync(configPath)) {
    const config = loadConfig();
    const repo = config.BACKUP_REPO.replace('https://', '').replace(/@.*/, '');
    log(`仓库: ${repo}`, 'blue');
  }
}

// 主入口
function main() {
  const command = process.argv[2];
  const args = process.argv.slice(3);
  
  switch (command) {
    case 'sync':
    case 'push':
      sync(args);
      break;
    case 'restore':
    case 'pull':
      restore(args);
      break;
    case 'status':
      status();
      break;
    default:
      log('Elegant Sync - 优雅安全的同步工具');
      log('');
      log('用法:');
      log('  elegant-sync sync           # 同步全部');
      log('  elegant-sync sync --dry-run # 预览');
      log('  elegant-sync sync memory    # 只同步 memory');
      log('  elegant-sync sync skills   # 只同步 skills');
      log('  elegant-sync restore       # 恢复');
      log('  elegant-sync status        # 查看状态');
  }
}

main();
