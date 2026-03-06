/**
 * Entity Normalization
 * 
 * Resolves entity mentions to canonical forms:
 * - Pronouns → Names (when resolvable)
 * - Abbreviations → Full names
 * - Dates → ISO 8601
 * - Aliases stored for retrieval
 */

import type { Entity, EntityType } from './entities.js';

export interface NormalizedEntity {
  original: string;      // Original mention
  canonical: string;     // Normalized form
  type: EntityType;
  confidence: number;
  context: string;
  aliases: string[];     // Alternative mentions
}

export interface NormalizationResult {
  entities: NormalizedEntity[];
  text: string;          // Text with normalized entities (optional)
}

// Current date for date calculations
const CURRENT_DATE = new Date('2026-02-24');

/**
 * English spelling variants (UK/Aus ↔ US)
 * Both forms should map to the same concept for retrieval
 */
const SPELLING_VARIANTS: Record<string, string[]> = {
  // -our ↔ -or
  'colour': ['color'],
  'flavour': ['flavor'],
  'honour': ['honor'],
  'humour': ['humor'],
  'labour': ['labor'],
  'neighbour': ['neighbor'],
  'rumour': ['rumor'],
  'savour': ['savor'],
  'valour': ['valor'],
  'vigour': ['vigor'],
  'ardour': ['ardor'],
  'clamour': ['clamor'],
  'dolour': ['dolor'],
  'enamour': ['enamor'],
  'fervour': ['fervor'],
  'glamour': ['glamor'],
  'odour': ['odor'],
  'parlour': ['parlor'],
  'splendour': ['splendor'],
  'tumour': ['tumor'],
  'vapour': ['vapor'],
  
  // -ise ↔ -ize
  'organise': ['organize'],
  'realise': ['realize'],
  'recognise': ['recognize'],
  'analyse': ['analyze'],
  'paralyse': ['paralyze'],
  'apologise': ['apologize'],
  'authorise': ['authorize'],
  'capitalise': ['capitalize'],
  'categorise': ['categorize'],
  'centralise': ['centralize'],
  'characterise': ['characterize'],
  'civilise': ['civilize'],
  'commercialise': ['commercialize'],
  'criticise': ['criticize'],
  'customise': ['customize'],
  'emphasise': ['emphasize'],
  'familiarise': ['familiarize'],
  'finalise': ['finalize'],
  'formalise': ['formalize'],
  'harmonise': ['harmonize'],
  'hypothesise': ['hypothesize'],
  'idealise': ['idealize'],
  'industrialise': ['industrialize'],
  'initialise': ['initialize'],
  'maximise': ['maximize'],
  'minimise': ['minimize'],
  'modernise': ['modernize'],
  'normalise': ['normalize'],
  'optimise': ['optimize'],
  'popularise': ['popularize'],
  'prioritise': ['prioritize'],
  'publicise': ['publicize'],
  'rationalise': ['rationalize'],
  'revolutionise': ['revolutionize'],
  'satirise': ['satirize'],
  'specialise': ['specialize'],
  'standardise': ['standardize'],
  'symbolise': ['symbolize'],
  'sympathise': ['sympathize'],
  'synchronise': ['synchronize'],
  'systematise': ['systematize'],
  'theorise': ['theorize'],
  'utilise': ['utilize'],
  'visualise': ['visualize'],
  
  // -re ↔ -er
  'centre': ['center'],
  'theatre': ['theater'],
  'fibre': ['fiber'],
  'litre': ['liter'],
  'metre': ['meter'],
  'sabre': ['saber'],
  'spectre': ['specter'],
  'lustre': ['luster'],
  'meagre': ['meager'],
  'sombre': ['somber'],
  
  // -ce ↔ -se
  'defence': ['defense'],
  'offence': ['offense'],
  'pretence': ['pretense'],
  'licence': ['license'],
  'practise': ['practice'],
  
  // -ogue ↔ -og
  'catalogue': ['catalog'],
  'dialogue': ['dialog'],
  'monologue': ['monolog'],
  'prologue': ['prolog'],
  'epilogue': ['epilog'],
  'analogue': ['analog'],
  
  // Double consonants
  'cancelled': ['canceled'],
  'cancellation': ['cancelation'],
  'counsellor': ['counselor'],
  'jewellery': ['jewelry'],
  'travelling': ['traveling'],
  'traveller': ['traveler'],
  'marvellous': ['marvelous'],
  'woollen': ['woolen'],
  'waggon': ['wagon'],
  
  // Miscellaneous
  'cheque': ['check'],
  'programme': ['program'],
  'tyre': ['tire'],
  'aluminium': ['aluminum'],
  'aeroplane': ['airplane'],
  'storey': ['story'],
  'moustache': ['mustache'],
  'plough': ['plow'],
  'sceptre': ['scepter'],
  'behaviour': ['behavior'],
  'behavioural': ['behavioral'],
  'behaviourism': ['behaviorism'],
};

