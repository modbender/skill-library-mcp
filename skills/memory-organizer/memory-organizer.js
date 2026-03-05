#!/usr/bin/env node

/**
 * Memory Organizer - 记忆整理压缩工具 v2.0
 * 功能：
 * 1. 扫描记忆文件
 * 2. 分析内容重要性
 * 3. 根据 Topic 分类
 * 4. 压缩/丢弃冗余内容
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/home/node/.openclaw/workspace-main';
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const MAIN_MEMORY = path.join(WORKSPACE, 'MEMORY.md');

// Topic 关键词映射
const TOPIC_KEYWORDS = {
  '用户偏好': ['用户', '偏好', 'preference', '称呼', '名字', '时区', 'timezone'],
  '项目配置': ['项目', '配置', 'config', 'agent', '工作空间', 'workspace', 'cron', '定时'],
  '技能': ['skill', '工具', 'tool', '安装', 'install', '配置'],
  '赚钱点子': ['赚钱', '副业', 'money', '收入', '点子', '项目'],
  '待办事项': ['待办', 'todo', '任务', 'task', '下一步', '计划'],
  '技术记录': ['代码', 'command', '命令', '技术', '调试', '问题', '解决'],
  '日常': ['日记', '日志', '记录', '今天', '昨天', '日常']
};

// 要保留的关键词
const IMPORTANT_KEYWORDS = [
  '用户', '偏好', '配置', '项目', '待办', '任务', 'Agent', '重要', '关键'
];

// 要丢弃的冗余关键词
const DISCARD_KEYWORDS = [
  '测试', 'test', '调试', '临时', 'temp', '日志', '详情', '具体过程'
];

/**
 * 扫描记忆目录
 */
function scanMemories() {
  if (!fs.existsSync(MEMORY_DIR)) {
    console.log('❌ memory 目录不存在');
    return [];
  }

  const files = fs.readdirSync(MEMORY_DIR)
    .filter(f => f.endsWith('.md') && !f.endsWith('.bak'))
    .map(f => {
      const filePath = path.join(MEMORY_DIR, f);
      const stats = fs.statSync(filePath);
      const content = fs.readFileSync(filePath, 'utf-8');
      return {
        name: f,
        size: stats.size,
        lines: content.split('\n').length,
        chars: content.length
      };
    });

  console.log('\n📁 记忆文件列表：\n');
  let totalChars = 0;
  files.forEach(f => {
    console.log(`  ${f.name}: ${f.chars} 字符, ${f.lines} 行`);
    totalChars += f.chars;
  });
  console.log(`\n总计: ${files.length} 个文件, ${totalChars} 字符`);

  return files;
}

/**
 * 分析记忆内容的主题
 */
function analyzeTopic(content) {
  const scores = {};
  
  // 初始化分数
  Object.keys(TOPIC_KEYWORDS).forEach(topic => {
    scores[topic] = 0;
  });
  scores['未分类'] = 0;

  // 统计每个 topic 的匹配次数
  Object.entries(TOPIC_KEYWORDS).forEach(([topic, keywords]) => {
    keywords.forEach(kw => {
      const regex = new RegExp(kw, 'gi');
      const matches = content.match(regex);
      if (matches) {
        scores[topic] += matches.length;
      }
    });
  });

  // 找出最高分的 topic
  let maxTopic = '未分类';
  let maxScore = 0;
  
  Object.entries(scores).forEach(([topic, score]) => {
    if (score > maxScore) {
      maxScore = score;
      maxTopic = topic;
    }
  });

  return { topic: maxTopic, scores };
}

/**
 * 分类所有记忆文件
 */
function classifyMemories() {
  if (!fs.existsSync(MEMORY_DIR)) {
    console.log('❌ memory 目录不存在');
    return;
  }

  const files = fs.readdirSync(MEMORY_DIR)
    .filter(f => f.endsWith('.md') && !f.endsWith('.bak'));

  const categories = {};

  console.log('\n🗂️ 记忆分类：\n');

  files.forEach(f => {
    const content = fs.readFileSync(path.join(MEMORY_DIR, f), 'utf-8');
    const { topic, scores } = analyzeTopic(content);
    
    if (!categories[topic]) {
      categories[topic] = [];
    }
    categories[topic].push({
      file: f,
      chars: content.length,
      scores
    });
  });

  // 打印分类结果
  Object.entries(categories).forEach(([topic, items]) => {
    console.log(`\n📌 ${topic} (${items.length} 个)`);
    items.forEach(item => {
      console.log(`   - ${item.file} (${item.chars} 字符)`);
    });
  });

  return categories;
}

