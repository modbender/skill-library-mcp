/**
 * Command Handlers for Plan2Meal Skill
 */

import type { ConvexClient } from './convex';
import type { RecipeMetadata, Recipe, GroceryList } from './types';
import { markdownEscape, formatTime } from './utils';

/**
 * OAuth Providers interface
 */
interface OAuthProviders {
  github: unknown;
  google: unknown;
  apple: unknown;
}

/**
 * Skill configuration interface
 */
interface SkillConfig {
  convexUrl: string;
  githubClientId: string;
  githubClientSecret: string;
  googleClientId: string;
  googleClientSecret: string;
  appleClientId: string;
  appleClientSecret: string;
  clawdbotUrl: string;
}

/**
 * Command Handlers for Plan2Meal Skill
 */
export class Plan2MealCommands {
  private convex: ConvexClient;
  private oauth: OAuthProviders;
  private config: SkillConfig;

  constructor(convexClient: ConvexClient, oauthProviders: OAuthProviders, config: SkillConfig) {
    this.convex = convexClient;
    this.oauth = oauthProviders;
    this.config = config;
  }

  /**
   * Show help
   */
  help(): { text: string } {
    return {
      text: `📚 **Plan2Meal Commands**

**Authentication**
\`plan2meal login\` - Authenticate with GitHub, Google, or Apple
\`plan2meal logout\` - Logout and clear session

**Recipes**
\`plan2meal add <url>\` - Fetch recipe from URL and add it
\`plan2meal list\` - List your recent recipes
\`plan2meal search <term>\` - Search your recipes
\`plan2meal show <id>\` - Show recipe details
\`plan2meal delete <id>\` - Delete a recipe

**Grocery Lists**
\`plan2meal lists\` - List your grocery lists
\`plan2meal list-create <name>\` - Create a new grocery list
\`plan2meal list-show <id>\` - Show grocery list with items
\`plan2meal list-add <listId> <recipeId>\` - Add recipe to grocery list

**Examples**
\`plan2meal add https://www.allrecipes.com/recipe/12345/pasta\`
\`plan2meal search pasta\`
\`plan2meal list-create Weekly Shopping\`
`
    };
  }

  /**
   * Add recipe from URL
   */
  async addRecipe(url: string): Promise<{ text: string }> {
    // Fetch metadata from URL
    const extractionResult = await this.convex.fetchRecipeMetadata(url);

    if (!extractionResult.success) {
      return {
        text: `❌ Failed to extract recipe from URL: ${extractionResult.error || 'Unknown error'}`
      };
    }

    const { metadata, scrapeMethod, scrapedAt } = extractionResult;

    // Create recipe in Convex
    await this.convex.createRecipe({
      name: metadata.name || 'Untitled Recipe',
      url: url,
      ingredients: metadata.ingredients || [],
      steps: metadata.steps || [],
      calories: metadata.calories || null,
      servings: metadata.servings || 2,
      prepTime: metadata.prepTime || null,
      cookTime: metadata.cookTime || null,
      difficulty: metadata.difficulty || 'medium',
      cuisine: metadata.cuisine || '',
      tags: metadata.tags || [],
      nutritionInfo: metadata.nutritionInfo || null,
      localization: metadata.localization || { language: 'en', region: 'US' }
    });

    const timestamp = new Date(scrapedAt).toLocaleTimeString();
    const methodEmoji = scrapeMethod === 'native-fetch-json' ? '⚡' : 
                       scrapeMethod === 'firecrawl-json' ? '🔥' : 
                       scrapeMethod === 'gpt-5-nano' ? '🤖' : '⚠️';

    return {
      text: `✅ Recipe added successfully!\n\n📖 **${markdownEscape(metadata.name || 'Untitled Recipe')}**\n` +
            `🔗 Source: ${new URL(url).hostname}\n` +
            `${methodEmoji} Method: \`${scrapeMethod}\`\n` +
            `⏰ Scraped at: ${timestamp}\n\n` +
            this.formatRecipePreview(metadata)
    };
  }

  /**
   * List user's recipes
   */
  async listRecipes(): Promise<{ text: string }> {
    const recipes = await this.convex.getMyRecipes();

    if (!recipes || recipes.length === 0) {
      return { text: '📭 You have no recipes yet. Add one with `plan2meal add <url>`' };
    }

    // Show most recent first
    const sorted = [...recipes].reverse().slice(0, 10);

    let text = `📚 **Your Recipes** (${recipes.length} total)\n\n`;
    for (const recipe of sorted) {
      const time = formatTime(recipe.prepTime, recipe.cookTime);
      text += `• \`${recipe._id}\` - ${markdownEscape(recipe.name)}\n`;
      if (time) text += `  └─ ${time}\n`;
    }

    return { text };
  }

  /**
   * Search recipes
   */
  async searchRecipes(term: string): Promise<{ text: string }> {
    const recipes = await this.convex.searchRecipes(term);

    if (!recipes || recipes.length === 0) {
      return { text: `🔍 No recipes found for "${markdownEscape(term)}"` };
    }

    let text = `🔍 **Search Results** for "${markdownEscape(term)}" (${recipes.length})\n\n`;
    for (const recipe of recipes.slice(0, 10)) {
      text += `• \`${recipe._id}\` - ${markdownEscape(recipe.name)}\n`;
    }

    return { text };
  }

