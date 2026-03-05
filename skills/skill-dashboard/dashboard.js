#!/usr/bin/env node

/**
 * Skill Dashboard - 技能可视化控制台
 * 
 * 分页显示已安装技能，支持快速管理
 * 像 360 软件管家一样管理 AI 技能
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  pageSize: 5,
  clawhubBase: 'https://clawhub.ai/skills',
  stateFile: path.join(__dirname, 'skill-state.json')
};

// 技能状态缓存
let skillState = {};

/**
 * 加载技能状态
 */
function loadSkillState() {
  try {
    if (fs.existsSync(CONFIG.stateFile)) {
      skillState = JSON.parse(fs.readFileSync(CONFIG.stateFile, 'utf8'));
    }
  } catch (error) {
    console.error('加载技能状态失败:', error.message);
    skillState = {};
  }
}

/**
 * 保存技能状态
 */
function saveSkillState() {
  try {
    fs.writeFileSync(CONFIG.stateFile, JSON.stringify(skillState, null, 2), 'utf8');
  } catch (error) {
    console.error('保存技能状态失败:', error.message);
  }
}

/**
 * 执行命令并拦截输出（安全约束）
 */
function execCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, { encoding: 'utf8', timeout: 30000 }, (error, stdout, stderr) => {
      if (error) {
        reject({ error: error.message, stderr });
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

/**
 * 获取已安装技能列表
 */
async function getInstalledSkills() {
  try {
    // 使用 clawhub list 获取已安装技能（纯文本格式）
    // 指定工作目录为 workspace，确保能正确读取已安装技能
    const workspaceDir = path.join(__dirname, '..', '..');
    
    const output = await new Promise((resolve, reject) => {
      exec('clawhub list', { cwd: workspaceDir, encoding: 'utf8', timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          reject(error);
        } else {
          resolve(stdout);
        }
      });
    });
    
    // 检查是否没有安装技能
    if (output.includes('No installed skills')) {
      return [];
    }
    
    // 解析纯文本格式：每行是 "技能名  版本号"
    const lines = output.split('\n').filter(line => line.trim());
    const skills = lines.map(line => {
      // 使用更宽松的分割：多个空格或制表符
      const match = line.trim().match(/^([a-zA-Z0-9_-]+)\s+([0-9.]+)$/);
      
      if (match) {
        const slug = match[1];
        const version = match[2];
        // 美化名称：连字符变空格，首字母大写
        const name = slug.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
        
        return {
          slug,
          name,
          version,
          description: '暂无描述',
          status: skillState[slug]?.enabled === false ? 'disabled' : 'active',
          lastUsed: skillState[slug]?.lastUsed || null,
          autoEnable: skillState[slug]?.autoEnable || false
        };
      }
      
      return null;
    }).filter(skill => skill !== null);
    
    return skills;
  } catch (error) {
    console.error('获取技能列表失败:', error.message);
    return [];
  }
}

/**
 * 检查技能更新
 */
async function checkUpdate(skill) {
  try {
    const output = await execCommand(`clawhub inspect ${skill.slug} --json`);
    const remote = JSON.parse(output);
    
    const localVersion = skill.version;
    const remoteVersion = remote.version;
    
    if (remoteVersion !== localVersion) {
      return {
        available: true,
        version: remoteVersion,
        changelog: remote.changelog || '版本更新'
      };
    }
    
    return { available: false };
  } catch (error) {
    return { available: false, error: error.message };
  }
}

/**
 * 分页显示技能
 */
function displaySkills(skills, page, totalPages) {
  let output = `\n`;
  output += `┌─────────────────────────────────────────┐\n`;
  output += `│  📊 技能控制台 (${page}/${totalPages})${' '.repeat(16)}🌐     │\n`;
  output += `├─────────────────────────────────────────┤\n`;
  
  skills.forEach((skill, index) => {
    // 状态图标
    let icon = '📞';
    let statusText = '主动调用';
    
    if (skill.autoEnable) {
      icon = '✅';
      statusText = '被动生效';
    } else if (skill.status === 'disabled') {
      icon = '⏸️';
      statusText = '已禁用';
    }
    
    // 技能信息
    output += `│  ${icon} ${skill.name} v${skill.version}${' '.repeat(Math.max(0, 18 - skill.name.length - skill.version.length))}│\n`;
    output += `│     ${skill.description.substring(0, 30)}${skill.description.length > 30 ? '...' : ''}${' '.repeat(Math.max(0, 30 - skill.description.length))}│\n`;
    output += `│     状态：${statusText}${' '.repeat(22)}│\n`;
    
    // 操作按钮
    let buttons = ['[详情]'];
    if (skill.status === 'disabled') {
      buttons.push('[启用]');
    } else {
      buttons.push('[禁用]');
    }
    buttons.push('[卸载]');
    
    output += `│     ${buttons.join(' ')}${' '.repeat(Math.max(0, 25 - buttons.join(' ').length))}│\n`;
    
    if (index < skills.length - 1) {
      output += `├─────────────────────────────────────────┤\n`;
    }
  });
  
  output += `└─────────────────────────────────────────┘\n`;
  
  return output;
}

/**
 * 人性化询问
 */
function askUser(page, totalPages, hasUpdate = false) {
  let messages = [];
  
  if (hasUpdate) {
    messages.push(`\n⚠️ 检测到有技能可以更新。`);
  }
  
  messages.push(`\n这 ${page} 页的技能有没有问题？`);
  
  if (page < totalPages) {
    messages.push(`要不要看下 一页？（回复"是"或"不用"）`);
  }
  
  messages.push(`你一共装了 ${totalPages * CONFIG.pageSize} 个技能，分 ${totalPages} 页显示。`);
  
  return messages.join('\n');
}

/**
 * 打开 ClawHub 主页
 */
async function openClawHub() {
  try {
    const platform = process.platform;
    let openCommand;
    
    if (platform === 'darwin') {
      openCommand = `open "${CONFIG.clawhubBase}"`;
    } else if (platform === 'win32') {
      openCommand = `start "" "${CONFIG.clawhubBase}"`;
    } else {
      openCommand = `xdg-open "${CONFIG.clawhubBase}"`;
    }
    
    await execCommand(openCommand);
    return `正在打开 ClawHub 技能主页...\n${CONFIG.clawhubBase}\n\n（已在浏览器中打开）`;
  } catch (error) {
    return `打开浏览器失败：${error.message}\n\n你可以手动访问：${CONFIG.clawhubBase}`;
  }
}

/**
 * 更新技能（带二次确认）
 */
async function updateSkill(skillSlug) {
  try {
    // 检查更新
    const update = await checkUpdate({ slug: skillSlug, version: 'current' });
    
    if (!update.available) {
      return `✅ ${skillSlug} 已经是最新版本。`;
    }
    
    // 返回确认信息（由主程序处理用户确认）
    return {
      needsConfirm: true,
      message: `检测到 ${skillSlug} 有新版本 v${update.version}\n\n更新内容：\n${update.changelog}\n\n确定要更新到 v${update.version} 吗？（回复"确定"或"取消"）`,
      version: update.version
    };
  } catch (error) {
    return `检查更新失败：${error.message}`;
  }
}

/**
 * 执行更新（用户确认后）
 */
async function executeUpdate(skillSlug) {
  try {
    const output = await execCommand(`clawhub update ${skillSlug}`);
    
    // 拦截 raw 输出，转化为自然语言
    return `✅ ${skillSlug} 已更新成功！\n\n新版本已安装，可以立即使用。`;
  } catch (error) {
    return `❌ 更新失败：${error.error || error.message}`;
  }
}

/**
 * 卸载技能（带二次确认）
 */
async function uninstallSkill(skillSlug) {
  // 返回确认信息（由主程序处理用户确认）
  return {
    needsConfirm: true,
    message: `⚠️ 确定要卸载 ${skillSlug} 吗？\n\n卸载后：\n- 技能文件将被删除\n- 配置将丢失\n- 需要重新安装才能使用\n\n这个操作不可逆，确定要继续吗？（回复"确定"或"取消"）`
  };
}

/**
 * 执行卸载（用户确认后）
 */
async function executeUninstall(skillSlug) {
  try {
    await execCommand(`clawhub uninstall ${skillSlug}`);
    
    // 清理状态缓存
    if (skillState[skillSlug]) {
      delete skillState[skillSlug];
      saveSkillState();
    }
    
    return `✅ ${skillSlug} 已卸载成功。`;
  } catch (error) {
    return `❌ 卸载失败：${error.error || error.message}`;
  }
}

/**
 * 切换技能状态（启用/禁用）
 */
async function toggleSkill(skillSlug, enable) {
  try {
    if (!skillState[skillSlug]) {
      skillState[skillSlug] = {};
    }
    
    skillState[skillSlug].enabled = enable;
    skillState[skillSlug].lastUsed = new Date().toISOString();
    saveSkillState();
    
    const action = enable ? '启用' : '禁用';
    return `✅ ${skillSlug} 已${action}。`;
  } catch (error) {
    return `❌ 操作失败：${error.message}`;
  }
}

/**
 * 主函数：显示技能控制台
 */
async function showDashboard(page = 1) {
  loadSkillState();
  
  const skills = await getInstalledSkills();
  
  if (skills.length === 0) {
    return `📊 技能控制台\n\n你还没有安装任何技能。\n\n可以使用 \`clawhub install <技能名>\` 安装技能，或者访问 ${CONFIG.clawhubBase} 浏览技能。`;
  }
  
  const totalPages = Math.ceil(skills.length / CONFIG.pageSize);
  const start = (page - 1) * CONFIG.pageSize;
  const end = Math.min(start + CONFIG.pageSize, skills.length);
  const pageSkills = skills.slice(start, end);
  
  // 检查是否有更新
  let hasUpdate = false;
  for (const skill of pageSkills) {
    skill.update = await checkUpdate(skill);
    if (skill.update.available) {
      hasUpdate = true;
    }
  }
  
  // 显示技能
  let output = displaySkills(pageSkills, page, totalPages);
  
  // 人性化询问
  output += askUser(page, totalPages, hasUpdate);
  
  return output;
}

// 导出函数
module.exports = {
  showDashboard,
  openClawHub,
  updateSkill,
  executeUpdate,
  uninstallSkill,
  executeUninstall,
  toggleSkill,
  getInstalledSkills,
  checkUpdate
};

// CLI 入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const param = args[1];
  
  switch (command) {
    case 'show':
      showDashboard(parseInt(param) || 1).then(console.log);
      break;
    case 'open':
      openClawHub().then(console.log);
      break;
    case 'update':
      if (param) {
        updateSkill(param).then(console.log);
      } else {
        console.log('用法：node dashboard.js update <技能名>');
      }
      break;
    case 'uninstall':
      if (param) {
        uninstallSkill(param).then(console.log);
      } else {
        console.log('用法：node dashboard.js uninstall <技能名>');
      }
      break;
    default:
      showDashboard(1).then(console.log);
  }
}
