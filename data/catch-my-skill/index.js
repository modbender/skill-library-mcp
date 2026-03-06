/**
 * Catch My Skill v1.0.0
 * 自动检测本地与线上 skill 版本差异
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

const HOME = os.homedir();
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills');
const DATA_DIR = path.join(__dirname, 'data');

// 颜色
const colors = { green: '\x1b[32m', red: '\x1b[31m', yellow: '\x1b[33m', cyan: '\x1b[36m', reset: '\x1b[0m' };
const log = (msg, c = 'reset') => console.log(`${colors[c]}${msg}${colors.reset}`);

// 确保 data 目录存在
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

// 本地 skill 列表
function getLocalSkills() {
  const localFile = path.join(DATA_DIR, 'local.json');
  if (fs.existsSync(localFile)) {
    return JSON.parse(fs.readFileSync(localFile, 'utf8'));
  }
  return { skills: [], updated: null };
}

// 加载配置
function loadConfig() {
  const envFile = path.join(HOME, '.openclaw', '.backup.env');
  const config = { githubUsername: 'russellfei', interval: 30 };
  if (fs.existsSync(envFile)) {
    const content = fs.readFileSync(envFile, 'utf8');
    content.split('\n').forEach(line => {
      const match = line.match(/^(GITHUB_USERNAME|CATCH_INTERVAL)=(.+)$/);
      if (match) {
        if (match[1] === 'GITHUB_USERNAME') config.githubUsername = match[2].trim();
        if (match[1] === 'CATCH_INTERVAL') config.interval = parseInt(match[2].trim());
      }
    });
  }
  return config;
}

// 已知技能列表（从 ClawHub 获取）
const KNOWN_SKILLS = [
  'white-stone-mem',
  'elegant-sync', 
  'minimax-mcp-call'
];

// 获取版本（只从 ClawHub）
function getOnlineSkills() {
  const skills = [];
  
  for (const name of KNOWN_SKILLS) {
    try {
      const output = execSync(`clawhub inspect ${name} 2>/dev/null`, { encoding: 'utf8', timeout: 10000 });
      const match = output.match(/Latest:\s*(\S+)/);
      if (match) {
        skills.push({ name, version: match[1], source: 'clawhub' });
      }
    } catch {}
  }
  
  return skills;
}

// 检查版本
function checkVersions() {
  log('🎯 Catch My Skill - 版本检查\n', 'cyan');
  
  const local = getLocalSkills();
  const config = loadConfig();
  
  // 获取线上版本
  log('📡 获取 ClawHub 版本...', 'cyan');
  const onlineSkills = getOnlineSkills();
  
  // 保存线上列表
  const online = {
    clawhub: onlineSkills,
    updated: new Date().toISOString()
  };
  
  fs.writeFileSync(path.join(DATA_DIR, 'online.json'), JSON.stringify(online, null, 2));
  
  // 对比
  log('\n=== 版本对比 ===\n', 'cyan');
  
  let hasUpdates = false;
  
  // 检查本地 skill
  for (const localSkill of local.skills) {
    const onlineSkill = onlineSkills.find(s => s.name === localSkill.name);
    if (onlineSkill) {
      if (localSkill.version !== onlineSkill.version) {
        log(`⚠️  ${localSkill.name}: 本地 ${localSkill.version} < 线上 ${onlineSkill.version}`, 'yellow');
        hasUpdates = true;
      } else {
        log(`✅ ${localSkill.name}: ${localSkill.version}`, 'green');
      }
    } else {
      log(`ℹ️  ${localSkill.name}: 线上未找到`, 'cyan');
    }
  }
  
  if (!hasUpdates) {
    log('\n✅ 所有本地 skill 都是最新版本!', 'green');
  }
  
  return hasUpdates;
}

// 获取本地 skill 版本
function getSkillVersion(skillPath) {
  const skillFile = path.join(skillPath, 'SKILL.md');
  if (fs.existsSync(skillFile)) {
    const content = fs.readFileSync(skillFile, 'utf8');
    // 尝试从 metadata 获取
    const versionMatch = content.match(/version:\s*["']?(\S+)["']?/);
    if (versionMatch) return versionMatch[1];
    // 尝试从更新日志获取
    const logMatch = content.match(/v(\d+\.\d+\.\d+)/);
    if (logMatch) return logMatch[1];
  }
  return 'unknown';
}

// 初始化本地列表（从线上拉取全部）
function initLocal() {
  log('📡 从 ClawHub 拉取 skills...', 'cyan');
  
  // 只从 ClawHub 获取
  const allSkills = getOnlineSkills();
  
  // 保存为本地列表
  const data = { 
    skills: allSkills, 
    updated: new Date().toISOString() 
  };
  
  fs.writeFileSync(path.join(DATA_DIR, 'local.json'), JSON.stringify(data, null, 2));
  
  log(`✅ 已拉取 ${allSkills.length} 个 skills`, 'green');
  log('');
  log('💡 可用命令:');
  log('   /catch-my-skill remove <name>  # 删除不想要的');
  log('   /catch-my-skill check          # 检查版本');
}

// 显示本地列表
function showLocal() {
  const local = getLocalSkills();
  log('=== 本地 Skills (跟踪中) ===', 'cyan');
  for (const s of local.skills) {
    log(`${s.name}: ${s.version}`);
  }
  log(`\n共 ${local.skills.length} 个 skills`, 'yellow');
}

// 移除 skill
function removeSkill(name) {
  const local = getLocalSkills();
  const filtered = local.skills.filter(s => s.name !== name);
  fs.writeFileSync(path.join(DATA_DIR, 'local.json'), JSON.stringify({ skills: filtered, updated: new Date().toISOString() }, null, 2));
  log(`✅ 已移除 ${name}`, 'green');
}

// 添加 skill
function addSkill(name) {
  const local = getLocalSkills();
  if (local.skills.find(s => s.name === name)) {
    log(`${name} 已在列表中`, 'yellow');
    return;
  }
  local.skills.push({ name, version: 'unknown' });
  fs.writeFileSync(path.join(DATA_DIR, 'local.json'), JSON.stringify({ skills: local.skills, updated: new Date().toISOString() }, null, 2));
  log(`✅ 已添加 ${name}`, 'green');
}

// 更新 skill（自动选择渠道）
function updateSkill(name) {
  const local = getLocalSkills();
  const skill = local.skills.find(s => s.name === name);
  if (!skill) {
    log(`${name} 不在本地列表中`, 'yellow');
    return;
  }
  
  log(`📦 更新 ${name}...`, 'cyan');
  
  // 尝试从 GitHub 更新
  const config = loadConfig();
  const repoUrl = `https://github.com/${config.githubUsername}/${name}`;
  
  try {
    execSync(`cd ~/.openclaw/workspace/skills && git clone ${repoUrl} 2>/dev/null`, { timeout: 30000 });
    log(`✅ 已从 GitHub 更新`, 'green');
  } catch {
    // 尝试 ClawHub
    execSync(`clawhub install ${name}`, { timeout: 30000 });
    log(`✅ 已从 ClawHub 更新`, 'green');
  }
}

// 显示线上列表
function showOnline() {
  const onlineFile = path.join(DATA_DIR, 'online.json');
  if (!fs.existsSync(onlineFile)) {
    log('请先运行 check 命令', 'yellow');
    return;
  }
  const online = JSON.parse(fs.readFileSync(onlineFile, 'utf8'));
  
  log('=== ClawHub Skills ===', 'cyan');
  for (const s of online.clawhub) {
    log(`${s.name}: ${s.version}`);
  }
  log('=== GitHub Skills ===', 'cyan');
  for (const s of online.github) {
    log(`${s.name}: ${s.version}`);
  }
}

// 主入口
function main() {
  const command = process.argv[2];
  const arg = process.argv[3];
  
  switch (command) {
    case 'check':
      checkVersions();
      break;
    case 'init':
      initLocal();  // 从线上拉取全部
      break;
    case 'local':
      showLocal();
      break;
    case 'online':
      showOnline();
      break;
    case 'remove':
      if (arg) removeSkill(arg);
      else log('用法: catch-my-skill remove <skill-name>');
      break;
    case 'add':
      if (arg) addSkill(arg);
      else log('用法: catch-my-skill add <skill-name>');
      break;
    case 'update':
      if (arg) updateSkill(arg);
      else log('用法: catch-my-skill update <skill-name>');
      break;
    default:
      log('Catch My Skill - 本地与线上 skill 版本检测');
      log('');
      log('用法:');
      log('  catch-my-skill init     # 首次：从线上拉取全部 skills');
      log('  catch-my-skill check   # 检查版本');
      log('  catch-my-skill remove  # 删除不想要的');
      log('  catch-my-skill add     # 添加想跟踪的');
      log('  catch-my-skill update  # 更新落后版本');
      log('  catch-my-skill local  # 查看本地列表');
  }
}

main();
