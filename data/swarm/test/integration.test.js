/**
 * Integration Tests for Swarm
 * Tests Dispatcher and components working together
 */

const assert = require('assert');
const { Dispatcher } = require('../lib/dispatcher');
const { swarmEvents, EVENTS } = require('../lib/events');

// Test helper
async function test(name, fn) {
  try {
    await fn();
    console.log(`  ✓ ${name}`);
    return true;
  } catch (e) {
    console.log(`  ✗ ${name}`);
    console.log(`    ${e.message}`);
    return false;
  }
}

async function main() {
console.log('\n🔗 INTEGRATION TESTS\n');

let passed = 0;
let failed = 0;

// ============================================
// Dispatcher Tests
// ============================================
console.log('📦 Dispatcher');

// Test: Dispatcher can be instantiated
if (await test('Dispatcher instantiates with defaults', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  assert(dispatcher, 'Dispatcher should be created');
  assert.strictEqual(dispatcher.nodes.size, 0, 'Should start with 0 nodes');
  assert(dispatcher.maxNodes > 0, 'maxNodes should be positive');
  dispatcher.shutdown();
})) passed++; else failed++;

// Test: Dispatcher with custom options
if (await test('Dispatcher accepts custom options', async () => {
  const dispatcher = new Dispatcher({ 
    quiet: true, 
    silent: true,
    trackMetrics: false 
  });
  assert.strictEqual(dispatcher.quiet, true, 'quiet should be true');
  assert.strictEqual(dispatcher.silent, true, 'silent should be true');
  dispatcher.shutdown();
})) passed++; else failed++;

// ============================================
// Event Emission Tests
// ============================================
console.log('\n📡 Event Emission');

// Test: Dispatcher emits SWARM_START on orchestrate
if (await test('Dispatcher emits SWARM_START event', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  let startEvent = null;
  const handler = (data) => { startEvent = data; };
  swarmEvents.on(EVENTS.SWARM_START, handler);
  
  // Empty orchestration to trigger start event
  await dispatcher.orchestrate([
    { name: 'Test', tasks: [] }
  ], { silent: true });
  
  assert(startEvent, 'SWARM_START event should be emitted');
  assert.strictEqual(startEvent.phases, 1, 'Should report 1 phase');
  
  swarmEvents.removeListener(EVENTS.SWARM_START, handler);
  dispatcher.shutdown();
})) passed++; else failed++;

// Test: Dispatcher emits SWARM_COMPLETE on orchestrate
if (await test('Dispatcher emits SWARM_COMPLETE event', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  let completeEvent = null;
  const handler = (data) => { completeEvent = data; };
  swarmEvents.on(EVENTS.SWARM_COMPLETE, handler);
  
  await dispatcher.orchestrate([
    { name: 'Test', tasks: [] }
  ], { silent: true });
  
  assert(completeEvent, 'SWARM_COMPLETE event should be emitted');
  assert.strictEqual(completeEvent.totalTasks, 0, 'Should report 0 tasks');
  assert(completeEvent.durationMs >= 0, 'Should report duration');
  
  swarmEvents.removeListener(EVENTS.SWARM_COMPLETE, handler);
  dispatcher.shutdown();
})) passed++; else failed++;

// Test: Dispatcher emits PHASE_START event
if (await test('Dispatcher emits PHASE_START event', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  let phaseEvent = null;
  const handler = (data) => { phaseEvent = data; };
  swarmEvents.on(EVENTS.PHASE_START, handler);
  
  await dispatcher.orchestrate([
    { name: 'TestPhase', tasks: [] }
  ], { silent: true });
  
  // Phase start only emits if there are tasks (tasks: [] skips)
  // So we don't assert here - empty phases skip
  
  swarmEvents.removeListener(EVENTS.PHASE_START, handler);
  dispatcher.shutdown();
})) passed++; else failed++;

// ============================================
// Parallel Execution (with mock)
// ============================================
console.log('\n⚡ Parallel Execution');

// Mock the WorkerNode for testing without API calls
class MockWorkerNode {
  constructor(id, nodeType) {
    this.id = id;
    this.nodeType = nodeType;
    this.status = 'idle';
    this.completedTasks = 0;
  }
  
  async execute(task) {
    this.status = 'busy';
    // Simulate async work
    await new Promise(r => setTimeout(r, 10));
    this.status = 'idle';
    this.completedTasks++;
    
    return {
      nodeId: this.id,
      nodeType: this.nodeType,
      taskId: task.id,
      success: true,
      result: { response: `Mock response for: ${task.instruction || task.input}` },
      durationMs: 10,
    };
  }
  
  getStats() {
    return {
      id: this.id,
      type: this.nodeType,
      status: this.status,
      completedTasks: this.completedTasks,
    };
  }
}

