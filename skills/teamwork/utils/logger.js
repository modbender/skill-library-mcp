const fs = require('fs');
const path = require('path');

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

class Logger {
  constructor(name, options = {}) {
    this.name = name;
    this.level = options.level || LOG_LEVELS.INFO;
    this.logFile = options.logFile || null;
    this.console = options.console !== false;
  }

  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      logger: this.name,
      message,
      data
    };
    return logEntry;
  }

  log(level, message, data = null) {
    if (level < this.level) return;

    const logEntry = this.formatMessage(level, message, data);
    const logString = JSON.stringify(logEntry);

    if (this.console) {
      const levelName = Object.keys(LOG_LEVELS).find(k => LOG_LEVELS[k] === level);
      const consoleMethod = level >= LOG_LEVELS.ERROR ? 'error' : 
                           level >= LOG_LEVELS.WARN ? 'warn' : 'log';
      console[consoleMethod](`[${logEntry.timestamp}] [${levelName}] [${this.name}] ${message}`);
      if (data) console[consoleMethod](data);
    }

    if (this.logFile) {
      fs.appendFileSync(this.logFile, logString + '\n', 'utf8');
    }
  }

  debug(message, data) {
    this.log(LOG_LEVELS.DEBUG, message, data);
  }

  info(message, data) {
    this.log(LOG_LEVELS.INFO, message, data);
  }

  warn(message, data) {
    this.log(LOG_LEVELS.WARN, message, data);
  }

  error(message, data) {
    this.log(LOG_LEVELS.ERROR, message, data);
  }

  setLevel(level) {
    this.level = level;
  }

  setLogFile(filePath) {
    this.logFile = filePath;
  }
}

function createLogger(name, options = {}) {
  return new Logger(name, options);
}

module.exports = {
  Logger,
  createLogger,
  LOG_LEVELS
};
