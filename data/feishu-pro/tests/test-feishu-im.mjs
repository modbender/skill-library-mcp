import fs from 'fs';
import os from 'os';
import path from 'path';
import {
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
} from '../dist/index.js';
import { applyFeishuDefaults, createStats, logSuiteStart, logSuiteEnd, runCase } from './_utils.mjs';

applyFeishuDefaults();

const stats = createStats();
logSuiteStart('feishu/im (消息/话题/群聊)');

const getChatId = () => process.env.TEST_CHAT_ID;
let messageId = process.env.TEST_MESSAGE_ID;
let threadRootId = process.env.TEST_THREAD_ROOT_ID || process.env.TEST_MESSAGE_ID;

function extractMessageId(response) {
  return (
    response?.data?.message_id ||
    response?.data?.message?.message_id ||
    response?.message_id
  );
}

function ensureAttachmentPath() {
  if (process.env.TEST_ATTACHMENT_PATH) return process.env.TEST_ATTACHMENT_PATH;
  if (process.env.ALLOW_SIDE_EFFECTS !== '1') return undefined;
  const filePath = path.join(os.tmpdir(), `openclaw-feishu-attachment-${Date.now()}.txt`);
  fs.writeFileSync(filePath, `OpenClaw test attachment ${new Date().toISOString()}\n`);
  process.env.TEST_ATTACHMENT_PATH = filePath;
  return filePath;
}

const attachmentPath = ensureAttachmentPath();
const chatMemberIds = (process.env.TEST_CHAT_MEMBER_IDS || '').split(',').map(s => s.trim()).filter(Boolean);
const createChatUserIds = (process.env.TEST_CREATE_CHAT_USER_IDS || '').split(',').map(s => s.trim()).filter(Boolean);

await runCase(stats, {
  name: 'listChats',
  fn: () => listChats(),
});

await runCase(stats, {
  name: 'getChatInfo',
  requires: ['TEST_CHAT_ID'],
  fn: () => getChatInfo(getChatId()),
});

await runCase(stats, {
  name: 'getChatMembers',
  requires: ['TEST_CHAT_ID'],
  fn: () => getChatMembers(getChatId()),
});

await runCase(stats, {
  name: 'isInChat',
  requires: ['TEST_CHAT_ID'],
  fn: () => isInChat(getChatId()),
});

await runCase(stats, {
  name: 'listMessages',
  requires: ['TEST_CHAT_ID'],
  fn: () => listMessages({ container_id_type: 'chat', container_id: getChatId() }),
});

await runCase(stats, {
  name: 'sendAttachment',
  requires: ['TEST_CHAT_ID', 'TEST_ATTACHMENT_PATH'],
  sideEffect: true,
  fn: async () => {
    const res = await sendAttachment(getChatId(), 'chat_id', attachmentPath);
    const id = extractMessageId(res);
    if (id) {
      messageId = id;
      if (!process.env.TEST_MESSAGE_ID) process.env.TEST_MESSAGE_ID = id;
      if (!process.env.TEST_THREAD_ROOT_ID) process.env.TEST_THREAD_ROOT_ID = id;
    }
    return res;
  },
});

await runCase(stats, {
  name: 'react',
  requires: ['TEST_MESSAGE_ID'],
  sideEffect: true,
  fn: () => react(messageId, '👍'),
});

await runCase(stats, {
  name: 'pinMessage',
  requires: ['TEST_MESSAGE_ID'],
  sideEffect: true,
  fn: () => pinMessage(messageId),
});

await runCase(stats, {
  name: 'unpinMessage',
  requires: ['TEST_MESSAGE_ID'],
  sideEffect: true,
  fn: () => unpinMessage(messageId),
});

await runCase(stats, {
  name: 'recallMessage',
  requires: ['TEST_MESSAGE_ID'],
  destructive: true,
  fn: () => recallMessage(messageId),
});

await runCase(stats, {
  name: 'updateMessage',
  requires: ['TEST_PATCH_MESSAGE_ID'],
  sideEffect: true,
  fn: () => updateMessage(process.env.TEST_PATCH_MESSAGE_ID, 'OpenClaw test update'),
});

await runCase(stats, {
  name: 'replyInThread',
  requires: ['TEST_THREAD_ROOT_ID'],
  sideEffect: true,
  fn: () => {
    threadRootId = process.env.TEST_THREAD_ROOT_ID || messageId;
    return replyInThread(threadRootId, 'OpenClaw thread reply');
  },
});

await runCase(stats, {
  name: 'listThreadMessages',
  requires: ['TEST_CHAT_ID', 'TEST_THREAD_ROOT_ID'],
  fn: () => {
    threadRootId = process.env.TEST_THREAD_ROOT_ID || messageId;
    return listThreadMessages(getChatId(), threadRootId);
  },
});

await runCase(stats, {
  name: 'createChat',
  requires: ['TEST_CREATE_CHAT_USER_IDS'],
  sideEffect: true,
  fn: () => createChat({ name: 'OpenClaw Test Chat', user_id_list: createChatUserIds }),
});

await runCase(stats, {
  name: 'addChatMembers',
  requires: ['TEST_CHAT_ID', 'TEST_CHAT_MEMBER_IDS'],
  sideEffect: true,
  fn: () => addChatMembers(getChatId(), chatMemberIds),
});

await runCase(stats, {
  name: 'removeChatMembers',
  requires: ['TEST_CHAT_ID', 'TEST_CHAT_MEMBER_IDS'],
  destructive: true,
  fn: () => removeChatMembers(getChatId(), chatMemberIds),
});

logSuiteEnd('feishu/im', stats);
