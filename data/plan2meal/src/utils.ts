/**
 * Utility functions for Plan2Meal skill
 */

/**
 * Escape markdown special characters
 */
export function markdownEscape(text: string): string {
  if (!text) return '';
  const str = String(text);
  return str
    .replace(/[_*[\]()~`>#+=|{}.!-]/g, '\\$&')
    .replace(/\n/g, ' ');
}

/**
 * Format prep and cook time
 */
export function formatTime(prepTime?: string | null, cookTime?: string | null): string | null {
  const parts: string[] = [];
  if (prepTime) parts.push(`prep: ${prepTime}`);
  if (cookTime) parts.push(`cook: ${cookTime}`);
  return parts.length > 0 ? parts.join(' | ') : null;
}

/**
 * Validate URL
 */
export function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
}

/**
 * Generate a random state string for OAuth
 */
export function generateState(): string {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number = 100): string {
  if (!text) return '';
  const str = String(text);
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '...';
}

/**
 * Parse recipe ID from various formats
 */
export function parseRecipeId(input: string): string {
  // Handle URL format: https://.../recipe/123
  if (input.includes('/')) {
    const parts = input.split('/');
    return parts[parts.length - 1];
  }
  return input.trim();
}

/**
 * Sleep for specified milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
