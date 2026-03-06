import chalk from 'chalk';
import { table } from 'table';

export function formatTable(data, columns) {
  if (!data || data.length === 0) {
    return chalk.yellow('No results found.');
  }

  const headers = columns.map(c => chalk.bold(c.header));
  const rows = data.map(item => columns.map(c => {
    const value = c.accessor(item);
    return c.format ? c.format(value) : String(value ?? '');
  }));

  return table([headers, ...rows], {
    border: {
      topBody: '─',
      topJoin: '┬',
      topLeft: '┌',
      topRight: '┐',
      bottomBody: '─',
      bottomJoin: '┴',
      bottomLeft: '└',
      bottomRight: '┘',
      bodyLeft: '│',
      bodyRight: '│',
      bodyJoin: '│',
      joinBody: '─',
      joinLeft: '├',
      joinRight: '┤',
      joinJoin: '┼'
    }
  });
}

export function formatJson(data) {
  return JSON.stringify(data, null, 2);
}

export function truncate(str, maxLength = 50) {
  if (!str) return '';
  str = String(str);
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '...';
}

export function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString('fr-FR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function success(message) {
  console.log(chalk.green('✓') + ' ' + message);
}

export function error(message) {
  console.error(chalk.red('✗') + ' ' + message);
}

export function warn(message) {
  console.log(chalk.yellow('⚠') + ' ' + message);
}

export function info(message) {
  console.log(chalk.blue('ℹ') + ' ' + message);
}

export function parseIdOrPath(input) {
  // If it's a number, return as ID
  const num = parseInt(input, 10);
  if (!isNaN(num) && String(num) === input) {
    return { type: 'id', value: num };
  }
  // Otherwise treat as path
  return { type: 'path', value: input };
}

export function parseTags(tagsStr) {
  if (!tagsStr) return [];
  return tagsStr.split(',').map(t => t.trim()).filter(Boolean);
}

export async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('readable', () => {
      let chunk;
      while ((chunk = process.stdin.read()) !== null) {
        data += chunk;
      }
    });
    process.stdin.on('end', () => {
      resolve(data);
    });
  });
}

export default {
  formatTable,
  formatJson,
  truncate,
  formatDate,
  formatBytes,
  success,
  error,
  warn,
  info,
  parseIdOrPath,
  parseTags,
  readStdin
};
