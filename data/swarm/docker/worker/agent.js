/**
 * Swarm Worker Agent
 * 
 * Runs on each "Mac Mini" node. Responsibilities:
 * - Register with coordinator
 * - Send heartbeats
 * - Fetch and execute assigned tasks
 * - Report results back
 */

const http = require('http');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const PRIMARY = process.env.SWARM_PRIMARY || 'localhost:9901';
const NODE_NAME = process.env.SWARM_NODE_NAME || `node-${process.pid}`;
const WORKER_COUNT = parseInt(process.env.SWARM_WORKERS || '2', 10);
const HEARTBEAT_INTERVAL = 5000;  // 5 seconds
const POLL_INTERVAL = 1000;       // 1 second

let nodeId = null;
let genAI = null;

// Initialize Gemini client
function initGemini() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    console.error('[AGENT] GEMINI_API_KEY not set');
    process.exit(1);
  }
  genAI = new GoogleGenerativeAI(apiKey);
}

// HTTP helper
function request(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const [host, port] = PRIMARY.split(':');
    const options = {
      hostname: host,
      port: parseInt(port, 10),
      path,
      method,
      headers: { 'Content-Type': 'application/json' }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(data);
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Register with coordinator
async function register() {
  console.log(`[AGENT] Registering with coordinator at ${PRIMARY}...`);
  
  const result = await request('POST', '/register', {
    name: NODE_NAME,
    workers: WORKER_COUNT
  });

  nodeId = result.nodeId;
  console.log(`[AGENT] Registered as ${nodeId}`);
}

// Send heartbeat
async function heartbeat() {
  if (!nodeId) return;
  
  try {
    await request('POST', '/heartbeat', { nodeId });
  } catch (e) {
    console.error(`[AGENT] Heartbeat failed: ${e.message}`);
  }
}

// Execute a task using Gemini
async function executeTask(task) {
  console.log(`[AGENT] Executing task: ${task.id}`);
  
  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    const result = await model.generateContent(task.prompt);
    const text = result.response.text();
    
    return { success: true, text };
  } catch (e) {
    console.error(`[AGENT] Task failed: ${e.message}`);
    return { success: false, error: e.message };
  }
}

// Poll for and execute tasks
async function pollTasks() {
  if (!nodeId) return;

  try {
    const tasks = await request('GET', `/tasks?nodeId=${nodeId}`);
    
    if (Array.isArray(tasks) && tasks.length > 0) {
      console.log(`[AGENT] Got ${tasks.length} tasks`);
      
      // Execute tasks in parallel (up to worker count)
      const batch = tasks.slice(0, WORKER_COUNT);
      const results = await Promise.all(
        batch.map(async (task) => {
          const result = await executeTask(task);
          await request('POST', '/result', { taskId: task.id, result });
          return { taskId: task.id, result };
        })
      );
      
      console.log(`[AGENT] Completed ${results.length} tasks`);
    }
  } catch (e) {
    // Silent on poll errors (coordinator might be restarting)
  }
}

// Main loop
async function main() {
  console.log(`[AGENT] Swarm Worker Agent starting`);
  console.log(`[AGENT] Node: ${NODE_NAME}`);
  console.log(`[AGENT] Workers: ${WORKER_COUNT}`);
  console.log(`[AGENT] Primary: ${PRIMARY}`);

  initGemini();

  // Wait for coordinator to be ready
  let connected = false;
  while (!connected) {
    try {
      await register();
      connected = true;
    } catch (e) {
      console.log(`[AGENT] Waiting for coordinator...`);
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  // Start heartbeat
  setInterval(heartbeat, HEARTBEAT_INTERVAL);

  // Start polling for tasks
  setInterval(pollTasks, POLL_INTERVAL);

  console.log(`[AGENT] Agent running`);
}

main().catch(e => {
  console.error(`[AGENT] Fatal error: ${e.message}`);
  process.exit(1);
});
