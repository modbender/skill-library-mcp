/**
 * Swarm Coordinator Server
 * 
 * Responsibilities:
 * - Accept task batches via REST API
 * - Distribute tasks to connected workers
 * - Track worker health via heartbeats
 * - Aggregate and return results
 */

const http = require('http');
const { EventEmitter } = require('events');

const PORT_API = process.env.SWARM_API_PORT || 9900;
const PORT_WORKER = process.env.SWARM_WORKER_PORT || 9901;

// State
const workers = new Map();  // nodeId -> { name, workers, lastHeartbeat, tasks }
const tasks = new Map();    // taskId -> { status, results, created }
const taskQueue = [];       // Pending tasks

class Coordinator extends EventEmitter {
  constructor() {
    super();
    this.startTime = Date.now();
  }

  // Register a worker node
  registerWorker(nodeId, info) {
    workers.set(nodeId, {
      ...info,
      lastHeartbeat: Date.now(),
      activeTasks: 0
    });
    console.log(`[COORDINATOR] Worker registered: ${info.name} (${info.workers} workers)`);
    this.emit('worker:registered', nodeId);
  }

  // Handle heartbeat from worker
  heartbeat(nodeId) {
    const worker = workers.get(nodeId);
    if (worker) {
      worker.lastHeartbeat = Date.now();
    }
  }

  // Submit a batch of tasks
  submitBatch(batch) {
    const batchId = `batch-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const taskIds = [];

    for (const task of batch.tasks) {
      const taskId = `task-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      tasks.set(taskId, {
        id: taskId,
        batchId,
        prompt: task.prompt,
        status: 'pending',
        result: null,
        created: Date.now()
      });
      taskQueue.push(taskId);
      taskIds.push(taskId);
    }

    console.log(`[COORDINATOR] Batch submitted: ${batchId} (${taskIds.length} tasks)`);
    this.distributeTasks();

    return { batchId, taskIds };
  }

  // Distribute pending tasks to available workers
  distributeTasks() {
    // Simple round-robin for now
    const availableWorkers = [...workers.entries()]
      .filter(([_, w]) => Date.now() - w.lastHeartbeat < 30000)
      .sort((a, b) => a[1].activeTasks - b[1].activeTasks);

    while (taskQueue.length > 0 && availableWorkers.length > 0) {
      const taskId = taskQueue.shift();
      const [nodeId, worker] = availableWorkers[0];
      
      worker.activeTasks++;
      tasks.get(taskId).status = 'assigned';
      tasks.get(taskId).assignedTo = nodeId;

      this.emit('task:assigned', { taskId, nodeId });
      
      // Re-sort to balance load
      availableWorkers.sort((a, b) => a[1].activeTasks - b[1].activeTasks);
    }
  }

  // Record task completion
  completeTask(taskId, result) {
    const task = tasks.get(taskId);
    if (task) {
      task.status = 'completed';
      task.result = result;
      task.completedAt = Date.now();

      const worker = workers.get(task.assignedTo);
      if (worker) worker.activeTasks--;

      console.log(`[COORDINATOR] Task completed: ${taskId}`);
      this.emit('task:completed', { taskId, result });
    }
  }

  // Get cluster status
  getStatus() {
    return {
      uptime: Date.now() - this.startTime,
      workers: [...workers.entries()].map(([id, w]) => ({
        id,
        name: w.name,
        workers: w.workers,
        activeTasks: w.activeTasks,
        healthy: Date.now() - w.lastHeartbeat < 30000
      })),
      tasks: {
        pending: taskQueue.length,
        active: [...tasks.values()].filter(t => t.status === 'assigned').length,
        completed: [...tasks.values()].filter(t => t.status === 'completed').length
      }
    };
  }
}

const coordinator = new Coordinator();

// REST API Server
const apiServer = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT_API}`);
  
  res.setHeader('Content-Type', 'application/json');

  // Health check
  if (req.method === 'GET' && url.pathname === '/health') {
    res.end(JSON.stringify({ status: 'ok', uptime: Date.now() - coordinator.startTime }));
    return;
  }

  // Cluster status
  if (req.method === 'GET' && url.pathname === '/status') {
    res.end(JSON.stringify(coordinator.getStatus()));
    return;
  }

  // List workers
  if (req.method === 'GET' && url.pathname === '/workers') {
    res.end(JSON.stringify(coordinator.getStatus().workers));
    return;
  }

  // Submit tasks
  if (req.method === 'POST' && url.pathname === '/tasks') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const batch = JSON.parse(body);
        const result = coordinator.submitBatch(batch);
        res.end(JSON.stringify(result));
      } catch (e) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // Get task status
  if (req.method === 'GET' && url.pathname.startsWith('/tasks/')) {
    const taskId = url.pathname.split('/')[2];
    const task = tasks.get(taskId);
    if (task) {
      res.end(JSON.stringify(task));
    } else {
      res.statusCode = 404;
      res.end(JSON.stringify({ error: 'Task not found' }));
    }
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Worker Protocol Server (TCP-like communication)
const workerServer = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT_WORKER}`);
  res.setHeader('Content-Type', 'application/json');

  // Worker registration
  if (req.method === 'POST' && url.pathname === '/register') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const info = JSON.parse(body);
      const nodeId = `node-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      coordinator.registerWorker(nodeId, info);
      res.end(JSON.stringify({ nodeId, status: 'registered' }));
    });
    return;
  }

  // Heartbeat
  if (req.method === 'POST' && url.pathname === '/heartbeat') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const { nodeId } = JSON.parse(body);
      coordinator.heartbeat(nodeId);
      res.end(JSON.stringify({ status: 'ok' }));
    });
    return;
  }

  // Get assigned tasks
  if (req.method === 'GET' && url.pathname === '/tasks') {
    const nodeId = url.searchParams.get('nodeId');
    const assigned = [...tasks.values()]
      .filter(t => t.assignedTo === nodeId && t.status === 'assigned');
    res.end(JSON.stringify(assigned));
    return;
  }

  // Submit result
  if (req.method === 'POST' && url.pathname === '/result') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const { taskId, result } = JSON.parse(body);
      coordinator.completeTask(taskId, result);
      res.end(JSON.stringify({ status: 'ok' }));
    });
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Start servers
apiServer.listen(PORT_API, () => {
  console.log(`[COORDINATOR] API server listening on port ${PORT_API}`);
});

workerServer.listen(PORT_WORKER, () => {
  console.log(`[COORDINATOR] Worker server listening on port ${PORT_WORKER}`);
});

console.log(`[COORDINATOR] Swarm coordinator started`);
console.log(`[COORDINATOR] Cluster: ${process.env.SWARM_CLUSTER_NAME || 'default'}`);
