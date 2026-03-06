import { DEFAULT_CONFIG } from '../types';

const DEFAULT_REDACTION = '[REDACTED]';

const BUILTIN_PATTERNS = [
  {
    pattern: /(?:sk-[a-zA-Z0-9]{20,})/g,
    name: 'api-key',
  },
  {
    pattern: /(?:pk-[a-zA-Z0-9]{20,})/g,
    name: 'public-key',
  },
  {
    pattern: /(?:password|passwd|pwd)[\s:=]+["']?[\w\-!@#$%^&*()]+["']?/gi,
    name: 'password',
  },
  {
    pattern: /(?:secret|token|api_key|apikey)[\s:=]+["']?[\w\-]+["']?/gi,
    name: 'secret',
  },
  {
    pattern: /(?:Bearer|Basic)\s+[a-zA-Z0-9._\-+]+=*/gi,
    name: 'auth-header',
  },
  {
    pattern: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
    name: 'email',
  },
  {
    pattern: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,
    name: 'phone',
  },
  {
    pattern: /\b(?:\d[ -]*?){13,16}\b/g,
    name: 'credit-card',
  },
  {
    pattern: /\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b/g,
    name: 'ssn',
  },
];

export function redactString(
  input: string,
  patterns: RegExp[] = DEFAULT_CONFIG.redactPatterns,
  replacement: string = DEFAULT_REDACTION
): string {
  let result = input;
  
  for (const pattern of [...BUILTIN_PATTERNS.map(p => p.pattern), ...patterns]) {
    result = result.replace(pattern, replacement);
  }
  
  return result;
}

export function redactObject(
  obj: Record<string, unknown>,
  patterns: RegExp[] = DEFAULT_CONFIG.redactPatterns,
  keysToRedact: string[] = ['password', 'secret', 'token', 'apiKey', 'api_key', 'credential']
): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  
  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    
    if (keysToRedact.some(k => lowerKey.includes(k.toLowerCase()))) {
      result[key] = DEFAULT_REDACTION;
      continue;
    }
    
    if (typeof value === 'string') {
      result[key] = redactString(value, patterns);
    } else if (typeof value === 'object' && value !== null) {
      result[key] = redactObject(value as Record<string, unknown>, patterns, keysToRedact);
    } else {
      result[key] = value;
    }
  }
  
  return result;
}

export function redactJsonLine(
  line: string,
  patterns: RegExp[] = DEFAULT_CONFIG.redactPatterns
): string {
  try {
    const obj = JSON.parse(line);
    const redacted = redactObject(obj, patterns);
    return JSON.stringify(redacted);
  } catch {
    return redactString(line, patterns);
  }
}

export function createRedactedCopy(
  data: Record<string, unknown>,
  fieldsToKeep: string[] = []
): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  
  for (const field of fieldsToKeep) {
    if (field in data) {
      const value = data[field];
      if (typeof value === 'string') {
        result[field] = redactString(value);
      } else {
        result[field] = value;
    }
  }
  }
  
  return result;
}
