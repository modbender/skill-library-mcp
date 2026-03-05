/**
 * 🔒 Input Validation & Sanitization
 * 
 * Security utilities to prevent:
 * - Path traversal attacks
 * - Command injection
 * - XSS in reports
 * - Invalid inputs
 * 
 * Author: Miloud Belarebia
 */

import path from 'path';
import { z } from 'zod';

// ============================================================
// PATH VALIDATION
// ============================================================

/**
 * Sanitize and validate file paths to prevent traversal attacks
 */
export function sanitizePath(inputPath, basePath = process.cwd()) {
  if (!inputPath || typeof inputPath !== 'string') {
    throw new Error('Invalid path: must be a non-empty string');
  }
  
  // Resolve to absolute path
  const resolved = path.resolve(basePath, inputPath);
  
  // Ensure it's within the base path (prevent traversal)
  const normalizedBase = path.normalize(basePath);
  const normalizedResolved = path.normalize(resolved);
  
  if (!normalizedResolved.startsWith(normalizedBase)) {
    throw new Error(`Path traversal detected: ${inputPath}`);
  }
  
  // Block dangerous patterns
  const dangerousPatterns = [
    /\.\./g,           // Parent directory
    /~\//g,            // Home directory shortcut in path
    /\0/g,             // Null byte
    /%2e%2e/gi,        // URL encoded ..
    /%252e%252e/gi,    // Double URL encoded ..
  ];
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(inputPath)) {
      throw new Error(`Dangerous path pattern detected: ${inputPath}`);
    }
  }
  
  return normalizedResolved;
}

/**
 * Check if a path is safe to read
 */
export function isPathSafe(inputPath, basePath = process.cwd()) {
  try {
    sanitizePath(inputPath, basePath);
    return true;
  } catch {
    return false;
  }
}

// ============================================================
// STRING SANITIZATION
// ============================================================

/**
 * Sanitize string for HTML output (prevent XSS)
 */
export function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  
  const htmlEntities = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
    '`': '&#x60;',
    '=': '&#x3D;'
  };
  
  return str.replace(/[&<>"'`=/]/g, char => htmlEntities[char]);
}

/**
 * Sanitize string for JSON output
 */
export function escapeJson(str) {
  if (typeof str !== 'string') return '';
  
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\t/g, '\\t');
}

/**
 * Sanitize string for shell commands (should be avoided, use parameterized)
 */