/**
 * 找出冗余的记忆（相同 topic 的多个文件）
 */
function findRedundant() {
  const categories = classifyMemories();
  const redundant = [];

  Object.entries(categories).forEach(([topic, items]) => {
    if (items.length > 1) {
      // 按时间排序（旧的在前）
      items.sort((a, b) => a.file.localeCompare(b.file));
      
      // 除了最新的，其他的都可以丢弃
      redundant.push({
        topic,
        keep: items[items.length - 1].file,
        discard: items.slice(0, items.length - 1).map(i => i.file)
      });
    }
  });

  if (redundant.length === 0) {
    console.log('\n✅ 没有发现冗余记忆');
    return [];
  }

  console.log('\n⚠️ 发现冗余记忆：\n');
  redundant.forEach(r => {
    console.log(`📌 ${r.topic}:`);
    console.log(`   保留: ${r.keep}`);
    console.log(`   可丢弃: ${r.discard.join(', ')}`);
  });

  return redundant;
}

/**
 * 丢弃指定的记忆文件
 */
function discardMemory(filename, force = false) {
  const filePath = path.join(MEMORY_DIR, filename);
  
  if (!fs.existsSync(filePath)) {
    console.log(`❌ 文件不存在: ${filename}`);
    return false;
  }

  if (!force) {
    console.log(`⚠️ 确定要丢弃 ${filename} 吗？`);
    console.log('   使用 --force 强制丢弃');
    return false;
  }

  // 备份再删除
  const backupPath = filePath + '.discarded';
  fs.renameSync(filePath, backupPath);
  
  console.log(`🗑️ 已丢弃: ${filename}`);
  console.log(`   备份: ${filename}.discarded`);
  
  return true;
}

/**
 * 批量丢弃冗余记忆
 */
function discardRedundant(force = false) {
  const redundant = findRedundant();
  
  if (redundant.length === 0) {
    console.log('✅ 没有需要丢弃的记忆');
    return;
  }

  let discarded = 0;
  redundant.forEach(r => {
    r.discard.forEach(filename => {
      if (discardMemory(filename, force)) {
        discarded++;
      }
    });
  });

  console.log(`\n✅ 共丢弃 ${discarded} 个冗余文件`);
}

/**
 * 压缩记忆文件
 */
