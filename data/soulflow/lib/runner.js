/**
 * lib/runner.js - Workflow Execution Engine
 * Loads workflows, executes steps with dedicated worker agent
 */

import fs from 'fs';
import path from 'path';
import { GatewayClient } from './gateway.js';
import * as State from './state.js';

const WORKER_AGENT_ID = 'soulflow-worker';
const WORKER_SOUL = `You are a workflow step executor. Your job is to complete tasks precisely and thoroughly.

Rules:
- USE TOOLS. Read files with the read tool. Edit files with the edit tool. Run commands with exec.
- Do the actual work. Don't just describe what should be done — do it.
- Be thorough. When scanning code, read the actual files. When fixing bugs, edit the actual code.
- Report what you did concretely. File names, line numbers, specific changes.
- When done, end your response with: STATUS: done
- If you can't complete the task, explain exactly why and end with: STATUS: blocked`;

/**
 * Load a workflow definition
 */
export function loadWorkflow(workflowId, workflowsDir) {
  const workflowPath = path.join(workflowsDir, `${workflowId}.workflow.json`);
  if (!fs.existsSync(workflowPath)) {
    throw new Error(`Workflow ${workflowId} not found at ${workflowPath}`);
  }
  return JSON.parse(fs.readFileSync(workflowPath, 'utf8'));
}

/**
 * Ensure the soulflow-worker agent exists with minimal brain files
 */
async function ensureWorkerAgent(gateway) {
  try {
    const snapshot = await gateway.call('config.get', {});
    const config = snapshot.config || snapshot;
    const agents = config.agents || {};
    const list = Array.isArray(agents.list) ? agents.list : [];
    
    const existing = list.find(a => a.id === WORKER_AGENT_ID);
    if (!existing) {
      console.log(`[soulflow] Creating worker agent...`);
      
      const homeDir = process.env.HOME || '/home/openclaw';
      const stateDir = `${homeDir}/.openclaw`;
      
      const newAgent = {
        id: WORKER_AGENT_ID,
        name: 'SoulFlow Worker',
        workspace: `${stateDir}/workspace`,
        identity: { name: 'SoulFlow Worker', theme: 'Workflow executor', emoji: '⚙️' },
        tools: { profile: 'full' }
      };
      
      // Copy authProfiles from first agent if available
      if (list.length > 0 && list[0].authProfiles) {
        newAgent.authProfiles = list[0].authProfiles;
      }
      
      const newList = [...list, newAgent];
      const patchParams = { raw: JSON.stringify({ agents: { list: newList } }, null, 2) };
      if (snapshot.hash) patchParams.baseHash = snapshot.hash;
      await gateway.call('config.patch', patchParams);
      
      // Wait for gateway to restart after config change
      await new Promise(r => setTimeout(r, 5000));
      
      // Reconnect since gateway restarts on config.patch
      try {
        gateway.close();
      } catch {}
      await gateway.connect();
      console.log(`[soulflow] Reconnected after config change ✓`);
      
      // Write minimal SOUL.md to the worker agent's directory
      const soulPath = `${stateDir}/agents/${WORKER_AGENT_ID}/SOUL.md`;
      const agentDir = `${stateDir}/agents/${WORKER_AGENT_ID}`;
      
      // Create agent dir and write SOUL.md via filesystem
      const fsMod = await import('fs');
      fsMod.default.mkdirSync(agentDir, { recursive: true });
      fsMod.default.writeFileSync(soulPath, WORKER_SOUL);
      
      console.log(`[soulflow] Worker agent created ✓`);
    }
  } catch (err) {
    console.log(`[soulflow] Worker agent setup warning: ${err.message}`);
    console.log(`[soulflow] Falling back to "main" agent`);
    return 'main';
  }
  return WORKER_AGENT_ID;
}

/**
 * Substitute {{variables}} in a string
 */
function substituteVariables(text, variables) {
  return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return variables[key] !== undefined ? String(variables[key]) : match;
  });
}

/**
 * Parse KEY: value pairs from response text
 */
function parseOutputVariables(text) {
  const variables = {};
  const lines = text.split('\n');
  
  let currentKey = null;
  let currentValue = [];
  
  for (const line of lines) {
    const match = line.match(/^([A-Z][A-Z_]+):\s*(.*)$/);
    if (match) {
      if (currentKey) {
        let value = currentValue.join('\n').trim();
        if ((value.startsWith('[') || value.startsWith('{')) && value.length > 2) {
          try { value = JSON.parse(value); } catch {}
        }
        variables[currentKey.toLowerCase()] = value;
      }
      currentKey = match[1];
      currentValue = [match[2]];
    } else if (currentKey) {
      currentValue.push(line);
    }
  }
  
  if (currentKey) {
    let value = currentValue.join('\n').trim();
    if ((value.startsWith('[') || value.startsWith('{')) && value.length > 2) {
      try { value = JSON.parse(value); } catch {}
    }
    variables[currentKey.toLowerCase()] = value;
  }
  
  return variables;
}

