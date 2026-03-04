import { readFileSync, writeFileSync, existsSync, renameSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { logger } from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Support FLOW_STATE_FILE env var to allow attack scripts to use a separate state file
// Set process.env.FLOW_STATE_FILE = 'flow-state-test.json' before calling any state functions
function getStateFilePath() {
  return join(__dirname, '../state/', process.env.FLOW_STATE_FILE || 'flow-state.json');
}

export function loadState() {
  const STATE_FILE = getStateFilePath();

  if (!existsSync(STATE_FILE)) {
    logger.info(`No existing state file found (${process.env.FLOW_STATE_FILE || 'flow-state.json'}), creating new state`);
    return {
      createdAt: new Date().toISOString(),
      steps: {}
    };
  }

  try {
    const data = readFileSync(STATE_FILE, 'utf8');
    const state = JSON.parse(data);
    logger.info(`State loaded from ${process.env.FLOW_STATE_FILE || 'flow-state.json'}`);
    return state;
  } catch (error) {
    logger.error('Failed to load state:', error.message);
    throw error;
  }
}

/**
 * Load state from a specific file (by filename, relative to state/ directory).
 * Used by attack scripts to read the original state while writing to a different file.
 */
export function loadStateFrom(filename) {
  const filePath = join(__dirname, '../state/', filename);
  if (!existsSync(filePath)) {
    throw new Error(`State file not found: ${filename}`);
  }
  const data = readFileSync(filePath, 'utf8');
  return JSON.parse(data);
}

export function saveState(state) {
  const STATE_FILE = getStateFilePath();

  try {
    state.updatedAt = new Date().toISOString();
    writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    logger.success(`State saved to ${process.env.FLOW_STATE_FILE || 'flow-state.json'}`);
  } catch (error) {
    logger.error('Failed to save state:', error.message);
    throw error;
  }
}

export function updateStep(stepName, data) {
  const state = loadState();
  state.steps[stepName] = {
    ...data,
    completedAt: new Date().toISOString()
  };
  saveState(state);
  return state;
}

export function getStep(stepName) {
  const state = loadState();
  return state.steps[stepName];
}

export function archiveState() {
  const STATE_FILE = getStateFilePath();
  if (!existsSync(STATE_FILE)) {
    logger.warning('No state file to archive');
    return null;
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const archiveName = `flow-state-${timestamp}.json`;
  const archivePath = join(dirname(STATE_FILE), archiveName);

  renameSync(STATE_FILE, archivePath);
  logger.success(`Archived: ${archiveName}`);

  return archivePath;
}

export function requireStep(stepName, fieldName = null) {
  const step = getStep(stepName);
  if (!step) {
    throw new Error(`Step "${stepName}" has not been completed yet. Please run it first.`);
  }

  if (fieldName && !step[fieldName]) {
    throw new Error(`Field "${fieldName}" not found in step "${stepName}"`);
  }

  return fieldName ? step[fieldName] : step;
}
