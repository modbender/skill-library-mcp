export const SCHEMA_VERSION = '1.0.0';

export type SensitivityTag = 'public' | 'internal' | 'confidential' | 'restricted';
export type VaultProvider = 'filesystem' | 's3';

export interface SourceContext {
  channel: string;
  sender: string;
  messageId?: string;
  sessionId?: string;
}

export interface RetentionPolicy {
  retentionDays: number;
  legalHold: boolean;
  deleteAfter: string;
}

export interface OriginalFile {
  filename: string;
  sha256: string;
  size: number;
  mime: string;
  receivedAt: string;
  source: SourceContext;
}

export interface FileMetadata {
  exif?: Record<string, unknown>;
  duration?: number;
  pages?: number;
  dimensions?: { width: number; height: number };
  author?: string;
  createdAt?: string;
  [key: string]: unknown;
}

export interface Derivative {
  type: 'thumbnail' | 'transcript' | 'preview' | 'ocr';
  filename: string;
  sha256: string;
  size: number;
  generatedAt: string;
}

export interface VaultInfo {
  provider: VaultProvider;
  vaultUrl: string;
  ingestedAt: string;
}

export interface EvidenceItem {
  evidenceId: string;
  original: OriginalFile;
  metadata: FileMetadata;
  derivatives: Derivative[];
  vault: VaultInfo;
}

export interface ChainEntry {
  event: string;
  timestamp: string;
  actor: string;
  evidenceId?: string;
  previousHash: string | null;
  currentHash: string;
  details?: Record<string, unknown>;
}

export interface CaseManifest {
  schemaVersion: string;
  caseId: string;
  createdAt: string;
  updatedAt: string;
  sensitivityTag: SensitivityTag;
  retentionPolicy: RetentionPolicy;
  items: EvidenceItem[];
  chainOfCustody: ChainEntry[];
}

export interface AuditEvent {
  eventType: string;
  timestamp: string;
  caseId: string;
  evidenceId?: string;
  actor: string;
  details: Record<string, unknown>;
  hash?: string;
  previousHash?: string;
}

export interface IngestResult {
  success: boolean;
  evidenceId: string;
  sha256: string;
  vaultUrl: string;
  timestamp: string;
  error?: VaultError;
}

export interface VerifyResult {
  success: boolean;
  evidenceId: string;
  caseId: string;
  verified: boolean;
  details: {
    originalIntact: boolean;
    hashMatch: boolean;
    lastVerifiedAt: string;
  };
  error?: VaultError;
}

export interface ExportResult {
  success: boolean;
  caseId: string;
  exportPath: string;
  sha256: string;
  size: number;
  itemCount: number;
  timestamp: string;
  error?: VaultError;
}

export interface AccessLogResult {
  success: boolean;
  caseId: string;
  events: AuditEvent[];
  count: number;
  error?: VaultError;
}

export interface VaultError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface VaultConfig {
  driver: VaultProvider;
  basePath: string;
  maxFileSizeBytes: number;
  allowedMimeTypes: string[];
  defaultRetentionDays: number;
  enforceLegalHold: boolean;
  auditLogPath: string;
  redactPatterns: string[];
}

export const DEFAULT_CONFIG: VaultConfig = {
  driver: 'filesystem',
  basePath: './evidence-vault',
  maxFileSizeBytes: 500 * 1024 * 1024,
  allowedMimeTypes: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'video/mp4',
    'video/webm',
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'application/pdf',
    'application/zip',
    'text/plain',
    'application/json',
  ],
  defaultRetentionDays: 2555,
  enforceLegalHold: true,
  auditLogPath: './evidence-vault/audit',
  redactPatterns: [
    /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
    /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,
    /\b\d{11,16}\b/g,
    /(?:sk-|pk-|api[_-]?key|token|secret|password|credential)[\s:=]+[\w\-]+/gi,
  ],
};

export const VAULT_ERRORS = {
  PATH_TRAVERSAL: 'E_PATH_TRAVERSAL',
  INVALID_MIME: 'E_INVALID_MIME',
  SIZE_LIMIT: 'E_SIZE_LIMIT',
  HASH_MISMATCH: 'E_HASH_MISMATCH',
  NOT_FOUND: 'E_NOT_FOUND',
  PERMISSION_DENIED: 'E_PERMISSION_DENIED',
  VAULT_ERROR: 'E_VAULT_ERROR',
  INVALID_CASE: 'E_INVALID_CASE',
  CHANNEL_BLOCKED: 'E_CHANNEL_BLOCKED',
  INVALID_INPUT: 'E_INVALID_INPUT',
  ALREADY_EXISTS: 'E_ALREADY_EXISTS',
} as const;

export function createVaultError(
  code: string,
  message: string,
  details?: Record<string, unknown>
): VaultError {
  return { code, message, details: details ?? {} };
}
