/**
 * 可靠通知队列
 * 本地持久化 + 失败重试机制
 */

import fs from 'fs-extra';
import path from 'path';
import { getUserDir } from './fileUtils.js';
import { createLogger } from '../core/logger.js';

const logger = createLogger('NotificationQueue');

/**
 * 获取通知队列目录
 * @param {string} chatId 
 * @returns {string}
 */
function getQueueDir(chatId) {
  return path.join(getUserDir(chatId), 'notification-queue');
}

/**
 * 初始化队列目录
 * @param {string} chatId 
 */
async function initQueue(chatId) {
  const queueDir = getQueueDir(chatId);
  await fs.ensureDir(queueDir);
  
  // 创建子目录
  await fs.ensureDir(path.join(queueDir, 'pending'));
  await fs.ensureDir(path.join(queueDir, 'failed'));
  await fs.ensureDir(path.join(queueDir, 'sent'));
}

/**
 * 生成通知 ID
 * @returns {string}
 */
function generateNotificationId() {
  return `notif_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * 添加通知到队列
 * @param {Object} notification 
 * @param {string} notification.chatId 
 * @param {string} notification.type - 类型: 'research_complete', 'monitor_trigger', 'progress'
 * @param {Object} notification.data - 通知数据
 * @returns {Promise<string>} 通知 ID
 */
export async function enqueueNotification({ chatId, type, data }) {
  await initQueue(chatId);
  
  const notificationId = generateNotificationId();
  const notification = {
    id: notificationId,
    chat_id: chatId,
    type,
    data,
    status: 'pending',
    created_at: new Date().toISOString(),
    retry_count: 0,
    max_retries: 3
  };
  
  const queueDir = getQueueDir(chatId);
  const filePath = path.join(queueDir, 'pending', `${notificationId}.json`);
  
  await fs.writeJson(filePath, notification, { spaces: 2 });
  await logger.info(`Notification enqueued: ${notificationId} (${type})`);
  
  return notificationId;
}

/**
 * 获取待发送通知
 * @param {string} chatId 
 * @returns {Promise<Array>}
 */
export async function getPendingNotifications(chatId) {
  try {
    const queueDir = getQueueDir(chatId);
    const pendingDir = path.join(queueDir, 'pending');
    
    const files = await fs.readdir(pendingDir);
    const notifications = [];
    
    for (const file of files.filter(f => f.endsWith('.json'))) {
      try {
        const notif = await fs.readJson(path.join(pendingDir, file));
        if (notif.status === 'pending') {
          notifications.push(notif);
        }
      } catch (e) {
        // 忽略读取错误
      }
    }
    
    // 按创建时间排序
    return notifications.sort((a, b) => 
      new Date(a.created_at) - new Date(b.created_at)
    );
  } catch (error) {
    return [];
  }
}

/**
 * 标记通知为已发送
 * @param {string} chatId 
 * @param {string} notificationId 
 */
export async function markNotificationSent(chatId, notificationId) {
  try {
    const queueDir = getQueueDir(chatId);
    const pendingPath = path.join(queueDir, 'pending', `${notificationId}.json`);
    const sentPath = path.join(queueDir, 'sent', `${notificationId}.json`);
    
    // 读取并更新状态
    const notification = await fs.readJson(pendingPath);
    notification.status = 'sent';
    notification.sent_at = new Date().toISOString();
    
    // 移动到 sent 目录
    await fs.writeJson(sentPath, notification, { spaces: 2 });
    await fs.remove(pendingPath);
    
    await logger.info(`Notification marked as sent: ${notificationId}`);
  } catch (error) {
    await logger.error(`Failed to mark notification as sent: ${notificationId}`, error);
  }
}

/**
 * 标记通知为失败
 * @param {string} chatId 
 * @param {string} notificationId 
 * @param {string} error 
 */
export async function markNotificationFailed(chatId, notificationId, error) {
  try {
    const queueDir = getQueueDir(chatId);
    const pendingPath = path.join(queueDir, 'pending', `${notificationId}.json`);
    const failedPath = path.join(queueDir, 'failed', `${notificationId}.json`);
    
    // 读取通知
    const notification = await fs.readJson(pendingPath);
    notification.retry_count++;
    notification.last_error = error;
    notification.last_attempt = new Date().toISOString();
    
    if (notification.retry_count >= notification.max_retries) {
      // 超过最大重试次数，移动到失败目录
      notification.status = 'failed';
      await fs.writeJson(failedPath, notification, { spaces: 2 });
      await fs.remove(pendingPath);
      await logger.warn(`Notification failed permanently: ${notificationId} (${notification.retry_count} retries)`);
    } else {
      // 更新重试计数，保留在 pending 目录
      await fs.writeJson(pendingPath, notification, { spaces: 2 });
      await logger.info(`Notification retry scheduled: ${notificationId} (attempt ${notification.retry_count})`);
    }
  } catch (err) {
    await logger.error(`Failed to mark notification failed: ${notificationId}`, err);
  }
}

/**
 * 获取需要重试的通知
 * @param {string} chatId 
 * @returns {Promise<Array>}
 */
export async function getNotificationsForRetry(chatId) {
  const pending = await getPendingNotifications(chatId);
  const now = Date.now();
  
  return pending.filter(notif => {
    if (notif.retry_count === 0) return true;
    
    // 指数退避：1分钟, 5分钟, 25分钟
    const backoffMinutes = Math.pow(5, notif.retry_count - 1);
    const lastAttempt = new Date(notif.last_attempt || notif.created_at).getTime();
    const nextRetry = lastAttempt + (backoffMinutes * 60 * 1000);
    
    return now >= nextRetry;
  });
}

/**
 * 获取失败通知列表
 * @param {string} chatId 
 * @param {number} limit 
 * @returns {Promise<Array>}
 */
export async function getFailedNotifications(chatId, limit = 10) {
  try {
    const queueDir = getQueueDir(chatId);
    const failedDir = path.join(queueDir, 'failed');
    
    const files = await fs.readdir(failedDir);
    const notifications = [];
    
    for (const file of files.filter(f => f.endsWith('.json')).slice(0, limit)) {
      try {
        const notif = await fs.readJson(path.join(failedDir, file));
        notifications.push(notif);
      } catch (e) {
        // 忽略
      }
    }
    
    return notifications.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    );
  } catch (error) {
    return [];
  }
}

/**
 * 清理已发送通知（保留最近7天）
 * @param {string} chatId 
 */
export async function cleanupSentNotifications(chatId) {
  try {
    const queueDir = getQueueDir(chatId);
    const sentDir = path.join(queueDir, 'sent');
    
    const files = await fs.readdir(sentDir);
    const cutoff = Date.now() - (7 * 24 * 60 * 60 * 1000); // 7天前
    
    let cleaned = 0;
    for (const file of files.filter(f => f.endsWith('.json'))) {
      try {
        const notif = await fs.readJson(path.join(sentDir, file));
        const sentAt = new Date(notif.sent_at || notif.created_at).getTime();
        
        if (sentAt < cutoff) {
          await fs.remove(path.join(sentDir, file));
          cleaned++;
        }
      } catch (e) {
        // 忽略
      }
    }
    
    if (cleaned > 0) {
      await logger.info(`Cleaned up ${cleaned} old sent notifications`);
    }
  } catch (error) {
    await logger.error('Failed to cleanup sent notifications', error);
  }
}

/**
 * 启动后台通知处理器
 * @param {string} chatId 
 * @param {Function} sendFn - 实际发送函数
 */
export function startNotificationProcessor(chatId, sendFn) {
  // 立即处理一次
  processNotificationQueue(chatId, sendFn);
  
  // 每30秒检查一次队列
  const intervalId = setInterval(() => {
    processNotificationQueue(chatId, sendFn);
  }, 30000);
  
  // 每小时清理一次已发送通知
  const cleanupInterval = setInterval(() => {
    cleanupSentNotifications(chatId);
  }, 60 * 60 * 1000);
  
  return {
    stop: () => {
      clearInterval(intervalId);
      clearInterval(cleanupInterval);
    }
  };
}

/**
 * 处理通知队列
 * @param {string} chatId 
 * @param {Function} sendFn 
 */
async function processNotificationQueue(chatId, sendFn) {
  try {
    const notifications = await getNotificationsForRetry(chatId);
    
    for (const notif of notifications) {
      try {
        await logger.info(`Processing notification: ${notif.id}`);
        
        // 调用实际发送函数
        const success = await sendFn(notif);
        
        if (success) {
          await markNotificationSent(chatId, notif.id);
        } else {
          await markNotificationFailed(chatId, notif.id, 'Send returned false');
        }
      } catch (error) {
        await markNotificationFailed(chatId, notif.id, error.message);
      }
    }
  } catch (error) {
    await logger.error('Failed to process notification queue', error);
  }
}
