/**
 * 用户状态管理
 * 管理用户初始化状态和版本信息
 */

import fs from 'fs-extra';
import path from 'path';
import { getUserDir, ensureDir } from '../utils/fileUtils.js';
import { createLogger } from './logger.js';

const logger = createLogger('UserState');

const CURRENT_VERSION = '1.0.4';

/**
 * 用户状态类
 */
export class UserState {
  constructor(chatId) {
    this.chatId = chatId;
    this.userDir = getUserDir(chatId);
    this.initializedFile = path.join(this.userDir, '.initialized');
    this.versionFile = path.join(this.userDir, '.version');
  }

  /**
   * 检查是否首次使用
   * @returns {Promise<boolean>}
   */
  async isFirstTime() {
    try {
      await fs.access(this.initializedFile);
      return false;
    } catch {
      return true;
    }
  }

  /**
   * 标记用户已初始化
   */
  async markInitialized() {
    await ensureDir(this.userDir);
    await fs.writeFile(this.initializedFile, '');
    await fs.writeFile(this.versionFile, CURRENT_VERSION);
    await logger.info(`User ${this.chatId} initialized`);
  }

  /**
   * 检查版本状态
   * @returns {Promise<'first_time'|'updated'|'normal'>}
   */
  async checkVersion() {
    // 首次使用
    if (await this.isFirstTime()) {
      return 'first_time';
    }

    // 检查版本
    try {
      const savedVersion = await fs.readFile(this.versionFile, 'utf-8');
      if (savedVersion.trim() !== CURRENT_VERSION) {
        // 版本更新
        await fs.writeFile(this.versionFile, CURRENT_VERSION);
        return 'updated';
      }
    } catch (error) {
      await logger.error('Failed to read version file', error);
    }

    return 'normal';
  }

  /**
   * 获取用户数据目录
   * @returns {string}
   */
  getUserDir() {
    return this.userDir;
  }

  /**
   * 获取任务目录
   * @returns {string}
   */
  getTasksDir() {
    return path.join(this.userDir, 'tasks');
  }

  /**
   * 获取监控目录
   * @returns {string}
   */
  getMonitorsDir() {
    return path.join(this.userDir, 'monitors');
  }

  /**
   * 获取通知目录
   * @returns {string}
   */
  getNotificationsDir() {
    return path.join(this.userDir, 'notifications');
  }
}

/**
 * 创建用户状态实例
 * @param {string} chatId
 * @returns {UserState}
 */
export function createUserState(chatId) {
  return new UserState(chatId);
}