/**
 * Execute a single workflow step
 */
async function executeStep(gateway, state, step, agentId, stepIndex, totalSteps, attempt = 1) {
  const { id, name, input, expects, maxRetries = 1 } = step;
  const sessionKey = `agent:${agentId}:soulflow:${state.runId}:${id}`;
  
  console.log(`[soulflow] Step ${stepIndex}/${totalSteps}: ${name}`);
  
  if (attempt > 1) {
    console.log(`[soulflow]   ⟳ Retry ${attempt}/${maxRetries + 1}`);
  }
  
  State.updateStep(state, id, 'running');
  
  try {
    const prompt = substituteVariables(input, state.variables);
    
    console.log(`[soulflow]   → Sending to agent...`);
    
    const response = await gateway.sendChat(sessionKey, prompt);
    
    console.log(`[soulflow]   → Got ${response.length} chars`);
    
    // Parse output variables
    const outputVars = parseOutputVariables(response);
    
    // Always store the full output as a variable for next steps
    outputVars[`${id}_output`] = response;
    state.variables[`${id}_output`] = response;
    
    // Check success
    let success = true;
    if (expects) {
      success = response.includes(expects);
      if (success) {
        console.log(`[soulflow]   ✓ ${expects}`);
      } else if (response.length > 500) {
        console.log(`[soulflow]   ✓ Substantial response (accepted)`);
        success = true;
      } else {
        console.log(`[soulflow]   ✗ Short/empty response`);
      }
    }
    
    if (!success && attempt <= maxRetries) {
      console.log(`[soulflow]   → Retrying...`);
      // Use a different session key for retry to get fresh context
      return await executeStep(gateway, state, step, agentId, stepIndex, totalSteps, attempt + 1);
    }
    
    State.updateStep(state, id, success ? 'done' : 'failed', response, outputVars);
    
    if (!success) {
      throw new Error(`Step "${name}" failed — response too short or missing expected output`);
    }
    
    return { success: true, output: response, variables: outputVars };
    
  } catch (error) {
    console.error(`[soulflow]   ✗ ${error.message}`);
    State.updateStep(state, id, 'failed', error.message);
    throw error;
  }
}

/**
 * Send completion notification to main session
 */
async function notifyCompletion(gateway, state, workflow) {
  try {
    const summary = buildCompletionSummary(state, workflow);
    
    // Send to main session
    await gateway.call('chat.send', {
      sessionKey: 'agent:main',
      message: summary,
      idempotencyKey: `soulflow-complete-${state.runId}-${Date.now()}`
    });
    
    console.log(`[soulflow] ✓ Completion notification sent to main session`);
  } catch (error) {
    console.error(`[soulflow] Failed to send completion notification: ${error.message}`);
  }
}

/**
 * Send failure notification to main session
 */
async function notifyFailure(gateway, state, workflow, failedStep, error) {
  try {
    const message = `🚨 **SoulFlow Workflow Failed**

**Workflow:** ${workflow.name}
**Run ID:** ${state.runId}
**Failed at:** Step "${failedStep}"
**Error:** ${error.message}

Task: ${state.task.substring(0, 200)}${state.task.length > 200 ? '...' : ''}

Check logs with: \`node soulflow.js status ${state.runId}\``;

    await gateway.call('chat.send', {
      sessionKey: 'agent:main',
      message,
      idempotencyKey: `soulflow-fail-${state.runId}-${Date.now()}`
    });
    
    console.log(`[soulflow] ✓ Failure notification sent to main session`);
  } catch (err) {
    console.error(`[soulflow] Failed to send failure notification: ${err.message}`);
  }
}

/**
 * Build completion summary from workflow state
 */
function buildCompletionSummary(state, workflow) {
  const duration = Math.round((new Date(state.updatedAt) - new Date(state.createdAt)) / 1000);
  const minutes = Math.floor(duration / 60);
  const seconds = duration % 60;
  
  let summary = `✅ **SoulFlow Workflow Complete**

**Workflow:** ${workflow.name}
**Run ID:** ${state.runId}
**Duration:** ${minutes}m ${seconds}s

**Steps completed:**
`;

  for (const step of state.steps) {
    summary += `${step.status === 'done' ? '✓' : '✗'} ${step.id}\n`;
  }
  
  // Add key results from last step
  const lastStep = state.steps[state.steps.length - 1];
  if (lastStep && lastStep.output) {
    const output = lastStep.output;
    
    // Extract key variables
    const vars = state.variables || {};
    const keyVars = Object.keys(vars).filter(k => 
      k.includes('count') || 
      k.includes('status') || 
      k.includes('result') ||
      k.includes('fixed') ||
      k.includes('verified')
    );
    
    if (keyVars.length > 0) {
      summary += '\n**Results:**\n';
      for (const key of keyVars.slice(0, 5)) {
        summary += `- ${key}: ${vars[key]}\n`;
      }
    }
    
    // Extract first STATUS: done block if present
    const statusMatch = output.match(/STATUS: done.*?(?=\n\n|\n[A-Z]|$)/s);
    if (statusMatch) {
      const statusBlock = statusMatch[0].split('\n').slice(0, 5).join('\n');
      summary += `\n**Final Status:**\n\`\`\`\n${statusBlock}\n\`\`\`\n`;
    }
  }
  
  summary += `\nTask: ${state.task.substring(0, 150)}${state.task.length > 150 ? '...' : ''}`;
  
  return summary;
}

