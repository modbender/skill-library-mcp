/**
 * Entity Extractor
 *
 * Extracts named entities with types from text.
 * Pattern-based approach (no LLM needed for speed).
 *
 * Entity types:
 * - person: Names of people
 * - organization: Companies, teams, groups
 * - project: Named projects, products, apps
 * - technology: Programming languages, frameworks, tools
 * - location: Places, cities, countries
 * - event: Named events, meetings, launches
 * - concept: Abstract ideas, methodologies
 */

export type EntityType = 'person' | 'organization' | 'project' | 'technology' | 'location' | 'event' | 'concept';

export interface Entity {
  text: string;
  type: EntityType;
  confidence: number;  // 0.0 - 1.0
  context: string;     // Surrounding text
}

// ============================================
// KNOWN ENTITIES (Domain Knowledge)
// ============================================

const KNOWN_PEOPLE = [
  // OpenClaw team
  'Phillip', 'Phillip Neho', 'KakāpōHiko', 'KH', 'KakapoHiko',
  'Sammy Clemens', 'Sammy', 'Charlie Babbage', 'Charlie', 'Donna Paulsen', 'Donna', 'Ernie',
  // Common names
  'John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Tom', 'Alex', 'Chris', 'Taylor',
];

const KNOWN_ORGANIZATIONS = [
  'OpenClaw', 'Elev8Advisory',
  'Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'OpenAI', 'Anthropic',
  'GitHub', 'GitLab', 'Stripe', 'Vercel', 'Netlify',
];

const KNOWN_PROJECTS = [
  'Muninn', 'Mission Control', 'NRL Fantasy', 'GigHunter', 'BrandForge',
  'ClawHub', 'Moltbook', 'AgentMail', 'memory system',
];

const KNOWN_TECHNOLOGIES = [
  // Languages
  'TypeScript', 'JavaScript', 'Python', 'Rust', 'Go', 'Java', 'Kotlin', 'Swift',
  'Ruby', 'PHP', 'C#', 'C++', 'C', 'SQL',
  // Frameworks
  'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt', 'SvelteKit',
  'Express', 'FastAPI', 'Django', 'Rails', 'Spring', 'Node.js',
  // Tools
  'Docker', 'Kubernetes', 'K8s', 'Terraform', 'Ansible', 'Jenkins', 'GitHub Actions',
  'npm', 'yarn', 'pnpm', 'pip', 'cargo', 'go mod',
  // Databases
  'PostgreSQL', 'Postgres', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'DynamoDB',
  // AI/ML
  'Ollama', 'OpenAI', 'Claude', 'GPT', 'LLM', 'LangChain', 'LlamaIndex',
  'embeddings', 'vector database', 'semantic search',
  // Other
  'Git', 'VS Code', 'Vim', 'Emacs', 'Linux', 'Ubuntu', 'macOS', 'Windows',
  'better-sqlite3', 'sqlite3',
];

const KNOWN_LOCATIONS = [
  // Australia
  'Brisbane', 'Sydney', 'Melbourne', 'Perth', 'Adelaide', 'Gold Coast', 'Canberra',
  'Queensland', 'NSW', 'Victoria', 'Australia', 'AEST',
  // Global
  'USA', 'UK', 'Europe', 'Asia', 'America', 'London', 'New York', 'San Francisco',
  'Tokyo', 'Singapore', 'homelab',
];

const KNOWN_EVENTS = [
  'planning session', 'product launch', 'meeting', 'standup', 'retro', 'retrospective',
  'sprint', 'demo', 'workshop', 'webinar', 'conference', 'hackathon',
];

const KNOWN_CONCEPTS = [
  'memory system', 'content router', 'entity extraction', 'semantic search',
  'knowledge graph', 'vector embedding', 'MCP server', 'agent architecture',
  'Australian English', 'machine learning', 'deep learning', 'neural network',
  'natural language processing', 'NLP', 'API', 'REST', 'GraphQL',
];

// ============================================
// PATTERN MATCHERS
// ============================================

// Capitalized words (potential names)
const CAPITALIZED_PATTERN = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g;

// CamelCase and PascalCase (potential tech/project names)
// Must have at least 2 actual words, not just a letter
const CAMELCASE_PATTERN = /\b[A-Z][a-z]{2,}[A-Z][a-z]{2,}(?:[A-Z][a-z]{2,})*\b/g;

// Technology patterns
const TECH_PATTERNS = [
  /\b[A-Z][a-z]*\.js\b/g,           // React.js, Vue.js, Next.js
  /\b[A-Z][a-z]*\.ts\b/g,           // Node.ts (rare)
  /\b[a-z]+-[a-z]+\d*\b/g,          // better-sqlite3
];

