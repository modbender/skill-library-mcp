/**
 * Swarm Event System
 * Emits events for UI feedback and monitoring
 */

const { EventEmitter } = require('events');

// Global event bus for swarm operations
const swarmEvents = new EventEmitter();

// Event types
const EVENTS = {
  // Lifecycle
  SWARM_START: 'swarm:start',
  SWARM_COMPLETE: 'swarm:complete',
  SWARM_ERROR: 'swarm:error',
  
  // Phase events
  PHASE_START: 'phase:start',
  PHASE_COMPLETE: 'phase:complete',
  
  // Task events
  TASK_QUEUED: 'task:queued',
  TASK_START: 'task:start',
  TASK_COMPLETE: 'task:complete',
  TASK_ERROR: 'task:error',
  
  // Worker events
  WORKER_SPAWN: 'worker:spawn',
  WORKER_BUSY: 'worker:busy',
  WORKER_IDLE: 'worker:idle',
  WORKER_RECYCLE: 'worker:recycle',
  
  // Progress
  PROGRESS: 'progress',
};

module.exports = { swarmEvents, EVENTS };