export function escapeShell(str) {
  if (typeof str !== 'string') return '';
  
  // Best practice: avoid shell commands entirely
  // This is a last resort sanitization
  return str.replace(/[;&|`$(){}[\]<>\\!#*?"']/g, '\\$&');
}

/**
 * Remove control characters from strings
 */
export function removeControlChars(str) {
  if (typeof str !== 'string') return '';
  
  // Remove ASCII control characters (0x00-0x1F, 0x7F)
  // Keep newlines and tabs for readability
  return str.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
}

// ============================================================
// INPUT VALIDATION SCHEMAS (Zod)
// ============================================================

/**
 * Schema for CLI options
 */
export const CliOptionsSchema = z.object({
  config: z.string().optional(),
  lang: z.enum(['en', 'fr', 'ar']).default('en'),
  verbose: z.boolean().default(false),
  quiet: z.boolean().default(false)
});

/**
 * Schema for audit options
 */
export const AuditOptionsSchema = z.object({
  deep: z.boolean().default(false),
  quick: z.boolean().default(false),
  output: z.string().optional(),
  format: z.enum(['text', 'json', 'html', 'md']).default('text'),
  ci: z.boolean().default(false)
});

/**
 * Schema for dashboard options
 */
export const DashboardOptionsSchema = z.object({
  port: z.number().int().min(1024).max(65535).default(18790),
  gateway: z.string().url().default('ws://127.0.0.1:18789'),
  browser: z.boolean().default(true)
});

/**
 * Schema for configuration file
 */
export const ConfigSchema = z.object({
  scanners: z.object({
    secrets: z.object({
      enabled: z.boolean().default(true),
      exclude: z.array(z.string()).default([])
    }).optional(),
    config: z.object({
      enabled: z.boolean().default(true),
      strict: z.boolean().default(false)
    }).optional(),
    prompts: z.object({
      enabled: z.boolean().default(true),
      sensitivity: z.enum(['low', 'medium', 'high']).default('medium')
    }).optional(),
    deps: z.object({
      enabled: z.boolean().default(true),
      severity: z.enum(['low', 'medium', 'high', 'critical']).default('medium')
    }).optional(),
    mcp: z.object({
      enabled: z.boolean().default(true),
      allowlist: z.array(z.string()).default([]),
      blockUnknown: z.boolean().default(false)
    }).optional()
  }).optional(),
  dashboard: z.object({
    port: z.number().int().min(1024).max(65535).default(18790),
    openBrowser: z.boolean().default(true)
  }).optional(),
  alerts: z.object({
    slack: z.object({
      enabled: z.boolean().default(false),
      webhook: z.string().url().optional()
    }).optional(),
    discord: z.object({
      enabled: z.boolean().default(false),
      webhook: z.string().url().optional()
    }).optional()
  }).optional()
}).passthrough();

// ============================================================
// VALIDATION FUNCTIONS
// ============================================================

/**
 * Validate and parse CLI options
 */
export function validateCliOptions(options) {
  return CliOptionsSchema.parse(options);
}

/**
 * Validate and parse audit options
 */
export function validateAuditOptions(options) {
  return AuditOptionsSchema.parse(options);
}

/**
 * Validate and parse dashboard options
 */
export function validateDashboardOptions(options) {
  return DashboardOptionsSchema.parse(options);
}

/**
 * Validate and parse config file
 */
export function validateConfig(config) {
  return ConfigSchema.parse(config);
}

// ============================================================
// SECURITY CHECKS
// ============================================================

/**
 * Check if running as root (not recommended)
 */
export function isRunningAsRoot() {
  return process.getuid && process.getuid() === 0;
}

/**
 * Check if a URL is safe (no file://, javascript:, etc.)
 */
export function isSafeUrl(url) {
  if (typeof url !== 'string') return false;
  
  const unsafeProtocols = ['javascript:', 'data:', 'file:', 'vbscript:'];
  const lowerUrl = url.toLowerCase().trim();
  
  return !unsafeProtocols.some(proto => lowerUrl.startsWith(proto));
}

/**
 * Check if WebSocket origin is allowed
 */
export function isAllowedOrigin(origin, allowedOrigins = ['http://localhost', 'http://127.0.0.1']) {
  if (!origin) return false;
  
  return allowedOrigins.some(allowed => origin.startsWith(allowed));
}

// ============================================================
// RATE LIMITING
// ============================================================

const rateLimitMap = new Map();

/**
 * Simple in-memory rate limiter
 */
export function checkRateLimit(key, maxRequests = 100, windowMs = 60000) {
  const now = Date.now();
  const windowStart = now - windowMs;
  
  if (!rateLimitMap.has(key)) {
    rateLimitMap.set(key, []);
  }
  
  const requests = rateLimitMap.get(key);
  
  // Remove old requests outside window
  const validRequests = requests.filter(time => time > windowStart);
  rateLimitMap.set(key, validRequests);
  
  if (validRequests.length >= maxRequests) {
    return { allowed: false, remaining: 0, resetIn: Math.ceil((validRequests[0] + windowMs - now) / 1000) };
  }
  
  validRequests.push(now);
  return { allowed: true, remaining: maxRequests - validRequests.length, resetIn: Math.ceil(windowMs / 1000) };
}

// ============================================================
// EXPORTS
// ============================================================

export default {
  sanitizePath,
  isPathSafe,
  escapeHtml,
  escapeJson,
  escapeShell,
  removeControlChars,
  validateCliOptions,
  validateAuditOptions,
  validateDashboardOptions,
  validateConfig,
  isRunningAsRoot,
  isSafeUrl,
  isAllowedOrigin,
  checkRateLimit
};
