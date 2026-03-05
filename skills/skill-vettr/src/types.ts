export interface SkillManifest {
  name: string;
  version: string;
  author?: string;
  description?: string;
  tools?: string[];
  permissions?: string[];
  dependencies?: Record<string, string>;
}

export interface VettingReport {
  skillName: string;
  riskScore: number;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  findings: Finding[];
  metadata: SkillMetadata;
  recommendation: 'INSTALL' | 'REVIEW' | 'BLOCK';
  vettedAt: string;
  vettrVersion: string;
}

export interface SkillMetadata {
  authorVerified: boolean;
  hasExternalDeps: boolean;
  networkCalls: NetworkCall[];
  fileCount: number;
  totalLines: number;
  checksumSha256?: string;
}

export interface NetworkCall {
  url: string;
  file: string;
  line?: number;
  allowed: boolean;
}

export interface Finding {
  id: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  category: FindingCategory;
  message: string;
  file: string;
  line?: number;
  evidence: string;
  cwe?: string;
}

export type FindingCategory =
  | 'PROMPT_INJECTION'
  | 'CODE_OBFUSCATION'
  | 'NETWORK_RISK'
  | 'PERMISSION_RISK'
  | 'DEPENDENCY_RISK'
  | 'TYPO_SQUATTING'
  | 'PATH_TRAVERSAL'
  | 'SHELL_INJECTION';

export interface VettingConfig {
  maxNetworkCalls: number;
  allowedHosts: string[];
  blockObfuscation: boolean;
  requireAuthor: boolean;
  maxRiskScore: number;
  checkTyposquatting: boolean;
  maliciousPatternsUrl?: string;
  maliciousPatternsRefreshHours: number;
  blockedAuthors?: string[];
  blockedPackages?: string[];
  typosquatTargets?: string[];
  allowCwd?: boolean;
}

export interface AllowedRootsConfig {
  allowCwd?: boolean;
  additionalRoots?: string[];
}

export interface ToolsInterface {
  readFile(path: string): Promise<string>;
  writeFile(path: string, content: string): Promise<void>;
  stat(path: string): Promise<{ isDirectory(): boolean; isFile(): boolean; isSymbolicLink(): boolean }>;
  lstat(path: string): Promise<{ isDirectory(): boolean; isFile(): boolean; isSymbolicLink(): boolean }>;
  realpath(path: string): Promise<string>;
  readdir(path: string): Promise<string[]>;
  mkdtemp(prefix: string): Promise<string>;
  rm(path: string, opts?: { recursive?: boolean; force?: boolean }): Promise<void>;
  exists(path: string): Promise<boolean>;
}
