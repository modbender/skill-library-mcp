import ssh2 from 'ssh2';
import SessionManager from './session-manager.js';
import TunnelManager from './tunnel-manager.js';
import SftpManager from './sftp-manager.js';
import { EventEmitter } from 'events';

/**
 * Rssh2 - SSH远程自动化工具
 * 提供会话管理、隧道管理、文件传输等功能
 */
export class Rssh2 extends EventEmitter {
  constructor(config, options = {}) {
    super();
    
    this.config = {
      host: config.host,
      port: config.port || 22,
      username: config.username,
      password: config.password,
      privateKey: config.privateKey,
      passphrase: config.passphrase,
      timeout: config.timeout || 10000,
      keepaliveInterval: config.keepaliveInterval || 30000
    };

    this.options = {
      autoConnect: true,
      ...options
    };

    this.client = null;
    this.connected = false;
    
    // 初始化管理器
    this.sessionManager = new SessionManager(this.config, options.sessionManager);
    this.tunnelManager = new TunnelManager(this.sessionManager);
    this.sftpManager = new SftpManager(this.sessionManager);

    // 自动连接
    if (this.options.autoConnect) {
      this.connect().catch(err => this.emit('error', err));
    }
  }

  /**
   * 建立连接
   */
  async connect() {
    if (this.connected) {
      return this.client;
    }

    const client = new ssh2.Client();
    
    // 加载私钥
    let privateKey = null;
    if (this.config.privateKey) {
      const fs = await import('fs');
      if (fs.existsSync(this.config.privateKey)) {
        privateKey = fs.readFileSync(this.config.privateKey);
      } else {
        privateKey = Buffer.from(this.config.privateKey);
      }
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        client.end();
        reject(new Error('Connection timeout'));
      }, this.config.timeout);

      client.on('ready', () => {
        clearTimeout(timeout);
        this.client = client;
        this.connected = true;
        this.emit('connected');
        resolve(client);
      });

      client.on('error', (err) => {
        clearTimeout(timeout);
        this.emit('error', err);
        reject(err);
      });

      client.on('close', () => {
        this.connected = false;
        this.emit('disconnected');
      });

      client.connect({
        host: this.config.host,
        port: this.config.port,
        username: this.config.username,
        password: this.config.password,
        privateKey,
        passphrase: this.config.passphrase,
        keepaliveInterval: this.config.keepaliveInterval,
        readyTimeout: this.config.timeout
      });
    });
  }

  /**
   * 断开连接
   */
  async disconnect() {
    if (this.client && this.connected) {
      this.client.end();
      this.connected = false;
    }
  }

  /**
   * 执行单个命令
   */
  async exec(command, options = {}) {
    const client = await this.connect();

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        stream.destroy();
        reject(new Error('Command timeout'));
      }, options.timeout || 30000);

      client.exec(command, (err, stream) => {
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
   * 获取会话管理器
   */
  getSessionManager() {
    return this.sessionManager;
  }

  /**
   * 获取隧道管理器
   */
  getTunnelManager() {
    return this.tunnelManager;
  }

  /**
   * 获取SFTP管理器
   */
  getSftpManager() {
    return this.sftpManager;
  }

  /**
   * 创建本地端口转发
   */
  async tunnelLocal(config, options) {
    return await this.tunnelManager.local(config, options);
  }

  /**
   * 创建远程端口转发
   */
  async tunnelRemote(config, options) {
    return await this.tunnelManager.remote(config, options);
  }

  /**
   * 创建动态端口转发（SOCKS）
   */
  async tunnelDynamic(config, options) {
    return await this.tunnelManager.dynamic(config, options);
  }

  /**
   * 上传文件
   */
  async upload(localPath, remotePath, options) {
    return await this.sftpManager.upload(localPath, remotePath, options);
  }

  /**
   * 下载文件
   */
  async download(remotePath, localPath, options) {
    return await this.sftpManager.download(remotePath, localPath, options);
  }

  /**
   * 同步目录
   */
  async sync(localDir, remoteDir, options) {
    return await this.sftpManager.sync(localDir, remoteDir, options);
  }

  /**
   * 关闭所有连接
   */
  async close() {
    await this.sessionManager.close();
    await this.tunnelManager.closeAll();
    await this.sftpManager.close();
    await this.disconnect();
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      connected: this.connected,
      session: this.sessionManager.getStats(),
      tunnel: this.tunnelManager.getStats()
    };
  }
}

/**
 * 创建Rssh2实例的便捷函数
 */
export function createRssh2(config, options) {
  return new Rssh2(config, options);
}

export default Rssh2;