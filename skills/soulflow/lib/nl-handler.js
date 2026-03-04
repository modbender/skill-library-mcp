/**
 * Natural language workflow invocation
 * Called by the main agent when user requests a workflow in conversation
 */

const { spawn } = require('child_process');
const path = require('path');

const WORKFLOW_PATTERNS = {
  'security-audit': [
    /security audit/i,
    /audit.*security/i,
    /scan.*vulnerabilit/i,
    /check.*security/i,
    /find.*vulnerabilit/i
  ],
  'bug-fix': [
    /fix.*bug/i,
    /bug.*fix/i,
    /issue.*fix/i,
    /problem.*fix/i,
    /broken/i,
    /not working/i,
    /throws.*error/i
  ],
  'feature-dev': [
    /build.*feature/i,
    /add.*feature/i,
    /implement/i,
    /create.*feature/i,
    /develop.*feature/i,
    /new feature/i
  ]
};

/**
 * Match user message to workflow
 */
function matchWorkflow(message) {
  for (const [workflow, patterns] of Object.entries(WORKFLOW_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(message)) {
        return workflow;
      }
    }
  }
  return null;
}

/**
 * Extract task description from message
 * Strips common prefixes like "run", "do", "please"
 */
function extractTask(message) {
  return message
    .replace(/^(please|can you|could you|run|do|execute)\s+/i, '')
    .replace(/^(a|an|the)\s+/i, '')
    .trim();
}

/**
 * Run workflow from natural language
 * Returns a promise that resolves with run ID
 */
function invokeWorkflow(userMessage) {
  return new Promise((resolve, reject) => {
    const workflow = matchWorkflow(userMessage);
    
    if (!workflow) {
      reject(new Error('Could not match message to a workflow. Available: security-audit, bug-fix, feature-dev'));
      return;
    }

    const task = extractTask(userMessage);
    
    if (!task) {
      reject(new Error('Could not extract task description from message'));
      return;
    }

    // Spawn soulflow.js as child process
    const soulflowPath = path.join(__dirname, '..', 'soulflow.js');
    const child = spawn('node', [soulflowPath, 'run', workflow, task], {
      cwd: path.dirname(soulflowPath),
      env: process.env,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';
    let runId = null;

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
      // Extract run ID from output
      const match = stdout.match(/Run ID: ([a-f0-9]+)/);
      if (match) {
        runId = match[1];
      }
    });

    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    child.on('close', (code) => {
      if (code === 0 && runId) {
        resolve({
          runId,
          workflow,
          task,
          message: `Started ${workflow} workflow (run ID: ${runId})`
        });
      } else {
        reject(new Error(stderr || 'Workflow failed to start'));
      }
    });
  });
}

module.exports = { matchWorkflow, extractTask, invokeWorkflow };
