/**
 * Example: Multi-Agent Task Coordination
 * 
 * Multiple agents share a task list and coordinate work via SQ.
 * No central database needed - agents read/write shared coordinates.
 */

/**
 * Agent A: Create a task
 */
async function createTask(taskId, description, assignedTo = null) {
  const coordinate = `shared/tasks/pending/${taskId}`;
  
  await remember(coordinate, JSON.stringify({
    id: taskId,
    description: description,
    assignedTo: assignedTo,
    status: 'pending',
    createdAt: Date.now(),
    createdBy: 'agent-a'  // Could be dynamic
  }));
  
  return `Task ${taskId} created`;
}

/**
 * Agent B: Claim a task
 */
async function claimTask(taskId, agentName) {
  const pendingCoord = `shared/tasks/pending/${taskId}`;
  const task = await recall(pendingCoord);
  
  if (!task) {
    return `Task ${taskId} not found`;
  }
  
  const data = JSON.parse(task);
  data.assignedTo = agentName;
  data.status = 'in-progress';
  data.claimedAt = Date.now();
  
  // Move from pending to in-progress
  await forget(pendingCoord);
  await remember(`shared/tasks/in-progress/${taskId}`, JSON.stringify(data));
  
  return `Task ${taskId} claimed by ${agentName}`;
}

/**
 * Agent B: Complete a task
 */
async function completeTask(taskId, result = null) {
  const inProgressCoord = `shared/tasks/in-progress/${taskId}`;
  const task = await recall(inProgressCoord);
  
  if (!task) {
    return `Task ${taskId} not found`;
  }
  
  const data = JSON.parse(task);
  data.status = 'completed';
  data.completedAt = Date.now();
  data.result = result;
  
  // Move from in-progress to completed
  await forget(inProgressCoord);
  await remember(`shared/tasks/completed/${taskId}`, JSON.stringify(data));
  
  return `Task ${taskId} marked complete`;
}

/**
 * Any agent: List pending tasks
 */
async function listPendingTasks() {
  const coords = await list_memories('shared/tasks/pending/');
  const tasks = [];
  
  for (const coord of coords) {
    const text = await recall(coord);
    if (text) {
      try {
        tasks.push(JSON.parse(text));
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return tasks.sort((a, b) => a.createdAt - b.createdAt);
}

/**
 * Any agent: List in-progress tasks
 */
async function listInProgressTasks() {
  const coords = await list_memories('shared/tasks/in-progress/');
  const tasks = [];
  
  for (const coord of coords) {
    const text = await recall(coord);
    if (text) {
      try {
        tasks.push(JSON.parse(text));
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return tasks;
}

/**
 * Workflow Example:
 */

// Agent A (Coordinator):
// await createTask("task-001", "Review PR #123", null);
// await createTask("task-002", "Write docs for feature X", "agent-b");

// Agent B (Worker):
// const pending = await listPendingTasks();
// // Sees: [{ id: "task-001", description: "Review PR #123", ... }]
// 
// await claimTask("task-001", "agent-b");
// // ... does work ...
// await completeTask("task-001", "PR approved and merged");

// Agent A (checking status):
// const inProgress = await listInProgressTasks();
// // Sees agent-b working on task-001
// 
// const completed = await listCompletedTasks();
// // Sees task-001 completed with result

/**
 * Advanced: Agent capability registry
 */

// Each agent registers what it can do:
async function registerCapability(agentName, capabilities) {
  const coordinate = `agents/registry/${agentName}`;
  await remember(coordinate, JSON.stringify({
    name: agentName,
    capabilities: capabilities,  // ["code-review", "documentation", "testing"]
    status: 'online',
    lastSeen: Date.now()
  }));
}

// Coordinator can find agents by capability:
async function findAgentsByCapability(capability) {
  const coords = await list_memories('agents/registry/');
  const agents = [];
  
  for (const coord of coords) {
    const text = await recall(coord);
    if (text) {
      try {
        const data = JSON.parse(text);
        if (data.capabilities.includes(capability)) {
          agents.push(data.name);
        }
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return agents;
}

// Usage:
// await registerCapability("agent-b", ["code-review", "documentation"]);
// const reviewers = await findAgentsByCapability("code-review");
// // Returns: ["agent-b"]
// await createTask("task-003", "Review security audit", reviewers[0]);

/**
 * Advanced: Inter-agent messaging
 */

async function sendMessage(fromAgent, toAgent, message) {
  const timestamp = Date.now();
  const coordinate = `messages/${toAgent}/inbox/${timestamp}`;
  
  await remember(coordinate, JSON.stringify({
    from: fromAgent,
    to: toAgent,
    message: message,
    timestamp: timestamp,
    read: false
  }));
}

async function readInbox(agentName) {
  const coords = await list_memories(`messages/${agentName}/inbox/`);
  const messages = [];
  
  for (const coord of coords) {
    const text = await recall(coord);
    if (text) {
      try {
        const msg = JSON.parse(text);
        if (!msg.read) {
          messages.push(msg);
          
          // Mark as read
          msg.read = true;
          await remember(coord, JSON.stringify(msg));
        }
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return messages.sort((a, b) => a.timestamp - b.timestamp);
}

// Usage:
// Agent A: await sendMessage("agent-a", "agent-b", "Please review PR #123");
// Agent B: const inbox = await readInbox("agent-b");
//          // Sees message from agent-a

/**
 * Coordinate structure for multi-agent workflows:
 * 
 * shared/tasks/pending/<task-id>
 * shared/tasks/in-progress/<task-id>
 * shared/tasks/completed/<task-id>
 * shared/tasks/failed/<task-id>
 * 
 * agents/registry/<agent-name>
 * agents/heartbeat/<agent-name>
 * 
 * messages/<agent-name>/inbox/<timestamp>
 * messages/<agent-name>/sent/<timestamp>
 * 
 * This enables:
 * - Distributed task queues
 * - Agent discovery
 * - Async coordination
 * - No central orchestrator needed
 */

/**
 * Heartbeat pattern for agent health monitoring:
 */
async function heartbeat(agentName, status = 'online') {
  const coordinate = `agents/heartbeat/${agentName}`;
  await remember(coordinate, JSON.stringify({
    name: agentName,
    status: status,  // "online", "busy", "offline"
    timestamp: Date.now()
  }));
}

async function checkAgentHealth(agentName, timeoutMs = 60000) {
  const coordinate = `agents/heartbeat/${agentName}`;
  const text = await recall(coordinate);
  
  if (!text) {
    return 'unknown';
  }
  
  try {
    const data = JSON.parse(text);
    const age = Date.now() - data.timestamp;
    
    if (age > timeoutMs) {
      return 'offline';
    }
    
    return data.status;
  } catch (e) {
    return 'error';
  }
}

// Each agent sends heartbeat every 30 seconds:
// setInterval(() => heartbeat("agent-b", "online"), 30000);

// Coordinator checks health:
// const health = await checkAgentHealth("agent-b");
// if (health === 'offline') {
//   console.log("Agent B is down, reassigning tasks...");
// }
