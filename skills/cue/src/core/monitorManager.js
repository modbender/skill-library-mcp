/**
 * 监控管理
 * 管理监控项的创建、更新和查询
 */

import fs from 'fs-extra';
import path from 'path';
import { getMonitorFilePath, listJsonFiles, ensureDir, getUserDir } from '../utils/fileUtils.js';
import { createLogger } from './logger.js';

const logger = createLogger('MonitorManager');

/**
 * 监控管理类
 */
export class MonitorManager {
  constructor(chatId) {
    this.chatId = chatId;
    this.monitorsDir = path.join(getUserDir(chatId), 'monitors');
  }

  /**
   * 创建监控项
   * @param {Object} monitorData - 监控数据
   * @returns {Promise<Object>}
   */
  async createMonitor(monitorData) {
    const { monitorId, title, symbol, category, trigger } = monitorData;
    
    await ensureDir(this.monitorsDir);
    
    const monitor = {
      monitor_id: monitorId,
      title,
      symbol,
      category,
      semantic_trigger: trigger,
      is_active: true,
      created_at: new Date().toISOString(),
      ...monitorData
    };
    
    const filePath = getMonitorFilePath(this.chatId, monitorId);
    await fs.writeJson(filePath, monitor, { spaces: 2 });
    
    await logger.info(`Monitor created: ${monitorId}`);
    return monitor;
  }

  /**
   * 更新监控项
   * @param {string} monitorId - 监控 ID
   * @param {Object} updates - 更新数据
   * @returns {Promise<Object|null>}
   */
  async updateMonitor(monitorId, updates) {
    const filePath = getMonitorFilePath(this.chatId, monitorId);
    
    try {
      const monitor = await fs.readJson(filePath);
      const updatedMonitor = { ...monitor, ...updates };
      await fs.writeJson(filePath, updatedMonitor, { spaces: 2 });
      await logger.info(`Monitor updated: ${monitorId}`);
      return updatedMonitor;
    } catch (error) {
      await logger.error(`Failed to update monitor ${monitorId}`, error);
      return null;
    }
  }

  /**
   * 获取监控项
   * @param {string} monitorId - 监控 ID
   * @returns {Promise<Object|null>}
   */
  async getMonitor(monitorId) {
    const filePath = getMonitorFilePath(this.chatId, monitorId);
    
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
   * 获取监控列表
   * @param {number} limit - 限制数量
   * @returns {Promise<Array>}
   */
  async getMonitors(limit = 15) {
    const files = await listJsonFiles(this.monitorsDir);
    const monitors = [];
    
    for (const file of files.slice(0, limit)) {
      try {
        const monitor = await fs.readJson(path.join(this.monitorsDir, file));
        monitors.push(monitor);
      } catch (error) {
        await logger.error(`Failed to read monitor ${file}`, error);
      }
    }
    
    return monitors;
  }

  /**
   * 获取激活的监控
   * @returns {Promise<Array>}
   */
  async getActiveMonitors() {
    const monitors = await this.getMonitors(100);
    return monitors.filter(m => m.is_active !== false);
  }

  /**
   * 统计监控数量
   * @returns {Promise<{total: number, active: number}>}
   */
  async getStats() {
    const monitors = await this.getMonitors(1000);
    return {
      total: monitors.length,
      active: monitors.filter(m => m.is_active !== false).length
    };
  }
}

/**
 * 创建监控管理器实例
 * @param {string} chatId
 * @returns {MonitorManager}
 */
export function createMonitorManager(chatId) {
  return new MonitorManager(chatId);
}
