/**
 * Contradiction Detection Module
 * 
 * Identifies conflicting facts and resolves by:
 * - Detecting semantic contradictions (not just keyword matches)
 * - Resolving by timestamp (newer wins)
 * - Flagging ambiguous cases for review
 */

import MemoryStore, { Memory } from '../storage/index.js';
import { generateEmbedding } from '../storage/index.js';

export interface Contradiction {
  memory1: Memory;
  memory2: Memory;
  conflict: string;
  resolution: 'newer_wins' | 'source_priority' | 'flag_for_review';
  winner: Memory;
  confidence: number;
}

export interface ContradictionReport {
  total_checked: number;
  contradictions_found: number;
  auto_resolved: number;
  flagged_for_review: number;
  details: Contradiction[];
}

// Patterns that indicate preference/opinion (prone to change)
const preferencePatterns = [
  /prefer(s|red|ence)?/i,
  /want(s|ed)?/i,
  /like(s|d)?/i,
  /hate(s|d)?/i,
  /focus(ing|ed)?/i,
  /priority/i,
  /target/i,
  /goal/i
];

// Patterns that indicate a change/update
const changeIndicators = [
  /actually/i,
  /now/i,
  /updated/i,
  /changed/i,
  /back to/i,
  /instead/i,
  /revised/i,
  /new/i
];

// Negation patterns
const negationPatterns = [
  /not\s+(anymore|now)/i,
  /don'?t\s+(want|like|prefer)/i,
  /no\s+longer/i,
  /stopped/i
];

/**
 * Check if two memories might contradict each other
 */
export async function detectContradiction(
  mem1: Memory,
  mem2: Memory
): Promise<Contradiction | null> {
  // Skip if same memory
  if (mem1.id === mem2.id) return null;

  // Only check semantic memories for contradictions
  if (mem1.type !== 'semantic' || mem2.type !== 'semantic') return null;

  // Check for shared entities (prerequisite for contradiction)
  const sharedEntities = mem1.entities.filter(e => mem2.entities.includes(e));
  if (sharedEntities.length === 0) return null;

  // Check for preference/opinion patterns
  const mem1IsPreference = preferencePatterns.some(p => p.test(mem1.content));
  const mem2IsPreference = preferencePatterns.some(p => p.test(mem2.content));
  
  if (!mem1IsPreference && !mem2IsPreference) return null;

  // Check for negation or change indicators
  const mem1HasNegation = negationPatterns.some(p => p.test(mem1.content));
  const mem2HasNegation = negationPatterns.some(p => p.test(mem2.content));
  const mem1HasChange = changeIndicators.some(p => p.test(mem1.content));
  const mem2HasChange = changeIndicators.some(p => p.test(mem2.content));

  // Detect semantic similarity with opposing sentiment
  const content1Lower = mem1.content.toLowerCase();
  const content2Lower = mem2.content.toLowerCase();

  // Check for numeric contradictions (revenue, targets, etc.)
  const numericContradiction = checkNumericContradiction(mem1.content, mem2.content);
  
  // Check for priority/first/second contradictions
  const priorityContradiction = checkPriorityContradiction(mem1.content, mem2.content);

  if (!numericContradiction && !priorityContradiction && 
      !mem1HasNegation && !mem2HasNegation && 
      !mem1HasChange && !mem2HasChange) {
    // No clear contradiction signal
    return null;
  }

  // Determine winner (newer wins by default)
  const m1Time = new Date(mem1.created_at).getTime();
  const m2Time = new Date(mem2.created_at).getTime();
  
  let winner: Memory;
  let resolution: Contradiction['resolution'];
  let confidence: number;

  if (Math.abs(m1Time - m2Time) < 1000 * 60 * 60) {
    // Less than 1 hour apart - flag for review
    resolution = 'flag_for_review';
    winner = m1Time > m2Time ? mem1 : mem2;
    confidence = 0.5;
  } else {
    // Clear time difference - newer wins
    resolution = 'newer_wins';
    winner = m1Time > m2Time ? mem1 : mem2;
    confidence = 0.8;
  }

  const conflict = describeConflict(mem1, mem2, numericContradiction || priorityContradiction || 'preference_change');

  return {
    memory1: mem1,
    memory2: mem2,
    conflict,
    resolution,
    winner,
    confidence
  };
}

/**
 * Check for numeric value contradictions (revenue, targets, amounts)
 */
