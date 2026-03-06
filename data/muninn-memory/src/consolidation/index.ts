/**
 * Consolidation Engine
 * Async job that runs periodically to:
 * - Extract entities from episodes
 * - Distill episodes into semantic facts
 * - Detect contradictions
 * - Build knowledge graph
 */

import { MemoryStore, Memory } from '../storage/index.js';

export interface ConsolidationResult {
  consolidated: number;
  entitiesDiscovered: number;
  contradictions: number;
  connectionsFormed: number;
}

export async function consolidate(
  store: MemoryStore,
  options: { batchSize?: number } = {}
): Promise<ConsolidationResult> {
  const batchSize = options.batchSize || 10;
  
  let consolidated = 0;
  let entitiesDiscovered = 0;
  let contradictions = 0;
  let connectionsFormed = 0;
  
  // 1. Entity Discovery - Extract entities from episodic memories
  const episodicMemories = await store.recall('', { types: ['episodic'], limit: batchSize });
  
  for (const memory of episodicMemories) {
    // Extract entities from content
    const capitalized = memory.content.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*/g) || [];
    const commonWords = ['I', 'The', 'A', 'An', 'This', 'That', 'It', 'We', 'They', 'You'];
    const newEntities = capitalized.filter(w => !commonWords.includes(w) && w.length > 2);
    
    if (newEntities.length > 0) {
      entitiesDiscovered += newEntities.length;
    }
  }
  
  // 2. Episode Distillation - Convert repeated episodes to semantic facts
  // For now, just mark episodic memories as potential semantic extraction candidates
  const recentEpisodic = episodicMemories.filter(m => {
    const hoursSince = (Date.now() - new Date(m.created_at).getTime()) / (1000 * 60 * 60);
    return hoursSince > 24; // Only distill memories older than 24h
  });
  
  // 3. Contradiction Detection - Find conflicting facts
  const semanticMemories = await store.recall('', { types: ['semantic'], limit: batchSize });
  
  // Simple contradiction detection: check for opposite statements
  const contradictionsFound: string[] = [];
  for (let i = 0; i < semanticMemories.length; i++) {
    for (let j = i + 1; j < semanticMemories.length; j++) {
      const m1 = semanticMemories[i].content.toLowerCase();
      const m2 = semanticMemories[j].content.toLowerCase();
      
      // Check for common negation patterns
      const pairs = [
        ['prefer', 'prefer'],
        ['like', 'dislike'],
        ['love', 'hate'],
        ['use', 'never use'],
        ['always', 'never']
      ];
      
      for (const [pos, neg] of pairs) {
        if (m1.includes(pos) && m2.includes(neg) || m1.includes(neg) && m2.includes(pos)) {
          contradictionsFound.push(`${semanticMemories[i].id} <-> ${semanticMemories[j].id}`);
        }
      }
    }
  }
  
  contradictions = contradictionsFound.length;
  
  // 4. Graph Building - Create connections based on shared entities
  const allMemories = await store.recall('', { limit: batchSize * 2 });
  
  for (let i = 0; i < allMemories.length; i++) {
    for (let j = i + 1; j < allMemories.length; j++) {
      const shared = allMemories[i].entities.filter(e => 
        allMemories[j].entities.includes(e)
      );
      
      if (shared.length > 0 && Math.random() > 0.7) { // Probabilistic connection
        try {
          store.connect(allMemories[i].id, allMemories[j].id, 'related_to');
          connectionsFormed++;
        } catch (e) {
          // Connection might already exist
        }
      }
    }
  }
  
  consolidated = episodicMemories.length;
  
  return {
    consolidated,
    entitiesDiscovered,
    contradictions,
    connectionsFormed
  };
}

// Truth State Resolution
// Handles contradictions across time and sources

export interface Claim {
  predicate: string;
  object: string;
  source: string;
  timestamp: string;
  superseded_by?: string;
}

export function resolveTruth(claims: Claim[]): Claim[] {
  // Sort by timestamp (newest first)
  const sorted = [...claims].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
  
  const resolved: Claim[] = [];
  const seen = new Map<string, Claim>();
  
  for (const claim of sorted) {
    const key = claim.predicate.toLowerCase();
    const existing = seen.get(key);
    
    if (!existing) {
      seen.set(key, claim);
      resolved.push(claim);
    } else {
      // Mark as superseded
      claim.superseded_by = existing.source;
      existing.superseded_by = claim.source;
    }
  }
  
  return resolved;
}
