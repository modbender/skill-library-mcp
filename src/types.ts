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
