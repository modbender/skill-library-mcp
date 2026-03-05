const fs = require('fs');
const path = require('path');

class QQBotLogger {
  constructor(config) {
    this.config = config?.logger || this.getDefaultConfig();
    this.logDir = this.config.logDir;
    this.ensureLogDir();
    
    const dateStr = this.getChinaDate();
    this.logFile = path.join(this.logDir, `qq-bot-${dateStr}.log`);
    this.debugFile = path.join(this.logDir, `qq-bot-${dateStr}-debug.log`);
    
    this.initLogRotation();
  }

  getDefaultConfig() {
    return {
      logDir: '/root/.openclaw/workspace/logs/qq-bot',
      maxLogSize: '10MB',
      maxLogFiles: 7,
      timezone: 'Asia/Shanghai',
      logLevel: 'debug',
      sanitizeSensitive: true
    };
  }

  ensureLogDir() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
      fs.chmodSync(this.logDir, 0o755);
    }
  }

  getChinaTime() {
    const now = new Date();
    const chinaTime = new Date(now.getTime() + (8 * 60 * 60 * 1000));
    return chinaTime.toISOString().replace('Z', '+08:00');
  }

  getChinaDate() {
    const now = new Date();
    const chinaTime = new Date(now.getTime() + (8 * 60 * 60 * 1000));
    return chinaTime.toISOString().split('T')[0];
  }

  sanitizeMessage(message) {
    if (!this.config.sanitizeSensitive) return message;
    
    return message
      .replace(/(token|password|key|secret)=\w+/gi, '$1=***')
      .replace(/sk-[a-zA-Z0-9]{32}/gi, 'sk-***');
  }

  writeLog(filePath, logStr) {
    fs.appendFile(filePath, logStr + '\n', (err) => {
      if (err) {
        try {
          fs.appendFileSync(filePath, logStr + '\n');
        } catch (syncErr) {
          console.error('Log write failed:', syncErr);
        }
      }
    });
  }

  initLogRotation() {
    this.checkAndRotateLogs();
    setInterval(() => this.checkAndRotateLogs(), 24 * 60 * 60 * 1000);
  }

  checkAndRotateLogs() {
    try {
      const dateStr = this.getChinaDate();
      const files = [
        path.join(this.logDir, `qq-bot-${dateStr}.log`),
        path.join(this.logDir, `qq-bot-${dateStr}-debug.log`)
      ];
      
      const maxSize = this.parseSize(this.config.maxLogSize);
      
      for (const file of files) {
        if (fs.existsSync(file)) {
          const stats = fs.statSync(file);
          if (stats.size > maxSize) {
            this.rotateLogFile(file);
          }
        }
      }
      
      this.cleanupOldLogs();
    } catch (error) {
      console.error('Log rotation check failed:', error);
    }
  }

  parseSize(sizeStr) {
    const units = { 'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024 };
    const match = sizeStr.match(/^(\d+)([KMGT]?B?)$/i);
    if (match) {
      const value = parseInt(match[1]);
      const unit = (match[2] || 'B').toUpperCase();
      return value * (units[unit] || 1);
    }
    return 10 * 1024 * 1024;
  }

  rotateLogFile(filePath) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const rotatedPath = `${filePath}.${timestamp}`;
    try {
      fs.renameSync(filePath, rotatedPath);
    } catch (error) {
      console.error('Log rotation failed:', error);
    }
  }

  cleanupOldLogs() {
    try {
      const files = fs.readdirSync(this.logDir);
      const logFiles = files.filter(f => 
        f.startsWith('qq-bot-') && (f.endsWith('.log') || f.endsWith('.log.gz'))
      );
      
      logFiles.sort((a, b) => {
        const timeA = fs.statSync(path.join(this.logDir, a)).mtime;
        const timeB = fs.statSync(path.join(this.logDir, b)).mtime;
        return timeB - timeA;
      });
      
      for (let i = this.config.maxLogFiles; i < logFiles.length; i++) {
        fs.unlinkSync(path.join(this.logDir, logFiles[i]));
      }
    } catch (error) {
      console.error('Log cleanup failed:', error);
    }
  }

  shouldLog(level) {
    const levels = { error: 0, info: 1, debug: 2 };
    const current = levels[this.config.logLevel] ?? 2;
    return current >= levels[level];
  }

  log(message, context = {}) {
    if (!this.shouldLog('info')) return;
    
    const timestamp = this.getChinaTime();
    const sanitizedMessage = this.sanitizeMessage(message);
    const logEntry = { timestamp, level: 'INFO', message: sanitizedMessage, ...context };
    
    const logStr = JSON.stringify(logEntry);
    console.log(logStr);
    this.writeLog(this.logFile, logStr);
  }

  debug(message, context = {}) {
    if (!this.shouldLog('debug')) return;
    
    const timestamp = this.getChinaTime();
    const sanitizedMessage = this.sanitizeMessage(message);
    const logEntry = { timestamp, level: 'DEBUG', message: sanitizedMessage, ...context };
    
    const logStr = JSON.stringify(logEntry, null, 2);
    console.log(logStr);
    this.writeLog(this.debugFile, logStr);
  }

  error(message, error = {}) {
    if (!this.shouldLog('error')) return;
    
    const timestamp = this.getChinaTime();
    const sanitizedMessage = this.sanitizeMessage(message);
    const logEntry = {
      timestamp,
      level: 'ERROR',
      message: sanitizedMessage,
      error: { message: error.message, stack: error.stack, code: error.code }
    };
    
    const logStr = JSON.stringify(logEntry, null, 2);
    console.error(logStr);
    this.writeLog(this.debugFile, logStr);
  }

  logOpenClawInteraction(sessionMessage, openclawReply) {
    this.debug('OpenClaw session interaction', {
      sentToOpenClaw: sessionMessage,
      receivedFromOpenClaw: openclawReply
    });
  }

  logApiCall(apiName, params, response) {
    this.debug(`API call: ${apiName}`, {
      requestParams: params,
      responseStatus: response?.status,
      responseData: response?.data
    });
  }
}

module.exports = QQBotLogger;