/**
 * Get all spelling variants for a word (both directions)
 */
function getSpellingVariants(word: string): string[] {
  const lower = word.toLowerCase();
  
  // Check if word is a key
  if (SPELLING_VARIANTS[lower]) {
    return [lower, ...SPELLING_VARIANTS[lower]];
  }
  
  // Check if word is a variant
  for (const [canonical, variants] of Object.entries(SPELLING_VARIANTS)) {
    if (variants.includes(lower)) {
      return [canonical, ...variants];
    }
  }
  
  return [lower]; // No variants found
}

/**
 * Calculate ISO date from relative date string
 */
function normalizeRelativeDate(dateStr: string): string {
  const lower = dateStr.toLowerCase().trim();
  const today = new Date(CURRENT_DATE);
  
  switch (lower) {
    case 'today':
      return formatDate(today);
    case 'yesterday':
      return formatDate(new Date(today.getTime() - 24 * 60 * 60 * 1000));
    case 'tomorrow':
      return formatDate(new Date(today.getTime() + 24 * 60 * 60 * 1000));
    case 'day after tomorrow':
      return formatDate(new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000));
    case 'day before yesterday':
    case 'day before':
      return formatDate(new Date(today.getTime() - 2 * 24 * 60 * 60 * 1000));
    default:
      // Try to parse "next Monday", "last Friday", etc.
      const dayMatch = lower.match(/(next|last|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/);
      if (dayMatch) {
        const [, modifier, dayName] = dayMatch;
        const dayIndex = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].indexOf(dayName);
        const currentDay = today.getDay();
        let targetDay = dayIndex;
        
        if (modifier === 'next') {
          targetDay = currentDay <= dayIndex ? dayIndex : dayIndex + 7;
        } else if (modifier === 'last') {
          targetDay = currentDay >= dayIndex ? dayIndex : dayIndex - 7;
        }
        
        const diff = targetDay - currentDay;
        return formatDate(new Date(today.getTime() + diff * 24 * 60 * 60 * 1000));
      }
      
      // Return as-is if can't parse
      return dateStr;
  }
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

/**
 * Common abbreviation expansions
 */
const ABBREVIATION_MAP: Record<string, string> = {
  // US Cities
  'NYC': 'New York City',
  'LA': 'Los Angeles',
  'SF': 'San Francisco',
  'DC': 'Washington DC',
  'Chi': 'Chicago',
  'Philly': 'Philadelphia',
  // Australian
  'QLD': 'Queensland',
  'NSW': 'New South Wales',
  'VIC': 'Victoria',
  'WA': 'Western Australia',
  'SA': 'South Australia',
  'TAS': 'Tasmania',
  'ACT': 'Australian Capital Territory',
  'NT': 'Northern Territory',
  // General
  'USA': 'United States',
  'UK': 'United Kingdom',
  'EU': 'European Union',
  'UN': 'United Nations',
  'NATO': 'North Atlantic Treaty Organization',
  'AI': 'Artificial Intelligence',
  'ML': 'Machine Learning',
  'DL': 'Deep Learning',
  'NLP': 'Natural Language Processing',
  'API': 'Application Programming Interface',
  'URL': 'Uniform Resource Locator',
  'HTTP': 'HyperText Transfer Protocol',
  'HTTPS': 'HyperText Transfer Protocol Secure',
  'SQL': 'Structured Query Language',
  'NoSQL': 'Non-Relational Database',
  'CTO': 'Chief Technology Officer',
  'CFO': 'Chief Financial Officer',
  'COO': 'Chief Operating Officer',
  'PM': 'Project Manager',
  'DevOps': 'Development Operations',
};

