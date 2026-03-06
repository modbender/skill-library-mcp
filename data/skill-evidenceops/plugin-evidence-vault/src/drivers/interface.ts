import {
  CaseManifest,
  VaultConfig,
  IngestResult,
  VerifyResult,
  ExportResult,
  AccessLogResult,
  AuditEvent,
  SourceContext,
  RetentionPolicy,
  createVaultError,
  VAULT_ERRORS,
} from '../types';

export interface IngestInput {
  filePath: string;
  filename: string;
  mimeType: string;
  size: number;
  caseId: string;
  sourceContext: SourceContext;
  retentionPolicy?: Partial<RetentionPolicy>;
  metadata?: Record<string, unknown>;
}

export interface VaultDriver {
  readonly name: string;
  initialize(config: VaultConfig): Promise<void>;
  healthCheck(): Promise<{ healthy: boolean; details: Record<string, unknown> }>;
  
  createCase(caseId: string, sensitivityTag?: string): Promise<{ success: boolean; caseId: string; error?: { code: string; message: string } }>;
  caseExists(caseId: string): Promise<boolean>;
  
  ingest(input: IngestInput): Promise<IngestResult>;
  verify(evidenceId: string, caseId?: string): Promise<VerifyResult>;
  export(caseId: string, format?: 'zip' | 'tar'): Promise<ExportResult>;
  
  getManifest(caseId: string): Promise<{ success: boolean; manifest?: CaseManifest; error?: { code: string; message: string } }>;
  updateManifest(caseId: string, manifest: CaseManifest): Promise<{ success: boolean; error?: { code: string; message: string } }>;
  
  writeAudit(event: AuditEvent): Promise<{ success: boolean; error?: { code: string; message: string } }>;
  getAccessLog(caseId: string, limit?: number): Promise<AccessLogResult>;
  
  shutdown(): Promise<void>;
}

export abstract class BaseDriver implements VaultDriver {
  abstract readonly name: string;
  protected config!: VaultConfig;
  protected initialized = false;
  
  abstract initialize(config: VaultConfig): Promise<void>;
  abstract healthCheck(): Promise<{ healthy: boolean; details: Record<string, unknown> }>;
  abstract createCase(caseId: string, sensitivityTag?: string): Promise<{ success: boolean; caseId: string; error?: { code: string; message: string } }>;
  abstract caseExists(caseId: string): Promise<boolean>;
  abstract ingest(input: IngestInput): Promise<IngestResult>;
  abstract verify(evidenceId: string, caseId?: string): Promise<VerifyResult>;
  abstract export(caseId: string, format?: 'zip' | 'tar'): Promise<ExportResult>;
  abstract getManifest(caseId: string): Promise<{ success: boolean; manifest?: CaseManifest; error?: { code: string; message: string } }>;
  abstract updateManifest(caseId: string, manifest: CaseManifest): Promise<{ success: boolean; error?: { code: string; message: string } }>;
  abstract writeAudit(event: AuditEvent): Promise<{ success: boolean; error?: { code: string; message: string } }>;
  abstract getAccessLog(caseId: string, limit?: number): Promise<AccessLogResult>;
  
  async shutdown(): Promise<void> {
    this.initialized = false;
  }
  
  protected ensureInitialized(): void {
    if (!this.initialized) {
      throw createVaultError(
        VAULT_ERRORS.VAULT_ERROR,
        'Driver not initialized. Call initialize() first.'
      );
    }
  }
  
  protected validateCaseId(caseId: string): void {
    if (!caseId || typeof caseId !== 'string') {
      throw createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID');
    }
    
    if (!/^case-[a-zA-Z0-9_-]+$/.test(caseId)) {
      throw createVaultError(
        VAULT_ERRORS.INVALID_CASE,
        'Case ID must match pattern: case-[alphanumeric_-]+'
      );
    }
  }
  
  protected validateMimeType(mimeType: string): void {
    if (!this.config.allowedMimeTypes.includes(mimeType)) {
      throw createVaultError(
        VAULT_ERRORS.INVALID_MIME,
        `MIME type not allowed: ${mimeType}`,
        { allowed: this.config.allowedMimeTypes }
      );
    }
  }
  
  protected validateFileSize(size: number): void {
    if (size > this.config.maxFileSizeBytes) {
      throw createVaultError(
        VAULT_ERRORS.SIZE_LIMIT,
        `File size ${size} exceeds limit ${this.config.maxFileSizeBytes}`,
        { maxSize: this.config.maxFileSizeBytes, actualSize: size }
      );
    }
  }
}
