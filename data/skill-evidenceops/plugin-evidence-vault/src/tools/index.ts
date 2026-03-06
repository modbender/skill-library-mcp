import {
  VaultConfig,
  IngestResult,
  VerifyResult,
  ExportResult,
  AccessLogResult,
  CaseManifest,
  SourceContext,
  RetentionPolicy,
  DEFAULT_CONFIG,
  createVaultError,
  VAULT_ERRORS,
} from '../types';
import { VaultDriver, IngestInput } from '../drivers/interface';
import { FilesystemDriver } from '../drivers/filesystem';
import { S3Driver, S3DriverConfig } from '../drivers/s3';
import * as path from 'path';
import * as fs from 'fs/promises';
import * as crypto from 'crypto';

export interface EvidenceVaultTools {
  ingest: (params: IngestParams) => Promise<IngestResult>;
  verify: (params: VerifyParams) => Promise<VerifyResult>;
  manifest: (params: ManifestParams) => Promise<{ success: boolean; manifest?: CaseManifest; error?: { code: string; message: string } }>;
  export: (params: ExportParams) => Promise<ExportResult>;
  accessLog: (params: AccessLogParams) => Promise<AccessLogResult>;
}

export interface IngestParams {
  filePath: string;
  filename: string;
  caseId: string;
  channel?: string;
  sender?: string;
  messageId?: string;
  sessionId?: string;
  retentionDays?: number;
  metadata?: Record<string, unknown>;
}

export interface VerifyParams {
  evidenceId: string;
  caseId?: string;
}

export interface ManifestParams {
  caseId: string;
}

export interface ExportParams {
  caseId: string;
  format?: 'zip' | 'tar';
}

export interface AccessLogParams {
  caseId: string;
  limit?: number;
}

export interface PluginContext {
  config?: Partial<VaultConfig>;
  channelAllowlist?: string[];
  channelDenylist?: string[];
  requirePairing?: boolean;
}

export class EvidenceVaultPlugin implements EvidenceVaultTools {
  private driver: VaultDriver;
  private config: VaultConfig;
  private channelAllowlist: string[];
  private channelDenylist: string[];
  private requirePairing: boolean;
  
  constructor(context?: PluginContext) {
    this.config = { ...DEFAULT_CONFIG, ...context?.config };
    this.channelAllowlist = context?.channelAllowlist ?? [];
    this.channelDenylist = context?.channelDenylist ?? [];
    this.requirePairing = context?.requirePairing ?? false;
    
    this.driver = this.createDriver();
  }
  
  private createDriver(): VaultDriver {
    switch (this.config.driver) {
      case 's3':
        return new S3Driver();
      case 'filesystem':
      default:
        return new FilesystemDriver();
    }
  }
  
  async initialize(): Promise<void> {
    await this.driver.initialize(this.config);
  }
  
  async shutdown(): Promise<void> {
    await this.driver.shutdown();
  }
  
  async healthCheck(): Promise<{ healthy: boolean; details: Record<string, unknown> }> {
    return this.driver.healthCheck();
  }
  
  private validateChannel(channel: string | undefined): void {
    if (!channel) return;
    
    if (this.channelDenylist.includes(channel)) {
      throw createVaultError(
        VAULT_ERRORS.CHANNEL_BLOCKED,
        `Channel ${channel} is blocked`
      );
    }
    
    if (this.channelAllowlist.length > 0 && !this.channelAllowlist.includes(channel)) {
      throw createVaultError(
        VAULT_ERRORS.CHANNEL_BLOCKED,
        `Channel ${channel} is not in allowlist`
      );
    }
  }
  
