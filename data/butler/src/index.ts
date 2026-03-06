/**
 * Butler - AI Agent Treasury & Orchestration Skill
 * 
 * Main entry point for the Butler skill.
 * Provides token management, agent orchestration, and treasury functions.
 */

export { Butler } from './Butler';
export { TokenManager } from './core/TokenManager';
export { AgentOrchestrator } from './core/AgentOrchestrator';

// Version info
export const BUTLER_VERSION = '0.1.0';
export const HACKATHON = 'Circle USDC Hackathon';
export const DEADLINE = '2026-02-08T20:00:00.000Z'; // Feb 8, 12 PM PST

// Quick start
export function createButler(keysPath?: string, statePath?: string) {
  const { Butler } = require('./Butler');
  return new Butler(keysPath, statePath);
}
