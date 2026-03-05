#!/usr/bin/env node
/**
 * Mealie CLI - Interact with Mealie recipe manager
 * 
 * Recipes:
 *   node mealie.js recipes                     - List all recipes
 *   node mealie.js recipe <slug>               - Get recipe details
 *   node mealie.js search "query"              - Search recipes
 *   node mealie.js create-recipe <url>         - Import recipe from URL
 *   node mealie.js delete-recipe <slug>        - Delete recipe
 * 
 * Shopping Lists:
 *   node mealie.js lists                       - List shopping lists
 *   node mealie.js list <id>                   - Show list items
 *   node mealie.js add-item <listId> "item"    - Add item to list
 *   node mealie.js check-item <listId> <itemId> - Mark checked
 *   node mealie.js delete-item <listId> <itemId> - Delete item
 * 
 * Meal Plans:
 *   node mealie.js mealplan [days]             - Show meal plan (default 7)
 *   node mealie.js add-meal <date> <slug> [meal] - Add meal
 * 
 * Requires: MEALIE_URL and MEALIE_API_TOKEN environment variables
 */

const fs = require('fs');
const path = require('path');
const https = require('http'); // May be http or https depending on URL

// Load Mealie credentials from environment
function loadEnv() {
  if (process.env.MEALIE_URL && process.env.MEALIE_API_TOKEN) {
    return;
  }
  
  // Try skill-level .env first
  const skillEnvPath = path.join(__dirname, '..', '.env');
  if (fs.existsSync(skillEnvPath)) {
    const content = fs.readFileSync(skillEnvPath, 'utf8');
    content.split('\n').forEach(line => {
      const match = line.match(/^(MEALIE_URL|MEALIE_API_TOKEN)=(.*)$/);
      if (match && !process.env[match[1]]) {
        process.env[match[1]] = match[2].trim().replace(/^["']|["']$/g, '');
      }
    });
  }
  
  // Fallback: agent-level .env (only MEALIE_* vars)
  const agentEnvPath = path.join(__dirname, '..', '..', '..', '.env');
  if (fs.existsSync(agentEnvPath)) {
    const content = fs.readFileSync(agentEnvPath, 'utf8');
    content.split('\n').forEach(line => {
      const match = line.match(/^(MEALIE_URL|MEALIE_API_TOKEN)=(.*)$/);
      if (match && !process.env[match[1]]) {
        process.env[match[1]] = match[2].trim().replace(/^["']|["']$/g, '');
      }
    });
  }
}

loadEnv();

const MEALIE_URL = process.env.MEALIE_URL;
const API_TOKEN = process.env.MEALIE_API_TOKEN;

if (!MEALIE_URL || !API_TOKEN) {
  console.error('Error: MEALIE_URL and MEALIE_API_TOKEN must be set');
  console.error('Set them in ~/.openclaw/.env or ~/.openclaw/skills/mealie/.env');
  process.exit(1);
}

// Parse URL
const urlObj = new URL(MEALIE_URL);
const isHttps = urlObj.protocol === 'https:';
const httpModule = isHttps ? require('https') : require('http');

// API request helper
async function api(method, endpoint, body = null) {
  return new Promise((resolve, reject) => {
    const path = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: path,
      method: method,
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      }
    };
    
    const req = httpModule.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = data ? JSON.parse(data) : {};
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          } else {
            resolve(parsed);
          }
        } catch (e) {
          reject(new Error(`Parse error: ${data}`));
        }
      });
    });
    
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Format recipe list
function formatRecipes(recipes) {
  const items = recipes.items || recipes.data || recipes;
  if (!items.length) {
    console.log('No recipes found');
    return;
  }
  console.log(`\n🍳 Recipes (${recipes.total || items.length})\n`);
  items.forEach(r => {
    console.log(`   ${r.name || r.slug}`);
    console.log(`   Slug: ${r.slug}`);
    console.log('');
  });
}

