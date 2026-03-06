/**
 * Types for Plan2Meal Skill
 */

// ==================== Recipe Types ====================

export interface RecipeMetadata {
  name: string;
  description?: string;
  url?: string;
  ingredients: string[];
  steps: string[];
  prepTime?: string | null;
  cookTime?: string | null;
  servings?: number | null;
  calories?: number | null;
  difficulty?: string | null;
  cuisine?: string | null;
  tags?: string[] | null;
  nutritionInfo?: NutritionInfo | null;
  localization?: Localization | null;
}

export interface NutritionInfo {
  protein: number;
  carbs: number;
  fat: number;
}

export interface Localization {
  language: string;
  region: string;
}

export interface Recipe extends RecipeMetadata {
  _id: string;
  createdBy: string;
  createdAt: number;
  updatedAt: number;
}

// ==================== Grocery List Types ====================

export interface GroceryList {
  _id: string;
  name: string;
  description?: string;
  createdBy: string;
  createdAt: number;
  updatedAt: number;
  isCompleted: boolean;
  items?: GroceryListItem[];
  recipes?: Recipe[];
}

export interface GroceryListItem {
  _id: string;
  groceryListId: string;
  ingredient: string;
  quantity?: string;
  unit?: string;
  isCompleted: boolean;
  sourceRecipes?: SourceRecipe[];
  createdAt: number;
  updatedAt: number;
}

export interface SourceRecipe {
  recipeId: string;
  recipeName: string;
  originalIngredient: string;
}

// ==================== Extraction Result Types ====================

export interface ExtractionResult {
  success: boolean;
  error?: string;
  metadata: RecipeMetadata;
  sourceUrl: string;
  scrapeMethod: ScrapeMethod;
  scrapedAt: number;
}

export type ScrapeMethod = 
  | 'native-fetch-json'
  | 'firecrawl-json'
  | 'gpt-5-nano'
  | 'fallback';

// ==================== Auth Types ====================

export interface UserInfo {
  id: string;
  name: string;
  email?: string;
  login: string;
  avatarUrl?: string;
}

export interface Session {
  authToken: string;
  provider: AuthProvider;
  userInfo: UserInfo | null;
  createdAt: number;
}

export type AuthProvider = 'github' | 'google' | 'apple';

// ==================== Config Types ====================

export interface SkillConfig {
  convexUrl: string;
  githubClientId: string;
  githubClientSecret: string;
  githubCallbackUrl: string;
  googleClientId: string;
  googleClientSecret: string;
  googleCallbackUrl: string;
  appleClientId: string;
  appleClientSecret: string;
  appleCallbackUrl: string;
  clawdbotUrl: string;
}

// ==================== Command Types ====================

export interface CommandHandlerResult {
  text: string;
  requiresAuth?: boolean;
}

export interface CommandPattern {
  pattern: RegExp;
  description: string;
}