  /**
   * Show recipe details
   */
  async showRecipe(id: string): Promise<{ text: string }> {
    const recipe = await this.convex.getRecipeById(id);

    if (!recipe) {
      return { text: `❌ Recipe not found: \`${id}\`` };
    }

    return {
      text: this.formatRecipe(recipe)
    };
  }

  /**
   * Delete recipe
   */
  async deleteRecipe(id: string): Promise<{ text: string }> {
    try {
      await this.convex.deleteRecipe(id);
      return { text: `✅ Recipe deleted: \`${id}\`` };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return { text: `❌ Failed to delete recipe: ${message}` };
    }
  }

  /**
   * List grocery lists
   */
  async lists(): Promise<{ text: string }> {
    const lists = await this.convex.getMyLists();

    if (!lists || lists.length === 0) {
      return { text: '📭 You have no grocery lists. Create one with `plan2meal list-create <name>`' };
    }

    let text = `🛒 **Your Grocery Lists** (${lists.length})\n\n`;
    for (const list of lists) {
      text += `• \`${list._id}\` - ${markdownEscape(list.name)}`;
      if (list.isCompleted) text += ' ✅';
      text += '\n';
    }

    return { text };
  }

  /**
   * Show grocery list
   */
  async showList(id: string): Promise<{ text: string }> {
    const list = await this.convex.getListById(id);

    if (!list) {
      return { text: `❌ Grocery list not found: \`${id}\`` };
    }

    return {
      text: this.formatGroceryList(list)
    };
  }

  /**
   * Create grocery list
   */
  async createList(name: string): Promise<{ text: string }> {
    const list = await this.convex.createGroceryList(name);
    return {
      text: `✅ Grocery list created!\n\n🛒 **${markdownEscape(name)}**\n` +
            `ID: \`${list}\``
    };
  }

  /**
   * Add recipe to grocery list
   */
  async addRecipeToList(listId: string, recipeId: string): Promise<{ text: string }> {
    try {
      await this.convex.addRecipeToList(listId, recipeId);
      return { text: `✅ Recipe added to grocery list!` };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return { text: `❌ Failed to add recipe: ${message}` };
    }
  }

  /**
   * Format recipe preview
   */
  private formatRecipePreview(metadata: RecipeMetadata): string {
    let text = '';
    
    if (metadata.ingredients && metadata.ingredients.length > 0) {
      text += `🥘 **Ingredients** (${metadata.ingredients.length})\n`;
      text += metadata.ingredients.slice(0, 5).map(i => `• ${markdownEscape(i)}`).join('\n');
      if (metadata.ingredients.length > 5) {
        text += `\n  ...and ${metadata.ingredients.length - 5} more`;
      }
      text += '\n';
    }
    
    return text;
  }

  /**
   * Format full recipe
   */
  private formatRecipe(recipe: Recipe): string {
    let text = `📖 **${markdownEscape(recipe.name)}**\n`;
    text += '─'.repeat(30) + '\n';
    
    if (recipe.url) {
      try {
        text += `🔗 Source: ${new URL(recipe.url).hostname}\n`;
      } catch {
        text += `🔗 Source: ${markdownEscape(recipe.url)}\n`;
      }
    }
    
    const time = formatTime(recipe.prepTime, recipe.cookTime);
    if (time) text += `⏰ ${time}\n`;
    
    if (recipe.servings) text += `🍽️ ${recipe.servings} servings\n`;
    if (recipe.difficulty) text += `📊 Difficulty: ${recipe.difficulty}\n`;
    if (recipe.cuisine) text += `🌍 Cuisine: ${recipe.cuisine}\n`;
    
    text += '\n';
    
    // Ingredients
    if (recipe.ingredients && recipe.ingredients.length > 0) {
      text += `🥘 **Ingredients** (${recipe.ingredients.length})\n`;
      recipe.ingredients.forEach(i => text += `• ${markdownEscape(i)}\n`);
      text += '\n';
    }
    
    // Steps
    if (recipe.steps && recipe.steps.length > 0) {
      text += `🔪 **Instructions**\n`;
      recipe.steps.forEach((step, i) => text += `${i + 1}. ${markdownEscape(step)}\n`);
    }
    
    text += `\n🆔 \`${recipe._id}\``;
    
    return text;
  }

  /**
   * Format grocery list
   */
  private formatGroceryList(list: GroceryList): string {
    let text = `🛒 **${markdownEscape(list.name)}**\n`;
    text += '─'.repeat(30) + '\n';
    
    if (list.description) {
      text += `${markdownEscape(list.description)}\n\n`;
    }
    
    // Recipes
    if (list.recipes && list.recipes.length > 0) {
      text += `📖 **Recipes** (${list.recipes.length})\n`;
      list.recipes.forEach(r => text += `• ${markdownEscape(r.name)}\n`);
      text += '\n';
    }
    
    // Items
    if (list.items && list.items.length > 0) {
      const completed = list.items.filter(i => i.isCompleted).length;
      text += `🛍️ **Items** (${list.items.length} total, ${completed} completed)\n`;
      list.items.forEach(item => {
        const check = item.isCompleted ? '✅' : '⬜';
        let itemText = `${check} ${markdownEscape(item.ingredient)}`;
        if (item.quantity) itemText += ` (${item.quantity}${item.unit ? ' ' + item.unit : ''})`;
        text += `${itemText}\n`;
      });
    }
    
    text += `\n🆔 \`${list._id}\``;
    
    return text;
  }
}
