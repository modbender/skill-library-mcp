/**
 * lib/state.js - State Management for Soulflow
 * Handles reading/writing workflow run state to JSON files
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

const STATE_DIR = path.join(os.homedir(), '.openclaw', 'workspace', '.soulflow', 'runs');

/**
 * Ensure state directory exists
 */
function ensureStateDir() {
  if (!fs.existsSync(STATE_DIR)) {
    fs.mkdirSync(STATE_DIR, { recursive: true });
  }
}

/**
 * Generate a random 8-character hex run ID
 */
export function generateRunId() {
  return Array.from({ length: 8 }, () => 
    Math.floor(Math.random() * 16).toString(16)
  ).join('');
}

/**
 * Initialize a new workflow run
 */
export function initRun(runId, workflowId, task) {
  ensureStateDir();
  
  const state = {
    runId,
    workflow: workflowId,
    task,
    status: 'running',
    steps: [],
    variables: { task },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  saveState(state);
  return state;
}

/**
 * Load state for a run
 */
export function loadState(runId) {
  ensureStateDir();
  const filePath = path.join(STATE_DIR, `${runId}.json`);
  
  if (!fs.existsSync(filePath)) {
    throw new Error(`Run ${runId} not found`);
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(content);
}

/**
 * Save state for a run
 */
export function saveState(state) {
  ensureStateDir();
  state.updatedAt = new Date().toISOString();
  
  const filePath = path.join(STATE_DIR, `${state.runId}.json`);
  fs.writeFileSync(filePath, JSON.stringify(state, null, 2), 'utf8');
}

/**
 * Update step status and output
 */
export function updateStep(state, stepId, status, output = null, variables = {}) {
  const stepIndex = state.steps.findIndex(s => s.id === stepId);
  
  if (stepIndex === -1) {
    state.steps.push({
      id: stepId,
      status,
      output,
      variables,
      startedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
  } else {
    state.steps[stepIndex].status = status;
    if (output !== null) state.steps[stepIndex].output = output;
    state.steps[stepIndex].variables = { ...state.steps[stepIndex].variables, ...variables };
    state.steps[stepIndex].updatedAt = new Date().toISOString();
  }
  
  // Merge step variables into global variables
  Object.assign(state.variables, variables);
  
  saveState(state);
}

/**
 * List all runs
 */
export function listRuns() {
  ensureStateDir();
  
  const files = fs.readdirSync(STATE_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => {
      const runId = f.replace('.json', '');
      try {
        const state = loadState(runId);
        return {
          runId: state.runId,
          workflow: state.workflow,
          status: state.status,
          createdAt: state.createdAt,
          updatedAt: state.updatedAt
        };
      } catch (e) {
        return null;
      }
    })
    .filter(r => r !== null)
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  
  return files;
}

/**
 * Get state directory path
 */
export function getStateDir() {
  return STATE_DIR;
}