/**
 * Pronoun resolution patterns
 * Maps pronouns to potential antecedents found in text
 */
const PRONOUN_PATTERNS = [
  { pronoun: 'he', pattern: /([A-Z][a-z]+)\s+(?:worked|built|created|designed|developed|wrote|said|mentioned|told|asked)/gi },
  { pronoun: 'she', pattern: /([A-Z][a-z]+)\s+(?:worked|built|created|designed|developed|wrote|said|mentioned|told|asked)/gi },
  { pronoun: 'they', pattern: /([A-Z][a-z]+)\s+(?:worked|built|created|designed|developed)/gi },
  { pronoun: 'it', pattern: /([A-Z][a-z]+)\s+(?:is|was|was built|was created)/gi },
];

/**
 * Find potential antecedent for a pronoun in text
 */
function findPronounAntecedent(text: string, pronoun: string): string | null {
  const lowerPronoun = pronoun.toLowerCase();
  
  for (const { pronoun: p, pattern } of PRONOUN_PATTERNS) {
    if (p === lowerPronoun) {
      const matches = text.matchAll(pattern);
      for (const match of matches) {
        if (match[1]) {
          return match[1];
        }
      }
    }
  }
  
  return null;
}

/**
 * Normalize entities using LLM (optional) or rule-based fallback
 * 
 * @param text - Input text
 * @param existingEntities - Pre-extracted entities (optional)
 * @param llmProvider - Optional LLM function for advanced normalization
 * @returns Normalized entities with aliases
 */
export async function normalizeEntities(
  text: string,
  existingEntities?: Entity[],
  llmProvider?: (prompt: string) => Promise<string>
): Promise<NormalizedEntity[]> {
  // Use rule-based normalization (always available)
  const ruleBased = normalizeEntitiesRuleBased(text, existingEntities || []);
  
  // If no LLM provider, return rule-based results
  if (!llmProvider) {
    return ruleBased;
  }
  
  try {
    // Try LLM-based normalization
    const prompt = buildNormalizationPrompt(text, existingEntities);
    const response = await llmProvider(prompt);
    const llmNormalized = parseLLMResponse(response);
    
    // Merge LLM results with rule-based (LLM takes precedence)
    return mergeNormalizationResults(ruleBased, llmNormalized);
  } catch (error) {
    console.warn('Entity normalization failed, using rule-based fallback:', error);
    return ruleBased;
  }
}

/**
 * Rule-based entity normalization (always available)
 */
