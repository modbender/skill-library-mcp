/**
 * Muninn Memory - Entry Point
 * 
 * A local-first memory system for AI agents.
 * 
 * Usage:
 *   import { MemoryStore } from 'muninn-memory';
 *   
 *   const memory = new MemoryStore('./memories.db');
 *   await memory.remember('content', 'semantic');
 *   const results = await memory.recall('query');
 */

// Re-export main classes and types
export { MemoryStore, generateEmbedding, type Memory, type MemoryType, type VaultStats, type Entity, type Procedure, type MemoryEdge } from './storage/index.js';
export type { MemoryStore as MuninnMemory };

// Default export
import { MemoryStore } from './storage/index.js';
export default MemoryStore;
