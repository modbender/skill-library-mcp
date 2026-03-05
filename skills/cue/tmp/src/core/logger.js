/**
 * 日志系统
 * 提供统一的日志记录功能
 */

import fs from 'fs-extra';
import path from 'path';
import { getLogDir } from '../utils/fileUtils.js';

/**
 * 日志级别
 */
export const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

/**
 * 日志类
 */
export class Logger {
  constructor(moduleName) {
    this.moduleName = moduleName;
    this.logDir = getLogDir();
    this.level = LogLevel.INFO;
  }

  /**
   * 获取日志文件路径
   * @returns {string}
   */
  getLogFilePath() {
    const today = new Date().toISOString().slice(0, 10);
    return path.join(this.logDir, `cue-${today}.log`);
  }

  /**
   * 格式化日志消息
   * @param {string} level - 日志级别
   * @param {string} message - 消息
   * @returns {string}
   */
  formatMessage(level, message) {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] [${this.moduleName}] ${message}`;
  }

  /**
   * 写入日志
   * @param {string} level - 日志级别
   * @param {string} message - 消息
   */
  async log(level, message) {
    try {
      await fs.ensureDir(this.logDir);
      const logLine = this.formatMessage(level, message) + '\n';
      await fs.appendFile(this.getLogFilePath(), logLine);
    } catch (error) {
      console.error('Failed to write log:', error);
    }
  }

  /**
   * 调试日志
   * @param {string} message
   */
  async debug(message) {
    if (this.level <= LogLevel.DEBUG) {
      await this.log('DEBUG', message);
    }
  }

  /**
   * 信息日志
   * @param {string} message
   */
  async info(message) {
    if (this.level <= LogLevel.INFO) {
      await this.log('INFO', message);
      console.log(message);
    }
  }

  /**
   * 警告日志
   * @param {string} message
   */
  async warn(message) {
    if (this.level <= LogLevel.WARN) {
      await this.log('WARN', message);
      console.warn('⚠️', message);
    }
  }

  /**
   * 错误日志
   * @param {string} message
   * @param {Error} [error]
   */
  async error(message, error = null) {
    if (this.level <= LogLevel.ERROR) {
      const fullMessage = error ? `${message}: ${error.message}` : message;
      await this.log('ERROR', fullMessage);
      console.error('❌', fullMessage);
      
      if (error?.stack) {
        await this.log('ERROR', error.stack);
      }
    }
  }

  /**
   * 设置日志级别
   * @param {number} level
   */
  setLevel(level) {
    this.level = level;
  }
}

/**
 * 创建日志实例
 * @param {string} moduleName - 模块名称
 * @returns {Logger}
 */
export function createLogger(moduleName) {
  return new Logger(moduleName);
}
