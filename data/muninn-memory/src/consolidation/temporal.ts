/**
 * Temporal Reasoning Module
 * 
 * Tracks how facts change over time and answers temporal queries:
 * - "When did X change?"
 * - "How did X evolve over sessions?"
 * - "What was X's value at time Y?"
 */

import MemoryStore, { Memory } from '../storage/index.js';

export interface TemporalEvent {
  timestamp: string;
  memory: Memory;
  change_type: 'created' | 'updated' | 'contradicted' | 'reinforced';
  value: string;
  previous_value?: string;
}

export interface TemporalTimeline {
  entity: string;
  attribute: string;
  events: TemporalEvent[];
  current_value: string;
  trend: 'increasing' | 'decreasing' | 'stable' | 'volatile';
}

export interface TemporalQueryResult {
  question: string;
  timeline: TemporalTimeline | null;
  answer: string;
  confidence: number;
}

// Attributes that commonly change over time
const temporalAttributes = [
  'revenue', 'target', 'priority', 'focus', 'status',
  'progress', 'price', 'value', 'count', 'stage'
];

// Entities to track (extracted from content)
const trackedEntityPatterns = [
  /Elev8Advisory/gi,
  /BrandForge/gi,
  /Muninn/gi,
  /OpenClaw/gi,
  /Phillip/gi,
  /KakāpōHiko/gi,
  /Sammy/gi,
  /Charlie/gi,
  /Donna/gi,
  /\$[\d,]+k?(?:\/mo|\/month)?/gi
];

/**
 * Extract temporal events from a memory
 */
export function extractTemporalEvents(memory: Memory): TemporalEvent[] {
  const events: TemporalEvent[] = [];
  const content = memory.content;

  // Extract numeric values with context
  const numericPattern = /\$?(\d+[,\d]*)\s*(k|thousand|m|million)?\s*(?:\/mo|\/month|revenue|target|price)?/gi;
  const matches = [...content.matchAll(numericPattern)];

  for (const match of matches) {
    const value = match[0];
    const context = content.slice(Math.max(0, match.index! - 30), match.index! + match[0].length + 30);
    
    // Determine attribute
    let attribute = 'value';
    if (context.toLowerCase().includes('revenue')) attribute = 'revenue';
    else if (context.toLowerCase().includes('target')) attribute = 'target';
    else if (context.toLowerCase().includes('price')) attribute = 'price';

    // Extract related entity
    let entity = 'unknown';
    for (const pattern of trackedEntityPatterns) {
      const entityMatch = content.match(pattern);
      if (entityMatch) {
        entity = entityMatch[0];
        break;
      }
    }

    events.push({
      timestamp: memory.created_at,
      memory,
      change_type: 'created',
      value,
      previous_value: undefined
    });
  }

  // Extract priority changes
  const priorityPattern = /(first|primary|priority|top|main|focus)/i;
  const secondaryPattern = /(second|secondary|backseat|lower)/i;

  if (priorityPattern.test(content) || secondaryPattern.test(content)) {
    const entityMatch = trackedEntityPatterns.find(p => content.match(p));
    if (entityMatch) {
      const entity = content.match(entityMatch)?.[0] || 'unknown';
      events.push({
        timestamp: memory.created_at,
        memory,
        change_type: 'updated',
        value: priorityPattern.test(content) ? 'priority' : 'secondary',
        previous_value: undefined
      });
    }
  }

  return events;
}

/**
 * Build a timeline for a specific entity and attribute
 */
export async function buildTimeline(
  store: MemoryStore,
  entity: string,
  attribute: string
): Promise<TemporalTimeline | null> {
  // Retrieve memories mentioning the entity
  const memories = await store.recall(entity, { limit: 50 });
  
  if (memories.length === 0) return null;

  // Extract temporal events
  const events: TemporalEvent[] = [];
  
  for (const memory of memories) {
    const memEvents = extractTemporalEvents(memory);
    
    // Filter to relevant attribute
    const relevant = memEvents.filter(e => {
      const context = memory.content.toLowerCase();
      return context.includes(attribute.toLowerCase());
    });
    
    events.push(...relevant);
  }

  // Sort by timestamp
  events.sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  // Detect changes between events
  for (let i = 1; i < events.length; i++) {
    const prev = events[i - 1];
    const curr = events[i];
    
    if (prev.value !== curr.value) {
      curr.change_type = 'updated';
      curr.previous_value = prev.value;
    } else {
      curr.change_type = 'reinforced';
      curr.previous_value = prev.value;
    }
  }

  // Calculate trend
  const trend = calculateTrend(events);

  return {
    entity,
    attribute,
    events,
    current_value: events.length > 0 ? events[events.length - 1].value : '',
    trend
  };
}

