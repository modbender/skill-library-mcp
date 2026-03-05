#!/usr/bin/env node
/**
 * Gousto Meal Picker - API-based
 * 
 * Usage: node gousto-pick.mjs [--dry-run] [--week YYYY-MM-DD]
 * 
 * Flow:
 * 1. Auth via browser (get Bearer token from saved state)
 * 2. Fetch upcoming orders to find unpicked weeks
 * 3. Fetch menu for target week
 * 4. Filter & score recipes by rules
 * 5. Select best 4 recipes
 * 6. PUT order with selections
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const CONFIG_DIR = path.dirname(new URL(import.meta.url).pathname);
const CONFIG = JSON.parse(fs.readFileSync(path.join(CONFIG_DIR, 'config.json'), 'utf8'));
const SELECTIONS_FILE = path.join(CONFIG_DIR, 'selections.json');

const DRY_RUN = process.argv.includes('--dry-run');
const WEEK_ARG = process.argv.includes('--week') ? process.argv[process.argv.indexOf('--week') + 1] : null;

// ── Helpers ──────────────────────────────────────────────────────────────────

function api(method, endpoint, body = null, token) {
  const url = `https://production-api.gousto.co.uk${endpoint}`;
  const args = ['curl', '-s', '--compressed', '-X', method,
    '-H', 'Content-Type: application/json',
    '-H', `Authorization: Bearer ${token}`,
    '-H', 'Origin: https://www.gousto.co.uk',
    '-H', 'Referer: https://www.gousto.co.uk/',
    '-H', `x-gousto-user-id: ${CONFIG.userId || ''}`,
    '-H', `x-gousto-device-id: ${CONFIG.deviceId || ''}`,
    '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  ];
  if (body) args.push('-d', JSON.stringify(body));
  args.push(url);
  
  const result = execSync(args.map(a => `'${a.replace(/'/g, "'\\''")}'`).join(' '), { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024, shell: '/bin/zsh' });
  try {
    return JSON.parse(result);
  } catch {
    console.error('Failed to parse API response:', result.substring(0, 500));
    throw new Error('API response not JSON');
  }
}

function getToken() {
  // Try to get token from saved browser state
  const statePath = path.join(CONFIG_DIR, 'gousto-auth.json');
  if (!fs.existsSync(statePath)) {
    throw new Error('No auth state found. Run agent-browser to log in first.');
  }
  
  // Extract token from browser state cookies
  const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  const cookies = state.cookies || [];
  const tokenCookie = cookies.find(c => c.name === 'v1_oauth_token');
  
  if (!tokenCookie) {
    throw new Error('No oauth token in saved state. Need to re-login.');
  }
  
  const tokenData = JSON.parse(decodeURIComponent(tokenCookie.value));
  const token = tokenData.access_token;
  
  // Check expiry
  const expiryCookie = cookies.find(c => c.name === 'v1_oauth_expiry');
  if (expiryCookie) {
    const expiryData = JSON.parse(decodeURIComponent(expiryCookie.value));
    const expiresAt = new Date(expiryData.expires_at);
    if (expiresAt < new Date()) {
      console.log('⚠️  Token expired. Attempting refresh...');
      return refreshToken(state);
    }
  }
  
  return token;
}

function refreshToken(state) {
  const cookies = state.cookies || [];
  const refreshCookie = cookies.find(c => c.name === 'v1_oauth_refresh');
  if (!refreshCookie) throw new Error('No refresh token available. Need to re-login.');
  
  const refreshData = JSON.parse(decodeURIComponent(refreshCookie.value));
  
  // Use agent-browser to refresh since WAF blocks curl on auth endpoints
  try {
    execSync(`agent-browser open "https://www.gousto.co.uk/my-gousto" 2>/dev/null`, { encoding: 'utf8' });
    execSync(`agent-browser wait --load networkidle 2>/dev/null`, { encoding: 'utf8' });
    
    // Get fresh cookies
    const cookieJson = execSync(`agent-browser cookies --json 2>/dev/null`, { encoding: 'utf8' });
    const cookieData = JSON.parse(cookieJson);
    const newTokenCookie = cookieData.data?.cookies?.find(c => c.name === 'v1_oauth_token');
    
    if (newTokenCookie) {
      // Save updated state
      const statePath = path.join(CONFIG_DIR, 'gousto-auth.json');
      execSync(`agent-browser state save "${statePath}" 2>/dev/null`, { encoding: 'utf8' });
      
      const tokenData = JSON.parse(decodeURIComponent(newTokenCookie.value));
      return tokenData.access_token;
    }
    
    throw new Error('Could not get fresh token from browser');
  } finally {
    try { execSync('agent-browser close 2>/dev/null'); } catch {}
  }
}

// ── Recipe Filtering & Scoring ───────────────────────────────────────────────

// All rules are driven by config.json — see DEFAULTS below for what's configurable.
const RULES = CONFIG.rules || {};

const DEFAULTS = {
  // Hard filters — set to true to exclude, false to allow
  noNuts: true,              // Exclude recipes containing nuts (allergy)
  noFish: true,              // Exclude fish dishes
  fishAndChipsException: false, // Allow fish & chips even when noFish is true
  noVegetarian: true,        // Exclude vegetarian meals
  noPlantBased: true,        // Exclude plant-based/vegan meals
  noSeafood: false,          // Exclude all seafood (broader than fish)
  noDairy: false,            // Exclude dairy-containing meals
  noGluten: false,           // Exclude gluten-containing meals
  maxCookTimeMins: 45,       // Exclude recipes over this cook time

  // Soft constraints — limits per week
  maxMealsOver40Mins: 1,     // Max meals with cook time >= 40 mins
  maxPastaPerWeek: 1,        // Max pasta dishes
  maxRicePerWeek: 1,         // Max rice dishes
  maxSameProtein: 2,         // Max meals with same protein type

  // Scoring preferences
  preferHealthy: true,       // Boost healthy-tagged recipes
  preferQuicker: true,       // Boost faster cook times

  // Custom allergen exclusions (slugs from Gousto allergen data)
  // e.g. ["sesame", "celery", "mustard"]
  excludeAllergens: [],

  // Custom keyword exclusions — exclude recipes whose name contains any of these
  // e.g. ["spicy", "chilli"]
  excludeKeywords: [],
};

// Merge user rules over defaults
const R = { ...DEFAULTS, ...RULES };

const NUT_ALLERGENS = ['peanut', 'nut', 'almond', 'cashew', 'walnut', 'hazelnut', 'pecan', 'pistachio', 'macadamia'];
const FISH_KEYWORDS = ['fish', 'salmon', 'cod', 'haddock', 'prawn', 'shrimp', 'tuna', 'sea bass', 'mackerel', 'sardine', 'anchov'];
const SEAFOOD_KEYWORDS = [...FISH_KEYWORDS, 'crab', 'lobster', 'mussel', 'clam', 'squid', 'calamari', 'scallop'];
const FISH_CHIPS_KEYWORDS = ['fish and chips', 'fish & chips', 'fish n chips', 'battered fish', 'beer battered'];
const PASTA_KEYWORDS = ['pasta', 'spaghetti', 'penne', 'tortiglioni', 'fusilli', 'rigatoni', 'macaroni', 'lasagne', 'linguine', 'tagliatelle', 'fettuccine', 'orecchiette', 'carbonara', 'bolognese'];
const RICE_KEYWORDS = ['rice', 'risotto', 'biryani', 'pilaf', 'paella', 'fried rice'];

function hasAllergen(recipe, slugs) {
  const allergens = recipe.allergens || [];
  return allergens.some(a => a.contain_type === 'contains' && slugs.includes(a.slug));
}

function containsNuts(recipe) {
  const name = (recipe.name || '').toLowerCase();
  if (hasAllergen(recipe, NUT_ALLERGENS)) return true;
  return NUT_ALLERGENS.some(n => name.includes(n));
}

function isFish(recipe) {
  const name = (recipe.name || '').toLowerCase();
  return FISH_KEYWORDS.some(f => name.includes(f));
}

function isFishAndChips(recipe) {
  const name = (recipe.name || '').toLowerCase();
  return FISH_CHIPS_KEYWORDS.some(f => name.includes(f));
}

function isSeafood(recipe) {
  const name = (recipe.name || '').toLowerCase();
  return SEAFOOD_KEYWORDS.some(f => name.includes(f));
}

function isPasta(recipe) {
  const name = (recipe.name || '').toLowerCase();
  const dishTypes = (recipe.dish_types || []).map(d => d.name?.toLowerCase() || '');
  return PASTA_KEYWORDS.some(p => name.includes(p)) || dishTypes.some(d => d.includes('pasta'));
}

function isRice(recipe) {
  const name = (recipe.name || '').toLowerCase();
  return RICE_KEYWORDS.some(r => name.includes(r));
}

function getProtein(recipe) {
  const name = (recipe.name || '').toLowerCase();
  if (name.includes('chicken')) return 'chicken';
  if (name.includes('beef')) return 'beef';
  if (name.includes('pork') || name.includes('sausage') || name.includes('bacon') || name.includes('ham')) return 'pork';
  if (name.includes('lamb')) return 'lamb';
  if (name.includes('turkey')) return 'turkey';
  if (name.includes('duck')) return 'duck';
  return 'other';
}

function matchesExcludeKeywords(recipe) {
  if (!R.excludeKeywords?.length) return false;
  const name = (recipe.name || '').toLowerCase();
  return R.excludeKeywords.some(kw => name.includes(kw.toLowerCase()));
}

function scoreRecipe(recipe) {
  let score = 100;
  const prepTime = recipe.prep_time || recipe.prep_times?.for2 || 30;
  const kcal = recipe.nutritional_information?.per_portion?.energy_kcal || recipe.calories?.for2 || 500;
  
  // Prefer quicker meals
  if (R.preferQuicker) {
    score += Math.max(-10, (40 - prepTime));
  }
  
  // Prefer lower calorie
  if (R.preferHealthy) {
    if (kcal < 500) score += 15;
    else if (kcal < 600) score += 5;
    else if (kcal > 700) score -= 15;
    else if (kcal > 800) score -= 30;
  }
  
  // Prefer higher rated recipes
  const rating = recipe.rating?.average || 0;
  score += rating * 3;
  
  // Prefer healthy-tagged recipes
  if (R.preferHealthy) {
    const healthAttrs = recipe.health_attributes || [];
    if (healthAttrs.some(h => h.slug === 'healthy')) score += 10;
    if (healthAttrs.some(h => h.slug === 'not-healthy')) score -= 10;
    
    const dietaryClaims = recipe.dietary_claims || [];
    if (dietaryClaims.some(d => d.slug === 'calorie-controlled')) score += 8;
  }
  
  return score;
}

function selectMeals(recipes, existingRecipes = []) {
  const existingProteins = existingRecipes.map(r => getProtein(r));
  const existingHasPasta = existingRecipes.some(r => isPasta(r));
  const existingHasRice = existingRecipes.some(r => isRice(r));
  const mealsPerWeek = CONFIG.plan?.mealsPerWeek || 4;
  const slotsNeeded = mealsPerWeek - existingRecipes.length;
  
  if (slotsNeeded <= 0) return { selected: [], reason: `Already have ${mealsPerWeek} recipes` };
  
  // Hard filters — all configurable via rules
  let candidates = recipes.filter(r => {
    if (!r.is_available) return false;

    // Nut allergy filter
    if (R.noNuts && containsNuts(r)) return false;

    // Fish filter (with optional fish & chips exception)
    if (R.noFish) {
      if (isFish(r) && !(R.fishAndChipsException && isFishAndChips(r))) return false;
    }

    // Seafood filter (broader than fish)
    if (R.noSeafood && isSeafood(r)) return false;

    // Allergen-based filters
    if (R.noDairy && hasAllergen(r, ['milk'])) return false;
    if (R.noGluten && hasAllergen(r, ['gluten'])) return false;
    if (R.excludeAllergens?.length && hasAllergen(r, R.excludeAllergens)) return false;

    // Cook time filter
    if ((r.prep_time || r.prep_times?.for2 || 30) > R.maxCookTimeMins) return false;

    // Diet type filters
    const diet = r.diet_type?.slug || '';
    if (R.noVegetarian && diet === 'vegetarian') return false;
    if (R.noPlantBased && diet === 'plant-based') return false;

    // Custom keyword exclusions
    if (matchesExcludeKeywords(r)) return false;

    // Skip if already in existing
    if (existingRecipes.some(e => e.id === r.id)) return false;

    return true;
  });
  
  // Score all candidates
  candidates = candidates.map(r => ({ ...r, _score: scoreRecipe(r), _protein: getProtein(r), _isPasta: isPasta(r), _isRice: isRice(r), _prepTime: r.prep_time || r.prep_times?.for2 || 30 }));
  candidates.sort((a, b) => b._score - a._score);
  
  // Greedy selection with soft constraints
  const selected = [];
  let pastaCount = existingHasPasta ? 1 : 0;
  let riceCount = existingHasRice ? 1 : 0;
  let longMealCount = existingRecipes.filter(r => (r.prep_time || r.prep_times?.for2 || 30) >= 40).length;
  const proteinCounts = {};
  existingProteins.forEach(p => proteinCounts[p] = (proteinCounts[p] || 0) + 1);
  
  for (const r of candidates) {
    if (selected.length >= slotsNeeded) break;
    
    if (r._isPasta && pastaCount >= R.maxPastaPerWeek) continue;
    if (r._isRice && riceCount >= R.maxRicePerWeek) continue;
    if (r._prepTime >= 40 && longMealCount >= R.maxMealsOver40Mins) continue;
    if ((proteinCounts[r._protein] || 0) >= R.maxSameProtein) continue;
    
    selected.push(r);
    if (r._isPasta) pastaCount++;
    if (r._isRice) riceCount++;
    if (r._prepTime >= 40) longMealCount++;
    proteinCounts[r._protein] = (proteinCounts[r._protein] || 0) + 1;
  }
  
  return { selected, proteinCounts, pastaCount, riceCount };
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log('🍽️  Gousto Meal Picker');
  console.log(DRY_RUN ? '  (DRY RUN - no changes will be made)' : '');
  
  // 1. Get auth token
  console.log('\n1. Getting auth token...');
  const token = getToken();
  console.log('   ✅ Got token');
  
  // 2. Verify auth
  const user = api('GET', '/user/current', null, token);
  if (user.status === 'error') throw new Error('Auth failed: ' + user.error);
  const userId = user.result?.data?.user?.auth_user_id || CONFIG.userId;
  const numericUserId = user.result?.data?.user?.id;
  console.log(`   👤 Logged in as ${user.result?.data?.user?.name_first}`);
  
  // 3. Get pending orders
  console.log('\n2. Checking upcoming orders...');
  const ordersResp = api('GET', '/user/current/orders?limit=10&sort_order=desc&state=pending', null, token);
  const orders = ordersResp.result?.data || [];
  
  // Get full details for each order via v2 API
  const orderDetails = [];
  for (const o of orders) {
    const detail = api('GET', `/order/v2/orders/${o.id}`, null, token);
    const comps = detail.data?.relationships?.components?.data || [];
    const recipeCount = comps.filter(c => c.type === 'recipe').length;
    const attrs = detail.data?.attributes || {};
    orderDetails.push({
      id: o.id,
      deliveryDate: attrs.phase === 'open' ? 'open' : '',
      phase: attrs.phase,
      state: attrs.state,
      recipeCount,
      components: comps,
      relationships: detail.data?.relationships,
      attributes: attrs,
      menuId: attrs.menu_id,
      included: detail.included || [],
    });
  }
  
  // 4. Find target week
  console.log('\n3. Finding target week...');
  let targetOrder = null;
  
  if (WEEK_ARG) {
    targetOrder = orderDetails.find(o => o.id === WEEK_ARG);
    if (!targetOrder) {
      console.log(`   ❌ Order ${WEEK_ARG} not found`);
      process.exit(1);
    }
  } else {
    // Find the first order that needs recipes (< 4 recipes, phase is open)
    for (const o of orderDetails) {
      console.log(`   Order ${o.id}: ${o.recipeCount}/4 recipes, phase=${o.phase}`);
      if (o.phase === 'open' && o.recipeCount < 4) {
        targetOrder = o;
        break;
      }
    }
  }
  
  if (!targetOrder) {
    console.log('   ✅ All orders already have recipes chosen!');
    process.exit(0);
  }
  
  const slotsNeeded = 4 - targetOrder.recipeCount;
  console.log(`   🎯 Target: Order ${targetOrder.id} (${targetOrder.recipeCount}/4 recipes, need ${slotsNeeded} more)`);
  
  // 5. Get existing recipe details
  const existingRecipes = targetOrder.included.filter(i => i.type === 'recipe').map(r => ({
    id: r.id,
    name: r.attributes?.name,
    prep_time: r.attributes?.prep_times?.for2,
    calories: r.attributes?.calories,
    dish_types: r.attributes?.dish_types,
    diet_type: r.attributes?.diet_type,
    allergens: r.attributes?.allergens,
  }));
  
  console.log('   Existing recipes:');
  existingRecipes.forEach(r => console.log(`     - ${r.name} (${r.prep_time || '?'} mins)`));
  
  // 6. Get delivery date from the order to fetch the right menu
  // We need to find the delivery date - get it from the delivery day
  const deliveryDayId = targetOrder.relationships?.delivery_day?.data?.id;
  
  // Fetch menu - try with the period from the order
  const periodId = targetOrder.relationships?.period?.data?.id;
  console.log(`\n4. Fetching menu (period ${periodId})...`);
  
  // Get the menu using the correct delivery date
  // First, get subscription to find delivery dates
  const subResp = api('GET', `/subscriptionquery/v1/projected-deliveries/${numericUserId}`, null, token);
  const projectedDeliveries = subResp.data || [];
  
  // Find the delivery matching our order
  let deliveryDate = null;
  for (const d of projectedDeliveries) {
    if (d.attributes?.order_id === targetOrder.id) {
      deliveryDate = d.attributes?.delivery_date;
      break;
    }
  }
  
  // If we can't find it from projected deliveries, try the day slot
  if (!deliveryDate) {
    const daySlotId = targetOrder.relationships?.delivery_day?.data?.id;
    // Try fetching all active periods
    const periodsResp = api('GET', '/menu/v1/active-periods', null, token);
    // Use the order's menu_active_from to derive the date
    const menuActiveFrom = targetOrder.attributes?.menu_active_from;
    if (menuActiveFrom) {
      // Delivery is usually the Monday of that week
      deliveryDate = menuActiveFrom.split('T')[0];
    }
  }
  
  if (!deliveryDate) {
    console.log('   ⚠️  Could not determine delivery date, trying without...');
  }
  
  const menuParams = new URLSearchParams({
    include_core_recipe_id: 'true',
    include_core_menu_id: 'true',
    num_portions: '2',
    'option_types': 'none',
    user_id: userId,
  });
  if (deliveryDate) menuParams.set('delivery_date', deliveryDate);
  
  const menuResp = api('GET', `/menu/v3/menus?${menuParams}`, null, token);
  const menuRecipes = menuResp.recipes || {};
  const recipeList = Object.entries(menuRecipes).map(([id, r]) => ({ ...r, id }));
  console.log(`   📋 ${recipeList.length} recipes available`);
  
  // 7. Select meals
  console.log('\n5. Selecting meals...');
  const { selected, proteinCounts, pastaCount, riceCount } = selectMeals(recipeList, existingRecipes);
  
  if (selected.length === 0) {
    console.log('   ❌ Could not find suitable recipes!');
    process.exit(1);
  }
  
  console.log(`   Selected ${selected.length} recipes:`);
  selected.forEach(r => {
    const prepTime = r._prepTime || r.prep_time || '?';
    const kcal = r.nutritional_information?.per_portion?.energy_kcal || '?';
    console.log(`     🍽️  ${r.name} | ${prepTime} mins | ${kcal} kcal | ${r._protein} | score: ${r._score}`);
  });
  
  console.log(`   Protein mix: ${JSON.stringify(proteinCounts)}`);
  console.log(`   Pasta dishes: ${pastaCount}, Rice dishes: ${riceCount}`);
  
  // 8. Update order
  if (DRY_RUN) {
    console.log('\n6. DRY RUN - skipping order update');
  } else {
    console.log('\n6. Updating order...');
    
    // Build components: existing + new
    const existingComponents = targetOrder.components;
    const newComponents = selected.map(r => ({
      id: r.id,
      type: 'recipe',
      meta: { portion_for: 2 }
    }));
    const allComponents = [...existingComponents, ...newComponents];
    
    const payload = {
      data: {
        type: 'order',
        id: targetOrder.id,
        attributes: { menu_id: targetOrder.menuId || menuResp.core_id?.toString() || '' },
        relationships: {
          components: { data: allComponents },
          shipping_address: targetOrder.relationships.shipping_address,
          delivery_slot: {
            data: {
              ...targetOrder.relationships.delivery_slot.data,
              meta: targetOrder.relationships.delivery_slot.data.meta || {}
            }
          },
          day_slot_lead_time: {
            data: {
              ...targetOrder.relationships.day_slot_lead_time.data,
              meta: targetOrder.relationships.day_slot_lead_time.data.meta || {}
            }
          },
          delivery_day: {
            data: {
              ...targetOrder.relationships.delivery_day.data,
              meta: targetOrder.relationships.delivery_day.data.meta || {}
            }
          },
          delivery_tariff: targetOrder.relationships.delivery_tariff,
        }
      }
    };
    
    const updateResp = api('PUT', `/order/v2/orders/${targetOrder.id}`, payload, token);
    
    if (updateResp.errors) {
      console.error('   ❌ Failed:', JSON.stringify(updateResp.errors));
      process.exit(1);
    }
    
    const finalComps = updateResp.data?.relationships?.components?.data || [];
    const finalRecipes = (updateResp.included || []).filter(i => i.type === 'recipe');
    console.log(`   ✅ Order updated! ${finalComps.length} recipes:`);
    finalRecipes.forEach(r => {
      console.log(`     - ${r.attributes?.name} | ${r.attributes?.prep_times?.for2 || '?'} mins | ${r.attributes?.calories?.for2 || '?'} kcal`);
    });
  }
  
  // 9. Save selections
  const selections = JSON.parse(fs.readFileSync(SELECTIONS_FILE, 'utf8'));
  selections.lastRun = new Date().toISOString();
  const weekKey = deliveryDate || targetOrder.id;
  selections.selections = selections.selections || {};
  selections.selections[weekKey] = {
    meals: selected.map(r => ({
      name: r.name,
      id: r.id,
      prepTime: r._prepTime,
      kcal: r.nutritional_information?.per_portion?.energy_kcal,
      protein: r._protein,
    })),
    selectedAt: new Date().toISOString(),
    orderId: targetOrder.id,
    dryRun: DRY_RUN,
  };
  fs.writeFileSync(SELECTIONS_FILE, JSON.stringify(selections, null, 2));
  console.log('\n✅ Done!');
  
  // Output summary for the agent
  return {
    orderId: targetOrder.id,
    deliveryDate,
    selected: selected.map(r => ({ name: r.name, prepTime: r._prepTime, kcal: r.nutritional_information?.per_portion?.energy_kcal, protein: r._protein })),
    existingRecipes: existingRecipes.map(r => ({ name: r.name })),
  };
}

main().then(result => {
  if (result) console.log('\n📊 Summary:', JSON.stringify(result, null, 2));
}).catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
