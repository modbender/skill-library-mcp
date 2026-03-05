import * as fs from 'fs/promises';
import * as path from 'path';
import { Readable } from 'stream';
import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  HeadObjectCommand,
  ListObjectsV2Command,
  PutObjectLegalHoldCommand,
  GetObjectLegalHoldCommand,
  ObjectLockLegalHoldStatus,
  LegalHold,
  _Object,
} from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import {
  CaseManifest,
  VaultConfig,
  IngestResult,
  VerifyResult,
  ExportResult,
  AccessLogResult,
  AuditEvent,
  SensitivityTag,
  SCHEMA_VERSION,
  createVaultError,
  VAULT_ERRORS,
  DEFAULT_CONFIG,
} from '../types';
import { BaseDriver, IngestInput } from './interface';
import { sanitizeFilename, sanitizeCaseId, ensureDirectory, sanitizePath } from '../utils/path';
import { hashFile, hashString, hashStream, generateChainHash, generateId } from '../utils/crypto';
import { redactObject } from '../utils/redaction';
import { FilesystemDriver } from './filesystem';

export interface S3DriverConfig {
  endpoint?: string;
  bucket: string;
  region: string;
  accessKeyId?: string;
  secretAccessKey?: string;
  prefix?: string;
  objectLock?: boolean;
  forcePathStyle?: boolean;
}

export class S3Driver extends BaseDriver {
  readonly name = 's3';
  
  private s3Client!: S3Client;
  private s3Config!: S3DriverConfig;
  private localCache!: FilesystemDriver;
  private objectLockSupported: boolean = false;
  
  async initialize(config: VaultConfig): Promise<void> {
    this.config = { ...DEFAULT_CONFIG, ...config };
    
    const s3Config = (config as VaultConfig & { s3: S3DriverConfig }).s3;
    if (!s3Config || !s3Config.bucket) {
      throw createVaultError(VAULT_ERRORS.VAULT_ERROR, 'S3 configuration missing bucket');
    }
    
    this.s3Config = {
      region: 'us-east-1',
      prefix: 'evidence-vault',
      objectLock: false,
      forcePathStyle: false,
      ...s3Config,
    };
    
    const clientConfig: ConstructorParameters<typeof S3Client>[0] = {
      region: this.s3Config.region,
    };
    
    if (this.s3Config.endpoint) {
      clientConfig.endpoint = this.s3Config.endpoint;
    }
    
    if (this.s3Config.forcePathStyle) {
      clientConfig.forcePathStyle = true;
    }
    
    if (this.s3Config.accessKeyId && this.s3Config.secretAccessKey) {
      clientConfig.credentials = {
        accessKeyId: this.s3Config.accessKeyId,
        secretAccessKey: this.s3Config.secretAccessKey,
      };
    }
    
    this.s3Client = new S3Client(clientConfig);
    
    this.localCache = new FilesystemDriver();
    await this.localCache.initialize({
      ...config,
      basePath: path.join(config.basePath, 's3-cache'),
    });
    
    await this.checkObjectLockSupport();
    
    this.initialized = true;
  }
  
  private async checkObjectLockSupport(): Promise<void> {
    try {
      await this.s3Client.send(
        new GetObjectLegalHoldCommand({
          Bucket: this.s3Config.bucket,
          Key: '.object-lock-check',
        })
      );
      this.objectLockSupported = true;
    } catch (error) {
      this.objectLockSupported = false;
      console.warn('S3 Object Lock not available or not enabled on bucket. Operating without legal hold.');
    }
  }
  
  async healthCheck(): Promise<{ healthy: boolean; details: Record<string, unknown> }> {
    try {
      await this.s3Client.send(
        new ListObjectsV2Command({
          Bucket: this.s3Config.bucket,
          MaxKeys: 1,
        })
      );
      
      return {
        healthy: true,
        details: {
          bucket: this.s3Config.bucket,
          region: this.s3Config.region,
          endpoint: this.s3Config.endpoint ?? 'aws',
          objectLockSupported: this.objectLockSupported,
          driver: this.name,
          timestamp: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        healthy: false,
        details: {
          error: error instanceof Error ? error.message : 'Unknown error',
          bucket: this.s3Config.bucket,
        },
      };
    }
  }
  
  async createCase(
    caseId: string,
    sensitivityTag: SensitivityTag = 'confidential'
  ): Promise<{ success: boolean; caseId: string; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        caseId,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID format'),
      };
    }
    
