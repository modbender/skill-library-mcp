/**
 * DingTalk Group Saver
 * 当在钉钉群里被@时，自动保存群 ID 和群名字到 memory 中（双写：JSON + MEMORY.md）
 */

const fs = require('fs');
const path = require('path');

const MEMORY_FILE = path.join(
  process.env.HOME || process.env.USERPROFILE,
  '.openclaw/workspace/memory/dingtalk-groups.json'
);

const MEMORY_MD_FILE = path.join(
  process.env.HOME || process.env.USERPROFILE,
  '.openclaw/workspace/MEMORY.md'
);

/**
 * 确保 memory 文件存在
 */
function ensureMemoryFile() {
  const dir = path.dirname(MEMORY_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  if (!fs.existsSync(MEMORY_FILE)) {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify({ groups: [] }, null, 2));
  }
}

/**
 * 读取 memory 数据
 */
function readMemory() {
  ensureMemoryFile();
  const content = fs.readFileSync(MEMORY_FILE, 'utf-8');
  return JSON.parse(content);
}

/**
 * 写入 memory 数据
 */
function writeMemory(data) {
  ensureMemoryFile();
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(data, null, 2));
}

/**
 * 保存或更新群信息
 * @param {string} conversationId - 群 ID
 * @param {string} groupName - 群名字
 */
function saveGroup(conversationId, groupName) {
  const data = readMemory();
  const now = new Date().toISOString();
  
  // 查找是否已存在
  let group = data.groups.find(g => g.conversationId === conversationId);
  
  if (group) {
    // 更新现有记录
    group.lastActiveAt = now;
    group.mentionCount = (group.mentionCount || 0) + 1;
    if (groupName && !group.groupName) {
      group.groupName = groupName;
    }
  } else {
    // 添加新记录
    group = {
      conversationId,
      groupName: groupName || '未知群名',
      firstSeenAt: now,
      lastActiveAt: now,
      mentionCount: 1
    };
    data.groups.push(group);
  }
  
  writeMemory(data);
  
  // 同步更新 MEMORY.md
  updateMemoryMd(data.groups);
  
  return group;
}

/**
 * 更新 MEMORY.md 中的钉钉群列表
 * @param {Array} groups - 群信息数组
 */
function updateMemoryMd(groups) {
  if (!fs.existsSync(MEMORY_MD_FILE)) {
    console.log('MEMORY.md 不存在，跳过更新');
    return;
  }
  
  let content = fs.readFileSync(MEMORY_MD_FILE, 'utf-8');
  
  // 生成 Markdown 表格
  const tableLines = ['| # | 群名称 | 群 ID | 用途 |', '|---|--------|-------|------|'];
  groups.forEach((g, index) => {
    const usage = getUsageByGroupId(g.conversationId);
    tableLines.push(`| ${index + 1} | ${g.groupName} | \`${g.conversationId}\` | ${usage} |`);
  });
  
  const newTable = tableLines.join('\n');
  
  // 查找并替换现有的钉钉群列表表格部分
  const sectionStart = '### 钉钉群列表（推送渠道）';
  const sectionEnd = '```'; // 工具调用示例的代码块结束
  
  const startIndex = content.indexOf(sectionStart);
  if (startIndex === -1) {
    console.log('未找到钉钉群列表章节，跳过更新');
    return;
  }
  
  const endIndex = content.indexOf(sectionEnd, startIndex);
  if (endIndex === -1) {
    console.log('未找到章节结束位置，跳过更新');
    return;
  }
  
  // 保留章节标题和数据来源说明
  const sectionHeader = content.substring(startIndex, content.indexOf('**数据来源**', startIndex));
  const dataSource = '**数据来源**：`/Users/jiangzhiyu/.openclaw/workspace/memory/dingtalk-groups.json`\n\n';
  
  // 查找表格后的内容（推送策略等）
  const afterTableMarker = '**推送策略**：';
  const afterTableStart = content.indexOf(afterTableMarker, endIndex);
  const afterTable = afterTableStart !== -1 ? content.substring(afterTableStart) : '';
  
  // 构建新的章节内容
  const newSection = `${sectionHeader}${dataSource}\n${newTable}\n\n${afterTable}`;
  
  // 替换旧内容
  const oldSectionEnd = afterTableStart !== -1 ? afterTableStart : content.length;
  content = content.substring(0, startIndex) + newSection;
  
  fs.writeFileSync(MEMORY_MD_FILE, content, 'utf-8');
  console.log('已更新 MEMORY.md 中的钉钉群列表');
}

/**
 * 根据群 ID 推断用途描述
 * @param {string} conversationId - 群 ID
 */
function getUsageByGroupId(conversationId) {
  const usageMap = {
    'cid6CH8CYSLB23HHRelp0lNjw==': '主工作群，日常自动化任务沟通和指令执行',
    'cidSHnFBRXlRBNR2RWpvwXa6Q==': '机器人功能测试、AI 新闻推送',
    'cid/nWOdc+gYckMMykcuivBBA==': '测试群，用于接收 AI 新闻推送和测试消息'
  };
  return usageMap[conversationId] || '未知用途';
}

/**
 * 获取所有已保存的群
 */
function getAllGroups() {
  return readMemory().groups;
}

/**
 * 根据群 ID 查找群信息
 */
function getGroupById(conversationId) {
  const data = readMemory();
  return data.groups.find(g => g.conversationId === conversationId);
}

// 导出函数
module.exports = {
  saveGroup,
  getAllGroups,
  getGroupById,
  updateMemoryMd,
  MEMORY_FILE,
  MEMORY_MD_FILE
};

// 如果直接运行，测试功能
if (require.main === module) {
  console.log('DingTalk Group Saver - 测试模式');
  console.log('JSON Memory 文件:', MEMORY_FILE);
  console.log('MEMORY.md 文件:', MEMORY_MD_FILE);
  console.log('已保存的群:', getAllGroups());
}