function compressMemory(filename, options = {}) {
  const filePath = path.join(MEMORY_DIR, filename);
  if (!fs.existsSync(filePath)) {
    console.log(`❌ 文件不存在: ${filename}`);
    return false;
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  let compressed;
  if (options.aggressive) {
    // 激进压缩：只保留标题
    compressed = lines.filter(l => l.startsWith('#'));
  } else if (options.keepTitles) {
    // 只保留标题和列表项
    compressed = lines.filter(l => 
      l.startsWith('#') || 
      l.startsWith('- ') || 
      l.startsWith('* ')
    );
  } else {
    // 默认：保留标题和关键内容
    compressed = lines.filter(l => {
      const lower = l.toLowerCase();
      return l.startsWith('#') || 
             l.startsWith('- ') || 
             l.startsWith('* ') ||
             IMPORTANT_KEYWORDS.some(kw => lower.includes(kw.toLowerCase()));
    });
  }

  const result = compressed.join('\n');
  
  // 备份原文件
  fs.writeFileSync(filePath + '.bak', content);
  fs.writeFileSync(filePath, result);

  console.log(`✅ 压缩完成: ${filename}`);
  console.log(`   原始: ${content.length} -> 压缩后: ${result.length} 字符`);

  return true;
}

/**
 * 合并到主记忆
 */
function mergeToMain(sourceFile) {
  const sourcePath = path.join(MEMORY_DIR, sourceFile);
  
  if (!fs.existsSync(sourcePath)) {
    console.log(`❌ 源文件不存在: ${sourceFile}`);
    return false;
  }

  const sourceContent = fs.readFileSync(sourcePath, 'utf-8');
  const { topic } = analyzeTopic(sourceContent);
  
  // 提取标题和关键内容
  const importantLines = sourceContent.split('\n').filter(l => 
    l.startsWith('#') || l.startsWith('- ') || l.startsWith('* ')
  );

  let mainContent = '';
  if (fs.existsSync(MAIN_MEMORY)) {
    mainContent = fs.readFileSync(MAIN_MEMORY, 'utf-8');
  }

  const merged = mainContent + '\n\n---\n\n## ' + topic + ': ' + sourceFile + '\n\n' + importantLines.join('\n');
  fs.writeFileSync(MAIN_MEMORY, merged);
  
  console.log(`✅ 已合并到 MEMORY.md [${topic}]: ${sourceFile}`);
  return true;
}

/**
 * 查看记忆内容
 */
function viewMemory(filename) {
  const filePath = path.join(MEMORY_DIR, filename);
  if (!fs.existsSync(filePath)) {
    console.log(`❌ 文件不存在: ${filename}`);
    return;
  }
  
  const content = fs.readFileSync(filePath, 'utf-8');
  const { topic } = analyzeTopic(content);
  
  console.log(`\n📄 ${filename} [${topic}]`);
  console.log('─'.repeat(40));
  console.log(content);
}

/**
 * 清理备份和丢弃文件
 */
function cleanup() {
  if (!fs.existsSync(MEMORY_DIR)) return;

  const patterns = ['.bak', '.discarded'];
  let count = 0;

  patterns.forEach(pattern => {
    fs.readdirSync(MEMORY_DIR)
      .filter(f => f.endsWith(pattern))
      .forEach(f => {
        fs.unlinkSync(path.join(MEMORY_DIR, f));
        count++;
        console.log(`🗑️ 删除: ${f}`);
      });
  });

  console.log(`\n✅ 共清理 ${count} 个文件`);
}

// 主程序
const args = process.argv.slice(2);
const command = args[0];

console.log('🧠 Memory Organizer v2.0');
console.log('=======================\n');

switch (command) {
  case 'scan':
    scanMemories();
    break;

  case 'classify':
  case 'cat':
    classifyMemories();
    break;

  case 'redundant':
    findRedundant();
    break;

  case 'discard':
    const force = args.includes('--force');
    if (args[1] === 'redundant') {
      discardRedundant(force);
    } else if (args[1]) {
      discardMemory(args[1], force);
    } else {
      console.log('用法: memory-organizer discard <文件名>');
      console.log('     memory-organizer discard redundant [--force]');
    }
    break;

  case 'compress':
    const fileToCompress = args[1];
    const options = {
      keepTitles: args.includes('--titles'),
      aggressive: args.includes('--aggressive')
    };
    if (fileToCompress) {
      compressMemory(fileToCompress, options);
    } else {
      console.log('用法: memory-organizer compress <文件名> [--titles] [--aggressive]');
    }
    break;

  case 'merge':
    const fileToMerge = args[1];
    if (fileToMerge) {
      mergeToMain(fileToMerge);
    } else {
      console.log('用法: memory-organizer merge <文件名>');
    }
    break;

  case 'view':
    const fileToView = args[1];
    if (fileToView) {
      viewMemory(fileToView);
    } else {
      console.log('用法: memory-organizer view <文件名>');
    }
    break;

  case 'clean':
    cleanup();
    break;

  case 'help':
  default:
    console.log(`
🧠 Memory Organizer v2.0 - 记忆整理工具

用法:
  memory-organizer scan              扫描所有记忆文件
  memory-organizer classify         按 Topic 分类记忆
  memory-organizer redundant        查找冗余记忆
  memory-organizer discard <文件>   丢弃指定记忆
  memory-organizer discard redundant [--force]  批量丢弃冗余记忆
  memory-organizer compress <文件>   压缩指定文件
  memory-organizer compress <文件> --titles  只保留标题
  memory-organizer compress <文件> --aggressive  激进压缩
  memory-organizer merge <文件>     合并到 MEMORY.md
  memory-organizer view <文件>      查看记忆内容
  memory-organizer clean            清理备份/丢弃文件

分类 Topic:
  - 用户偏好
  - 项目配置
  - 技能
  - 赚钱点子
  - 待办事项
  - 技术记录
  - 日常
`);
}
