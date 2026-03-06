import { jest } from '@jest/globals';
import * as path from 'path';
import * as fs from 'fs/promises';
import * as os from 'os';
import { FilesystemDriver } from '../src/drivers/filesystem';
import { hashString, hashBuffer } from '../src/utils/crypto';
import { sanitizeFilename, sanitizePath, sanitizeCaseId, sanitizeEvidenceId } from '../src/utils/path';
import { redactString, redactObject } from '../src/utils/redaction';

describe('Crypto Utils', () => {
  describe('hashString', () => {
    it('should produce consistent SHA-256 hashes', () => {
      const input = 'test-content';
      const hash1 = hashString(input);
      const hash2 = hashString(input);
      
      expect(hash1).toBe(hash2);
      expect(hash1).toMatch(/^[a-f0-9]{64}$/);
    });
    
    it('should produce different hashes for different inputs', () => {
      const hash1 = hashString('input1');
      const hash2 = hashString('input2');
      
      expect(hash1).not.toBe(hash2);
    });
    
    it('should match known SHA-256 output', () => {
      const hash = hashString('');
      expect(hash).toBe('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
    });
  });
  
  describe('hashBuffer', () => {
    it('should hash buffer content', async () => {
      const buffer = Buffer.from('test-content');
      const hash = await hashBuffer(buffer);
      
      expect(hash).toMatch(/^[a-f0-9]{64}$/);
    });
  });
});

describe('Path Utils', () => {
  describe('sanitizeFilename', () => {
    it('should allow normal filenames', () => {
      expect(sanitizeFilename('document.pdf')).toBe('document.pdf');
      expect(sanitizeFilename('image_001.jpg')).toBe('image_001.jpg');
      expect(sanitizeFilename('file-name.txt')).toBe('file-name.txt');
    });
    
    it('should sanitize dangerous characters', () => {
      expect(sanitizeFilename('../../../etc/passwd')).not.toContain('..');
      expect(sanitizeFilename('file<>:"|?.txt')).not.toMatch(/[<>:"|?]/);
    });
    
    it('should handle empty input', () => {
      expect(sanitizeFilename('')).toBe('unnamed');
      expect(sanitizeFilename(null as unknown as string)).toBe('unnamed');
    });
    
    it('should truncate long filenames', () => {
      const longName = 'a'.repeat(300) + '.txt';
      const sanitized = sanitizeFilename(longName);
      expect(sanitized.length).toBeLessThanOrEqual(200);
    });
  });
  
  describe('sanitizePath', () => {
    const basePath = '/safe/directory';
    
    it('should allow paths within base', () => {
      const result = sanitizePath('subdir/file.txt', basePath);
      expect(result).toBe(path.resolve(basePath, 'subdir/file.txt'));
    });
    
    it('should reject path traversal attempts', () => {
      expect(sanitizePath('../../../etc/passwd', basePath)).toBeNull();
      expect(sanitizePath('..\\..\\windows\\system32', basePath)).toBeNull();
    });
    
    it('should reject paths outside base', () => {
      expect(sanitizePath('/etc/passwd', basePath)).toBeNull();
      expect(sanitizePath('~/secrets', basePath)).toBeNull();
    });
    
    it('should reject null bytes', () => {
      expect(sanitizePath('file\0.txt', basePath)).toBeNull();
    });
  });
  
  describe('sanitizeCaseId', () => {
    it('should accept valid case IDs', () => {
      expect(sanitizeCaseId('case-2026-001')).toBe('case-2026-001');
      expect(sanitizeCaseId('case-incident-alpha')).toBe('case-incident-alpha');
      expect(sanitizeCaseId('case-TEST_123')).toBe('case-TEST_123');
    });
    
    it('should reject invalid case IDs', () => {
      expect(sanitizeCaseId('2026-001')).toBeNull();
      expect(sanitizeCaseId('CASE-2026-001')).toBeNull();
      expect(sanitizeCaseId('case-2026-001!')).toBeNull();
      expect(sanitizeCaseId('case-../../../etc')).toBeNull();
    });
  });
  
  describe('sanitizeEvidenceId', () => {
    it('should accept valid evidence IDs', () => {
      expect(sanitizeEvidenceId('ev-abc123')).toBe('ev-abc123');
      expect(sanitizeEvidenceId('ev-abc123-def456')).toBe('ev-abc123-def456');
    });
    
    it('should reject invalid evidence IDs', () => {
      expect(sanitizeEvidenceId('evidence-123')).toBeNull();
      expect(sanitizeEvidenceId('EV-123')).toBeNull();
    });
  });
});

describe('Redaction Utils', () => {
  describe('redactString', () => {
    it('should redact email addresses', () => {
      const input = 'Contact user@example.com for details';
      const redacted = redactString(input);
      expect(redacted).not.toContain('user@example.com');
      expect(redacted).toContain('[REDACTED]');
    });
    
    it('should redact phone numbers', () => {
      const input = 'Call 555-123-4567 now';
      const redacted = redactString(input);
      expect(redacted).not.toContain('555-123-4567');
    });
    
    it('should redact API keys', () => {
      const input = 'api_key=sk-1234567890abcdefghijklmnop';
      const redacted = redactString(input);
      expect(redacted).not.toContain('sk-1234567890');
    });
    
    it('should redact passwords', () => {
      const input = 'password=SuperSecret123!';
      const redacted = redactString(input);
      expect(redacted).not.toContain('SuperSecret123');
    });
    
    it('should preserve non-sensitive content', () => {
      const input = 'The case number is case-2026-001';
      const redacted = redactString(input);
      expect(redacted).toContain('case-2026-001');
    });
  });
  
  describe('redactObject', () => {
    it('should redact sensitive keys', () => {
      const obj = {
        caseId: 'case-001',
        password: 'secret123',
        apiKey: 'key-abc',
      };
      
      const redacted = redactObject(obj);
      
      expect(redacted.caseId).toBe('case-001');
      expect(redacted.password).toBe('[REDACTED]');
      expect(redacted.apiKey).toBe('[REDACTED]');
    });
    
    it('should redact nested objects', () => {
      const obj = {
        caseId: 'case-001',
        source: {
          channel: 'whatsapp',
          sender: 'user@example.com',
        },
      };
      
      const redacted = redactObject(obj);
      
      expect(redacted.caseId).toBe('case-001');
      expect(redacted.source.channel).toBe('whatsapp');
      expect((redacted.source.sender as string)).not.toContain('user@example.com');
    });
  });
});

describe('FilesystemDriver', () => {
  let driver: FilesystemDriver;
  let tempDir: string;
  
  beforeAll(async () => {
    tempDir = path.join(os.tmpdir(), `evidence-test-${Date.now()}`);
    await fs.mkdir(tempDir, { recursive: true });
    
    driver = new FilesystemDriver();
    await driver.initialize({
      driver: 'filesystem',
      basePath: tempDir,
      maxFileSizeBytes: 10485760,
      allowedMimeTypes: ['image/jpeg', 'image/png', 'application/pdf'],
      defaultRetentionDays: 365,
      enforceLegalHold: false,
      auditLogPath: path.join(tempDir, 'audit'),
      redactPatterns: [],
    });
  });
  
  afterAll(async () => {
    await driver.shutdown();
    await fs.rm(tempDir, { recursive: true, force: true });
  });
  
  describe('healthCheck', () => {
    it('should return healthy status', async () => {
      const result = await driver.healthCheck();
      expect(result.healthy).toBe(true);
    });
  });
  
  describe('createCase', () => {
    it('should create a new case', async () => {
      const result = await driver.createCase('case-test-001', 'confidential');
      expect(result.success).toBe(true);
      expect(result.caseId).toBe('case-test-001');
    });
    
    it('should reject duplicate case IDs', async () => {
      await driver.createCase('case-test-002');
      const result = await driver.createCase('case-test-002');
      expect(result.success).toBe(false);
    });
    
    it('should reject invalid case IDs', async () => {
      const result = await driver.createCase('invalid-case-id');
      expect(result.success).toBe(false);
    });
  });
  
  describe('caseExists', () => {
    it('should return true for existing case', async () => {
      await driver.createCase('case-test-003');
      const exists = await driver.caseExists('case-test-003');
      expect(exists).toBe(true);
    });
    
    it('should return false for non-existing case', async () => {
      const exists = await driver.caseExists('case-nonexistent');
      expect(exists).toBe(false);
    });
  });
  
  describe('getManifest', () => {
    it('should return manifest for existing case', async () => {
      await driver.createCase('case-test-004');
      const result = await driver.getManifest('case-test-004');
      
      expect(result.success).toBe(true);
      expect(result.manifest?.caseId).toBe('case-test-004');
      expect(result.manifest?.items).toEqual([]);
    });
    
    it('should return error for non-existing case', async () => {
      const result = await driver.getManifest('case-nonexistent');
      expect(result.success).toBe(false);
    });
  });
  
  describe('ingest', () => {
    it('should ingest a file', async () => {
      const testFile = path.join(tempDir, 'test-file.png');
      await fs.writeFile(testFile, Buffer.from('fake png content'));
      
      await driver.createCase('case-test-005');
      
      const result = await driver.ingest({
        filePath: testFile,
        filename: 'evidence.png',
        mimeType: 'image/png',
        size: 17,
        caseId: 'case-test-005',
        sourceContext: {
          channel: 'test',
          sender: 'test-user',
        },
      });
      
      expect(result.success).toBe(true);
      expect(result.evidenceId).toMatch(/^ev-/);
      expect(result.sha256).toMatch(/^[a-f0-9]{64}$/);
    });
    
    it('should reject files with disallowed MIME types', async () => {
      const testFile = path.join(tempDir, 'test.exe');
      await fs.writeFile(testFile, Buffer.from('fake exe'));
      
      await driver.createCase('case-test-006');
      
      const result = await driver.ingest({
        filePath: testFile,
        filename: 'malware.exe',
        mimeType: 'application/x-msdos-program',
        size: 8,
        caseId: 'case-test-006',
        sourceContext: {
          channel: 'test',
          sender: 'test-user',
        },
      });
      
      expect(result.success).toBe(false);
      expect(result.error?.code).toBe('E_INVALID_MIME');
    });
    
    it('should reject files exceeding size limit', async () => {
      const testFile = path.join(tempDir, 'large.png');
      await fs.writeFile(testFile, Buffer.alloc(20 * 1024 * 1024));
      
      await driver.createCase('case-test-007');
      
      const result = await driver.ingest({
        filePath: testFile,
        filename: 'large.png',
        mimeType: 'image/png',
        size: 20 * 1024 * 1024,
        caseId: 'case-test-007',
        sourceContext: {
          channel: 'test',
          sender: 'test-user',
        },
      });
      
      expect(result.success).toBe(false);
      expect(result.error?.code).toBe('E_SIZE_LIMIT');
    });
  });
  
  describe('verify', () => {
    it('should verify existing evidence', async () => {
      const testFile = path.join(tempDir, 'verify-test.png');
      await fs.writeFile(testFile, Buffer.from('content to verify'));
      
      await driver.createCase('case-test-008');
      
      const ingestResult = await driver.ingest({
        filePath: testFile,
        filename: 'verify.png',
        mimeType: 'image/png',
        size: 18,
        caseId: 'case-test-008',
        sourceContext: {
          channel: 'test',
          sender: 'test-user',
        },
      });
      
      const verifyResult = await driver.verify(ingestResult.evidenceId, 'case-test-008');
      
      expect(verifyResult.success).toBe(true);
      expect(verifyResult.verified).toBe(true);
      expect(verifyResult.details.hashMatch).toBe(true);
    });
  });
  
  describe('getAccessLog', () => {
    it('should return audit events', async () => {
      await driver.createCase('case-test-009');
      
      const result = await driver.getAccessLog('case-test-009');
      
      expect(result.success).toBe(true);
      expect(result.events.length).toBeGreaterThan(0);
      expect(result.events[0].eventType).toBe('case_created');
    });
  });
});
