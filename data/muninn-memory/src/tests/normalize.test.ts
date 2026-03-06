/**
 * Tests for Entity Normalization
 * 
 * Tests LLM-based entity normalization that resolves pronouns to names,
 * expands abbreviations, normalizes dates, and stores aliases for retrieval.
 */

import { normalizeEntities, createAliasStore } from '../extractors/normalize.js';
import type { Entity } from '../extractors/entities.js';

// Mock LLM response generator for testing
const createMockLLM = (responses: Record<string, string>) => {
  return async (prompt: string): Promise<string> => {
    for (const [key, response] of Object.entries(responses)) {
      if (prompt.includes(key)) {
        return response;
      }
    }
    return '[]';
  };
};

// Test runner
async function runNormalizationTests() {
  console.log('🧪 Running Entity Normalization Tests\n');
  console.log('='.repeat(60));
  
  let passed = 0;
  let failed = 0;
  
  // Test 1: Resolves pronouns to canonical names
  {
    console.log('\n📝 Test: Resolves pronouns to canonical names');
    try {
      const mockResponse = JSON.stringify([
        { original: 'He', canonical: 'Phillip', type: 'person', confidence: 0.9 }
      ]);
      
      const mockLLM = createMockLLM({
        'Phillip worked on Muninn': mockResponse
      });
      
      const text = "Phillip worked on Muninn. He built the router.";
      const result = await normalizeEntities(text, undefined, mockLLM);
      
      const heEntity = result.find(e => e.original === 'He');
      if (heEntity && heEntity.canonical === 'Phillip') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: He not resolved to Phillip');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 2: Expands abbreviations
  {
    console.log('\n📝 Test: Expands abbreviations');
    try {
      const mockResponse = JSON.stringify([
        { original: 'NYC', canonical: 'New York City', type: 'location', confidence: 0.95 }
      ]);
      
      const mockLLM = createMockLLM({
        'Working from NYC': mockResponse
      });
      
      const text = "Working from NYC next week.";
      const result = await normalizeEntities(text, undefined, mockLLM);
      
      const nycEntity = result.find(e => e.original === 'NYC');
      if (nycEntity && nycEntity.canonical === 'New York City') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: NYC not expanded');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 3: Stores aliases for retrieval
  {
    console.log('\n📝 Test: Stores aliases for retrieval');
    try {
      const mockResponse = JSON.stringify([
        { original: 'Sammy Clemens', canonical: 'Sammy Clemens', type: 'person', confidence: 0.95 },
        { original: 'Sammy', canonical: 'Sammy Clemens', type: 'person', confidence: 0.9 }
      ]);
      
      const mockLLM = createMockLLM({
        'Sammy Clemens drafted': mockResponse
      });
      
      const text = "Sammy Clemens drafted the post. Sammy reviewed it.";
      const result = await normalizeEntities(text, undefined, mockLLM);
      
      const sammyRefs = result.filter(e => e.canonical === 'Sammy Clemens');
      if (sammyRefs.length >= 1 && sammyRefs[0].aliases.includes('Sammy Clemens')) {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Aliases not stored');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 4: Falls back to original entities on LLM failure
  {
    console.log('\n📝 Test: Falls back to original entities on LLM failure');
    try {
      const failingLLM = async () => { throw new Error('LLM unavailable'); };
      
      const text = "Phillip worked on Muninn.";
      const existingEntities: Entity[] = [
        { text: 'Phillip', type: 'person', confidence: 0.95, context: 'Phillip worked' },
        { text: 'Muninn', type: 'project', confidence: 0.95, context: 'worked on Muninn' }
      ];
      
      const result = await normalizeEntities(text, existingEntities, failingLLM);
      
      if (result.length === 2 && result[0].canonical === 'Phillip' && result[1].canonical === 'Muninn') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Fallback not working');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 5: Alias store can find canonical forms
  {
    console.log('\n📝 Test: Alias store can find canonical forms');
    try {
      const store = createAliasStore();
      
      store.addAlias('Sammy Clemens', 'Sammy');
      store.addAlias('Sammy Clemens', 'Sam');
      
      const found1 = store.findCanonical('Sammy');
      const found2 = store.findCanonical('sam');
      const aliases = store.getAliases('Sammy Clemens');
      
      // Check case-insensitively
      const hasSammy = aliases.some(a => a.toLowerCase() === 'sammy');
      const hasSam = aliases.some(a => a.toLowerCase() === 'sam');
      
      if (found1 === 'Sammy Clemens' && found2 === 'Sammy Clemens' && hasSammy && hasSam) {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Alias store not working correctly');
        console.log('   found1:', found1, 'found2:', found2, 'aliases:', aliases);
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 6: Alias store returns null for unknown aliases
  {
    console.log('\n📝 Test: Alias store returns null for unknown aliases');
    try {
      const store = createAliasStore();
      
      store.addAlias('Phillip', 'Phil');
      
      const found = store.findCanonical('Unknown');
      
      if (found === null) {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Should have returned null');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 7: Rule-based abbreviation expansion works without LLM
  {
    console.log('\n📝 Test: Rule-based abbreviation expansion (no LLM)');
    try {
      const text = "Working from NYC next week.";
      const result = await normalizeEntities(text);
      
      const nycEntity = result.find(e => e.original === 'NYC');
      if (nycEntity && nycEntity.canonical === 'New York City') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Rule-based abbreviation not working');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 8: Rule-based date normalization works without LLM
  {
    console.log('\n📝 Test: Rule-based date normalization (no LLM)');
    try {
      const text = "Meeting scheduled for tomorrow.";
      const result = await normalizeEntities(text);
      
      const tomorrowEntity = result.find(e => e.original === 'tomorrow');
      if (tomorrowEntity && tomorrowEntity.canonical === '2026-02-25') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Rule-based date not working');
        console.log('   Got:', tomorrowEntity?.canonical);
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 9: Multiple abbreviation expansions
  {
    console.log('\n📝 Test: Multiple abbreviation expansions');
    try {
      const text = "QLD and NSW are both in Australia.";
      const result = await normalizeEntities(text);
      
      const qld = result.find(e => e.original === 'QLD');
      const nsw = result.find(e => e.original === 'NSW');
      
      if (qld?.canonical === 'Queensland' && nsw?.canonical === 'New South Wales') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Multiple abbreviations not working');
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 10: Normalizes UK spelling to canonical with US alias
  {
    console.log('\n📝 Test: Normalizes UK spelling to canonical with US alias');
    try {
      const text = "The colour scheme needs work.";
      const result = await normalizeEntities(text);
      
      const colourEntity = result.find(e => e.original.toLowerCase() === 'colour');
      if (colourEntity && colourEntity.aliases.includes('color') && colourEntity.aliases.includes('colour')) {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Colour entity not normalized with color alias');
        console.log('   Got:', colourEntity?.aliases);
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 11: Normalizes US spelling to canonical with UK alias
  {
    console.log('\n📝 Test: Normalizes US spelling to canonical with UK alias');
    try {
      const text = "We need to organize the files.";
      const result = await normalizeEntities(text);
      
      const organizeEntity = result.find(e => e.original.toLowerCase() === 'organize');
      if (organizeEntity && organizeEntity.aliases.includes('organise') && organizeEntity.aliases.includes('organize')) {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Organize entity not normalized with organise alias');
        console.log('   Got:', organizeEntity?.aliases);
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 12: Retrieval matches both spellings via alias store
  {
    console.log('\n📝 Test: Retrieval matches both spellings via alias store');
    try {
      const store = createAliasStore();
      const text = "The behaviour was unusual.";
      const result = await normalizeEntities(text);
      
      // Add to alias store
      result.forEach(e => {
        e.aliases.forEach(a => store.addAlias(e.canonical, a));
      });
      
      // Should find canonical when searching US spelling
      const foundUS = store.findCanonical('behavior');
      const foundUK = store.findCanonical('behaviour');
      
      if (foundUS === 'behaviour' && foundUK === 'behaviour') {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Alias store not finding canonical');
        console.log('   foundUS:', foundUS, 'foundUK:', foundUK);
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  // Test 13: Multiple spelling variants in same text
  {
    console.log('\n📝 Test: Multiple spelling variants in same text');
    try {
      const text = "The colour was marvelous but the centre needs more analyse.";
      const result = await normalizeEntities(text);
      
      const colour = result.find(e => e.original.toLowerCase() === 'colour');
      const centre = result.find(e => e.original.toLowerCase() === 'centre');
      const analyse = result.find(e => e.original.toLowerCase() === 'analyse');
      
      if (colour?.aliases.includes('color') && centre?.aliases.includes('center') && analyse?.aliases.includes('analyze')) {
        console.log('   ✅ PASS');
        passed++;
      } else {
        console.log('   ❌ FAIL: Multiple variants not all captured');
        console.log('   colour:', colour?.aliases);
        console.log('   centre:', centre?.aliases);
        console.log('   analyse:', analyse?.aliases);
        failed++;
      }
    } catch (err) {
      console.log('   ❌ FAIL:', err);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(60));
  console.log(`\n📊 Results: ${passed}/${passed + failed} passed (${Math.round(passed/(passed + failed)*100)}%)`);
  
  return { passed, failed };
}

// Run tests
runNormalizationTests()
  .then(({ passed, failed }) => {
    process.exit(failed > 0 ? 1 : 0);
  })
  .catch(err => {
    console.error('Test error:', err);
    process.exit(1);
  });
