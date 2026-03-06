#!/usr/bin/env node

/**
 * Developer Dashboard - 开发者模式（一键巡查）
 * 
 * 查询技能数据（ClawHub + 本地），生成巡查报告
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  cacheFile: path.join(__dirname, 'dev-cache.json'),
  cacheTimeout: 3600000, // 1 小时缓存
  clawhubBase: 'https://clawhub.ai/skills'
};

/**
 * 执行命令并拦截输出
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
 * 加载缓存
 */
function loadCache() {
  try {
    if (fs.existsSync(CONFIG.cacheFile)) {
      const data = JSON.parse(fs.readFileSync(CONFIG.cacheFile, 'utf8'));
      
      // 检查缓存是否过期
      const now = Date.now();
      if (now - data.timestamp < CONFIG.cacheTimeout) {
        return data.data;
      }
    }
  } catch (error) {
    console.error('加载缓存失败:', error.message);
  }
  
  return null;
}

/**
 * 保存缓存
 */
function saveCache(data) {
  try {
    const cacheData = {
      timestamp: Date.now(),
      data: data
    };
    
    fs.writeFileSync(CONFIG.cacheFile, JSON.stringify(cacheData, null, 2), 'utf8');
  } catch (error) {
    console.error('保存缓存失败:', error.message);
  }
}

/**
 * 获取已安装技能列表
 */
