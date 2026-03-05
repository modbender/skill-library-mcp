#!/usr/bin/env node

/**
 * BrowserManager v2 - 企业级浏览器会话管理器
 * 特性: 超时重试、智能等待、并发锁、结构化日志、资源清理
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// 简单结构化日志（可根据需要升级为 pino/winston）
class Logger {
  constructor(prefix = 'BM') {
    this.prefix = prefix;
  }
  info(...args) { console.log(`[${this.prefix}] ℹ️`, ...args); }
  warn(...args) { console.warn(`[${this.prefix}] ⚠️`, ...args); }
  error(...args) { console.error(`[${this.prefix}] ❌`, ...args); }
  debug(...args) { if (process.env.DEBUG) console.debug(`[${this.prefix}] 🔍`, ...args); }
}

class LockManager {
  constructor(profile) {
    this.profile = profile;
    this.lockFile = path.join('/tmp', `openclaw-${profile}.lock`);
  }
  
  async acquire() {
    if (fs.existsSync(this.lockFile)) {
      const oldPid = parseInt(fs.readFileSync(this.lockFile, 'utf8'), 10);
      try {
        process.kill(oldPid, 0);
        throw new Error(`Profile ${this.profile} locked by PID ${oldPid}`);
      } catch (e) {
        // Stale lock
        fs.unlinkSync(this.lockFile);
      }
    }
    fs.writeFileSync(this.lockFile, process.pid.toString(), 'utf8');
  }
  
  async release() {
    try {
      if (fs.existsSync(this.lockFile)) fs.unlinkSync(this.lockFile);
    } catch (_) {}
  }
}

class BrowserManager {
  constructor(profile = 'openclaw', options = {}) {
    this.profile = profile;
    this.currentTabId = null;
    this.running = false;
    this.logger = new Logger(`BM:${profile}`);
    this.lockManager = new LockManager(profile);
    this.defaultTimeout = options.timeout || 30000;
    this.defaultRetries = options.retries || 2;
  }
  
  async runCommand(cmd, options = {}) {
    const { timeout = this.defaultTimeout, retries = this.defaultRetries } = options;
    return new Promise((resolve, reject) => {
      const attempt = (n) => {
        this.logger.debug(`Exec: ${cmd} (attempt ${n + 1})`);
        exec(cmd, { timeout }, async (err, stdout, stderr) => {
          if (err) {
            this.logger.warn(`Command failed: ${stderr || err.message}`);
            if (n < retries && /ENETUNREACH|ECONNREFUSED|ETIMEDOUT/.test(stderr || '')) {
              const backoff = 1000 * Math.pow(2, n);
              this.logger.info(`Retrying in ${backoff}ms...`);
              await new Promise(r => setTimeout(r, backoff));
              return attempt(n + 1);
            }
            reject({ err, stdout, stderr, attempt: n + 1 });
          } else {
            resolve({ stdout, stderr });
          }
        });
      };
      attempt(0);
    });
  }
  
  async acquireLock() {
    await this.lockManager.acquire();
    this.logger.debug('Lock acquired');
  }
  
  async releaseLock() {
    await this.lockManager.release();
    this.logger.debug('Lock released');
  }
  
  async start() {
    if (this.running) {
      this.logger.info('Browser already running');
      return;
    }
    await this.acquireLock();
    try {
      await this.runCommand(`openclaw browser --browser-profile ${this.profile} start`);
      this.running = true;
      this.logger.info('Browser started');
    } catch (e) {
      await this.releaseLock();
      throw e;
    }
  }
  
  async stop() {
    if (!this.running) {
      this.logger.info('Browser not running');
      await this.releaseLock();
      return;
    }
    try {
      await this.runCommand(`openclaw browser --browser-profile ${this.profile} stop`);
      this.running = false;
      this.logger.info('Browser stopped');
    } finally {
      await this.releaseLock();
    }
  }
  
  async open(url) {
    if (!this.running) throw new Error('Browser not started');
    try {
      const res = await this.runCommand(`openclaw browser --browser-profile ${this.profile} open "${url}"`);
      const match = res.stdout.match(/id:\s*([A-F0-9]+)/i);
      if (match) {
        this.currentTabId = match[1];
        this.logger.info(`Opened ${url}`, { tabId: this.currentTabId });
      } else {
        this.logger.warn(`Opened ${url} but no tab ID found`);
      }
      return this.currentTabId;
    } catch (e) {
      this.logger.error(`Open failed: ${url}`, { error: e.message });
      throw e;
    }
  }
  
  async snapshot(format = 'ai', limit = 100) {
    if (!this.running) throw new Error('Browser not started');
    const res = await this.runCommand(
      `openclaw browser --browser-profile ${this.profile} snapshot --format ${format} --limit ${limit}`
    );
    return res.stdout;
  }
  
  async type(ref, text) {
    if (!this.running) throw new Error('Browser not started');
    await this.runCommand(`openclaw browser --browser-profile ${this.profile} type ${ref} "${text}"`);
    this.logger.debug(`Typed into ${ref}`);
  }
  
  async click(ref) {
    if (!this.running) throw new Error('Browser not started');
    await this.runCommand(`openclaw browser --browser-profile ${this.profile} click ${ref}`);
    this.logger.debug(`Clicked ${ref}`);
  }
  
  async press(key) {
    if (!this.running) throw new Error('Browser not started');
    await this.runCommand(`openclaw browser --browser-profile ${this.profile} press ${key}`);
    this.logger.debug(`Pressed ${key}`);
  }
  
  async screenshot() {
    if (!this.running) throw new Error('Browser not started');
    const res = await this.runCommand(`openclaw browser --browser-profile ${this.profile} screenshot`);
    return res.stdout.trim();
  }
  
  async pdf() {
    if (!this.running) throw new Error('Browser not started');
    await this.runCommand(`openclaw browser --browser-profile ${this.profile} pdf`);
    this.logger.info('PDF saved');
  }
  
  async closeTab(tabId = null) {
    const id = tabId || this.currentTabId;
    if (!id) return;
    try {
      await this.runCommand(`openclaw browser --browser-profile ${this.profile} close ${id}`);
      this.logger.info(`Closed tab ${id}`);
      if (id === this.currentTabId) this.currentTabId = null;
    } catch (e) {
      this.logger.warn(`Close tab ${id} failed`, { error: e.message });
    }
  }
  
  async closeAllTabs() {
    if (!this.running) return;
    try {
      const tabsRes = await this.runCommand(`openclaw browser --browser-profile ${this.profile} tabs`);
      const lines = tabsRes.stdout.split('\n').filter(l => l.trim());
      const tabIds = [];
      
      for (const line of lines) {
        if (line.includes('no tabs')) break;
        const match = line.match(/id:\s*([A-F0-9]+)/i);
        if (match) tabIds.push(match[1]);
      }
      
      for (const id of tabIds) {
        try {
          await this.runCommand(`openclaw browser --browser-profile ${this.profile} close ${id}`);
          this.logger.debug(`Closed tab ${id}`);
        } catch (e) {
          this.logger.warn(`Failed to close ${id}`, { error: e.message });
        }
      }
      
      this.currentTabId = null;
      this.logger.info(`Cleaned up ${tabIds.length} tabs`);
    } catch (e) {
      this.logger.error('Close all tabs failed', { error: e.message });
    }
  }
  
  async waitForLoadState(state = 'networkidle', timeout = 15000) {
    if (!this.running) throw new Error('Browser not started');
    await this.runCommand(
      `openclaw browser --browser-profile ${this.profile} wait --load ${state} --timeout ${timeout}`
    );
    this.logger.debug(`Wait for load state: ${state}`);
  }
  
  async waitForSelector(ref, timeout = 10000) {
    if (!this.running) throw new Error('Browser not started');
    await this.runCommand(
      `openclaw browser --browser-profile ${this.profile} wait "[ref=${ref}]" --timeout ${timeout}`
    );
    this.logger.debug(`Wait for selector: ${ref}`);
  }
  
  async sleep(ms) {
    await new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async cleanup() {
    try {
      await this.closeAllTabs();
    } finally {
      await this.stop();
    }
  }
}

module.exports = BrowserManager;

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const manager = new BrowserManager(process.env.BROWSER_PROFILE || 'openclaw', {
    timeout: parseInt(process.env.BROWSER_TIMEOUT) || 30000,
    retries: parseInt(process.env.BROWSER_RETRIES) || 2
  });
  
  async function run() {
    try {
      if (command === 'test') {
        await manager.start();
        await manager.open('https://www.google.com');
        await manager.waitForLoadState('domcontentloaded');
        const snapshot = await manager.snapshot();
        console.log('Snapshot length:', snapshot.length);
        await manager.cleanup();
        console.log('✅ Test completed');
      } else if (command === 'bench') {
        await manager.start();
        const urls = args.slice(1);
        for (const url of urls) {
          await manager.open(url);
          await manager.waitForLoadState('domcontentloaded');
          console.log(`✓ Loaded: ${url}`);
          await manager.closeTab();
        }
        await manager.stop();
        console.log('✅ Benchmark complete');
      } else {
        console.log('Usage: node browser-manager.v2.js [test|bench <url1> <url2>...]');
      }
    } catch (e) {
      manager.logger.error('Command failed', { error: e.message });
      await manager.cleanup();
      process.exit(1);
    }
  }
  
  run();
}
