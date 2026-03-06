/**
 * Configuration Loader
 * 
 * Loads surf-check config from:
 * 1. ./surf-check.json (local, highest priority)
 * 2. ~/.surf-check.json (global)
 * 3. Built-in defaults
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import {
  SpotConfig,
  AlertConfig,
  QuietHours,
  SPOTS as DEFAULT_SPOTS,
  DEFAULT_ALERT_CONFIG,
} from './types.js';

export interface SurfCheckConfig {
  spots: SpotConfig[];
  alertConfig: AlertConfig;
}

interface ConfigFileSpot {
  id: string;
  name: string;
  slug?: string;
  url?: string;
}

interface ConfigFile {
  spots?: ConfigFileSpot[];
  waveMin?: number;
  waveMax?: number;
  forecastDays?: number;
  quietHours?: Partial<QuietHours>;
}

const CONFIG_FILENAME = 'surf-check.json';

/**
 * Find and load config file
 */
function loadConfigFile(): ConfigFile | null {
  // Try local first
  const localPath = path.join(process.cwd(), CONFIG_FILENAME);
  if (fs.existsSync(localPath)) {
    try {
      const content = fs.readFileSync(localPath, 'utf-8');
      return JSON.parse(content);
    } catch (e) {
      console.error(`Error reading ${localPath}:`, e);
    }
  }

  // Try global
  const globalPath = path.join(os.homedir(), `.${CONFIG_FILENAME}`);
  if (fs.existsSync(globalPath)) {
    try {
      const content = fs.readFileSync(globalPath, 'utf-8');
      return JSON.parse(content);
    } catch (e) {
      console.error(`Error reading ${globalPath}:`, e);
    }
  }

  return null;
}

/**
 * Convert config file spot to full SpotConfig
 */
function toSpotConfig(spot: ConfigFileSpot): SpotConfig {
  const slug = spot.slug || spot.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  return {
    id: spot.id,
    name: spot.name,
    slug,
    url: spot.url || `https://www.surfline.com/surf-report/${slug}/${spot.id}`,
  };
}

/**
 * Load configuration with fallbacks
 */
export function loadConfig(): SurfCheckConfig {
  const file = loadConfigFile();

  // Default spots
  let spots: SpotConfig[] = Object.values(DEFAULT_SPOTS);

  // Default alert config
  let alertConfig: AlertConfig = { ...DEFAULT_ALERT_CONFIG };

  if (file) {
    // Override spots if provided
    if (file.spots && file.spots.length > 0) {
      spots = file.spots.map(toSpotConfig);
    }

    // Override alert config fields if provided
    if (file.waveMin !== undefined) {
      alertConfig.waveMin = file.waveMin;
    }
    if (file.waveMax !== undefined) {
      alertConfig.waveMax = file.waveMax;
    }
    if (file.forecastDays !== undefined) {
      alertConfig.forecastDays = file.forecastDays;
    }
    if (file.quietHours) {
      alertConfig.quietHours = {
        ...alertConfig.quietHours,
        ...file.quietHours,
      };
    }
  }

  return { spots, alertConfig };
}

/**
 * Get config file path for display
 */
export function getConfigPath(): string | null {
  const localPath = path.join(process.cwd(), CONFIG_FILENAME);
  if (fs.existsSync(localPath)) {
    return localPath;
  }

  const globalPath = path.join(os.homedir(), `.${CONFIG_FILENAME}`);
  if (fs.existsSync(globalPath)) {
    return globalPath;
  }

  return null;
}
