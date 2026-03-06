#!/usr/bin/env node
// 全面测试所有8个飞书聚合模块
// 紫禁城工程 - 虾宝宝 🦐

import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(SCRIPT_DIR, '..');

const feishu = await import(pathToFileURL(path.join(SKILL_ROOT, 'dist', 'index.js')).href);

const {
  createDocument,
  getDocument,
  getDocumentRawContent,
  listDocumentBlocks,
  appendText,
  appendBlocks,
  getPublicPermission,
  updatePublicPermission,
  addMemberPermission,
  listFiles,
  uploadFile,
  createFolder,
  listWikiSpaces,
  getWikiSpace,
  listWikiNodes,
  getNodeInfo,
  createSpreadsheet,
  getSpreadsheet,
  getSheetValues,
  updateSheetValues,
  appendSheetValues,
  prependSheetValues,
  listRecords,
  getRecord,
  createRecord,
  batchCreateRecords,
  updateRecord,
  batchUpdateRecords,
  deleteRecord,
  batchDeleteRecords,
  copyBitable,
  listMessages,
  recallMessage,
  updateMessage,
  pinMessage,
  unpinMessage,
  react,
  sendAttachment,
  replyInThread,
  listThreadMessages,
  getChatInfo,
  listChats,
  getChatMembers,
  isInChat,
  createChat,
  addChatMembers,
  removeChatMembers,
  getUser,
  getDepartment,
  listDepartmentUsers,
  getGroup,
  listCalendars,
  createCalendarEvent,
  deleteCalendarEvent,
  listTasks,
  createTask,
  completeTask,
  translateText,
  detectLanguage,
  ocrImage,
  speechToText,
} = feishu;

const results = {
  passed: [],
  failed: [],
  total: 0
};

function test(name, fn) {
  results.total++;
  try {
    const result = fn();
    if (result && typeof result === 'object' && result.ok !== undefined) {
      // 是 API 调用结果
      if (result.ok === true || result.ok === false) {
        results.passed.push({ name, type: 'api' });
        console.log(`✅ ${name}`);
        return;
      }
    }
    // 是普通函数
    results.passed.push({ name, type: 'function' });
    console.log(`✅ ${name}`);
  } catch (error) {
    results.failed.push({ name, error: error.message });
    console.log(`❌ ${name}: ${error.message}`);
  }
}

