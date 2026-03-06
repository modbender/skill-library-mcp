/**
 * 文件操作工具
 * 封装 fs-extra 提供便捷的文件操作
 */

import fs from 'fs-extra';
import path from 'path';
import { homedir } from 'os';

const CUECUE_DIR = path.join(homedir(), '.cuecue');

/**
 * 确保目录存在
 * @param {string} dir - 目录路径
 */
export async function ensureDir(dir) {
  await fs.ensureDir(dir);
}

/**
 * 读取 JSON 文件
 * @param {string} filePath - 文件路径
 * @returns {Promise<object>} JSON 对象
 */
export async function readJson(filePath) {
  try {
    return await fs.readJson(filePath);
  } catch (error) {
    if (error.code === 'ENOENT') {
      return null;
    }
    throw error;
  }
}

/**
 * 写入 JSON 文件
 * @param {string} filePath - 文件路径
 * @param {object} data - 数据对象
 */
export async function writeJson(filePath, data) {
  await fs.ensureDir(path.dirname(filePath));
  await fs.writeJson(filePath, data, { spaces: 2 });
}

/**
 * 获取用户数据目录
 * @param {string} chatId - 用户 ID
 * @returns {string} 用户目录路径
 */
export function getUserDir(chatId) {
  return path.join(CUECUE_DIR, 'users', chatId);
}

/**
 * 获取任务文件路径
 * @param {string} chatId - 用户 ID
 * @param {string} taskId - 任务 ID
 * @returns {string} 任务文件路径
 */
export function getTaskFilePath(chatId, taskId) {
  return path.join(getUserDir(chatId), 'tasks', `${taskId}.json`);
}

/**
 * 获取监控文件路径
 * @param {string} chatId - 用户 ID
 * @param {string} monitorId - 监控 ID
 * @returns {string} 监控文件路径
 */
export function getMonitorFilePath(chatId, monitorId) {
  return path.join(getUserDir(chatId), 'monitors', `${monitorId}.json`);
}

/**
 * 获取通知文件路径
 * @param {string} chatId - 用户 ID
 * @param {string} notificationId - 通知 ID
 * @returns {string} 通知文件路径
 */
export function getNotificationFilePath(chatId, notificationId) {
  return path.join(getUserDir(chatId), 'notifications', `${notificationId}.json`);
}

/**
 * 获取日志目录
 * @returns {string} 日志目录路径
 */
export function getLogDir() {
  return path.join(CUECUE_DIR, 'logs');
}

/**
 * 列出目录中的 JSON 文件
 * @param {string} dir - 目录路径
 * @returns {Promise<string[]>} 文件名列表
 */
export async function listJsonFiles(dir) {
  try {
    const files = await fs.readdir(dir);
    return files.filter(f => f.endsWith('.json')).sort().reverse();
  } catch (error) {
    if (error.code === 'ENOENT') {
      return [];
    }
    throw error;
  }
}

/**
 * 检查文件是否存在
 * @param {string} filePath - 文件路径
 * @returns {Promise<boolean>}
 */
export async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * 获取文件修改时间
 * @param {string} filePath - 文件路径
 * @returns {Promise<Date|null>}
 */
export async function getFileMtime(filePath) {
  try {
    const stats = await fs.stat(filePath);
    return stats.mtime;
  } catch {
    return null;
  }
}
