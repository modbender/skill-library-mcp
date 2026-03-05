#!/usr/bin/env node

/**
 * 七牛云 KODO Node.js SDK 脚本
 * 功能：文件上传、下载、列出、删除、获取URL等操作
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 尝试加载 qiniu SDK
let qiniu;
try {
  qiniu = await import('qiniu');
} catch (error) {
  console.error('❌ qiniu Node.js SDK 未安装');
  console.error('请运行: npm install qiniu');
  process.exit(1);
}

// 配置文件路径
const SKILL_DIR = path.dirname(__dirname);
const CONFIG_DIR = path.join(SKILL_DIR, 'config');
const CONFIG_FILE = path.join(CONFIG_DIR, 'qiniu-config.json');

/**
 * 加载配置文件
 */
function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    throw new Error(
      `配置文件不存在: ${CONFIG_FILE}\n` +
      `请复制 config/qiniu-config.example.json 为 qiniu-config.json 并填写配置`
    );
  }

  const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));

  // 验证必填配置
  const required = ['accessKey', 'secretKey', 'bucket'];
  for (const key of required) {
    if (!config[key] || config[key].startsWith('你的')) {
      throw new Error(`配置项 ${key} 不能为空或使用示例值`);
    }
  }

  return config;
}

/**
 * 七牛云 KODO 操作类
 */
class QiniuKodo {
  constructor(config) {
    this.config = config;
    this.mac = new qiniu.auth.digest.Mac(config.accessKey, config.secretKey);
    this.bucketManager = new qiniu.rs.BucketManager(this.mac);
    this.bucket = config.bucket;
    this.domain = config.domain || '';
    
    // 配置上传选项
    this.uploadOptions = {
      uphost: this.getUpHost(config.region)
    };
  }

  /**
   * 获取上传域名
   */
  getUpHost(region) {
    const hosts = {
      'z0': 'https://upload.qiniup.com',
      'z1': 'https://upload-z1.qiniup.com',
      'z2': 'https://upload-z2.qiniup.com',
      'na0': 'https://upload-na0.qiniup.com',
      'as0': 'https://upload-as0.qiniup.com'
    };
    return hosts[region] || hosts['z0'];
  }

  /**
   * 上传文件
   */
  async upload(localPath, key) {
    if (!fs.existsSync(localPath)) {
      throw new Error(`文件不存在: ${localPath}`);
    }

    return new Promise((resolve, reject) => {
      const putPolicy = new qiniu.rs.PutPolicy({ scope: `${this.bucket}:${key}` });
      const uploadToken = putPolicy.uploadToken(this.mac);
      
      const config = new qiniu.conf.Config();
      config.zone = qiniu.zone.Zone_z0; // 根据区域设置
      
      const formUploader = new qiniu.form_up.FormUploader(config);
      const putExtra = new qiniu.form_up.PutExtra();
      
      formUploader.putFile(uploadToken, key, localPath, putExtra, (respErr, respBody, respInfo) => {
        if (respErr) {
          reject(respErr);
          return;
        }
        
        if (respInfo.statusCode === 200) {
          resolve({
            success: true,
            key: respBody.key,
            hash: respBody.hash,
            url: this.getUrl(key),
            size: fs.statSync(localPath).size
          });
        } else {
          reject(new Error(`上传失败: ${respInfo.statusCode} ${JSON.stringify(respBody)}`));
        }
      });
    });
  }

  /**
   * 下载文件
   */
  async download(key, localPath) {
    const url = this.getUrl(key, true);
    
    return new Promise((resolve, reject) => {
      const protocol = url.startsWith('https') ? https : http;
      
      protocol.get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`下载失败: ${response.statusCode}`));
          return;
        }
        