// Event patterns
const EVENT_PATTERNS = [
  /Q[1-4]\s+\w+\s+(session|planning|review)/gi,  // Q1 planning session
  /\w+\s+launch/gi,                              // product launch
  /(weekly|daily|monthly)\s+\w+/gi,              // weekly standup
];

// ============================================
// CONTEXT WORDS (disambiguation)
// ============================================

const PERSON_CONTEXT = ['met', 'spoke', 'talked', 'discussed', 'called', 'emailed', 'said', 'told', 'asked', 'replied'];
const ORG_CONTEXT = ['company', 'team', 'organization', 'at', 'joined', 'left', 'works', 'partner'];
const PROJECT_CONTEXT = ['project', 'app', 'application', 'system', 'platform', 'built', 'developed', 'deployed'];
const TECH_CONTEXT = ['uses', 'using', 'built with', 'framework', 'library', 'language', 'tool', 'database'];
const LOCATION_CONTEXT = ['in', 'at', 'from', 'based', 'located', 'office', 'server'];
const EVENT_CONTEXT = ['meeting', 'session', 'launch', 'conference', 'workshop', 'attended', 'scheduled'];

// ============================================
// MAIN EXTRACTION FUNCTION
// ============================================

export function extractEntities(text: string): Entity[] {
  const entities: Entity[] = [];
  const found = new Set<string>();  // Track found entities to avoid duplicates
  const lower = text.toLowerCase();

  // 1. Check known entities first (high confidence)
  // Use word boundary matching for single-word entities to avoid substring matches
  // Sort by length (longest first) to avoid substring matches
  const sortedPeople = [...KNOWN_PEOPLE].sort((a, b) => b.length - a.length);
  const sortedOrgs = [...KNOWN_ORGANIZATIONS].sort((a, b) => b.length - a.length);
  const sortedProjects = [...KNOWN_PROJECTS].sort((a, b) => b.length - a.length);
  const sortedTech = [...KNOWN_TECHNOLOGIES].sort((a, b) => b.length - a.length);
  const sortedLocations = [...KNOWN_LOCATIONS].sort((a, b) => b.length - a.length);

  for (const person of sortedPeople) {
    const regex = new RegExp(`\\b${person.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(person.toLowerCase())) {
      entities.push(createEntity(person, 'person', 0.95, text));
      found.add(person.toLowerCase());
      // Also mark any contained names (e.g., "Sammy" when "Sammy Clemens" found)
      const parts = person.split(/\s+/);
      for (const part of parts) {
        if (part.length > 2) found.add(part.toLowerCase());
      }
    }
  }

  for (const org of sortedOrgs) {
    const regex = new RegExp(`\\b${org.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(org.toLowerCase())) {
      entities.push(createEntity(org, 'organization', 0.95, text));
      found.add(org.toLowerCase());
    }
  }

  for (const project of sortedProjects) {
    const regex = new RegExp(`\\b${project.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(project.toLowerCase())) {
      entities.push(createEntity(project, 'project', 0.95, text));
      found.add(project.toLowerCase());
    }
  }

  for (const tech of sortedTech) {
    const regex = new RegExp(`\\b${tech.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(tech.toLowerCase())) {
      entities.push(createEntity(tech, 'technology', 0.95, text));
      found.add(tech.toLowerCase());
    }
  }

  for (const location of sortedLocations) {
    const regex = new RegExp(`\\b${location.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(location.toLowerCase())) {
      entities.push(createEntity(location, 'location', 0.95, text));
      found.add(location.toLowerCase());
    }
  }

  // 2. Extract events (pattern-based) - longest first
  const sortedEvents = [...KNOWN_EVENTS].sort((a, b) => b.length - a.length);
  
  for (const pattern of EVENT_PATTERNS) {
    const matches = text.match(pattern) || [];
    for (const match of matches) {
      if (!found.has(match.toLowerCase())) {
        entities.push(createEntity(match, 'event', 0.85, text));
        found.add(match.toLowerCase());
      }
    }
  }

  for (const event of sortedEvents) {
    const regex = new RegExp(`\\b${event.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(event.toLowerCase())) {
      entities.push(createEntity(event, 'event', 0.85, text));
      found.add(event.toLowerCase());
    }
  }

  // 3. Extract concepts (pattern-based) - longest first
  const sortedConcepts = [...KNOWN_CONCEPTS].sort((a, b) => b.length - a.length);
  
  for (const concept of sortedConcepts) {
    const regex = new RegExp(`\\b${concept.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (regex.test(text) && !found.has(concept.toLowerCase())) {
      entities.push(createEntity(concept, 'concept', 0.8, text));
      found.add(concept.toLowerCase());
    }
  }

  // 4. Extract CamelCase/PascalCase (potential tech/project names) - AFTER known entities
  const camelCase = text.match(CAMELCASE_PATTERN) || [];
  for (const word of camelCase) {
    if (found.has(word.toLowerCase())) continue;
    entities.push(createEntity(word, 'technology', 0.7, text));
    found.add(word.toLowerCase());
  }

  // 5. Extract tech patterns (.js, etc.)
  for (const pattern of TECH_PATTERNS) {
    const matches = text.match(pattern) || [];
    for (const match of matches) {
      if (!found.has(match.toLowerCase())) {
        entities.push(createEntity(match, 'technology', 0.8, text));
        found.add(match.toLowerCase());
      }
    }
  }

  // 6. Extract capitalized words (potential names) - ONLY if not already found
  // This is the lowest confidence, so we're very conservative
  const capitalized = text.match(CAPITALIZED_PATTERN) || [];
  for (const word of capitalized) {
    // Skip if already found (handles "Sammy" vs "Sammy Clemens" case)
    if (found.has(word.toLowerCase())) continue;

    // Skip common words
    const commonWords = ['I', 'The', 'A', 'An', 'This', 'That', 'It', 'We', 'They', 'You',
      'He', 'She', 'But', 'However', 'When', 'Where', 'Why', 'How', 'What', 'If', 'Then',
      'Yesterday', 'Today', 'Tomorrow', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
      'Saturday', 'Sunday', 'First', 'Second', 'Third', 'Finally', 'Last', 'Next'];
    if (commonWords.includes(word)) continue;

    // Skip single words that are part of a known multi-word entity
    const isPartOfKnown = KNOWN_PEOPLE.some(p => p.toLowerCase().includes(word.toLowerCase()) && p !== word) ||
      KNOWN_ORGANIZATIONS.some(o => o.toLowerCase().includes(word.toLowerCase()) && o !== word) ||
      KNOWN_PROJECTS.some(p => p.toLowerCase().includes(word.toLowerCase()) && p !== word);
    if (isPartOfKnown) continue;

    // Skip if looks like it's preceded by a time word (e.g., "Yesterday Charlie" shouldn't be a project)
    const wordIndex = lower.indexOf(word.toLowerCase());
    const precedingWords = lower.slice(Math.max(0, wordIndex - 15), wordIndex).trim().split(/\s+/);
    const timeWords = ['yesterday', 'today', 'tomorrow', 'last', 'next', 'this', 'previous'];
    if (precedingWords.some(w => timeWords.includes(w))) continue;

    // Only infer type from context - don't guess
    const type = inferTypeFromContext(word, text);
    if (type) {
      entities.push(createEntity(word, type, 0.5, text));
      found.add(word.toLowerCase());
    }
  }

  return entities;
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function createEntity(text: string, type: EntityType, confidence: number, fullText: string): Entity {
  // Extract context (surrounding words)
  const index = fullText.toLowerCase().indexOf(text.toLowerCase());
  const start = Math.max(0, index - 20);
  const end = Math.min(fullText.length, index + text.length + 20);
  const context = fullText.slice(start, end);

  return { text, type, confidence, context };
}

function inferTypeFromContext(word: string, text: string): EntityType | null {
  const lower = text.toLowerCase();
  const wordLower = word.toLowerCase();
  const wordIndex = lower.indexOf(wordLower);

  // Get context around the word
  const contextStart = Math.max(0, wordIndex - 50);
  const contextEnd = Math.min(lower.length, wordIndex + word.length + 50);
  const context = lower.slice(contextStart, contextEnd);

  // Check for person context
  if (PERSON_CONTEXT.some(c => context.includes(c))) {
    // But also check if it looks like a name (capitalized, not a common noun)
    if (/^[A-Z][a-z]+$/.test(word)) {
      return 'person';
    }
  }

  // Check for organization context
  if (ORG_CONTEXT.some(c => context.includes(c + ' ' + wordLower))) {
    return 'organization';
  }

  // Check for project context
  if (PROJECT_CONTEXT.some(c => context.includes(c))) {
    return 'project';
  }

  // Check for technology context
  if (TECH_CONTEXT.some(c => context.includes(c))) {
    return 'technology';
  }

  // Check for location context
  if (LOCATION_CONTEXT.some(c => context.includes(c + ' ' + wordLower))) {
    return 'location';
  }

  // Default: if capitalized and looks like a name, guess person
  if (/^[A-Z][a-z]+$/.test(word) && word.length > 2) {
    return 'person';
  }

  return null;  // Skip if can't determine
}