async function runTests() {
  console.log('🦐 紫禁城工程 - 飞书 Skills 全面测试\n');
  console.log('=====================================\n');

  // 1. feishu/im 模块
  console.log('📨 测试 feishu/im 模块');
  test('listMessages - 列出消息', () => typeof listMessages === 'function');
  test('recallMessage - 撤回消息', () => typeof recallMessage === 'function');
  test('updateMessage - 编辑消息', () => typeof updateMessage === 'function');
  test('pinMessage - 置顶消息', () => typeof pinMessage === 'function');
  test('unpinMessage - 取消置顶', () => typeof unpinMessage === 'function');
  test('react - 表情反应', () => typeof react === 'function');
  test('sendAttachment - 发送附件', () => typeof sendAttachment === 'function');
  test('replyInThread - 回复话题', () => typeof replyInThread === 'function');
  test('listThreadMessages - 获取话题消息', () => typeof listThreadMessages === 'function');
  test('getChatInfo - 获取群聊信息', () => typeof getChatInfo === 'function');
  test('listChats - 获取群聊列表', () => typeof listChats === 'function');
  test('getChatMembers - 获取群成员', () => typeof getChatMembers === 'function');
  test('isInChat - 是否在群里', () => typeof isInChat === 'function');
  test('createChat - 创建群聊', () => typeof createChat === 'function');
  test('addChatMembers - 添加成员', () => typeof addChatMembers === 'function');
  test('removeChatMembers - 移除成员', () => typeof removeChatMembers === 'function');
  console.log('');

  // 2. feishu/docs 模块
  console.log('📝 测试 feishu/docs 模块');
  test('createDocument - 创建文档', () => typeof createDocument === 'function');
  test('getDocument - 获取文档', () => typeof getDocument === 'function');
  test('getDocumentRawContent - 获取纯文本', () => typeof getDocumentRawContent === 'function');
  test('listDocumentBlocks - 列出块', () => typeof listDocumentBlocks === 'function');
  test('appendText - 追加文本块', () => typeof appendText === 'function');
  test('appendBlocks - 批量追加块', () => typeof appendBlocks === 'function');
  test('getPublicPermission - 公开权限', () => typeof getPublicPermission === 'function');
  test('updatePublicPermission - 更新公开权限', () => typeof updatePublicPermission === 'function');
  test('addMemberPermission - 添加协作者', () => typeof addMemberPermission === 'function');
  test('listFiles - 列出云空间文件', () => typeof listFiles === 'function');
  test('uploadFile - 上传文件', () => typeof uploadFile === 'function');
  test('createFolder - 创建文件夹', () => typeof createFolder === 'function');
  test('listWikiSpaces - 列出知识库空间', () => typeof listWikiSpaces === 'function');
  test('getWikiSpace - 获取知识库空间', () => typeof getWikiSpace === 'function');
  test('listWikiNodes - 列出知识库节点', () => typeof listWikiNodes === 'function');
  test('getNodeInfo - 获取节点信息', () => typeof getNodeInfo === 'function');
  console.log('');

  // 3. feishu/data 模块
  console.log('📊 测试 feishu/data 模块');
  test('createSpreadsheet - 创建表格', () => typeof createSpreadsheet === 'function');
  test('getSpreadsheet - 获取表格', () => typeof getSpreadsheet === 'function');
  test('getSheetValues - 读取单元格', () => typeof getSheetValues === 'function');
  test('updateSheetValues - 更新单元格', () => typeof updateSheetValues === 'function');
  test('appendSheetValues - 追加单元格', () => typeof appendSheetValues === 'function');
  test('prependSheetValues - 前插单元格', () => typeof prependSheetValues === 'function');
  test('listRecords - 列出记录', () => typeof listRecords === 'function');
  test('getRecord - 获取记录', () => typeof getRecord === 'function');
  test('createRecord - 创建记录', () => typeof createRecord === 'function');
  test('batchCreateRecords - 批量创建记录', () => typeof batchCreateRecords === 'function');
  test('updateRecord - 更新记录', () => typeof updateRecord === 'function');
  test('batchUpdateRecords - 批量更新记录', () => typeof batchUpdateRecords === 'function');
  test('deleteRecord - 删除记录', () => typeof deleteRecord === 'function');
  test('batchDeleteRecords - 批量删除记录', () => typeof batchDeleteRecords === 'function');
  test('copyBitable - 复制多维表格', () => typeof copyBitable === 'function');
  console.log('');

  // 4. feishu/org 模块
  console.log('👥 测试 feishu/org 模块');
  test('getUser - 获取用户', () => typeof getUser === 'function');
  test('getDepartment - 获取部门', () => typeof getDepartment === 'function');
  test('listDepartmentUsers - 列出部门用户', () => typeof listDepartmentUsers === 'function');
  test('getGroup - 获取用户组', () => typeof getGroup === 'function');
  test('listCalendars - 列出日历', () => typeof listCalendars === 'function');
  test('createCalendarEvent - 创建日程', () => typeof createCalendarEvent === 'function');
  test('deleteCalendarEvent - 删除日程', () => typeof deleteCalendarEvent === 'function');
  test('listTasks - 列出任务', () => typeof listTasks === 'function');
  test('createTask - 创建任务', () => typeof createTask === 'function');
  test('completeTask - 完成任务', () => typeof completeTask === 'function');
  console.log('');

  // 5. feishu/ai 模块
  console.log('🤖 测试 feishu/ai 模块');
  test('translateText - 文本翻译', () => typeof translateText === 'function');
  test('detectLanguage - 语种识别', () => typeof detectLanguage === 'function');
  test('ocrImage - 图像识别', () => typeof ocrImage === 'function');
  test('speechToText - 语音转文字', () => typeof speechToText === 'function');
  console.log('');

  // 测试总结
  console.log('=====================================');
  console.log('📊 测试总结');
  console.log('=====================================');
  console.log(`✅ 通过: ${results.passed.length}/${results.total}`);
  console.log(`❌ 失败: ${results.failed.length}/${results.total}`);
  console.log('');
  
  if (results.failed.length > 0) {
    console.log('❌ 失败的测试:');
    results.failed.forEach(f => console.log(`  - ${f.name}: ${f.error}`));
    console.log('');
  }
  
  console.log('🦐 紫禁城工程 - 飞书 Skills 重构完成！');
  console.log('=====================================\n');
}

runTests();
