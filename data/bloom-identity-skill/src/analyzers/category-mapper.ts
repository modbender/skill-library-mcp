/**
 * Category Mapper
 *
 * Provides fallback categories when conversation analysis detects nothing.
 * Categories represent WHAT the user is interested in — they come from
 * conversation analysis, not personality type. This fallback is a last resort.
 */

import { PersonalityType } from '../types/personality';
import { DEFAULT_FALLBACK_CATEGORIES } from '../types/categories';

export class CategoryMapper {
  /**
   * Get fallback categories when conversation analysis returns nothing.
   *
   * Returns generic popular categories regardless of personality type,
   * since personality (HOW you think) doesn't determine categories (WHAT you're into).
   */
  getMainCategories(_personalityType: PersonalityType): string[] {
    return [...DEFAULT_FALLBACK_CATEGORIES];
  }
}