  async ingest(params: IngestParams): Promise<IngestResult> {
    this.validateChannel(params.channel);
    
    try {
      const stats = await fs.stat(params.filePath);
      const mimeType = this.detectMimeType(params.filePath, params.filename);
      
      const input: IngestInput = {
        filePath: params.filePath,
        filename: params.filename,
        mimeType,
        size: stats.size,
        caseId: params.caseId,
        sourceContext: {
          channel: params.channel ?? 'unknown',
          sender: params.sender ?? 'unknown',
          messageId: params.messageId,
          sessionId: params.sessionId,
        },
        retentionPolicy: params.retentionDays
          ? {
              retentionDays: params.retentionDays,
              legalHold: false,
              deleteAfter: new Date(
                Date.now() + params.retentionDays * 24 * 60 * 60 * 1000
              ).toISOString(),
            }
          : undefined,
        metadata: params.metadata,
      };
      
      return this.driver.ingest(input);
    } catch (error) {
      return {
        success: false,
        evidenceId: '',
        sha256: '',
        vaultUrl: '',
        timestamp: new Date().toISOString(),
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          error instanceof Error ? error.message : 'Unknown error'
        ),
      };
    }
  }
  
  async verify(params: VerifyParams): Promise<VerifyResult> {
    return this.driver.verify(params.evidenceId, params.caseId);
  }
  
  async manifest(params: ManifestParams): Promise<{ success: boolean; manifest?: CaseManifest; error?: { code: string; message: string } }> {
    return this.driver.getManifest(params.caseId);
  }
  
  async export(params: ExportParams): Promise<ExportResult> {
    return this.driver.export(params.caseId, params.format);
  }
  
  async accessLog(params: AccessLogParams): Promise<AccessLogResult> {
    return this.driver.getAccessLog(params.caseId, params.limit);
  }
  
  private detectMimeType(filePath: string, filename: string): string {
    const ext = path.extname(filename).toLowerCase();
    
    const mimeMap: Record<string, string> = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.mp4': 'video/mp4',
      '.webm': 'video/webm',
      '.mp3': 'audio/mpeg',
      '.wav': 'audio/wav',
      '.ogg': 'audio/ogg',
      '.pdf': 'application/pdf',
      '.zip': 'application/zip',
      '.txt': 'text/plain',
      '.json': 'application/json',
      '.md': 'text/markdown',
    };
    
    return mimeMap[ext] ?? 'application/octet-stream';
  }
}

export function createTools(context?: PluginContext): EvidenceVaultTools {
  return new EvidenceVaultPlugin(context);
}

export const toolDefinitions = [
  {
    name: 'evidence.ingest',
    description: 'Ingest evidence file into the vault with chain of custody tracking',
    parameters: {
      type: 'object',
      properties: {
        filePath: {
          type: 'string',
          description: 'Path to the evidence file',
        },
        filename: {
          type: 'string',
          description: 'Original filename',
        },
        caseId: {
          type: 'string',
          description: 'Case identifier (format: case-XXX)',
        },
        channel: {
          type: 'string',
          description: 'Source channel (whatsapp, telegram, etc.)',
        },
        sender: {
          type: 'string',
          description: 'Sender identifier',
        },
        messageId: {
          type: 'string',
          description: 'Message ID from source channel',
        },
        retentionDays: {
          type: 'number',
          description: 'Retention period in days',
        },
      },
      required: ['filePath', 'filename', 'caseId'],
    },
  },
  {
    name: 'evidence.verify',
    description: 'Verify integrity of ingested evidence',
    parameters: {
      type: 'object',
      properties: {
        evidenceId: {
          type: 'string',
          description: 'Evidence identifier',
        },
        caseId: {
          type: 'string',
          description: 'Optional case ID to search within',
        },
      },
      required: ['evidenceId'],
    },
  },
  {
    name: 'evidence.manifest',
    description: 'Get case manifest with all evidence items and chain of custody',
    parameters: {
      type: 'object',
      properties: {
        caseId: {
          type: 'string',
          description: 'Case identifier',
        },
      },
      required: ['caseId'],
    },
  },
  {
    name: 'evidence.export',
    description: 'Export case evidence as archive',
    parameters: {
      type: 'object',
      properties: {
        caseId: {
          type: 'string',
          description: 'Case identifier',
        },
        format: {
          type: 'string',
          enum: ['zip', 'tar'],
          description: 'Export format (default: zip)',
        },
      },
      required: ['caseId'],
    },
  },
  {
    name: 'evidence.access_log',
    description: 'Get audit trail for a case',
    parameters: {
      type: 'object',
      properties: {
        caseId: {
          type: 'string',
          description: 'Case identifier',
        },
        limit: {
          type: 'number',
          description: 'Maximum number of events to return',
        },
      },
      required: ['caseId'],
    },
  },
];
