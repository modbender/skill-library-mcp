export interface VaultConfig {
  path: string;
  name: string;
  categories: string[];
  autoSync?: boolean;
  notion?: NotionConfig;
}

export interface NotionConfig {
  token: string;
  rootPageId: string;
  databases?: Record<string, string>;
}

export interface VaultMeta {
  name: string;
  version: string;
  created: string;
  lastUpdated: string;
  categories: string[];
  documentCount: number;
}

export interface MemDocument {
  id: string;
  path: string;
  category: string;
  title: string;
  content: string;
  frontmatter: Record<string, unknown>;
  tags: string[];
  created: string;
  updated: string;
}

export interface SearchResult {
  document: MemDocument;
  score: number;
  snippet: string;
}

export interface SearchOptions {
  limit?: number;
  minScore?: number;
  category?: string;
  tags?: string[];
}

export interface StoreOptions {
  category: string;
  title: string;
  content: string;
  frontmatter?: Record<string, unknown>;
  overwrite?: boolean;
}

export type MemoryType =
  | 'fact'
  | 'decision'
  | 'lesson'
  | 'commitment'
  | 'preference'
  | 'relationship'
  | 'project';

export const MEMORY_TYPES: MemoryType[] = [
  'fact', 'decision', 'lesson', 'commitment',
  'preference', 'relationship', 'project',
];

export const TYPE_TO_CATEGORY: Record<MemoryType, string> = {
  fact: 'facts',
  decision: 'decisions',
  lesson: 'lessons',
  commitment: 'commitments',
  preference: 'preferences',
  relationship: 'people',
  project: 'projects',
};

export const DEFAULT_CATEGORIES: string[] = [
  'decisions',
  'preferences',
  'lessons',
  'facts',
  'commitments',
  'people',
  'projects',
  'inbox',
  'sessions',
  'observations',
];

export type SessionState = 'idle' | 'active';

export interface SessionData {
  state: SessionState;
  startedAt?: string;
  workingOn?: string;
  focus?: string;
  lastCheckpoint?: string;
}

export interface HandoffDocument {
  created: string;
  summary: string;
  workingOn?: string;
  focus?: string;
  nextSteps?: string;
  decisions?: string[];
  openQuestions?: string[];
}

export interface SyncStateEntry {
  localPath: string;
  notionPageId: string;
  lastSyncedAt: string;
  localUpdatedAt: string;
  notionUpdatedAt: string;
}

export interface SyncState {
  lastSyncAt: string;
  databases: Record<string, string>;
  entries: Record<string, SyncStateEntry>;
}
