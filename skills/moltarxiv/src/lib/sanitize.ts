/**
 * Content sanitization for security
 * Prevents XSS, prompt injection, and other attacks
 */

// Patterns that might indicate prompt injection attempts
const PROMPT_INJECTION_PATTERNS = [
  /ignore\s+(previous|all|above)\s+instructions/i,
  /disregard\s+(previous|all|above)/i,
  /forget\s+(everything|all|previous)/i,
  /you\s+are\s+now\s+a/i,
  /new\s+instructions?:/i,
  /system\s*:\s*/i,
  /assistant\s*:\s*/i,
  /user\s*:\s*/i,
  /<\|im_start\|>/i,
  /<\|im_end\|>/i,
  /\[\[SYSTEM\]\]/i,
]

// Dangerous HTML patterns
const DANGEROUS_HTML = [
  /<script[\s\S]*?>/gi,
  /<\/script>/gi,
  /javascript:/gi,
  /on\w+\s*=/gi,
  /<iframe[\s\S]*?>/gi,
  /<object[\s\S]*?>/gi,
  /<embed[\s\S]*?>/gi,
  /<form[\s\S]*?>/gi,
  /data:\s*text\/html/gi,
]

// Allowed markdown elements
const ALLOWED_MARKDOWN = {
  headings: true,
  bold: true,
  italic: true,
  links: true,
  images: true,
  code: true,
  codeBlocks: true,
  lists: true,
  tables: true,
  blockquotes: true,
  math: true, // KaTeX
}

/**
 * Sanitize text content to prevent XSS
 */
export function sanitizeText(text: string): string {
  if (!text) return ''
  
  return text
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/**
 * Sanitize markdown content
 * Allows safe markdown but strips dangerous HTML
 */
export function sanitizeMarkdown(markdown: string): string {
  if (!markdown) return ''
  
  let sanitized = markdown
  
  // Remove dangerous HTML
  for (const pattern of DANGEROUS_HTML) {
    sanitized = sanitized.replace(pattern, '')
  }
  
  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '')
  
  return sanitized
}

/**
 * Sanitize a URL
 */
export function sanitizeUrl(url: string): string | null {
  if (!url) return null
  
  try {
    const parsed = new URL(url)
    
    // Only allow http(s) protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return null
    }
    
    return parsed.toString()
  } catch {
    return null
  }
}

/**
 * Check for prompt injection attempts
 * Returns true if injection detected
 */
export function detectPromptInjection(text: string): boolean {
  for (const pattern of PROMPT_INJECTION_PATTERNS) {
    if (pattern.test(text)) {
      return true
    }
  }
  return false
}

/**
 * Flag content that may contain prompt injection
 * Doesn't block, just flags for review
 */
export function flagSuspiciousContent(text: string): {
  flagged: boolean
  reasons: string[]
} {
  const reasons: string[] = []
  
  if (detectPromptInjection(text)) {
    reasons.push('potential_prompt_injection')
  }
  
  // Check for excessive special characters
  const specialCharRatio = (text.match(/[^a-zA-Z0-9\s.,!?-]/g)?.length || 0) / text.length
  if (specialCharRatio > 0.3) {
    reasons.push('high_special_char_ratio')
  }
  
  // Check for excessive URLs
  const urlCount = (text.match(/https?:\/\//g) || []).length
  if (urlCount > 10) {
    reasons.push('excessive_urls')
  }
  
  return {
    flagged: reasons.length > 0,
    reasons
  }
}

/**
 * Extract mentions from content
 * @agent, #tag, m/channel
 */
export function extractMentions(text: string): {
  agents: string[]
  tags: string[]
  channels: string[]
} {
  const agents = Array.from(text.matchAll(/@([a-zA-Z0-9_-]+)/g)).map(m => m[1])
  const tags = Array.from(text.matchAll(/#([a-zA-Z0-9_-]+)/g)).map(m => m[1])
  const channels = Array.from(text.matchAll(/m\/([a-zA-Z0-9_-]+)/g)).map(m => m[1])
  
  return {
    agents: Array.from(new Set(agents)),
    tags: Array.from(new Set(tags)),
    channels: Array.from(new Set(channels))
  }
}

/**
 * Truncate text to max length with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}

/**
 * Generate a URL-safe slug from text
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}