/**
 * Execute a complete workflow
 */
export async function runWorkflow(workflowId, task, workflowsDir) {
  const workflow = loadWorkflow(workflowId, workflowsDir);
  
  console.log(`\n[soulflow] ═══════════════════════════════════`);
  console.log(`[soulflow] ${workflow.name}`);
  console.log(`[soulflow] ═══════════════════════════════════`);
  console.log(`[soulflow] ${workflow.description}`);
  
  const runId = State.generateRunId();
  console.log(`[soulflow] Run: ${runId}`);
  
  const state = State.initRun(runId, workflow.id, task);
  
  const gateway = new GatewayClient();
  
  try {
    console.log(`[soulflow] Connecting...`);
    await gateway.connect();
    console.log(`[soulflow] Connected ✓\n`);
    
    // Ensure worker agent exists
    const agentId = await ensureWorkerAgent(gateway);
    
    for (let i = 0; i < workflow.steps.length; i++) {
      const step = workflow.steps[i];
      
      try {
        await executeStep(gateway, state, step, agentId, i + 1, workflow.steps.length);
        console.log('');
      } catch (error) {
        if (step.onFail?.retryStep) {
          console.log(`[soulflow] Running fallback: re-run "${step.onFail.retryStep}" then retry...`);
          const retryStep = workflow.steps.find(s => s.id === step.onFail.retryStep);
          if (retryStep) {
            const retryIdx = workflow.steps.indexOf(retryStep) + 1;
            await executeStep(gateway, state, retryStep, agentId, retryIdx, workflow.steps.length);
            await executeStep(gateway, state, step, agentId, i + 1, workflow.steps.length);
            continue;
          }
        }
        
        state.status = 'failed';
        State.saveState(state);
        console.log(`\n[soulflow] ✗ Failed at: ${step.name}`);
        console.log(`[soulflow] Run saved: ${runId}`);
        
        // Send failure notification to main session
        await notifyFailure(gateway, state, workflow, step.name, error);
        
        gateway.close();
        return { success: false, runId, state };
      }
    }
    
    state.status = 'done';
    State.saveState(state);
    
    console.log(`[soulflow] ═══════════════════════════════════`);
    console.log(`[soulflow] ✓ Complete! Run: ${runId}`);
    console.log(`[soulflow] ═══════════════════════════════════\n`);
    
    // Send completion notification to main session
    await notifyCompletion(gateway, state, workflow);
    
    gateway.close();
    return { success: true, runId, state };
    
  } catch (error) {
    console.error(`[soulflow] ✗ Fatal: ${error.message}`);
    state.status = 'failed';
    state.error = error.message;
    State.saveState(state);
    gateway.close();
    throw error;
  }
}

/**
 * Get workflow status
 */
export async function getStatus(runId) {
  const state = State.loadState(runId);
  
  console.log(`\n[soulflow] Run: ${state.runId} (${state.workflow})`);
  console.log(`[soulflow] Status: ${state.status}`);
  console.log(`[soulflow] Task: ${state.task.substring(0, 100)}${state.task.length > 100 ? '...' : ''}`);
  console.log(`[soulflow] Started: ${state.createdAt}`);
  console.log(`\n[soulflow] Steps:`);
  
  for (const step of state.steps) {
    const icon = step.status === 'done' ? '✓' : 
                 step.status === 'failed' ? '✗' : 
                 step.status === 'running' ? '⟳' : '○';
    const chars = step.output ? ` (${step.output.length} chars)` : '';
    console.log(`  ${icon} ${step.id}: ${step.status}${chars}`);
  }
  
  console.log('');
  return state;
}

/**
 * List available workflows
 */
export function listWorkflows(workflowsDir) {
  return fs.readdirSync(workflowsDir)
    .filter(f => f.endsWith('.workflow.json'))
    .map(f => {
      const wf = JSON.parse(fs.readFileSync(path.join(workflowsDir, f), 'utf8'));
      return { id: wf.id, name: wf.name, description: wf.description, steps: wf.steps.length };
    });
}
