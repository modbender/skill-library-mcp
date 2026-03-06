/**
 * 任务管理
 * 管理研究任务的创建、更新和查询
 */

import fs from 'fs-extra';
import path from 'path';
import { getTaskFilePath, listJsonFiles, ensureDir, getUserDir } from '../utils/fileUtils.js';
import { createLogger } from './logger.js';

const logger = createLogger('TaskManager');

/**
 * 任务状态枚举
 */
export const TaskStatus = {
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  TIMEOUT: 'timeout'
};

/**
 * 任务管理类
 */
export class TaskManager {
  constructor(chatId) {
    this.chatId = chatId;
    this.tasksDir = path.join(getUserDir(chatId), 'tasks');
  }

  /**
   * 创建任务
   * @param {Object} taskData - 任务数据
   * @returns {Promise<Object>}
   */
  async createTask(taskData) {
    const { taskId, topic, mode = 'default' } = taskData;
    
    await ensureDir(this.tasksDir);
    
    const task = {
      task_id: taskId,
      topic,
      mode,
      chat_id: this.chatId,
      status: TaskStatus.RUNNING,
      created_at: new Date().toISOString(),
      progress: '初始化',
      ...taskData
    };
    
    const filePath = getTaskFilePath(this.chatId, taskId);
    await fs.writeJson(filePath, task, { spaces: 2 });
    
    await logger.info(`Task created: ${taskId}`);
    return task;
  }

  /**
   * 更新任务状态
   * @param {string} taskId - 任务 ID
   * @param {Object} updates - 更新数据
   * @returns {Promise<Object|null>}
   */
  async updateTask(taskId, updates) {
    const filePath = getTaskFilePath(this.chatId, taskId);
    
    try {
      const task = await fs.readJson(filePath);
      const updatedTask = { ...task, ...updates };
      
      if (updates.status === TaskStatus.COMPLETED) {
        updatedTask.completed_at = new Date().toISOString();
      }
      
      await fs.writeJson(filePath, updatedTask, { spaces: 2 });
      await logger.info(`Task updated: ${taskId}`);
      return updatedTask;
    } catch (error) {
      await logger.error(`Failed to update task ${taskId}`, error);
      return null;
    }
  }

  /**
   * 获取任务
   * @param {string} taskId - 任务 ID
   * @returns {Promise<Object|null>}
   */
  async getTask(taskId) {
    const filePath = getTaskFilePath(this.chatId, taskId);
    
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
   * 获取任务列表
   * @param {number} limit - 限制数量
   * @returns {Promise<Array>}
   */
  async getTasks(limit = 10) {
    const files = await listJsonFiles(this.tasksDir);
    const tasks = [];
    
    for (const file of files.slice(0, limit)) {
      try {
        const task = await fs.readJson(path.join(this.tasksDir, file));
        tasks.push(task);
      } catch (error) {
        await logger.error(`Failed to read task ${file}`, error);
      }
    }
    
    return tasks;
  }

  /**
   * 获取运行中的任务
   * @returns {Promise<Array>}
   */
  async getRunningTasks() {
    const tasks = await this.getTasks(100);
    return tasks.filter(t => t.status === TaskStatus.RUNNING);
  }

  /**
   * 获取最近的任务
   * @returns {Promise<Object|null>}
   */
  async getLatestTask() {
    const tasks = await this.getTasks(1);
    return tasks[0] || null;
  }
}

/**
 * 创建任务管理器实例
 * @param {string} chatId
 * @returns {TaskManager}
 */
export function createTaskManager(chatId) {
  return new TaskManager(chatId);
}
