/**
 * Memory-as-Tools Type Definitions
 *
 * Core types for the agent-controlled memory system with
 * confidence scoring, decay, and semantic search.
 */

export const MEMORY_CATEGORIES = [
  'fact',         // "User's dog is named Rex"
  'preference',   // "User prefers dark mode"
  'event',        // "User has dentist appointment Tuesday"
  'relationship', // "User's sister is named Sarah"
  'context',      // "User is working on a React project"
  'instruction',  // "Always respond in Spanish"
  'decision',     // "We decided to use PostgreSQL"
  'entity',       // Contact info, phone numbers, emails
] as const;

export type MemoryCategory = typeof MEMORY_CATEGORIES[number];

export interface Memory {
  id: string;
  content: string;
  category: MemoryCategory;
  confidence: number;        // 0.0 - 1.0: how sure are we this is accurate
  importance: number;        // 0.0 - 1.0: how important is this

  // Temporal
  createdAt: number;         // Unix timestamp ms
  updatedAt: number;         // Unix timestamp ms
  lastAccessedAt: number;    // Unix timestamp ms
  decayDays: number | null;  // null = permanent

  // Provenance
  sourceChannel?: string;    // 'whatsapp' | 'telegram' | 'discord' | etc
  sourceMessageId?: string;  // for traceability

  // Relations
  tags: string[];
  supersedes?: string;       // id of memory this updates/replaces

  // Soft delete
  deletedAt?: number;
  deleteReason?: string;
}

export interface MemorySearchResult {
  memory: Memory;
  score: number;             // Similarity score 0-1
}

export interface CreateMemoryInput {
  content: string;
  category: MemoryCategory;
  confidence?: number;
  importance?: number;
  decayDays?: number | null;
  tags?: string[];
  sourceChannel?: string;
  sourceMessageId?: string;
}

export interface UpdateMemoryInput {
  content?: string;
  confidence?: number;
  importance?: number;
  decayDays?: number | null;
  tags?: string[];
}

export interface SearchOptions {
  query?: string;
  category?: MemoryCategory;
  tags?: string[];
  minConfidence?: number;
  minImportance?: number;
  limit?: number;
  excludeDecayed?: boolean;
  includeDeleted?: boolean;
}

export interface ListOptions {
  category?: MemoryCategory;
  sortBy?: 'createdAt' | 'updatedAt' | 'importance' | 'confidence' | 'lastAccessedAt';
  sortOrder?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}