// Format single recipe
function formatRecipe(recipe) {
  console.log(`\n🍳 ${recipe.name}\n`);
  console.log(`   Slug: ${recipe.slug}`);
  console.log(`   Serves: ${recipe.recipeYield || 'N/A'}`);
  console.log(`   Prep: ${recipe.prepTime || 'N/A'} | Cook: ${recipe.performTime || 'N/A'}`);
  
  if (recipe.recipeIngredient?.length) {
    console.log('\n   Ingredients:');
    recipe.recipeIngredient.forEach(ing => {
      const text = ing.display || ing.note || (typeof ing === 'string' ? ing : JSON.stringify(ing));
      console.log(`     • ${text}`);
    });
  }
  
  if (recipe.recipeInstructions?.length) {
    console.log('\n   Instructions:');
    recipe.recipeInstructions.forEach((step, i) => {
      const text = step.text || step;
      console.log(`     ${i + 1}. ${text.slice(0, 80)}${text.length > 80 ? '...' : ''}`);
    });
  }
  console.log('');
}

// Format shopping lists
function formatLists(lists) {
  const items = lists.items || lists.data || lists;
  if (!items.length) {
    console.log('No shopping lists found');
    return;
  }
  console.log(`\n🛒 Shopping Lists\n`);
  items.forEach(list => {
    const checked = list.listItems?.filter(i => i.checked).length || 0;
    const total = list.listItems?.length || 0;
    console.log(`   ${list.name}`);
    console.log(`   ID: ${list.id} | ${checked}/${total} items checked`);
    console.log('');
  });
}

// Format single list
function formatList(list) {
  console.log(`\n🛒 ${list.name}\n`);
  if (!list.listItems?.length) {
    console.log('   (empty)');
    return;
  }
  list.listItems.forEach(item => {
    const check = item.checked ? '☑' : '☐';
    console.log(`   ${check} ${item.display || item.note || item.food?.name || 'Item'}`);
    if (item.quantity) console.log(`      Qty: ${item.quantity} ${item.unit?.name || ''}`);
  });
  console.log('');
}

// Format meal plan
function formatMealplan(plans) {
  const items = plans.items || plans.data || plans;
  if (!items.length) {
    console.log('No meals planned');
    return;
  }
  
  // Group by date
  const byDate = {};
  items.forEach(meal => {
    const date = meal.date;
    if (!byDate[date]) byDate[date] = [];
    byDate[date].push(meal);
  });
  
  console.log(`\n📅 Meal Plan\n`);
  
  Object.keys(byDate).sort().forEach(date => {
    const d = new Date(date);
    const weekday = d.toLocaleDateString('en-US', { weekday: 'short' });
    const day = d.getDate();
    console.log(`   ${day.toString().padStart(2, ' ')} ${weekday}`);
    byDate[date].forEach(meal => {
      const recipe = meal.recipe?.name || meal.recipe?.slug || 'No recipe';
      const mealType = meal.entryType || '';
      console.log(`       ${mealType}: ${recipe}`);
    });
  });
  console.log('');
}

