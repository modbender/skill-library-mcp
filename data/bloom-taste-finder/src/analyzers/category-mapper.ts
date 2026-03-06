/**
 * Category Mapper
 *
 * Maps personality types to main categories for project matching
 */

import { PersonalityType } from '../types/personality';

export class CategoryMapper {
  /**
   * Get main categories for a personality type
   */
  getMainCategories(personalityType: PersonalityType): string[] {
    const categoryMap: Record<PersonalityType, string[]> = {
      [PersonalityType.THE_VISIONARY]: ['Crypto', 'DeFi', 'Web3', 'Blockchain'],
      [PersonalityType.THE_EXPLORER]: ['Education', 'Learning', 'Knowledge', 'Research'],
      [PersonalityType.THE_CULTIVATOR]: ['Community', 'Social', 'Content', 'Collaboration'],
      [PersonalityType.THE_OPTIMIZER]: ['Productivity', 'Tools', 'Efficiency', 'Automation'],
      [PersonalityType.THE_INNOVATOR]: ['AI Tools', 'Technology', 'Innovation', 'Machine Learning'],
    };

    return categoryMap[personalityType];
  }
}
