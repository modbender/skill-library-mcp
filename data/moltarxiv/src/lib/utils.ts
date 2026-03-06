import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date relative to now
 */
export function formatRelativeTime(date: Date | string): string {
  const now = new Date()
  const then = new Date(date)
  const diffMs = now.getTime() - then.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  const diffWeeks = Math.floor(diffDays / 7)
  const diffMonths = Math.floor(diffDays / 30)
  const diffYears = Math.floor(diffDays / 365)
  
  if (diffSecs < 60) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffWeeks < 4) return `${diffWeeks}w ago`
  if (diffMonths < 12) return `${diffMonths}mo ago`
  return `${diffYears}y ago`
}

/**
 * Format a number with K/M/B suffixes
 */
export function formatNumber(num: number): string {
  if (num < 1000) return num.toString()
  if (num < 1000000) return `${(num / 1000).toFixed(1)}K`
  if (num < 1000000000) return `${(num / 1000000).toFixed(1)}M`
  return `${(num / 1000000000).toFixed(1)}B`
}

/**
 * Format karma with sign
 */
export function formatKarma(karma: number): string {
  const sign = karma > 0 ? '+' : ''
  return `${sign}${formatNumber(karma)}`
}

/**
 * Calculate score from upvotes and downvotes
 */
export function calculateScore(upvotes: number, downvotes: number): number {
  return upvotes - downvotes
}

/**
 * Calculate controversial score (for sorting)
 * Higher score = more controversial
 */
export function calculateControversy(upvotes: number, downvotes: number): number {
  if (upvotes + downvotes === 0) return 0
  const total = upvotes + downvotes
  const ratio = Math.min(upvotes, downvotes) / Math.max(upvotes, downvotes)
  return total * ratio
}

/**
 * Calculate Wilson score for ranking
 * Better for sorting posts with different vote counts
 */
export function wilsonScore(upvotes: number, downvotes: number, z: number = 1.96): number {
  const n = upvotes + downvotes
  if (n === 0) return 0
  
  const p = upvotes / n
  const score = (p + z * z / (2 * n) - z * Math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) /
    (1 + z * z / n)
  
  return score
}

/**
 * Generate avatar URL from handle (fallback)
 */
export function generateAvatarUrl(handle: string): string {
  // Using DiceBear API for generated avatars
  return `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(handle)}&backgroundColor=b6e3f4,c0aede,d1d4f9`
}

/**
 * Parse tags from a string
 */
export function parseTags(input: string): string[] {
  return input
    .toLowerCase()
    .split(/[,\s]+/)
    .filter(tag => tag.length >= 2 && tag.length <= 50)
    .map(tag => tag.replace(/[^a-z0-9-]/g, ''))
    .filter((tag, index, self) => tag && self.indexOf(tag) === index)
    .slice(0, 20)
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: Parameters<T>) => ReturnType<T>>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * Sleep function for async delays
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Get initials from a name
 */
export function getInitials(name: string): string {
  return name
    .split(/\s+/)
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Check if a string is a valid URL
 */
export function isValidUrl(string: string): boolean {
  try {
    const url = new URL(string)
    return ['http:', 'https:'].includes(url.protocol)
  } catch {
    return false
  }
}

/**
 * Extract domain from URL
 */
export function extractDomain(url: string): string | null {
  try {
    return new URL(url).hostname
  } catch {
    return null
  }
}

/**
 * Truncate text to max length with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}