/**
 * Calculate trend from temporal events
 */
function calculateTrend(events: TemporalEvent[]): 'increasing' | 'decreasing' | 'stable' | 'volatile' {
  if (events.length < 2) return 'stable';

  // Extract numeric values
  const values: number[] = [];
  for (const event of events) {
    const numMatch = event.value.match(/\$?(\d+[,\d]*)/);
    if (numMatch) {
      values.push(parseInt(numMatch[1].replace(/,/g, '')));
    }
  }

  if (values.length < 2) {
    // Check for priority changes
    const priorities = events.map(e => e.value);
    if (priorities.some(p => p === 'priority') && priorities.some(p => p === 'secondary')) {
      return 'volatile';
    }
    return 'stable';
  }

  // Count direction changes
  let increases = 0;
  let decreases = 0;
  
  for (let i = 1; i < values.length; i++) {
    if (values[i] > values[i - 1]) increases++;
    else if (values[i] < values[i - 1]) decreases++;
  }

  if (increases > 0 && decreases === 0) return 'increasing';
  if (decreases > 0 && increases === 0) return 'decreasing';
  if (increases > 0 && decreases > 0) return 'volatile';
  return 'stable';
}

/**
 * Answer a temporal query
 */
export async function answerTemporalQuery(
  store: MemoryStore,
  query: string
): Promise<TemporalQueryResult> {
  // Detect what's being asked
  const entityMatch = trackedEntityPatterns.find(p => query.match(p));
  
  if (!entityMatch) {
    return {
      question: query,
      timeline: null,
      answer: 'Could not identify entity in query',
      confidence: 0
    };
  }

  const entity = query.match(entityMatch)?.[0] || '';

  // Detect what attribute is being asked about
  let attribute = 'value';
  for (const attr of temporalAttributes) {
    if (query.toLowerCase().includes(attr)) {
      attribute = attr;
      break;
    }
  }

  // Detect query type
  const askingChange = /how.*change|evolve|over time|when|history/i.test(query);
  const askingCurrent = /current|now|today|latest/i.test(query);

  // Build timeline
  const timeline = await buildTimeline(store, entity, attribute);

  if (!timeline || timeline.events.length === 0) {
    return {
      question: query,
      timeline: null,
      answer: `No temporal data found for ${entity}`,
      confidence: 0
    };
  }

  // Build answer
  let answer = '';

  if (askingChange) {
    // Build change history
    const changes = timeline.events
      .filter(e => e.change_type === 'updated' || e.change_type === 'created')
      .map(e => {
        const date = new Date(e.timestamp).toLocaleDateString();
        if (e.previous_value && e.previous_value !== e.value) {
          return `${date}: changed from ${e.previous_value} to ${e.value}`;
        }
        return `${date}: ${e.value}`;
      });

    answer = `${entity} ${attribute} history:\n${changes.join('\n')}`;
  } else if (askingCurrent) {
    answer = `Current ${entity} ${attribute}: ${timeline.current_value} (as of ${new Date(timeline.events[timeline.events.length - 1].timestamp).toLocaleDateString()})`;
  } else {
    // General summary
    const changes = timeline.events.filter(e => e.change_type === 'updated').length;
    answer = `${entity} ${attribute} has ${timeline.trend} over time. Current: ${timeline.current_value}. ${changes} changes recorded.`;
  }

  return {
    question: query,
    timeline,
    answer,
    confidence: timeline.events.length > 3 ? 0.9 : 0.6
  };
}

/**
 * Detect temporal relationships between memories
 */
export function detectTemporalRelationships(memories: Memory[]): Map<string, Memory[]> {
  const relationships = new Map<string, Memory[]>();

  // Group by entity
  for (const memory of memories) {
    for (const entity of memory.entities) {
      if (!relationships.has(entity)) {
        relationships.set(entity, []);
      }
      relationships.get(entity)!.push(memory);
    }
  }

  // Sort each group by time
  for (const [entity, mems] of relationships) {
    mems.sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
  }

  return relationships;
}