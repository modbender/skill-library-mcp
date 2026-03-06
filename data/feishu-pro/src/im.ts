import * as fs from 'fs';
import * as path from 'path';
import { createClient } from '@openclaw-feishu/feishu-client';
import { formatEmoji, formatMessage } from '@openclaw-feishu/feishu-utils';

function getAuth() {
  const appId = process.env.FEISHU_APP_ID;
  const appSecret = process.env.FEISHU_APP_SECRET;
  if (!appId || !appSecret) throw new Error('Missing FEISHU_APP_ID or FEISHU_APP_SECRET');
  return { appId, appSecret };
}

/**
 * 列出消息
 */
export async function listMessages(params: { container_id_type: 'chat'; container_id: string; page_token?: string; page_size?: number }) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });
  return await client.call(() => client.getClient().im.message.list({
    params: {
      container_id_type: params.container_id_type,
      container_id: params.container_id,
      page_token: params.page_token,
      page_size: params.page_size || 20,
    }
  }));
}

/**
 * 撤回消息 (实际上是删除自己发送的消息)
 */
export async function recallMessage(messageId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });
  return await client.call(() => client.getClient().im.message.delete({
    path: { message_id: messageId }
  }));
}

/**
 * 更新消息内容 (仅支持消息卡片 patch)
 */
export async function updateMessage(messageId: string, content: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });
  return await client.call(() => client.getClient().im.message.patch({
    path: { message_id: messageId },
    data: { content: formatMessage(content) }
  }));
}

/**
 * Pin 消息
 */
export async function pinMessage(messageId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });
  return await client.call(() => client.getClient().im.pin.create({
    data: { message_id: messageId }
  }));
}

/**
 * 移除 Pin 消息
 */
export async function unpinMessage(messageId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });
  return await client.call(() => client.getClient().im.pin.delete({
    path: { message_id: messageId }
  }));
}

/**
 * 表情反应
 */
export async function react(messageId: string, emoji: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });
  const emojiType = formatEmoji(emoji);

  return await client.call(() => client.getClient().im.messageReaction.create({
    path: { message_id: messageId },
    data: {
      reaction_type: {
        emoji_type: emojiType,
      },
    },
  }));
}

/**
 * 发送附件（图片或文件）
 * @param receiveId - 接收人/群 ID
 * @param receiveIdType - 接收人 ID 类型 (open_id, user_id, chat_id)
 * @param filePath - 文件本地路径
 * @param fileName - 文件名（可选）
 */
export async function sendAttachment(receiveId: string, receiveIdType: 'open_id' | 'user_id' | 'chat_id', filePath: string, fileName?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  if (!fs.existsSync(filePath)) {
    return { ok: false, error: `文件不存在: ${filePath}` };
  }

  const ext = path.extname(filePath).toLowerCase();
  const isImage = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'].includes(ext);
  const finalFileName = fileName || path.basename(filePath);

  try {
    let key: string | undefined;
    let msgType: string;

    if (isImage) {
      const uploadRes = await client.getClient().im.image.create({
        data: {
          image_type: 'message',
          image: fs.createReadStream(filePath),
        }
      });
      key = uploadRes?.image_key;
      msgType = 'image';
    } else {
      const uploadRes = await client.getClient().im.file.create({
        data: {
          file_type: 'stream',
          file_name: finalFileName,
          file: fs.createReadStream(filePath),
        }
      });
      key = uploadRes?.file_key;
      msgType = 'file';
    }

    if (!key) {
      return { ok: false, error: '文件上传失败，未获得 Key' };
    }

    // 发送消息
    return await client.call(() => client.getClient().im.message.create({
      params: { receive_id_type: receiveIdType },
      data: {
        receive_id: receiveId,
        msg_type: msgType,
        content: JSON.stringify({ [msgType === 'image' ? 'image_key' : 'file_key']: key }),
      }
    }));
  } catch (error: any) {
    return { ok: false, error: error.message || '发送附件过程中发生错误' };
  }
}

/**
 * 话题回复
 */
export async function replyInThread(messageId: string, content: string, replyInThread: boolean = true, msgType: 'text' | 'post' | 'interactive' = 'text') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.message.reply({
    path: { message_id: messageId },
    data: {
      content: formatMessage(content, msgType),
      msg_type: msgType,
      reply_in_thread: replyInThread,
    }
  }));
}

/**
 * 获取话题消息
 */
export async function listThreadMessages(chatId: string, threadId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  const res = await client.call(() => client.getClient().im.message.list({
    params: {
      container_id_type: 'chat',
      container_id: chatId,
      page_size: 50,
    }
  }));

  if (res.ok && res.data?.items) {
    res.data.items = res.data.items.filter((item: any) => item.thread_id === threadId || item.message_id === threadId);
  }

  return res;
}

/**
 * 获取群聊信息
 * @param chatId - 群聊 ID
 */
export async function getChatInfo(chatId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chat.get({
    path: { chat_id: chatId }
  }));
}

/**
 * 获取群聊列表
 */
export async function listChats(pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chat.list({
    params: {
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 获取群成员列表
 */
export async function getChatMembers(chatId: string, memberIdType: 'user_id' | 'union_id' | 'open_id' = 'open_id', pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chatMembers.get({
    path: { chat_id: chatId },
    params: {
      member_id_type: memberIdType,
      page_token: pageToken,
      page_size: pageSize || 100,
    }
  }));
}

/**
 * 判断用户是否在群里
 */
export async function isInChat(chatId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chatMembers.isInChat({
    path: { chat_id: chatId }
  }));
}

/**
 * 创建群聊
 */
export async function createChat(params: { name?: string; description?: string; user_id_list?: string[]; bot_id_list?: string[]; chat_type?: 'private' | 'public' }) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chat.create({
    data: {
      name: params.name,
      description: params.description,
      user_id_list: params.user_id_list,
      bot_id_list: params.bot_id_list,
      chat_type: params.chat_type || 'private',
    },
    params: {
      user_id_type: 'open_id',
    }
  }));
}

/**
 * 拉人进群
 */
export async function addChatMembers(chatId: string, idList: string[], memberIdType: 'user_id' | 'union_id' | 'open_id' = 'open_id') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chatMembers.create({
    path: { chat_id: chatId },
    data: {
      id_list: idList,
    },
    params: {
      member_id_type: memberIdType,
    }
  }));
}

/**
 * 踢人出群
 */
export async function removeChatMembers(chatId: string, idList: string[], memberIdType: 'user_id' | 'union_id' | 'open_id' = 'open_id') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().im.chatMembers.delete({
    path: { chat_id: chatId },
    data: {
      id_list: idList,
    },
    params: {
      member_id_type: memberIdType,
    }
  }));
}