function normalizeEntitiesRuleBased(
  text: string,
  existingEntities: Entity[]
): NormalizedEntity[] {
  const results: NormalizedEntity[] = [];
  const processed = new Set<string>();
  
  // 1. Process existing entities
  for (const entity of existingEntities) {
    const normalized = normalizeSingleEntity(entity, text);
    results.push(normalized);
    processed.add(entity.text.toLowerCase());
  }
  
  // 2. Look for abbreviations in text
  for (const [abbr, expansion] of Object.entries(ABBREVIATION_MAP)) {
    const regex = new RegExp(`\\b${abbr}\\b`, 'g');
    if (regex.test(text) && !processed.has(abbr.toLowerCase())) {
      results.push({
        original: abbr,
        canonical: expansion,
        type: determineAbbreviationType(abbr),
        confidence: 0.9,
        aliases: [abbr, expansion],
        context: ''
      });
      processed.add(abbr.toLowerCase());
    }
  }
  
  // 3. Look for relative dates in text
  const datePatterns = [
    /\b(today|yesterday|tomorrow|day after tomorrow)\b/gi,
    /\b(next|last|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/gi,
  ];
  
  for (const pattern of datePatterns) {
    const matches = text.match(pattern);
    if (matches) {
      for (const match of matches) {
        if (!processed.has(match.toLowerCase())) {
          const normalizedDate = normalizeRelativeDate(match);
          results.push({
            original: match,
            canonical: normalizedDate,
            type: 'event',
            confidence: 0.85,
            aliases: [match, normalizedDate],
            context: ''
          });
          processed.add(match.toLowerCase());
        }
      }
    }
  }
  
  // 4. Check for spelling variants
  for (const [canonical, variants] of Object.entries(SPELLING_VARIANTS)) {
    // Check if canonical (UK/Aus) form appears in text
    const canonicalRegex = new RegExp(`\\b${canonical}\\b`, 'gi');
    if (canonicalRegex.test(text) && !processed.has(canonical.toLowerCase())) {
      results.push({
        original: canonical,
        canonical: canonical, // Use UK/Aus as canonical
        type: 'concept',
        confidence: 0.95,
        aliases: [canonical, ...variants],
        context: ''
      });
      processed.add(canonical.toLowerCase());
      variants.forEach(v => processed.add(v.toLowerCase()));
    }
    
    // Check if any variant (US) form appears in text
    for (const variant of variants) {
      const variantRegex = new RegExp(`\\b${variant}\\b`, 'gi');
      if (variantRegex.test(text) && !processed.has(variant.toLowerCase())) {
        results.push({
          original: variant,
          canonical: canonical, // Map to canonical UK/Aus form
          type: 'concept',
          confidence: 0.95,
          aliases: [variant, canonical, ...variants.filter(v => v !== variant)],
          context: ''
        });
        processed.add(variant.toLowerCase());
        processed.add(canonical.toLowerCase());
        variants.forEach(v => processed.add(v.toLowerCase()));
      }
    }
  }
  
  return results;
}

/**
 * Normalize a single entity
 */
function normalizeSingleEntity(entity: Entity, text: string): NormalizedEntity {
  // Check if entity text is an abbreviation
  const abbrExpansion = ABBREVIATION_MAP[entity.text];
  if (abbrExpansion) {
    return {
      ...entity,
      original: entity.text,
      canonical: abbrExpansion,
      aliases: [entity.text, abbrExpansion],
    };
  }
  
  // Check if entity text is a pronoun that can be resolved
  const pronouns = ['he', 'she', 'they', 'it', 'him', 'her', 'them'];
  if (pronouns.includes(entity.text.toLowerCase())) {
    const antecedent = findPronounAntecedent(text, entity.text);
    if (antecedent) {
      return {
        ...entity,
        original: entity.text,
        canonical: antecedent,
        aliases: [entity.text, antecedent],
      };
    }
  }
  
  // Check if entity text contains a date reference
  const dateMatch = entity.text.match(/\b(today|yesterday|tomorrow)\b/i);
  if (dateMatch) {
    return {
      ...entity,
      original: entity.text,
      canonical: normalizeRelativeDate(entity.text),
      aliases: [entity.text, normalizeRelativeDate(entity.text)],
    };
  }
  
  // Default: keep as-is
  return {
    ...entity,
    original: entity.text,
    canonical: entity.text,
    aliases: [entity.text],
  };
}

/**
 * Determine type for abbreviation
 */
function determineAbbreviationType(abbr: string): EntityType {
  const locationAbbreviations = ['NYC', 'LA', 'SF', 'DC', 'Chi', 'Philly', 'QLD', 'NSW', 'VIC', 'WA', 'SA', 'TAS', 'ACT', 'NT'];
  const orgAbbreviations = ['USA', 'UK', 'EU', 'UN', 'NATO'];
  const techAbbreviations = ['AI', 'ML', 'DL', 'NLP', 'API', 'URL', 'HTTP', 'HTTPS', 'SQL', 'NoSQL'];
  
  if (locationAbbreviations.includes(abbr)) return 'location';
  if (orgAbbreviations.includes(abbr)) return 'organization';
  if (techAbbreviations.includes(abbr)) return 'technology';
  
  return 'concept';
}

/**
 * Build LLM prompt for normalization
 */
function buildNormalizationPrompt(text: string, entities?: Entity[]): string {
  const entityList = entities?.map(e => `- ${e.text} (${e.type})`).join('\n') || 'None pre-extracted';
  
  return `Analyze the following text and normalize all entity mentions.

Text: "${text}"

Pre-extracted entities:
${entityList}

Normalization rules:
1. PRONOUNS: Resolve to canonical names when context is clear
   - "Phillip worked on Muninn. He built..." → "He" = "Phillip"
   - If pronoun reference is unclear, leave as-is
   
2. ABBREVIATIONS: Expand to full names
   - "NYC" → "New York City"
   - "SF" → "San Francisco"
   - "QLD" → "Queensland"
   
3. DATES: Normalize to ISO 8601 (YYYY-MM-DD)
   - "tomorrow" → 2026-02-25
   - "yesterday" → 2026-02-23
   - "next week" → calculate date range
   
4. NAME VARIANTS: Link aliases
   - "Sammy Clemens" and "Sammy" → same canonical "Sammy Clemens"

Return JSON array of normalized entities:
[
  {
    "original": "He",
    "canonical": "Phillip",
    "type": "person",
    "confidence": 0.9
  }
]

Only include entities that CAN be normalized. Skip entities that are already in canonical form.`;
}

/**
 * Parse LLM response into NormalizedEntity array
 */
function parseLLMResponse(response: string): NormalizedEntity[] {
  try {
    const jsonMatch = response.match(/\[[\s\S]*\]/);
    if (!jsonMatch) return [];
    
    const parsed = JSON.parse(jsonMatch[0]);
    return parsed.map((e: any) => ({
      original: e.original,
      canonical: e.canonical,
      type: (e.type as EntityType) || 'concept',
      confidence: e.confidence || 0.8,
      aliases: [e.original, e.canonical],
      context: ''
    }));
  } catch (error) {
    console.warn('Failed to parse normalization response:', error);
    return [];
  }
}

/**
 * Merge rule-based and LLM normalization results
 */
function mergeNormalizationResults(
  ruleBased: NormalizedEntity[],
  llmResults: NormalizedEntity[]
): NormalizedEntity[] {
  const merged = new Map<string, NormalizedEntity>();
  
  // Add rule-based results first
  for (const entity of ruleBased) {
    merged.set(entity.original.toLowerCase(), entity);
  }
  
  // LLM results override rule-based (more accurate)
  for (const entity of llmResults) {
    const key = entity.original.toLowerCase();
    if (entity.confidence > (merged.get(key)?.confidence || 0)) {
      merged.set(key, entity);
    }
  }
  
  return Array.from(merged.values());
}

/**
 * Alias storage for retrieval
 */
export interface EntityAliasStore {
  getAliases(canonical: string): string[];
  addAlias(canonical: string, alias: string): void;
  findCanonical(alias: string): string | null;
}

export function createAliasStore(): EntityAliasStore {
  const aliases = new Map<string, Set<string>>();
  const canonicals = new Map<string, string>(); // Store original case
  
  return {
    getAliases(canonical: string): string[] {
      return [...(aliases.get(canonical.toLowerCase()) || new Set())];
    },
    
    addAlias(canonical: string, alias: string): void {
      const key = canonical.toLowerCase();
      if (!aliases.has(key)) {
        aliases.set(key, new Set([canonical]));
        canonicals.set(key, canonical); // Store original case
      }
      // Store lowercase for case-insensitive lookup
      aliases.get(key)!.add(alias.toLowerCase());
    },
    
    findCanonical(alias: string): string | null {
      const aliasLower = alias.toLowerCase();
      for (const [canonical, aliasSet] of aliases) {
        if (aliasSet.has(aliasLower)) {
          return canonicals.get(canonical) || canonical; // Return with original case
        }
      }
      return null;
    }
  };
}

/**
 * Extract with normalization (combined function)
 */
export async function extractWithNormalization(
  text: string,
  existingEntities?: Entity[],
  llmProvider?: (prompt: string) => Promise<string>
): Promise<{
  entities: Entity[];
  normalized: NormalizedEntity[];
}> {
  const { extractEntities } = await import('./entities.js');
  const entities = extractEntities(text);
  const normalized = await normalizeEntities(text, entities, llmProvider);
  
  return { entities, normalized };
}