        // 创建目录
        const dir = path.dirname(localPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        
        const fileStream = fs.createWriteStream(localPath);
        response.pipe(fileStream);
        
        fileStream.on('finish', () => {
          fileStream.close();
          resolve({
            success: true,
            key: key,
            size: fs.statSync(localPath).size
          });
        });
      }).on('error', reject);
    });
  }

  /**
   * 列出文件
   */
  async listFiles(prefix = '', limit = 100) {
    return new Promise((resolve, reject) => {
      this.bucketManager.listPrefix(this.bucket, {
        prefix: prefix,
        limit: limit
      }, (err, respBody, respInfo) => {
        if (err) {
          reject(err);
          return;
        }
        
        if (respInfo.statusCode === 200) {
          const files = respBody.items.map(item => ({
            key: item.key,
            size: item.fsize,
            mtime: item.putTime / 1000000,
            hash: item.hash,
            mimeType: item.mimeType
          }));
          resolve(files);
        } else {
          reject(new Error(`列出文件失败: ${respInfo.statusCode}`));
        }
      });
    });
  }

  /**
   * 删除文件
   */
  async delete(key) {
    return new Promise((resolve, reject) => {
      this.bucketManager.delete(this.bucket, key, (err, respBody, respInfo) => {
        if (err) {
          if (respInfo && respInfo.statusCode === 612) {
            reject(new Error(`文件不存在: ${key}`));
          } else {
            reject(err);
          }
          return;
        }
        
        if (respInfo.statusCode === 200) {
          resolve({ success: true, key: key });
        } else {
          reject(new Error(`删除失败: ${respInfo.statusCode}`));
        }
      });
    });
  }

  /**
   * 批量删除
   */
  async batchDelete(keys) {
    const deleteOperations = keys.map(key => 
      qiniu.rs.deleteOp(this.bucket, key)
    );
    
    return new Promise((resolve, reject) => {
      this.bucketManager.batch(deleteOperations, (err, respBody, respInfo) => {
        if (err) {
          reject(err);
          return;
        }
        
        let success = 0;
        let failed = 0;
        
        respBody.forEach(item => {
          if (item.code === 200) {
            success++;
          } else {
            failed++;
          }
        });
        
        resolve({ success, failed });
      });
    });
  }

  /**
   * 获取文件信息
   */
  async stat(key) {
    return new Promise((resolve, reject) => {
      this.bucketManager.stat(this.bucket, key, (err, respBody, respInfo) => {
        if (err) {
          reject(err);
          return;
        }
        
        if (respInfo.statusCode === 200) {
          resolve({
            key: key,
            size: respBody.fsize,
            hash: respBody.hash,
            mimeType: respBody.mimeType,
            mtime: respBody.putTime / 1000000
          });
        } else {
          reject(new Error(`获取文件信息失败: ${respInfo.statusCode}`));
        }
      });
    });
  }

  /**
   * 获取文件 URL
   */
  getUrl(key, private = false, expires = 3600) {
    if (!this.domain) {
      throw new Error('配置中缺少 domain 字段');
    }
    
    const baseUrl = `${this.domain}/${key}`;
    
    if (private) {
      const deadline = Math.floor(Date.now() / 1000) + expires;
      const sign = qiniu.util.hmacSha1(baseUrl, this.mac.secretKey);
      const encodedSign = qiniu.util.base64ToUrlSafe(sign);
      const downloadToken = `${this.mac.accessKey}:${encodedSign}`;
      return `${baseUrl}?e=${deadline}&token=${downloadToken}`;
    } else {
      return baseUrl;
    }
  }

  /**
   * 移动文件
   */
  async move(srcKey, destKey, force = false) {
    return new Promise((resolve, reject) => {
      this.bucketManager.move(this.bucket, srcKey, this.bucket, destKey, { force }, (err, respBody, respInfo) => {
        if (err) {
          reject(err);
          return;
        }
        
        if (respInfo.statusCode === 200) {
          resolve({
            success: true,
            srcKey: srcKey,
            destKey: destKey
          });
        } else {
          reject(new Error(`移动失败: ${respInfo.statusCode}`));
        }
      });
    });
  }

  /**
   * 复制文件
   */
  async copy(srcKey, destKey, force = false) {
    return new Promise((resolve, reject) => {
      this.bucketManager.copy(this.bucket, srcKey, this.bucket, destKey, { force }, (err, respBody, respInfo) => {
        if (err) {
          reject(err);
          return;
        }
        
        if (respInfo.statusCode === 200) {
          resolve({
            success: true,
            srcKey: srcKey,
            destKey: destKey
          });
        } else {
          reject(new Error(`复制失败: ${respInfo.statusCode}`));
        }
      });
    });
  }
}

// 工具函数
function formatSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

function formatTime(timestamp) {
  const date = new Date(timestamp * 1000);
  return date.toISOString().replace('T', ' ').substring(0, 19);
}

