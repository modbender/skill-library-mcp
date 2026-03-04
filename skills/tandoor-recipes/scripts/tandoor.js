#!/usr/bin/env node
import { z } from 'zod';
import { apiRequest, apiRequestRaw } from './api.js';
import { RecipeSchema, RecipeListResponseSchema, MealTypeSchema, MealPlanListResponseSchema, ShoppingListResponseSchema, FoodListResponseSchema, UnitListResponseSchema, KeywordListResponseSchema, } from './schemas.js';
// ============================================
// Commands
// ============================================
async function searchRecipes(query, limit = 10) {
    const data = await apiRequest(`/api/recipe/?query=${encodeURIComponent(query)}&page_size=${limit}`, RecipeListResponseSchema);
    console.log(`Found ${data.count} recipes:`);
    data.results.forEach(r => {
        console.log(`  ID: ${r.id} - ${r.name}`);
    });
}
async function getRecipe(recipeId) {
    const recipe = await apiRequest(`/api/recipe/${recipeId}/`, RecipeSchema);
    console.log(JSON.stringify(recipe, null, 2));
    return recipe;
}
async function getMealTypes() {
    const types = await apiRequest('/api/meal-type/', z.array(MealTypeSchema));
    console.log('Meal Types:');
    types.forEach(t => console.log(`  ID: ${t.id} - ${t.name}`));
    return types;
}
async function getMealTypeId(name) {
    const types = await apiRequest('/api/meal-type/', z.array(MealTypeSchema));
    const found = types.find(t => t.name.toLowerCase() === name.toLowerCase());
    return found?.id ?? null;
}
async function addToMealPlan(recipeId, mealType, date, servings = 1) {
    // Get meal type ID
    const mealTypeId = await getMealTypeId(mealType);
    if (!mealTypeId) {
        throw new Error(`Meal type "${mealType}" not found`);
    }
    // Get recipe details
    const recipe = await apiRequest(`/api/recipe/${recipeId}/`, RecipeSchema);
    const payload = {
        recipe: { id: recipeId, name: recipe.name, keywords: recipe.keywords ?? [] },
        meal_type: { id: mealTypeId, name: mealType },
        from_date: `${date}T00:00:00`,
        servings: String(servings),
    };
    await apiRequestRaw('/api/meal-plan/', { method: 'POST', body: payload });
    console.log(`Added "${recipe.name}" to ${mealType} on ${date}`);
}
async function getMealPlans(fromDate, toDate) {
    let url = `/api/meal-plan/?from_date=${fromDate}`;
    if (toDate)
        url += `&to_date=${toDate}`;
    const plans = await apiRequest(url, MealPlanListResponseSchema);
    console.log('Meal Plans:');
    plans.forEach(p => {
        const date = p.from_date.split('T')[0];
        console.log(`  ${date} - ${p.meal_type?.name ?? 'Unknown'}: ${p.recipe?.name ?? 'Unknown'}`);
    });
}
async function getShoppingList(checked = 'false') {
    const items = await apiRequest(`/api/shopping-list-entry/?checked=${checked}`, ShoppingListResponseSchema);
    console.log('Shopping List:');
    items.forEach(i => {
        const check = i.checked ? '[✓]' : '[ ]';
        console.log(`  ${check} ${i.amount} ${i.unit?.name ?? 'x'} ${i.food?.name ?? 'Unknown'}`);
    });
}
async function lookupFoodId(name) {
    const data = await apiRequest(`/api/food/?query=${encodeURIComponent(name)}`, FoodListResponseSchema);
    return data.results[0] ?? null;
}
async function lookupUnitId(name) {
    const data = await apiRequest(`/api/unit/?query=${encodeURIComponent(name)}`, UnitListResponseSchema);
    return data.results[0] ?? null;
}
async function addShoppingItem(foodName, amount, unitName, note) {
    const food = await lookupFoodId(foodName);
    if (!food)
        throw new Error(`Food "${foodName}" not found`);
    const unit = await lookupUnitId(unitName);
    if (!unit)
        throw new Error(`Unit "${unitName}" not found`);
    const payload = {
        food: { id: food.id, name: food.name },
        unit: { id: unit.id, name: unit.name },
        amount,
        note,
    };
    await apiRequestRaw('/api/shopping-list-entry/', { method: 'POST', body: payload });
    console.log(`Added: ${amount} ${unit.name} ${food.name}`);
}
async function checkShoppingItem(itemId) {
    await apiRequestRaw(`/api/shopping-list-entry/${itemId}/`, {
        method: 'PATCH',
        body: { checked: true },
    });
    console.log(`Checked off item ${itemId}`);
}
async function removeShoppingItem(itemId) {
    await apiRequestRaw(`/api/shopping-list-entry/${itemId}/`, { method: 'DELETE' });
    console.log(`Removed item ${itemId}`);
}
async function createRecipe(name, ingredientsBlock, instructionsBlock, servings = 4) {
    const ingredients = ingredientsBlock
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => ({
        food: { name: line },
        unit: { name: 'unit' },
        amount: '1',
    }));
    const payload = {
        name,
        servings,
        steps: [{ instruction: instructionsBlock, ingredients }],
    };
    const result = await apiRequestRaw('/api/recipe/', { method: 'POST', body: payload });
    console.log(`Created recipe "${name}" with ID: ${result.id}`);
}
async function getKeywords(query) {
    const url = query ? `/api/keyword/?query=${encodeURIComponent(query)}` : '/api/keyword/';
    const data = await apiRequest(url, KeywordListResponseSchema);
    data.results.forEach(k => console.log(`  ID: ${k.id} - ${k.name ?? k.label ?? 'Unknown'}`));
}
async function getFoods(query) {
    const url = query ? `/api/food/?query=${encodeURIComponent(query)}` : '/api/food/';
    const data = await apiRequest(url, FoodListResponseSchema);
    data.results.forEach(f => console.log(`  ID: ${f.id} - ${f.name}`));
}
async function getUnits(query) {
    const url = query ? `/api/unit/?query=${encodeURIComponent(query)}` : '/api/unit/';
    const data = await apiRequest(url, UnitListResponseSchema);
    data.results.forEach(u => console.log(`  ID: ${u.id} - ${u.name}`));
}
// ============================================
// CLI
// ============================================
function showHelp() {
    console.log(`
Tandoor Recipe Manager CLI

Usage: node tandoor.js <command> [args...]

Commands:
  search-recipes <query> [limit]           Search recipes
  get-recipe <id>                          Get recipe details
  create-recipe <name> <ingredients> <instructions> [servings]
  
  get-meal-types                           List meal types
  add-to-meal-plan <recipe_id> <meal_type> <YYYY-MM-DD> [servings]
  get-meal-plans <from_date> [to_date]     Get meal plans
  
  get-shopping-list [checked]              Get shopping list
  add-shopping-item <food> <amount> <unit> [note]
  check-shopping-item <item_id>            Check off item
  remove-shopping-item <item_id>           Remove item
  
  get-keywords [query]                     List keywords
  get-foods [query]                        List foods
  get-units [query]                        List units

Environment:
  TANDOOR_URL          Tandoor instance URL
  TANDOOR_API_TOKEN    API authentication token
`);
}
async function main() {
    const [, , command, ...args] = process.argv;
    if (!command || command === 'help' || command === '--help') {
        showHelp();
        return;
    }
    try {
        switch (command) {
            case 'search-recipes':
                await searchRecipes(args[0], args[1] ? parseInt(args[1]) : undefined);
                break;
            case 'get-recipe':
                await getRecipe(parseInt(args[0]));
                break;
            case 'create-recipe':
                await createRecipe(args[0], args[1], args[2], args[3] ? parseInt(args[3]) : undefined);
                break;
            case 'get-meal-types':
                await getMealTypes();
                break;
            case 'add-to-meal-plan':
                await addToMealPlan(parseInt(args[0]), args[1], args[2], args[3] ? parseInt(args[3]) : undefined);
                break;
            case 'get-meal-plans':
                await getMealPlans(args[0], args[1]);
                break;
            case 'get-shopping-list':
                await getShoppingList(args[0]);
                break;
            case 'add-shopping-item':
                await addShoppingItem(args[0], args[1], args[2], args[3]);
                break;
            case 'check-shopping-item':
                await checkShoppingItem(parseInt(args[0]));
                break;
            case 'remove-shopping-item':
                await removeShoppingItem(parseInt(args[0]));
                break;
            case 'get-keywords':
                await getKeywords(args[0]);
                break;
            case 'get-foods':
                await getFoods(args[0]);
                break;
            case 'get-units':
                await getUnits(args[0]);
                break;
            default:
                console.error(`Unknown command: ${command}`);
                console.error('Run with --help for usage');
                process.exit(1);
        }
    }
    catch (err) {
        console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
        process.exit(1);
    }
}
main();
//# sourceMappingURL=tandoor.js.map