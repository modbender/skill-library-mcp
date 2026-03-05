// ============================================================================
// ui.js — Colored output helpers (no external dependencies)
// ============================================================================

'use strict';

// ANSI color codes
const colors = {
  red:     '\x1b[0;31m',
  green:   '\x1b[0;32m',
  yellow:  '\x1b[1;33m',
  blue:    '\x1b[0;34m',
  cyan:    '\x1b[0;36m',
  magenta: '\x1b[0;35m',
  bold:    '\x1b[1m',
  dim:     '\x1b[2m',
  reset:   '\x1b[0m',
};

// Check if color output should be enabled
const useColor = process.env.NO_COLOR === undefined && process.stdout.isTTY !== false;

/**
 * Wrap text with ANSI color codes (no-op if colors disabled)
 */
function c(colorName, text) {
  if (!useColor) return text;
  return `${colors[colorName] || ''}${text}${colors.reset}`;
}

// Semantic log helpers (match the bash version)
function info(msg)  { console.log(`${c('blue', 'ℹ')} ${msg}`); }
function ok(msg)    { console.log(`${c('green', '✅')} ${msg}`); }
function warn(msg)  { console.log(`${c('yellow', '⚠️')} ${msg}`); }
function err(msg)   { console.error(`${c('red', '❌')} ${msg}`); }
function fish(msg)  { console.log(`${c('cyan', '🐟')} ${msg}`); }

/**
 * Print a key-value detail line (indented)
 */
function detail(key, value) {
  console.log(`   ${c('dim', `${key}:`)} ${value}`);
}

/**
 * Type icons for asset types
 */
const typeIcons = {
  skill:    '🧩',
  config:   '⚙️',
  plugin:   '🔌',
  trigger:  '⚡',
  channel:  '📡',
  template: '📋',
};

function typeIcon(type) {
  return typeIcons[type] || '📦';
}

/**
 * Simple spinner for async operations
 */
class Spinner {
  constructor(message) {
    this.message = message;
    this.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
    this.index = 0;
    this.timer = null;
  }

  start() {
    if (!useColor || !process.stderr.isTTY) {
      process.stderr.write(`  ${this.message}...\n`);
      return this;
    }
    this.timer = setInterval(() => {
      const frame = this.frames[this.index % this.frames.length];
      process.stderr.write(`\r  ${frame} ${this.message}`);
      this.index++;
    }, 80);
    return this;
  }

  stop(finalMessage) {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
      process.stderr.write('\r\x1b[K'); // clear line
    }
    if (finalMessage) {
      console.log(`  ${finalMessage}`);
    }
  }
}

module.exports = {
  colors, c, useColor,
  info, ok, warn, err, fish,
  detail,
  typeIcon, typeIcons,
  Spinner,
};