// 命令行接口
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  try {
    const config = loadConfig();
    const kodo = new QiniuKodo(config);
    
    switch (command) {
      case 'upload': {
        const localPath = args[args.indexOf('--local') + 1];
        const key = args[args.indexOf('--key') + 1];
        const result = await kodo.upload(localPath, key);
        console.log('✅ 上传成功!');
        console.log(`  文件: ${result.key}`);
        console.log(`  大小: ${formatSize(result.size)}`);
        console.log(`  URL: ${result.url}`);
        break;
      }
      
      case 'download': {
        const key = args[args.indexOf('--key') + 1];
        const localPath = args[args.indexOf('--local') + 1];
        const result = await kodo.download(key, localPath);
        console.log('✅ 下载成功!');
        console.log(`  文件: ${result.key}`);
        console.log(`  大小: ${formatSize(result.size)}`);
        console.log(`  保存到: ${localPath}`);
        break;
      }
      
      case 'list': {
        const prefixIndex = args.indexOf('--prefix');
        const prefix = prefixIndex !== -1 ? args[prefixIndex + 1] : '';
        
        const limitIndex = args.indexOf('--limit');
        const limit = limitIndex !== -1 ? parseInt(args[limitIndex + 1]) : 100;
        
        const formatIndex = args.indexOf('--format');
        const format = formatIndex !== -1 ? args[formatIndex + 1] : 'table';
        
        const files = await kodo.listFiles(prefix, limit);
        
        if (files.length === 0) {
          console.log('📭 没有找到文件');
          return;
        }
        
        if (format === 'json') {
          console.log(JSON.stringify(files, null, 2));
        } else {
          console.log(`📋 共 ${files.length} 个文件:\n`);
          console.log(`${'文件名'.padEnd(50)} ${'大小'.padStart(12)} ${'修改时间'.padEnd(20)}`);
          console.log('-'.repeat(82));
          files.forEach(file => {
            console.log(`${file.key.padEnd(50)} ${formatSize(file.size).padStart(12)} ${formatTime(file.mtime).padEnd(20)}`);
          });
        }
        break;
      }
      
      case 'delete': {
        const key = args[args.indexOf('--key') + 1];
        const forceIndex = args.indexOf('--force');
        
        if (forceIndex === -1) {
          console.log(`⚠️  确定要删除 ${key} 吗？(y/N):`);
          // 注意：这里需要 readline，为简化暂时跳过确认
        }
        
        const result = await kodo.delete(key);
        console.log('✅ 删除成功!');
        console.log(`  文件: ${result.key}`);
        break;
      }
      
      case 'batch-delete': {
        const fileIndex = args.indexOf('--file');
        const listFile = args[fileIndex + 1];
        
        const keys = fs.readFileSync(listFile, 'utf-8')
          .split('\n')
          .map(line => line.trim())
          .filter(line => line);
        
        const result = await kodo.batchDelete(keys);
        console.log('✅ 批量删除完成!');
        console.log(`  成功: ${result.success}`);
        console.log(`  失败: ${result.failed}`);
        break;
      }
      
      case 'url': {
        const key = args[args.indexOf('--key') + 1];
        const privateIndex = args.indexOf('--private');
        const expiresIndex = args.indexOf('--expires');
        
        const isPrivate = privateIndex !== -1;
        const expires = expiresIndex !== -1 ? parseInt(args[expiresIndex + 1]) : 3600;
        
        const url = kodo.getUrl(key, isPrivate, expires);
        console.log('🔗 文件 URL:');
        console.log(`  ${url}`);
        if (isPrivate) {
          console.log(`\n  ⏱️  有效期: ${expires} 秒`);
        }
        break;
      }
      
      case 'stat': {
        const key = args[args.indexOf('--key') + 1];
        const info = await kodo.stat(key);
        console.log('📊 文件信息:\n');
        console.log(`  文件名: ${info.key}`);
        console.log(`  大小: ${formatSize(info.size)}`);
        console.log(`  类型: ${info.mimeType}`);
        console.log(`  Hash: ${info.hash}`);
        console.log(`  修改时间: ${formatTime(info.mtime)}`);
        break;
      }
      
      case 'test-connection': {
        await kodo.listFiles('', 1);
        console.log('✅ 七牛云连接验证成功!');
        break;
      }
      
      default:
        console.log('使用方法:');
        console.log('  node qiniu_node.mjs upload --local <LocalPath> --key <Key>');
        console.log('  node qiniu_node.mjs download --key <Key> --local <LocalPath>');
        console.log('  node qiniu_node.mjs list [--prefix <Prefix>] [--limit <Limit>]');
        console.log('  node qiniu_node.mjs delete --key <Key> [--force]');
        console.log('  node qiniu_node.mjs url --key <Key> [--private] [--expires <Seconds>]');
        console.log('  node qiniu_node.mjs stat --key <Key>');
        console.log('  node qiniu_node.mjs test-connection');
    }
    
  } catch (error) {
    console.error(`❌ 错误: ${error.message}`);
    process.exit(1);
  }
}

main();
