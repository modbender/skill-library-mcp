/**
 * OpenClaw Vault Plugin
 *
 * 安全密码管理工具（支持 AES-256-GCM 加密）
 *
 * 命令:
 *   vault <key> <password>  - 设置密码
 *   vault <key> show        - 显示密码
 *   vault <key> remove      - 删除密码
 *   vault list              - 列出所有密钥
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { join, dirname } from 'path';
import { homedir } from 'os';
import { existsSync } from 'fs';
import { createCipheriv, createDecipheriv, randomBytes, scryptSync } from 'crypto';

// ============================================================================
// 加密工具
// ============================================================================

class Encryption {
  constructor(masterKey) {
    this.masterKey = masterKey;
    this.algorithm = 'aes-256-gcm';
  }

  encrypt(text) {
    // 生成随机盐和 IV（12 字节 IV 是 GCM 推荐大小）
    const salt = randomBytes(32);
    const iv = randomBytes(12);

    // 使用随机盐派生密钥
    const key = scryptSync(this.masterKey, salt, 32);
    const cipher = createCipheriv(this.algorithm, key, iv);

    let encrypted = cipher.update(text, 'utf8', 'base64');
    encrypted += cipher.final('base64');

    const authTag = cipher.getAuthTag();

    return {
      encrypted,
      salt: salt.toString('base64'),
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64')
    };
  }

  decrypt(encryptedData) {
    // 使用存储的盐派生密钥
    const key = scryptSync(
      this.masterKey,
      Buffer.from(encryptedData.salt, 'base64'),
      32
    );

    const decipher = createDecipheriv(
      this.algorithm,
      key,
      Buffer.from(encryptedData.iv, 'base64')
    );

    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'base64'));

    let decrypted = decipher.update(encryptedData.encrypted, 'base64', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }
}

// ============================================================================
// 存储管理
// ============================================================================

class VaultStorage {
  constructor(storagePath, encryption) {
    this.storagePath = join(homedir(), storagePath);
    this.encryption = encryption;
  }

  async ensureStorage() {
    const dir = dirname(this.storagePath);
    if (!existsSync(dir)) {
      await mkdir(dir, { recursive: true });
    }
    if (!existsSync(this.storagePath)) {
      await writeFile(this.storagePath, JSON.stringify({}, null, 2));
    }
  }

  async load() {
    await this.ensureStorage();
    const content = await readFile(this.storagePath, 'utf-8');
    return JSON.parse(content);
  }

  async save(data) {
    await this.ensureStorage();
    await writeFile(this.storagePath, JSON.stringify(data, null, 2));
  }

  async set(key, password) {
    const data = await this.load();
    const encryptedPassword = this.encryption.encrypt(password);

    data[key] = {
      password: encryptedPassword,
      createdAt: data[key]?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    await this.save(data);
    return true;
  }

  async get(key) {
    const data = await this.load();
    const entry = data[key];

    if (!entry) {
      return null;
    }

    // 解密密码
    const decryptedPassword = this.encryption.decrypt(entry.password);

    return {
      password: decryptedPassword,
      createdAt: entry.createdAt,
      updatedAt: entry.updatedAt
    };
  }

  async remove(key) {
    const data = await this.load();
    if (!(key in data)) {
      return false;
    }
    delete data[key];
    await this.save(data);
    return true;
  }

  async list() {
    const data = await this.load();
    return Object.keys(data).map(key => ({
      key,
      createdAt: data[key].createdAt,
      updatedAt: data[key].updatedAt
    }));
  }
}

// ============================================================================
// 插件导出
// ============================================================================

export default function vaultPlugin(api) {
  const config = api.getConfig() || {};
  const storagePath = config.storageFile || '.vault/passwords.json';

  // 获取主密钥
  const masterKey = process.env.VAULT_MASTER_KEY || config.masterKey;

  if (!masterKey) {
    console.error('⚠️  VAULT_MASTER_KEY not set!');
    console.error('Please set environment variable: export VAULT_MASTER_KEY="your-secure-key"');
    console.error('Or add to config: { "plugins": { "vault": { "masterKey": "your-secure-key" } } }');
    throw new Error('VAULT_MASTER_KEY is required for encryption');
  }

  const encryption = new Encryption(masterKey);
  const storage = new VaultStorage(storagePath, encryption);

  // 注册 vault 命令
  api.registerSkill({
    id: 'vault',
    name: 'Vault',
    description: 'Password management tool',

    async execute(args) {
      const parts = args.trim().split(/\s+/);

      // vault list
      if (parts[0] === 'list') {
        const entries = await storage.list();
        if (entries.length === 0) {
          return { success: true, message: 'No passwords stored.' };
        }

        const list = entries.map(e =>
          `• ${e.key} (created: ${e.createdAt}, updated: ${e.updatedAt})`
        ).join('\n');

        return {
          success: true,
          message: `Stored passwords:\n${list}`
        };
      }

      // vault <key> show
      if (parts.length === 2 && parts[1] === 'show') {
        const key = parts[0];
        const entry = await storage.get(key);

        if (!entry) {
          return { success: false, message: `Password for '${key}' not found.` };
        }

        return {
          success: true,
          message: `Password for '${key}': ${entry.password}`
        };
      }

      // vault <key> remove
      if (parts.length === 2 && parts[1] === 'remove') {
        const key = parts[0];
        const removed = await storage.remove(key);

        if (!removed) {
          return { success: false, message: `Password for '${key}' not found.` };
        }

        return {
          success: true,
          message: `Password for '${key}' removed.`
        };
      }

      // vault <key> <password>
      if (parts.length === 2) {
        const [key, password] = parts;
        await storage.set(key, password);

        return {
          success: true,
          message: `Password for '${key}' saved.`
        };
      }

      // 无效命令
      return {
        success: false,
        message: `Usage:
  vault <key> <password>  - Set password
  vault <key> show        - Show password
  vault <key> remove      - Remove password
  vault list              - List all keys`
      };
    }
  });

  return {
    id: 'vault',
    name: 'Vault',
    version: '1.1.2'
  };
}
