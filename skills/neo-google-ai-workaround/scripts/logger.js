#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

class Logger {
  constructor(options = {}) {
    this.level = LOG_LEVELS[options.level] ?? LOG_LEVELS.INFO;
    this.logFile = options.logFile || null;
    this.silent = options.silent || false;
    this.entries = [];
  }

  _timestamp() {
    return new Date().toISOString();
  }

  _format(level, message, meta) {
    const entry = {
      timestamp: this._timestamp(),
      level,
      message,
    };
    if (meta && Object.keys(meta).length > 0) {
      entry.meta = meta;
    }
    return entry;
  }

  _write(entry) {
    this.entries.push(entry);

    if (!this.silent) {
      const prefix = `[${entry.timestamp}] [${entry.level}]`;
      const line = entry.meta
        ? `${prefix} ${entry.message} ${JSON.stringify(entry.meta)}`
        : `${prefix} ${entry.message}`;

      if (entry.level === "ERROR") {
        process.stderr.write(line + "\n");
      } else {
        process.stdout.write(line + "\n");
      }
    }

    if (this.logFile) {
      try {
        const dir = path.dirname(this.logFile);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        fs.appendFileSync(this.logFile, JSON.stringify(entry) + "\n");
      } catch (err) {
        // Fallback: write to stderr if log file is not writable
        process.stderr.write(
          `[Logger] Failed to write to log file: ${err.message}\n`
        );
      }
    }
  }

  debug(message, meta) {
    if (this.level <= LOG_LEVELS.DEBUG) {
      this._write(this._format("DEBUG", message, meta));
    }
  }

  info(message, meta) {
    if (this.level <= LOG_LEVELS.INFO) {
      this._write(this._format("INFO", message, meta));
    }
  }

  warn(message, meta) {
    if (this.level <= LOG_LEVELS.WARN) {
      this._write(this._format("WARN", message, meta));
    }
  }

  error(message, meta) {
    if (this.level <= LOG_LEVELS.ERROR) {
      this._write(this._format("ERROR", message, meta));
    }
  }

  categorize(error) {
    if (!error) return { category: "UNKNOWN", message: "No error provided" };

    const msg = error.message || String(error);

    if (msg.includes("ECONNREFUSED") || msg.includes("ENOTFOUND")) {
      return { category: "NETWORK", message: msg };
    }
    if (msg.includes("401") || msg.includes("403") || msg.includes("auth")) {
      return { category: "AUTH", message: msg };
    }
    if (msg.includes("429") || msg.includes("rate")) {
      return { category: "RATE_LIMIT", message: msg };
    }
    if (msg.includes("timeout") || msg.includes("ETIMEDOUT")) {
      return { category: "TIMEOUT", message: msg };
    }
    if (msg.includes("proxy") || msg.includes("ECONNRESET")) {
      return { category: "PROXY", message: msg };
    }
    return { category: "GENERAL", message: msg };
  }

  getEntries(level) {
    if (!level) return [...this.entries];
    return this.entries.filter((e) => e.level === level);
  }

  generateReport() {
    const counts = { DEBUG: 0, INFO: 0, WARN: 0, ERROR: 0 };
    for (const entry of this.entries) {
      counts[entry.level] = (counts[entry.level] || 0) + 1;
    }

    return {
      totalEntries: this.entries.length,
      counts,
      errors: this.getEntries("ERROR"),
      warnings: this.getEntries("WARN"),
      generatedAt: this._timestamp(),
    };
  }

  clear() {
    this.entries = [];
  }
}

module.exports = { Logger, LOG_LEVELS };