async function getInstalledSkills() {
  try {
    const output = await execCommand('clawhub list');
    
    if (output.includes('No installed skills')) {
      return [];
    }
    
    const lines = output.split('\n').filter(line => line.trim());
    const skills = lines.map(line => {
      const match = line.trim().match(/^([a-zA-Z0-9_-]+)\s+([0-9.]+)$/);
      
      if (match) {
        const slug = match[1];
        const version = match[2];
        const name = slug.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
        
        return { slug, name, version };
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
 * 查询 ClawHub 数据
 */
async function fetchClawhubData(slug) {
  try {
    const output = await execCommand(`clawhub inspect ${slug} --json`);
    const data = JSON.parse(output);
    
    return {
      downloads: data.downloads || 0,
      rating: data.rating || 0,
      reviews: data.reviews || 0,
      url: `${CONFIG.clawhubBase}/${slug}`
    };
  } catch (error) {
    return { downloads: 0, rating: 0, reviews: 0, error: error.message };
  }
}

/**
 * 查询本地使用数据
 */
async function fetchLocalData(slug) {
  try {
    const stateFile = path.join(__dirname, '..', 'skill-dashboard', 'skill-state.json');
    
    if (fs.existsSync(stateFile)) {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      const skillState = state[slug] || {};
      
      return {
        usageCount: skillState.usageCount || 0,
        lastUsed: skillState.lastUsed ? new Date(skillState.lastUsed).toLocaleString('zh-CN') : '从未使用',
        enabled: skillState.enabled !== false
      };
    }
    
    return { usageCount: 0, lastUsed: '从未使用', enabled: true };
  } catch (error) {
    return { usageCount: 0, lastUsed: '从未使用', enabled: true };
  }
}

/**
 * 格式化数字（添加千位分隔符）
 */
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * 生成巡查报告
 */
async function generatePatrolReport() {
  const skills = await getInstalledSkills();
  
  if (skills.length === 0) {
    return `🛠️ 开发者模式 - 技能巡查报告\n\n你还没有安装任何技能。\n\n可以使用 \`clawhub install <技能名>\` 安装技能。`;
  }
  
  const report = [];
  
  // 查询每个技能的数据
  for (const skill of skills) {
    const clawhubData = await fetchClawhubData(skill.slug);
    const localData = await fetchLocalData(skill.slug);
    
    report.push({
      slug: skill.slug,
      name: skill.name,
      version: skill.version,
      clawhub: clawhubData,
      local: localData
    });
  }
  
  // 生成报告
  let output = `\n`;
  output += `┌─────────────────────────────────────────────────┐\n`;
  output += `│  🛠️ 开发者模式 - 技能巡查报告          📊      │\n`;
  output += `│  生成时间：${new Date().toLocaleString('zh-CN')}  │\n`;
  output += `├─────────────────────────────────────────────────┤\n`;
  
  let totalDownloads = 0;
  let totalRating = 0;
  
  report.forEach((skill, index) => {
    output += `│                                                 │\n`;
    output += `│  📦 ${skill.name} v${skill.version}${' '.repeat(Math.max(0, 20 - skill.name.length - skill.version.length))}│\n`;
    output += `│  ├─ ClawHub: ⬇️ ${formatNumber(skill.clawhub.downloads)}  ⭐ ${skill.clawhub.rating}/5  💬 ${skill.clawhub.reviews} 条  │\n`;
    output += `│  └─ 本地：   使用 ${skill.local.usageCount} 次，最后使用：${skill.local.lastUsed}  │\n`;
    
    totalDownloads += skill.clawhub.downloads;
    totalRating += skill.clawhub.rating;
    
    if (index < report.length - 1) {
      output += `│                                                 │\n`;
    }
  });
  
  const avgRating = report.length > 0 ? (totalRating / report.length).toFixed(1) : 0;
  
  output += `│                                                 │\n`;
  output += `├─────────────────────────────────────────────────┤\n`;
  output += `│  总结：${report.length} 个技能，总下载 ${formatNumber(totalDownloads)} 次，平均评分 ${avgRating}/5  │\n`;
  output += `│                                                 │\n`;
  output += `│  [导出 Markdown] [刷新数据] [查看详情]          │\n`;
  output += `└─────────────────────────────────────────────────┘\n`;
  
  // 保存缓存
  saveCache(report);
  
  return output;
}

/**
 * 导出为 Markdown
 */
async function exportToMarkdown() {
  const cache = loadCache();
  
  if (!cache || cache.length === 0) {
    return '没有缓存数据，请先生成巡查报告。';
  }
  
  let markdown = `# 开发者模式 - 技能巡查报告\n\n`;
  markdown += `**生成时间：** ${new Date().toLocaleString('zh-CN')}\n\n`;
  markdown += `---\n\n`;
  
  markdown += `## 技能清单\n\n`;
  
  cache.forEach(skill => {
    markdown += `### 📦 ${skill.name} v${skill.version}\n\n`;
    markdown += `**ClawHub 数据：**\n`;
    markdown += `- 下载量：${formatNumber(skill.clawhub.downloads)} 次\n`;
    markdown += `- 评分：${skill.clawhub.rating}/5\n`;
    markdown += `- 评论：${skill.clawhub.reviews} 条\n`;
    markdown += `- 链接：${skill.clawhub.url}\n\n`;
    
    markdown += `**本地使用数据：**\n`;
    markdown += `- 使用次数：${skill.local.usageCount} 次\n`;
    markdown += `- 最后使用：${skill.local.lastUsed}\n`;
    markdown += `- 状态：${skill.local.enabled ? '✅ 启用' : '⏸️ 禁用'}\n\n`;
    markdown += `---\n\n`;
  });
  
  const totalDownloads = cache.reduce((sum, skill) => sum + skill.clawhub.downloads, 0);
  const avgRating = (cache.reduce((sum, skill) => sum + skill.clawhub.rating, 0) / cache.length).toFixed(1);
  
  markdown += `## 总结\n\n`;
  markdown += `- **技能总数：** ${cache.length} 个\n`;
  markdown += `- **总下载量：** ${formatNumber(totalDownloads)} 次\n`;
  markdown += `- **平均评分：** ${avgRating}/5\n`;
  
  return markdown;
}

// 导出函数
module.exports = {
  generatePatrolReport,
  exportToMarkdown,
  getInstalledSkills,
  fetchClawhubData,
  fetchLocalData
};

// CLI 入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'patrol':
      generatePatrolReport().then(console.log);
      break;
    case 'export':
      exportToMarkdown().then(console.log);
      break;
    default:
      generatePatrolReport().then(console.log);
  }
}