    const exists = await this.caseExists(sanitizedCaseId);
    if (exists) {
      return {
        success: false,
        caseId: sanitizedCaseId,
        error: createVaultError(VAULT_ERRORS.ALREADY_EXISTS, `Case ${sanitizedCaseId} already exists`),
      };
    }
    
    const result = await this.localCache.createCase(sanitizedCaseId, sensitivityTag);
    if (!result.success) {
      return result;
    }
    
    const manifestResult = await this.localCache.getManifest(sanitizedCaseId);
    if (manifestResult.success && manifestResult.manifest) {
      await this.uploadManifest(sanitizedCaseId, manifestResult.manifest);
    }
    
    return result;
  }
  
  async caseExists(caseId: string): Promise<boolean> {
    const sanitized = sanitizeCaseId(caseId);
    if (!sanitized) return false;
    
    const key = this.getS3Key(sanitized, 'manifest.json');
    
    try {
      await this.s3Client.send(
        new HeadObjectCommand({
          Bucket: this.s3Config.bucket,
          Key: key,
        })
      );
      return true;
    } catch {
      return this.localCache.caseExists(sanitized);
    }
  }
  
  async ingest(input: IngestInput): Promise<IngestResult> {
    this.ensureInitialized();
    
    try {
      this.validateCaseId(input.caseId);
      this.validateMimeType(input.mimeType);
      this.validateFileSize(input.size);
      
      const sanitizedCaseId = sanitizeCaseId(input.caseId);
      if (!sanitizedCaseId) {
        return this.ingestError(input.caseId, VAULT_ERRORS.INVALID_CASE, 'Invalid case ID');
      }
      
      const exists = await this.caseExists(sanitizedCaseId);
      if (!exists) {
        await this.createCase(sanitizedCaseId);
      }
      
      const evidenceId = generateId('ev');
      const sanitizedFilename = sanitizeFilename(input.filename);
      const ext = path.extname(sanitizedFilename);
      const storedFilename = `${evidenceId}${ext}`;
      
      const sha256 = await hashFile(input.filePath);
      
      const fileContent = await fs.readFile(input.filePath);
      const s3Key = this.getS3Key(sanitizedCaseId, `originals/${storedFilename}`);
      
      await this.s3Client.send(
        new PutObjectCommand({
          Bucket: this.s3Config.bucket,
          Key: s3Key,
          Body: fileContent,
          ContentType: input.mimeType,
          Metadata: {
            'original-filename': sanitizedFilename,
            'evidence-id': evidenceId,
            'sha256': sha256,
            'case-id': sanitizedCaseId,
            'ingested-at': new Date().toISOString(),
          },
        })
      );
      
      if (this.s3Config.objectLock && this.objectLockSupported) {
        try {
          await this.s3Client.send(
            new PutObjectLegalHoldCommand({
              Bucket: this.s3Config.bucket,
              Key: s3Key,
              LegalHold: {
                Status: ObjectLockLegalHoldStatus.ON,
              },
            })
          );
        } catch (lockError) {
          console.warn('Failed to set legal hold:', lockError);
        }
      }
      
      const vaultUrl = `s3://${this.s3Config.bucket}/${s3Key}`;
      const now = new Date().toISOString();
      
      const manifestResult = await this.getManifest(sanitizedCaseId);
      if (!manifestResult.success || !manifestResult.manifest) {
        return this.ingestError(sanitizedCaseId, VAULT_ERRORS.VAULT_ERROR, 'Failed to read manifest');
      }
      
      const manifest = manifestResult.manifest;
      const lastChainEntry = manifest.chainOfCustody[manifest.chainOfCustody.length - 1];
      const newChainHash = generateChainHash(
        lastChainEntry?.currentHash ?? null,
        'evidence_ingested',
        now,
        evidenceId
      );
      
      const newItem = {
        evidenceId,
        original: {
          filename: sanitizedFilename,
          sha256,
          size: input.size,
          mime: input.mimeType,
          receivedAt: now,
          source: input.sourceContext,
        },
        metadata: input.metadata ?? {},
        derivatives: [],
        vault: {
          provider: 's3' as const,
          vaultUrl,
          ingestedAt: now,
        },
      };
      
      manifest.items.push(newItem);
      manifest.updatedAt = now;
      manifest.chainOfCustody.push({
        event: 'evidence_ingested',
        timestamp: now,
        actor: input.sourceContext.sessionId ?? 'unknown',
        evidenceId,
        previousHash: lastChainEntry?.currentHash ?? null,
        currentHash: newChainHash,
      });
      
      await this.localCache.updateManifest(sanitizedCaseId, manifest);
      await this.uploadManifest(sanitizedCaseId, manifest);
      
      await this.writeAudit({
        eventType: 'evidence_ingested',
        timestamp: now,
        caseId: sanitizedCaseId,
        evidenceId,
        actor: input.sourceContext.sessionId ?? 'unknown',
        details: redactObject({
          filename: sanitizedFilename,
          sha256,
          size: input.size,
          source: input.sourceContext,
          s3Key,
        }),
        hash: newChainHash,
        previousHash: lastChainEntry?.currentHash,
      });
      
      return {
        success: true,
        evidenceId,
        sha256,
        vaultUrl,
        timestamp: now,
      };
    } catch (error) {
      return this.ingestError(
        input.caseId,
        VAULT_ERRORS.VAULT_ERROR,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }
  
  async verify(evidenceId: string, caseId?: string): Promise<VerifyResult> {
    this.ensureInitialized();
    
    try {
      let targetCaseId = caseId;
      
      if (!targetCaseId) {
        const manifests = await this.listManifests();
        for (const manifest of manifests) {
          const item = manifest.items.find(i => i.evidenceId === evidenceId);
          if (item) {
            targetCaseId = manifest.caseId;
            break;
          }
        }
      }
      
      if (!targetCaseId) {
        return {
          success: false,
          evidenceId,
          caseId: caseId ?? '',
          verified: false,
          details: {
            originalIntact: false,
            hashMatch: false,
            lastVerifiedAt: new Date().toISOString(),
          },
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Evidence not found'),
        };
      }
      
      const manifestResult = await this.getManifest(targetCaseId);
      if (!manifestResult.success || !manifestResult.manifest) {
        return {
          success: false,
          evidenceId,
          caseId: targetCaseId,
          verified: false,
          details: {
            originalIntact: false,
            hashMatch: false,
            lastVerifiedAt: new Date().toISOString(),
          },
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Case manifest not found'),
        };
      }
      
      const item = manifestResult.manifest.items.find(i => i.evidenceId === evidenceId);
      if (!item) {
        return {
          success: false,
          evidenceId,
          caseId: targetCaseId,
          verified: false,
          details: {
            originalIntact: false,
            hashMatch: false,
            lastVerifiedAt: new Date().toISOString(),
          },
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Evidence item not found'),
        };
      }
      
      const s3Key = item.vault.vaultUrl.replace(`s3://${this.s3Config.bucket}/`, '');
      let originalIntact = false;
      let hashMatch = false;
      
      try {
        const response = await this.s3Client.send(
          new GetObjectCommand({
            Bucket: this.s3Config.bucket,
            Key: s3Key,
          })
        );
        
        if (response.Body) {
          const stream = response.Body as Readable;
          const currentHash = await hashStream(stream);
          hashMatch = currentHash === item.original.sha256;
          originalIntact = hashMatch;
        }
      } catch {
        originalIntact = false;
        hashMatch = false;
      }
      
      const now = new Date().toISOString();
      await this.writeAudit({
        eventType: 'evidence_verified',
        timestamp: now,
        caseId: targetCaseId,
        evidenceId,
        actor: 'system',
        details: { originalIntact, hashMatch },
      });
      
      return {
        success: true,
        evidenceId,
        caseId: targetCaseId,
        verified: hashMatch && originalIntact,
        details: {
          originalIntact,
          hashMatch,
          lastVerifiedAt: now,
        },
      };
    } catch (error) {
      return {
        success: false,
        evidenceId,
        caseId: caseId ?? '',
        verified: false,
        details: {
          originalIntact: false,
          hashMatch: false,
          lastVerifiedAt: new Date().toISOString(),
        },
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          error instanceof Error ? error.message : 'Unknown error'
        ),
      };
    }
  }
  
  async export(caseId: string, format: 'zip' | 'tar' = 'zip'): Promise<ExportResult> {
    this.ensureInitialized();
    
    return this.localCache.export(caseId, format);
  }
  
  async getManifest(caseId: string): Promise<{ success: boolean; manifest?: CaseManifest; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID'),
      };
    }
    
    try {
      const s3Key = this.getS3Key(sanitizedCaseId, 'manifest.json');
      const response = await this.s3Client.send(
        new GetObjectCommand({
          Bucket: this.s3Config.bucket,
          Key: s3Key,
        })
      );
      
      if (response.Body) {
        const content = await streamToString(response.Body as Readable);
        const manifest = JSON.parse(content) as CaseManifest;
        
        await this.localCache.updateManifest(sanitizedCaseId, manifest);
        
        return { success: true, manifest };
      }
      
      return {
        success: false,
        error: createVaultError(VAULT_ERRORS.VAULT_ERROR, 'Empty response from S3'),
      };
    } catch (error) {
      if ((error as { name?: string }).name === 'NoSuchKey') {
        return this.localCache.getManifest(sanitizedCaseId);
      }
      
      return {
        success: false,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to get manifest: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async updateManifest(caseId: string, manifest: CaseManifest): Promise<{ success: boolean; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const result = await this.localCache.updateManifest(caseId, manifest);
    if (!result.success) {
      return result;
    }
    
    try {
      await this.uploadManifest(caseId, manifest);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to upload manifest: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async writeAudit(event: AuditEvent): Promise<{ success: boolean; error?: { code: string; message: string } }> {
    return this.localCache.writeAudit(event);
  }
  
  async getAccessLog(caseId: string, limit?: number): Promise<AccessLogResult> {
    return this.localCache.getAccessLog(caseId, limit);
  }
  
  private getS3Key(caseId: string, relativePath: string): string {
    const prefix = this.s3Config.prefix ?? 'evidence-vault';
    return `${prefix}/cases/${caseId}/${relativePath}`;
  }
  
  private async uploadManifest(caseId: string, manifest: CaseManifest): Promise<void> {
    const s3Key = this.getS3Key(caseId, 'manifest.json');
    const content = JSON.stringify(manifest, null, 2);
    
    await this.s3Client.send(
      new PutObjectCommand({
        Bucket: this.s3Config.bucket,
        Key: s3Key,
        Body: content,
        ContentType: 'application/json',
        Metadata: {
          'case-id': caseId,
          'schema-version': SCHEMA_VERSION,
          'updated-at': manifest.updatedAt,
        },
      })
    );
  }
  
  private async listManifests(): Promise<CaseManifest[]> {
    const prefix = this.s3Config.prefix ?? 'evidence-vault';
    const manifests: CaseManifest[] = [];
    
    try {
      let continuationToken: string | undefined;
      
      do {
        const response = await this.s3Client.send(
          new ListObjectsV2Command({
            Bucket: this.s3Config.bucket,
            Prefix: `${prefix}/cases/`,
            Delimiter: '/',
            ContinuationToken: continuationToken,
          })
        );
        
        if (response.CommonPrefixes) {
          for (const prefix of response.CommonPrefixes) {
            const caseId = prefix.Prefix?.split('/').filter(Boolean)[2];
            if (caseId) {
              const result = await this.getManifest(caseId);
              if (result.success && result.manifest) {
                manifests.push(result.manifest);
              }
            }
          }
        }
        
        continuationToken = response.NextContinuationToken;
      } while (continuationToken);
      
      return manifests;
    } catch {
      return [];
    }
  }
  
  private ingestError(caseId: string, code: string, message: string): IngestResult {
    return {
      success: false,
      evidenceId: '',
      sha256: '',
      vaultUrl: '',
      timestamp: new Date().toISOString(),
      error: createVaultError(code, message),
    };
  }
}

async function streamToString(stream: Readable): Promise<string> {
  const chunks: Buffer[] = [];
  return new Promise((resolve, reject) => {
    stream.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf-8')));
    stream.on('error', reject);
  });
}
