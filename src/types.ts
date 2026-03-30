export interface SkillFrontmatter {
  name: string;
  description: string;
  metadata?: Record<string, unknown>;
  allowedTools?: string[];
}

export interface SkillEntry {
  dirName: string;
  frontmatter: SkillFrontmatter;
  searchTokens: Set<string>;
  hasResources: boolean;
  resourceFiles: string[];
}

export interface SearchIndex {
  entries: SkillEntry[];
  idfScores: Map<string, number>;
  totalDocs: number;
  categories: Map<string, string[]>;
}

export interface SearchResult {
  name: string;
  dirName: string;
  description: string;
  score: number;
  hasResources: boolean;
}

export interface SkillsIndexEntry {
  name: string;
  description: string;
  hasResources: boolean;
  resourceFiles: string[];
  metadata?: Record<string, unknown>;
  allowedTools?: string[];
}

export interface SkillsIndex {
  version: number;
  skills: Record<string, SkillsIndexEntry>;
}

export interface SkillsBundleEntry {
  content: string;
  resources?: Record<string, string>;
}

export interface SkillsBundle {
  version: number;
  skills: Record<string, SkillsBundleEntry>;
}