// Commands
async function main() {
  const [cmd, ...args] = process.argv.slice(2);
  
  try {
    switch (cmd) {
      case 'recipes':
        const recipes = await api('GET', '/recipes?perPage=100');
        formatRecipes(recipes);
        break;
        
      case 'recipe':
        if (!args[0]) {
          console.error('Usage: mealie.js recipe <slug>');
          process.exit(1);
        }
        const recipe = await api('GET', `/recipes/${args[0]}`);
        formatRecipe(recipe);
        break;
        
      case 'search':
        if (!args[0]) {
          console.error('Usage: mealie.js search "query"');
          process.exit(1);
        }
        const results = await api('GET', `/recipes?search=${encodeURIComponent(args[0])}`);
        formatRecipes(results);
        break;
        
      case 'create-recipe':
        if (!args[0]) {
          console.error('Usage: mealie.js create-recipe <url>');
          process.exit(1);
        }
        const created = await api('POST', '/recipes/create/url', { url: args[0] });
        console.log(`✓ Created recipe: ${created.slug}`);
        break;
        
      case 'delete-recipe':
        if (!args[0]) {
          console.error('Usage: mealie.js delete-recipe <slug>');
          process.exit(1);
        }
        await api('DELETE', `/recipes/${args[0]}`);
        console.log(`✓ Deleted recipe: ${args[0]}`);
        break;
        
      case 'lists':
        const lists = await api('GET', '/households/shopping/lists');
        formatLists(lists);
        break;
        
      case 'list':
        if (!args[0]) {
          console.error('Usage: mealie.js list <id>');
          process.exit(1);
        }
        const list = await api('GET', `/households/shopping/lists/${args[0]}`);
        formatList(list);
        break;
        
      case 'add-item':
        if (!args[0] || !args[1]) {
          console.error('Usage: mealie.js add-item <listId> "item" [quantity]');
          process.exit(1);
        }
        const newItem = await api('POST', '/households/shopping/items', {
          shoppingListId: args[0],
          note: args[1],
          quantity: args[2] ? parseFloat(args[2]) : 1
        });
        console.log(`✓ Added item to list`);
        break;
        
      case 'check-item':
        if (!args[0] || !args[1]) {
          console.error('Usage: mealie.js check-item <listId> <itemId>');
          process.exit(1);
        }
        await api('PUT', `/households/shopping/items/${args[1]}`, { checked: true });
        console.log(`✓ Item checked`);
        break;
        
      case 'uncheck-item':
        if (!args[0] || !args[1]) {
          console.error('Usage: mealie.js uncheck-item <listId> <itemId>');
          process.exit(1);
        }
        await api('PUT', `/households/shopping/items/${args[1]}`, { checked: false });
        console.log(`✓ Item unchecked`);
        break;
        
      case 'delete-item':
        if (!args[0] || !args[1]) {
          console.error('Usage: mealie.js delete-item <listId> <itemId>');
          process.exit(1);
        }
        await api('DELETE', `/households/shopping/items/${args[1]}`);
        console.log(`✓ Item deleted`);
        break;
        
      case 'mealplan':
        const days = args[0] ? parseInt(args[0]) : 7;
        const today = new Date().toISOString().split('T')[0];
        const endDate = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        const plans = await api('GET', `/households/mealplans?start_date=${today}&end_date=${endDate}`);
        formatMealplan(plans);
        break;
        
      case 'add-meal':
        if (!args[0] || !args[1]) {
          console.error('Usage: mealie.js add-meal <date> <recipeSlug> [mealType]');
          process.exit(1);
        }
        const meal = await api('POST', '/households/mealplans', {
          date: args[0],
          recipeSlug: args[1],
          entryType: args[2] || 'dinner'
        });
        console.log(`✓ Added meal for ${args[0]}`);
        break;
        
      case 'stats':
        const stats = await api('GET', '/households/statistics');
        console.log('\n📊 Statistics\n');
        console.log(`   Total recipes: ${stats.totalRecipes || 'N/A'}`);
        console.log(`   Total users: ${stats.totalUsers || 'N/A'}`);
        console.log(`   Total categories: ${stats.totalCategories || 'N/A'}`);
        console.log(`   Total tags: ${stats.totalTags || 'N/A'}`);
        console.log('');
        break;
        
      case 'tags':
        const tags = await api('GET', '/organizers/tags');
        console.log('\n🏷️ Tags\n');
        (tags.items || tags.data || tags).forEach(t => console.log(`   ${t.name}`));
        console.log('');
        break;
        
      case 'categories':
        const cats = await api('GET', '/organizers/categories');
        console.log('\n📁 Categories\n');
        (cats.items || cats.data || cats).forEach(c => console.log(`   ${c.name}`));
        console.log('');
        break;
        
      default:
        console.log('Usage: mealie.js <command> [args]');
        console.log('\nRecipes: recipes, recipe, search, create-recipe, delete-recipe');
        console.log('Lists: lists, list, add-item, check-item, uncheck-item, delete-item');
        console.log('Meal Plans: mealplan, add-meal');
        console.log('Other: stats, tags, categories');
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