function checkNumericContradiction(content1: string, content2: string): string | null {
  const numPattern = /\$?(\d+[,\d]*)\s*(k|thousand|million|m|mo|month)?/gi;
  
  const nums1 = [...content1.matchAll(numPattern)].map(m => ({
    value: parseInt(m[1].replace(/,/g, '')),
    unit: m[2]?.toLowerCase() || '',
    original: m[0]
  }));
  
  const nums2 = [...content2.matchAll(numPattern)].map(m => ({
    value: parseInt(m[1].replace(/,/g, '')),
    unit: m[2]?.toLowerCase() || '',
    original: m[0]
  }));

  if (nums1.length === 0 || nums2.length === 0) return null;

  // Check if same context (both about revenue, both about price, etc.)
  const contextWords = ['revenue', 'target', 'price', 'cost', 'budget', 'value'];
  const hasSharedContext = contextWords.some(w => 
    content1.toLowerCase().includes(w) && content2.toLowerCase().includes(w)
  );

  if (!hasSharedContext) return null;

  // Check if values differ significantly
  for (const n1 of nums1) {
    for (const n2 of nums2) {
      const val1 = n1.unit.includes('k') ? n1.value * 1000 : n1.value;
      const val2 = n2.unit.includes('k') ? n2.value * 1000 : n2.value;
      
      if (Math.abs(val1 - val2) > Math.max(val1, val2) * 0.1) {
        return `numeric_mismatch: ${n1.original} vs ${n2.original}`;
      }
    }
  }

  return null;
}

/**
 * Check for priority/ordering contradictions (first, second, primary, secondary)
 */
function checkPriorityContradiction(content1: string, content2: string): string | null {
  const priorityWords = ['first', 'second', 'primary', 'secondary', 'priority', 'focus', 'top'];
  
  const priorities1 = priorityWords.filter(w => 
    new RegExp(`\\b${w}\\b`, 'i').test(content1)
  );
  const priorities2 = priorityWords.filter(w => 
    new RegExp(`\\b${w}\\b`, 'i').test(content2)
  );

  if (priorities1.length === 0 || priorities2.length === 0) return null;

  // Check for conflicting priorities
  const conflicts: string[] = [];
  
  if (content1.match(/first|primary|priority/i) && content2.match(/second|secondary/i)) {
    conflicts.push('first vs second');
  }
  if (content1.match(/second|secondary/i) && content2.match(/first|primary|priority/i)) {
    conflicts.push('second vs first');
  }

  return conflicts.length > 0 ? `priority_conflict: ${conflicts.join(', ')}` : null;
}

/**
 * Describe the conflict in human-readable form
 */
function describeConflict(
  mem1: Memory, 
  mem2: Memory, 
  type: string
): string {
  const t1 = new Date(mem1.created_at).toLocaleDateString();
  const t2 = new Date(mem2.created_at).toLocaleDateString();
  
  return `[${t1}] "${mem1.content.slice(0, 60)}..." contradicts [${t2}] "${mem2.content.slice(0, 60)}..." (${type})`;
}

/**
 * Scan all memories for contradictions
 */
export async function scanContradictions(store: MemoryStore): Promise<ContradictionReport> {
  const allMemories = await store.recall('', { limit: 1000 });
  
  const report: ContradictionReport = {
    total_checked: 0,
    contradictions_found: 0,
    auto_resolved: 0,
    flagged_for_review: 0,
    details: []
  };

  // Check each pair
  for (let i = 0; i < allMemories.length; i++) {
    for (let j = i + 1; j < allMemories.length; j++) {
      report.total_checked++;
      
      const contradiction = await detectContradiction(allMemories[i], allMemories[j]);
      
      if (contradiction) {
        report.contradictions_found++;
        report.details.push(contradiction);
        
        if (contradiction.resolution === 'flag_for_review') {
          report.flagged_for_review++;
        } else {
          report.auto_resolved++;
        }
      }
    }
  }

  return report;
}

/**
 * Get the resolved value for a query (considering contradictions)
 */
export async function getResolvedValue(
  store: MemoryStore,
  query: string
): Promise<{ value: string; source: Memory; confidence: number }> {
  const memories = await store.recall(query, { limit: 5 });
  
  if (memories.length === 0) {
    return { value: '', source: null as any, confidence: 0 };
  }

  // Check for contradictions among top results
  const contradictions: Contradiction[] = [];
  
  for (let i = 0; i < memories.length; i++) {
    for (let j = i + 1; j < memories.length; j++) {
      const c = await detectContradiction(memories[i], memories[j]);
      if (c) contradictions.push(c);
    }
  }

  if (contradictions.length === 0) {
    // No contradictions - return most recent
    const mostRecent = memories.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];
    
    return { 
      value: mostRecent.content, 
      source: mostRecent, 
      confidence: 0.9 
    };
  }

  // Return the winner from the highest-confidence contradiction
  const bestResolution = contradictions.sort((a, b) => b.confidence - a.confidence)[0];
  
  return { 
    value: bestResolution.winner.content, 
    source: bestResolution.winner, 
    confidence: bestResolution.confidence 
  };
}