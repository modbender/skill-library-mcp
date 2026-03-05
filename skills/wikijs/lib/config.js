import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const CONFIG_PATH = join(homedir(), '.config', 'wikijs.json');

let cachedConfig = null;

export function loadConfig() {
  if (cachedConfig) return cachedConfig;

  if (!existsSync(CONFIG_PATH)) {
    throw new Error(`Config file not found: ${CONFIG_PATH}\nCopy wikijs.example.json to ${CONFIG_PATH} and configure it.`);
  }

  try {
    const content = readFileSync(CONFIG_PATH, 'utf-8');
    cachedConfig = JSON.parse(content);

    // Validate required fields
    if (!cachedConfig.url) {
      throw new Error('Missing "url" in config');
    }
    if (!cachedConfig.apiToken) {
      throw new Error('Missing "apiToken" in config');
    }

    // Expand ~ in paths
    if (cachedConfig.autoSync?.path) {
      cachedConfig.autoSync.path = expandPath(cachedConfig.autoSync.path);
    }
    if (cachedConfig.backup?.path) {
      cachedConfig.backup.path = expandPath(cachedConfig.backup.path);
    }

    return cachedConfig;
  } catch (err) {
    if (err.code === 'ENOENT') {
      throw new Error(`Config file not found: ${CONFIG_PATH}`);
    }
    throw new Error(`Failed to parse config: ${err.message}`);
  }
}

export function getConfigPath() {
  return CONFIG_PATH;
}

function expandPath(path) {
  if (path.startsWith('~/')) {
    return join(homedir(), path.slice(2));
  }
  return path;
}

export default { loadConfig, getConfigPath };