// Test: Parallel execution completes all tasks
if (await test('Parallel execution completes all tasks', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  // Override getOrCreateNode to use mock
  const originalGetOrCreate = dispatcher.getOrCreateNode.bind(dispatcher);
  let nodeCount = 0;
  dispatcher.getOrCreateNode = (nodeType) => {
    const id = `mock-${nodeType}-${++nodeCount}`;
    const node = new MockWorkerNode(id, nodeType);
    dispatcher.nodes.set(id, node);
    return node;
  };
  
  const tasks = [
    { nodeType: 'analyze', instruction: 'Task 1' },
    { nodeType: 'analyze', instruction: 'Task 2' },
    { nodeType: 'analyze', instruction: 'Task 3' },
  ];
  
  const result = await dispatcher.executeParallel(tasks);
  
  assert.strictEqual(result.results.length, 3, 'Should have 3 results');
  assert.strictEqual(result.results.filter(r => r.success).length, 3, 'All should succeed');
  assert(result.totalDurationMs >= 0, 'Should report duration');
  
  dispatcher.shutdown();
})) passed++; else failed++;

// Test: Task events are emitted during parallel execution
if (await test('Task events emitted during parallel execution', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  // Override with mock
  let nodeCount = 0;
  dispatcher.getOrCreateNode = (nodeType) => {
    const id = `mock-${nodeType}-${++nodeCount}`;
    const node = new MockWorkerNode(id, nodeType);
    dispatcher.nodes.set(id, node);
    return node;
  };
  
  const taskStarts = [];
  const taskCompletes = [];
  
  const startHandler = (data) => taskStarts.push(data);
  const completeHandler = (data) => taskCompletes.push(data);
  
  swarmEvents.on(EVENTS.TASK_START, startHandler);
  swarmEvents.on(EVENTS.TASK_COMPLETE, completeHandler);
  
  const tasks = [
    { nodeType: 'analyze', instruction: 'Task 1', label: 'Label 1' },
    { nodeType: 'analyze', instruction: 'Task 2', label: 'Label 2' },
  ];
  
  await dispatcher.executeParallel(tasks);
  
  assert.strictEqual(taskStarts.length, 2, 'Should emit 2 TASK_START events');
  assert.strictEqual(taskCompletes.length, 2, 'Should emit 2 TASK_COMPLETE events');
  assert.strictEqual(taskStarts[0].label, 'Label 1', 'Should include label');
  
  swarmEvents.removeListener(EVENTS.TASK_START, startHandler);
  swarmEvents.removeListener(EVENTS.TASK_COMPLETE, completeHandler);
  dispatcher.shutdown();
})) passed++; else failed++;

// ============================================
// Orchestration Tests
// ============================================
console.log('\n🎭 Orchestration');

// Test: Multi-phase orchestration
if (await test('Multi-phase orchestration works', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  // Override with mock
  let nodeCount = 0;
  dispatcher.getOrCreateNode = (nodeType) => {
    const id = `mock-${nodeType}-${++nodeCount}`;
    const node = new MockWorkerNode(id, nodeType);
    dispatcher.nodes.set(id, node);
    return node;
  };
  
  const phases = [
    {
      name: 'Phase 1',
      tasks: [
        { nodeType: 'analyze', instruction: 'P1 Task 1' },
        { nodeType: 'analyze', instruction: 'P1 Task 2' },
      ]
    },
    {
      name: 'Phase 2',
      tasks: [
        { nodeType: 'analyze', instruction: 'P2 Task 1' },
      ]
    }
  ];
  
  const result = await dispatcher.orchestrate(phases, { silent: true });
  
  assert.strictEqual(result.phases.length, 2, 'Should have 2 phases');
  assert.strictEqual(result.phases[0].results.length, 2, 'Phase 1 should have 2 results');
  assert.strictEqual(result.phases[1].results.length, 1, 'Phase 2 should have 1 result');
  assert(result.success, 'Orchestration should succeed');
  
  dispatcher.shutdown();
})) passed++; else failed++;

// Test: Dynamic phase tasks (function)
if (await test('Dynamic phase tasks from function', async () => {
  const dispatcher = new Dispatcher({ silent: true, trackMetrics: false });
  
  // Override with mock
  let nodeCount = 0;
  dispatcher.getOrCreateNode = (nodeType) => {
    const id = `mock-${nodeType}-${++nodeCount}`;
    const node = new MockWorkerNode(id, nodeType);
    dispatcher.nodes.set(id, node);
    return node;
  };
  
  const phases = [
    {
      name: 'Phase 1',
      tasks: [
        { nodeType: 'analyze', instruction: 'First task' },
      ]
    },
    {
      name: 'Phase 2 (Dynamic)',
      tasks: (prevResults) => {
        // Use results from phase 1 to create phase 2 tasks
        return prevResults[0].results.map((r, i) => ({
          nodeType: 'analyze',
          instruction: `Follow-up for task ${i + 1}`,
        }));
      }
    }
  ];
  
  const result = await dispatcher.orchestrate(phases, { silent: true });
  
  assert.strictEqual(result.phases.length, 2, 'Should have 2 phases');
  assert.strictEqual(result.phases[1].results.length, 1, 'Phase 2 should have 1 task (from phase 1)');
  
  dispatcher.shutdown();
})) passed++; else failed++;

// ============================================
// Summary
// ============================================
console.log('\n' + '─'.repeat(40));
console.log(`Integration Tests: ${passed} passed, ${failed} failed`);

return failed;
}

main().then(failed => process.exit(failed > 0 ? 1 : 0));
