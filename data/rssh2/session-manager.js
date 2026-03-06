import { Client } from 'ssh2';
import fs from 'fs';
import path from 'path';
import { EventEmitter } from 'events';

/**
 * SSH会话管理器
 * 提供连接池、命令队列、自动重连等功能
 */
export class SessionManager extends EventEmitter {
  constructor(config, options = {}) {
    super();
    this.config = config;
    this.options = {
      maxPoolSize: 5,
      maxConcurrent: 10,
      commandTimeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      keepaliveInterval: 30000,
      ...options
    };
    
    this.connectionPool = [];
    this.activeCommands = 0;
    this.commandQueue = [];
    this.isClosing = false;
  }

  /**
   * 获取或创建连接
   */
  async getConnection() {
    if (this.isClosing) {
      throw new Error('SessionManager is closing');
    }

    // 尝试从池中获取空闲连接
    const idleConn = this.connectionPool.find(c => !c.busy && c.connected);
    if (idleConn) {
      idleConn.busy = true;
      return idleConn;
    }

    // 检查连接池大小
    if (this.connectionPool.length >= this.options.maxPoolSize) {
      // 等待空闲连接
      return await this.waitForIdleConnection();
    }

    // 创建新连接
    return await this.createConnection();
  }

  /**
   * 等待空闲连接
   */
  async waitForIdleConnection() {
    return new Promise((resolve, reject) => {
      const checkInterval = setInterval(() => {
        const idleConn = this.connectionPool.find(c => !c.busy && c.connected);
        if (idleConn) {
          clearInterval(checkInterval);
          idleConn.busy = true;
          resolve(idleConn);
        } else if (this.isClosing) {
          clearInterval(checkInterval);
          reject(new Error('SessionManager is closing'));
        }
      }, 100);
    });
  }

  /**
   * 创建新连接
   */
  async createConnection() {
    const client = new Client();
    
    // 加载私钥
    let privateKey = null;
    if (this.config.privateKey) {
      if (fs.existsSync(this.config.privateKey)) {
        privateKey = fs.readFileSync(this.config.privateKey);
      } else {
        privateKey = Buffer.from(this.config.privateKey);
      }
    }

    const conn = {
      client,
      busy: true,
      connected: false,
      createdAt: Date.now()
    };

    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        client.end();
        reject(new Error('Connection timeout'));
      }, this.config.timeout || 10000);

      client.on('ready', () => {
        clearTimeout(timeout);
        conn.connected = true;
        this.emit('connected', conn);
        resolve();
      });

      client.on('error', (err) => {
        clearTimeout(timeout);
        this.emit('error', err);
        reject(err);
      });

      client.on('close', () => {
        conn.connected = false;
        this.emit('disconnected', conn);
      });

      client.connect({
        host: this.config.host,
        port: this.config.port || 22,
        username: this.config.username,
        password: this.config.password,
        privateKey,
        passphrase: this.config.passphrase,
        keepaliveInterval: this.options.keepaliveInterval,
        readyTimeout: this.config.timeout || 10000
      });
    });

    this.connectionPool.push(conn);
    return conn;
  }

  /**
   * 释放连接
   */
  releaseConnection(conn) {
    if (conn && conn.client) {
      conn.busy = false;
      this.activeCommands--;
    }
  }

  /**
   * 执行命令
   */
  async exec(command, options = {}) {
    const opts = { ...this.options, ...options };
    
    // 并发控制
    if (this.activeCommands >= opts.maxConcurrent) {
      await this.waitForCommandSlot();
    }

    this.activeCommands++;
    
    let lastError = null;
    
    // 重试逻辑
    for (let attempt = 0; attempt < opts.retryAttempts; attempt++) {
      try {
        const conn = await this.getConnection();
        const result = await this.execOnConnection(conn, command, opts);
        this.releaseConnection(conn);
        return result;
      } catch (error) {
        lastError = error;
        this.emit('commandError', { command, error, attempt });
        
        if (attempt < opts.retryAttempts - 1) {
          await this.sleep(opts.retryDelay);
        }
      }
    }

    this.activeCommands--;
    throw lastError || new Error('Command execution failed');
  }

  /**
   * 等待命令槽
   */
  async waitForCommandSlot() {
    return new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        if (this.activeCommands < this.options.maxConcurrent) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 50);
    });
  }

  /**
   * 在连接上执行命令
   */
  async execOnConnection(conn, command, options) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        stream.destroy();
        reject(new Error('Command timeout'));
      }, options.commandTimeout);

      conn.client.exec(command, (err, stream) => {
        if (err) {
          clearTimeout(timeout);
          reject(err);
          return;
        }

        let stdout = '';
        let stderr = '';

        stream.on('data', (data) => {
          stdout += data.toString();
        });

        stream.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        stream.on('close', (code) => {
          clearTimeout(timeout);
          resolve({
            code,
            stdout: stdout.trim(),
            stderr: stderr.trim(),
            success: code === 0
          });
        });

        stream.on('error', (err) => {
          clearTimeout(timeout);
          reject(err);
        });
      });
    });
  }

  /**
   * 执行多个命令
   */
  async execMultiple(commands) {
    const results = await Promise.all(
      commands.map(cmd => this.exec(cmd))
    );
    return results;
  }

  /**
   * 休眠
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 关闭所有连接
   */
  async close() {
    this.isClosing = true;
    
    for (const conn of this.connectionPool) {
      if (conn.client && conn.connected) {
        conn.client.end();
      }
    }
    
    this.connectionPool = [];
    this.emit('closed');
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      totalConnections: this.connectionPool.length,
      activeConnections: this.connectionPool.filter(c => c.busy).length,
      idleConnections: this.connectionPool.filter(c => !c.busy).length,
      activeCommands: this.activeCommands,
      queuedCommands: this.commandQueue.length
    };
  }
}

export default SessionManager;