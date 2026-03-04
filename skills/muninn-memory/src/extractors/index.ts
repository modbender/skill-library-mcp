/**
 * Content Extractors
 * Extract structured data from raw conversation/content
 * 
 * Uses enhanced keyword router for classification (95%+ accuracy)
 */

// Re-export router
export { routeContent, routeWithKeywords, RoutingResult } from './router.js';

// Re-export normalization
export {
  normalizeEntities,
  extractWithNormalization,
  createAliasStore,
  type NormalizedEntity,
  type EntityAliasStore
} from './normalize.js';

// Import entity extraction
import { extractEntities as extractEntitiesImpl, Entity } from './entities.js';

export interface ExtractionResult {
  type: 'episodic' | 'semantic' | 'procedural';
  title?: string;
  summary?: string;
  entities: string[];
  topics: string[];
  salience: number;
}

// Extract episodic memory data (events, conversations)
export function extractEpisodic(content: string): ExtractionResult {
  const entities: string[] = [];
  const topics: string[] = [];
  
  // Extract potential entities (capitalized words, excluding common words)
  const capitalized = content.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*/g) || [];
  const commonWords = ['I', 'The', 'A', 'An', 'This', 'That', 'It', 'We', 'They', 'You', 'He', 'She', 'But', 'However', 'When', 'Where', 'Why', 'How', 'What'];
  const filtered = capitalized.filter(w => !commonWords.includes(w) && w.length > 2);
  entities.push(...filtered.slice(0, 5));
  
  // Extract topics (keywords)
  const topicKeywords: Record<string, string[]> = {
    'programming': ['code', 'function', 'api', 'bug', 'feature', 'deploy', 'build'],
    'business': ['customer', 'revenue', 'sales', 'meeting', 'partner', 'deal'],
    'personal': ['family', 'friend', 'home', 'health', 'fitness', 'hobby'],
    'ai': ['model', 'llm', 'agent', 'memory', 'embedding', 'training'],
    'project': ['task', 'milestone', 'deadline', 'sprint', 'release']
  };
  
  const lowerContent = content.toLowerCase();
  for (const [topic, keywords] of Object.entries(topicKeywords)) {
    if (keywords.some(k => lowerContent.includes(k))) {
      topics.push(topic);
    }
  }
  
  // Generate summary (first 100 chars)
  const summary = content.length > 100 ? content.slice(0, 100) + '...' : content;
  
  return {
    type: 'episodic',
    summary,
    entities,
    topics,
    salience: 0.7
  };
}

// Extract semantic memory data (facts, preferences)
export function extractSemantic(content: string): ExtractionResult {
  const entities: string[] = [];
  const topics: string[] = [];
  
  // Extract potential entities
  const capitalized = content.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*/g) || [];
  const commonWords = ['I', 'The', 'A', 'An', 'This', 'That', 'It', 'We', 'They', 'You', 'He', 'She', 'But', 'However', 'When', 'Where', 'Why', 'How', 'What', 'Prefer', 'Like', 'Use', 'Am'];
  const filtered = capitalized.filter(w => !commonWords.includes(w) && w.length > 2);
  entities.push(...filtered.slice(0, 5));
  
  // Preference detection
  const isPreference = /prefer|like|love|hate|dislike|want|need|always|never|usually/i.test(content);
  if (isPreference) {
    topics.push('preference');
  }
  
  // Fact detection
  const isFact = /is|are|was|were|have|has|had/i.test(content);
  if (isFact) {
    topics.push('fact');
  }
  
  // Skill detection
  const isSkill = /know|can|capable|expert|proficient|experience/i.test(content);
  if (isSkill) {
    topics.push('skill');
  }
  
  return {
    type: 'semantic',
    entities,
    topics,
    salience: isPreference ? 0.9 : 0.6
  };
}

// Extract procedural memory data (workflows, processes)
export function extractProcedural(content: string): { title?: string; steps: string[] } {
  // Try to extract steps from content
  const steps: string[] = [];
  
  // Numbered steps
  const numberedSteps = content.match(/^\d+[.)]\s*.+$/gm);
  if (numberedSteps) {
    steps.push(...numberedSteps.map(s => s.replace(/^\d+[.)]\s*/, '')));
  }
  
  // Bullet points
  const bulletSteps = content.match(/^[-*•]\s*.+$/gm);
  if (bulletSteps) {
    steps.push(...bulletSteps.map(s => s.replace(/^[-*•]\s*/, '')));
  }
  
  // Try to extract title
  const lines = content.split('\n');
  const title = lines[0]?.length < 100 ? lines[0] : 'Untitled Procedure';
  
  return { title, steps };
}

// Main extraction function
export async function extract(
  content: string,
  context?: string
): Promise<ExtractionResult> {
  // Import router dynamically to avoid circular deps
  const { routeContent } = await import('./router.js');
  const routing = await routeContent(content, context);
  
  // Extract entities using the imported function
  const entityResults = extractEntitiesImpl(content);
  
  if (routing.episodic) {
    return {
      ...extractEpisodic(content),
      entities: entityResults.map((e: Entity) => e.text),
    };
  } else if (routing.procedural) {
    const proc = extractProcedural(content);
    return {
      type: 'procedural',
      title: proc.title,
      entities: entityResults.map((e: Entity) => e.text),
      topics: ['workflow', 'process'],
      salience: 0.8
    };
  } else {
    return {
      ...extractSemantic(content),
      entities: entityResults.map((e: Entity) => e.text),
    };
  }
}

// Re-export entity extraction function
export { extractEntitiesImpl as extractEntities };