/**
 * PMP-Agent — Project Management Professional Agent
 * PMBOK 7th Edition TypeScript Implementation
 * 
 * @packageDocumentation
 */

// Export all core functionality
export * from './core';

// Version
export const VERSION = '1.0.0';
export const PMBOK_VERSION = '7th Edition';

// Default export
export { calculateEVM as default } from './core';
