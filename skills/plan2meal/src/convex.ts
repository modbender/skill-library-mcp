/**
 * Convex API Client for Plan2Meal
 */

import type { AxiosInstance } from 'axios';
import axios from 'axios';
import type { RecipeMetadata, ExtractionResult, Recipe, GroceryList, GroceryListItem } from './types';

/**
 * Convex API Client for Plan2Meal
 */
export class ConvexClient {
  private convexUrl: string;
  private authToken: string;
  private provider: string;
  private httpClient: AxiosInstance;

  constructor(convexUrl: string, authToken: string, provider: string = 'github') {
    this.convexUrl = convexUrl;
    this.authToken = authToken;
    this.provider = provider;
    
    this.httpClient = axios.create({
      baseURL: convexUrl,
      headers: this.getAuthHeaders(),
    });
  }

  /**
   * Get authentication headers based on provider
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Different providers use different auth mechanisms
    if (this.provider === 'github') {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    } else if (this.provider === 'google') {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    } else if (this.provider === 'apple') {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    } else {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  /**
   * Generic query executor
   */
  async query<T>(functionName: string, args: Record<string, unknown> = {}): Promise<T> {
    try {
      const response = await this.httpClient.post('/api/query', {
        functionName,
        args,
      });
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      console.error(`Convex query ${functionName} failed:`, message);
      throw new Error(`Query failed: ${message}`);
    }
  }

  /**
   * Generic mutation executor
   */
  async mutation<T>(functionName: string, args: Record<string, unknown> = {}): Promise<T> {
    try {
      const response = await this.httpClient.post('/api/mutation', {
        functionName,
        args,
      });
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      console.error(`Convex mutation ${functionName} failed:`, message);
      throw new Error(`Mutation failed: ${message}`);
    }
  }

  /**
   * Generic action executor
   */
  async action<T>(functionName: string, args: Record<string, unknown> = {}): Promise<T> {
    try {
      const response = await this.httpClient.post('/api/action', {
        functionName,
        args,
      });
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      console.error(`Convex action ${functionName} failed:`, message);
      throw new Error(`Action failed: ${message}`);
    }
  }

  // ==================== Recipes ====================

  async getAllRecipes(): Promise<Recipe[]> {
    return this.query<Recipe[]>('recipes.get');
  }

  async getMyRecipes(): Promise<Recipe[]> {
    return this.query<Recipe[]>('recipes.getMyRecipes');
  }

  async getRecipeById(id: string): Promise<Recipe | null> {
    return this.query<Recipe | null>('recipes.getById', { id });
  }

  async searchRecipes(term: string): Promise<Recipe[]> {
    return this.query<Recipe[]>('recipes.searchMyRecipes', { searchTerm: term });
  }

  async createRecipe(recipeData: RecipeMetadata): Promise<string> {
    return this.mutation<string>('recipes.create', recipeData as unknown as Record<string, unknown>);
  }

  async updateRecipe(id: string, updates: Partial<RecipeMetadata>): Promise<Recipe | null> {
    return this.mutation<Recipe | null>('recipes.update', { id, ...updates });
  }

  async deleteRecipe(id: string): Promise<void> {
    await this.mutation<void>('recipes.remove', { id });
  }

  // ==================== Recipe Extraction ====================

  async fetchRecipeMetadata(url: string): Promise<ExtractionResult> {
    return this.action<ExtractionResult>('recipeExtraction.fetchRecipeMetadata', { url });
  }

  // ==================== Grocery Lists ====================

  async getMyLists(): Promise<GroceryList[]> {
    return this.query<GroceryList[]>('groceryLists.getMyLists');
  }

  async getListById(id: string): Promise<GroceryList | null> {
    return this.query<GroceryList | null>('groceryLists.getById', { id });
  }

  async createGroceryList(name: string, description: string = ''): Promise<string> {
    return this.mutation<string>('groceryLists.create', { name, description });
  }

  async updateGroceryList(id: string, updates: Partial<GroceryList>): Promise<GroceryList | null> {
    return this.mutation<GroceryList | null>('groceryLists.update', { id, ...updates });
  }

  async deleteGroceryList(id: string): Promise<void> {
    await this.mutation<void>('groceryLists.remove', { id });
  }

  async addRecipeToList(groceryListId: string, recipeId: string, servings: number = 1): Promise<void> {
    await this.mutation<void>('groceryLists.addRecipeToList', { groceryListId, recipeId, servings });
  }

  async removeRecipeFromList(groceryListId: string, recipeId: string): Promise<void> {
    await this.mutation<void>('groceryLists.removeRecipeFromList', { groceryListId, recipeId });
  }

  async toggleItemCompleted(id: string, isCompleted: boolean): Promise<GroceryListItem | null> {
    return this.mutation<GroceryListItem | null>('groceryLists.toggleItemCompleted', { id, isCompleted });
  }

  async addCustomItem(
    groceryListId: string,
    ingredient: string,
    quantity?: string,
    unit?: string
  ): Promise<void> {
    await this.mutation<void>('groceryLists.addCustomItem', { groceryListId, ingredient, quantity, unit });
  }

  async removeItem(id: string): Promise<void> {
    await this.mutation<void>('groceryLists.removeItem', { id });
  }

  async regenerateListItems(groceryListId: string): Promise<void> {
    await this.mutation<void>('groceryLists.regenerateItems', { groceryListId });
  }
}
