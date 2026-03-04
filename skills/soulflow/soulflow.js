#!/usr/bin/env node
/**
 * soulflow.js - Lightweight workflow engine for OpenClaw
 * 
 * Usage:
 *   node soulflow.js run <workflow> "<task description>"
 *   node soulflow.js status [run-id]
 *   node soulflow.js list
 *   node soulflow.js runs
 */

import path from 'path';
import { fileURLToPath } from 'url';
import * as Runner from './lib/runner.js';
import * as State from './lib/state.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const WORKFLOWS_DIR = path.join(__dirname, 'workflows');

/**
 * Show usage
 */
function showUsage() {
  console.log(`
soulflow - Lightweight workflow engine for OpenClaw

Usage:
  node soulflow.js run <workflow> "<task description>"
  node soulflow.js status [run-id]
  node soulflow.js list
  node soulflow.js runs
  node soulflow.js test

Commands:
  run <workflow> <task>   Run a workflow with a task description
  status [run-id]          Show status of a run (latest if no ID given)
  list                     List available workflows
  runs                     List all workflow runs
  test                     Test gateway connection

Examples:
  node soulflow.js run security-audit "Check the auth module"
  node soulflow.js status a1b2c3d4
  node soulflow.js list
  node soulflow.js runs
`);
}

/**
 * Main CLI handler
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    showUsage();
    process.exit(0);
  }
  
  const command = args[0];
  
  try {
    switch (command) {
      case 'run': {
        if (args.length < 3) {
          console.error('Error: Missing workflow ID or task description');
          console.error('Usage: node soulflow.js run <workflow> "<task>"');
          process.exit(1);
        }
        
        const workflowId = args[1];
        const task = args.slice(2).join(' ');
        
        const result = await Runner.runWorkflow(workflowId, task, WORKFLOWS_DIR);
        process.exit(result.success ? 0 : 1);
        break;
      }
      
      case 'status': {
        const runId = args[1];
        
        if (runId) {
          await Runner.getStatus(runId);
        } else {
          // Show latest run
          const runs = State.listRuns();
          if (runs.length === 0) {
            console.log('[soulflow] No runs found');
            process.exit(0);
          }
          
          await Runner.getStatus(runs[0].runId);
        }
        break;
      }
      
      case 'list': {
        const workflows = Runner.listWorkflows(WORKFLOWS_DIR);
        
        console.log('\n[soulflow] Available workflows:\n');
        for (const wf of workflows) {
          console.log(`  ${wf.id}`);
          console.log(`    ${wf.name} - ${wf.description}`);
          console.log(`    Steps: ${wf.steps}`);
          console.log('');
        }
        break;
      }
      
      case 'runs': {
        const runs = State.listRuns();
        
        if (runs.length === 0) {
          console.log('\n[soulflow] No runs found\n');
          process.exit(0);
        }
        
        console.log('\n[soulflow] Recent runs:\n');
        for (const run of runs.slice(0, 10)) {
          const icon = run.status === 'done' ? '✓' : 
                       run.status === 'failed' ? '✗' : 
                       '⟳';
          console.log(`  ${icon} ${run.runId} - ${run.workflow} (${run.status})`);
          console.log(`    Created: ${new Date(run.createdAt).toLocaleString()}`);
          console.log('');
        }
        break;
      }
      
      case 'test': {
        console.log('[soulflow] Testing gateway connection...\n');
        
        const { GatewayClient } = await import('./lib/gateway.js');
        const gateway = new GatewayClient();
        
        try {
          await gateway.connect();
          console.log('[soulflow] ✓ Connected and authenticated');
          
          // Try a simple call
          const result = await gateway.call('config.get', {});
          console.log('[soulflow] ✓ Config call successful');
          console.log(`[soulflow] Gateway version: ${result.version || 'unknown'}`);
          
          gateway.close();
          console.log('[soulflow] ✓ Connection closed\n');
        } catch (error) {
          console.error(`[soulflow] ✗ Connection failed: ${error.message}\n`);
          process.exit(1);
        }
        break;
      }
      
      case 'help':
      case '--help':
      case '-h':
        showUsage();
        break;
      
      default:
        console.error(`Unknown command: ${command}`);
        showUsage();
        process.exit(1);
    }
  } catch (error) {
    console.error(`\n[soulflow] Error: ${error.message}\n`);
    process.exit(1);
  }
}

// Run CLI
main();
