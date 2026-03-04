import ssh2 from 'ssh2';
import fs from 'fs';
import path from 'path';
import { EventEmitter } from 'events';

/**
 * SFTP管理器
 * 提供文件上传、下载、目录同步等功能
 */
export class SftpManager extends EventEmitter {
  constructor(sessionManager) {
    super();
    this.sessionManager = sessionManager;
    this.sftp = null;
  }

  /**
   * 获取SFTP客户端
   */
  async getSFTP() {
    if (this.sftp) {
      return this.sftp;
    }

    const conn = await this.sessionManager.getConnection();
    
    return new Promise((resolve, reject) => {
      conn.client.sftp((err, sftp) => {
        if (err) {
          reject(err);
          return;
        }

        this.sftp = sftp;
        this.emit('sftpConnected');
        resolve(sftp);
      });
    });
  }

  /**
   * 上传文件
   */
  async upload(localPath, remotePath, options = {}) {
    const opts = {
      mode: 0o644,
      ...options
    };

    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.fastPut(localPath, remotePath, opts, (err) => {
        if (err) {
          this.emit('uploadError', { localPath, remotePath, error: err });
          reject(err);
          return;
        }

        this.emit('uploaded', { localPath, remotePath });
        resolve({ localPath, remotePath });
      });
    });
  }

  /**
   * 下载文件
   */
  async download(remotePath, localPath, options = {}) {
    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.fastGet(remotePath, localPath, options, (err) => {
        if (err) {
          this.emit('downloadError', { remotePath, localPath, error: err });
          reject(err);
          return;
        }

        this.emit('downloaded', { remotePath, localPath });
        resolve({ remotePath, localPath });
      });
    });
  }

  /**
   * 上传目录
   */
  async uploadDir(localDir, remoteDir, options = {}) {
    const opts = {
      recursive: true,
      ...options
    };

    const sftp = await this.getSFTP();
    const files = this.getLocalFiles(localDir, opts.recursive);

    await this.mkdir(remoteDir, true);

    const results = [];
    for (const file of files) {
      const relativePath = path.relative(localDir, file);
      const remotePath = path.posix.join(remoteDir, relativePath.replace(/\\/g, '/'));
      
      const remoteSubDir = path.posix.dirname(remotePath);
      await this.mkdir(remoteSubDir, true);

      const result = await this.upload(file, remotePath);
      results.push(result);
    }

    return results;
  }

  /**
   * 下载目录
   */
  async downloadDir(remoteDir, localDir, options = {}) {
    const opts = {
      recursive: true,
      ...options
    };

    const sftp = await this.getSFTP();
    const files = await this.listRemoteFiles(remoteDir, opts.recursive);

    if (!fs.existsSync(localDir)) {
      fs.mkdirSync(localDir, { recursive: true });
    }

    const results = [];
    for (const file of files) {
      const relativePath = path.posix.relative(remoteDir, file);
      const localPath = path.join(localDir, relativePath);

      const localSubDir = path.dirname(localPath);
      if (!fs.existsSync(localSubDir)) {
        fs.mkdirSync(localSubDir, { recursive: true });
      }

      const result = await this.download(file, localPath);
      results.push(result);
    }

    return results;
  }

  /**
   * 同步目录（本地 -> 远程）
   */
  async sync(localDir, remoteDir, options = {}) {
    const opts = {
      delete: false,
      ...options
    };

    const uploaded = await this.uploadDir(localDir, remoteDir);

    if (opts.delete) {
      const remoteFiles = await this.listRemoteFiles(remoteDir, true);
      const localFiles = this.getLocalFiles(localDir, true).map(f => 
        path.posix.join(remoteDir, path.relative(localDir, f).replace(/\\/g, '/'))
      );

      for (const remoteFile of remoteFiles) {
        if (!localFiles.includes(remoteFile)) {
          await this.delete(remoteFile);
        }
      }
    }

    return uploaded;
  }

  /**
   * 列出文件
   */
  async list(remotePath) {
    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.readdir(remotePath, (err, list) => {
        if (err) {
          reject(err);
          return;
        }

        const files = list.map(item => ({
          name: item.filename,
          type: item.type,
          size: item.attrs.size,
          modifyTime: item.attrs.mtime,
          accessTime: item.attrs.atime,
          permissions: item.attrs.mode
        }));

        resolve(files);
      });
    });
  }

  /**
   * 创建目录
   */
  async mkdir(remotePath, recursive = false) {
    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.mkdir(remotePath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        resolve();
      });
    });
  }

  /**
   * 删除文件
   */
  async delete(remotePath) {
    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.unlink(remotePath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        resolve();
      });
    });
  }

  /**
   * 删除目录
   */
  async rmdir(remotePath, recursive = false) {
    const sftp = await this.getSFTP();

    if (recursive) {
      const files = await this.list(remotePath);
      for (const file of files) {
        const filePath = path.posix.join(remotePath, file.name);
        if (file.type === 'd') {
          await this.rmdir(filePath, true);
        } else {
          await this.delete(filePath);
        }
      }
    }

    return new Promise((resolve, reject) => {
      sftp.rmdir(remotePath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        resolve();
      });
    });
  }

  /**
   * 检查文件是否存在
   */
  async exists(remotePath) {
    const sftp = await this.getSFTP();

    return new Promise((resolve) => {
      sftp.stat(remotePath, (err) => {
        resolve(!err);
      });
    });
  }

  /**
   * 获取文件信息
   */
  async stat(remotePath) {
    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.stat(remotePath, (err, stats) => {
        if (err) {
          reject(err);
          return;
        }

        resolve({
          size: stats.size,
          mode: stats.mode,
          uid: stats.uid,
          gid: stats.gid,
          atime: stats.atime,
          mtime: stats.mtime
        });
      });
    });
  }

  /**
   * 重命名文件
   */
  async rename(oldPath, newPath) {
    const sftp = await this.getSFTP();

    return new Promise((resolve, reject) => {
      sftp.rename(oldPath, newPath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        resolve();
      });
    });
  }

  /**
   * 获取本地文件列表
   */
  getLocalFiles(dir, recursive = true) {
    const files = [];

    const scan = (currentDir) => {
      const items = fs.readdirSync(currentDir);
      for (const item of items) {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isFile()) {
          files.push(fullPath);
        } else if (stat.isDirectory() && recursive) {
          scan(fullPath);
        }
      }
    };

    scan(dir);
    return files;
  }

  /**
   * 获取远程文件列表
   */
  async listRemoteFiles(dir, recursive = true) {
    const sftp = await this.getSFTP();
    const files = [];

    const scan = async (currentDir) => {
      const list = await this.list(currentDir);
      for (const item of list) {
        const fullPath = path.posix.join(currentDir, item.name);

        if (item.type === '-') {
          files.push(fullPath);
        } else if (item.type === 'd' && recursive && item.name !== '.' && item.name !== '..') {
          await scan(fullPath);
        }
      }
    };

    await scan(dir);
    return files;
  }

  /**
   * 关闭SFTP连接
   */
  async close() {
    if (this.sftp) {
      this.sftp.end();
      this.sftp = null;
    }
  }
}

export default SftpManager;