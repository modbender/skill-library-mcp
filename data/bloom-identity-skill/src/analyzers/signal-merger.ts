/**
 * Signal Merger
 *
 * Blends three signal sources into final identity inputs:
 * 1. Conversation — what the user talked about (primary)
 * 2. USER.md — static profile the user declared
 * 3. Feedback — dynamic signals from recommendation interactions
 *
 * Weight model:
 *   No feedback yet:   Conversation 60%, USER.md 30%, Feedback 10%
 *   After 10+ events:  Conversation 50%, USER.md 20%, Feedback 30%
 *
 * feedbackWeight = min(0.3, events.length * 0.02)
 */

import { UserMdSignals } from '../parsers/user-md-parser';

export interface FeedbackData {
  categoryWeights?: Record<string, number>; // 1.0 = neutral, >1 = boosted, <1 = suppressed
  excludeSkillIds?: string[];
  eventCount: number;
}

export interface MergedSignals {
  mainCategories: string[];
  subCategories: string[];
  dimensionNudges: {
    conviction: number; // -15 to +15
    intuition: number;
    contribution: number;
    learning?: number;  // taste spectrum nudges
    decision?: number;
    novelty?: number;
    risk?: number;
  };
  excludedSkillIds?: string[];
  categoryWeights?: Record<string, number>;
}

/**
 * Merge conversation, USER.md, and feedback signals into a unified result.
 */
export function mergeSignals(
  conversationCategories: string[],
  conversationDimensions: { conviction: number; intuition: number; contribution: number },
  userMd: UserMdSignals | null,
  feedback: FeedbackData | null,
): MergedSignals {
  // Calculate dynamic weights
  const eventCount = feedback?.eventCount ?? 0;
  const feedbackWeight = Math.min(0.3, eventCount * 0.02);
  const userMdWeight = userMd ? Math.max(0.2, 0.3 - feedbackWeight * 0.33) : 0;

  // ─── Category merging ──────────────────────────────────────────────

  // Extract categories from USER.md fields
  const userMdCategories = userMd ? mapUserMdToCategories(userMd) : [];
  const userMdSubCategories = userMd?.interests ?? [];

  // Build weighted category ranking
  const categoryScores = new Map<string, number>();

  // Conversation categories get base weight
  const convWeight = 1.0 - userMdWeight - feedbackWeight;
  for (let i = 0; i < conversationCategories.length; i++) {
    const cat = conversationCategories[i];
    const positionBonus = 1.0 - (i * 0.1); // First category scores higher
    categoryScores.set(cat, (categoryScores.get(cat) || 0) + convWeight * positionBonus);
  }

  // USER.md categories get their weight
  for (let i = 0; i < userMdCategories.length; i++) {
    const cat = userMdCategories[i];
    const positionBonus = 1.0 - (i * 0.1);
    categoryScores.set(cat, (categoryScores.get(cat) || 0) + userMdWeight * positionBonus);
  }

  // Feedback category weights as multiplier
  if (feedback?.categoryWeights) {
    for (const [cat, weight] of Object.entries(feedback.categoryWeights)) {
      const existing = categoryScores.get(cat) || 0;
      if (existing > 0) {
        // Apply feedback weight as multiplier to existing score
        categoryScores.set(cat, existing * weight);
      } else if (weight > 1.2) {
        // Feedback can introduce new categories if strongly boosted
        categoryScores.set(cat, feedbackWeight * (weight - 1.0));
      }
    }
  }

  // Sort by score, take top categories
  const sortedCategories = Array.from(categoryScores.entries())
    .sort(([, a], [, b]) => b - a)
    .map(([cat]) => cat);

  const mainCategories = sortedCategories.slice(0, 3);

  // Merge sub-categories: conversation interests + USER.md interests (deduplicated)
  const subCategorySet = new Set<string>();
  // Conversation sub-categories are already in conversationCategories beyond top 3
  for (const cat of sortedCategories.slice(3)) {
    subCategorySet.add(cat);
  }
  for (const interest of userMdSubCategories) {
    subCategorySet.add(interest);
  }
  const subCategories = Array.from(subCategorySet).slice(0, 10);

  // ─── Dimension nudges ──────────────────────────────────────────────

  const dimensionNudges = userMd ? calculateDimensionNudges(userMd) : {
    conviction: 0, intuition: 0, contribution: 0,
  };

  // Scale nudges by userMdWeight (less influence when feedback dominates)
  dimensionNudges.conviction = Math.round(dimensionNudges.conviction * (userMdWeight / 0.3));
  dimensionNudges.intuition = Math.round(dimensionNudges.intuition * (userMdWeight / 0.3));
  dimensionNudges.contribution = Math.round(dimensionNudges.contribution * (userMdWeight / 0.3));

  return {
    mainCategories: mainCategories.length > 0 ? mainCategories : conversationCategories,
    subCategories,
    dimensionNudges,
    excludedSkillIds: feedback?.excludeSkillIds,
    categoryWeights: feedback?.categoryWeights,
  };
}

// ─── USER.md → Category mapping ──────────────────────────────────────────

const ROLE_CATEGORY_MAP: [RegExp, string][] = [
  [/\b(bd|sales|growth|business dev)/i, 'Marketing'],
  [/\b(develop|engineer|programmer|software|coding)/i, 'Development'],
  [/\b(research|scientist|academic)/i, 'Education'],
  [/\b(design|ui|ux|creative)/i, 'Design'],
  [/\b(market|seo|content|brand)/i, 'Marketing'],
  [/\b(financ|invest|trad)/i, 'Finance'],
  [/\b(founder|cto|ceo|co-founder)/i, 'Development'],
  [/\b(community|advocate|ambassador)/i, 'Marketing'],
];

const FOCUS_CATEGORY_MAP: [RegExp, string][] = [
  [/\b(defi|crypto|web3|blockchain|token|dao|nft|onchain)/i, 'Crypto'],
  [/\b(ai|llm|agent|machine learning|gpt|neural)/i, 'AI Tools'],
  [/\b(design|ui|ux|figma)/i, 'Design'],
  [/\b(educat|learn|teach|course)/i, 'Education'],
  [/\b(wellness|health|fitness|meditation)/i, 'Wellness'],
  [/\b(productiv|workflow|automat)/i, 'Productivity'],
];

const TECH_CATEGORY_MAP: [RegExp, string][] = [
  [/\b(claude-code|claude|anthropic|openai|gpt)/i, 'AI Tools'],
  [/\b(typescript|javascript|python|rust|go|java)\b/i, 'Development'],
  [/\b(solidity|hardhat|foundry|ethers|viem|wagmi)/i, 'Crypto'],
  [/\b(react|next|vue|svelte|angular)/i, 'Development'],
  [/\b(figma|sketch|adobe)/i, 'Design'],
];

function mapUserMdToCategories(userMd: UserMdSignals): string[] {
  const categories = new Set<string>();

  // Role mapping
  if (userMd.role) {
    for (const [regex, category] of ROLE_CATEGORY_MAP) {
      if (regex.test(userMd.role)) {
        categories.add(category);
      }
    }
  }

  // Current focus mapping
  if (userMd.currentFocus) {
    const focusText = userMd.currentFocus.join(' ');
    for (const [regex, category] of FOCUS_CATEGORY_MAP) {
      if (regex.test(focusText)) {
        categories.add(category);
      }
    }
  }

  // Tech stack mapping
  if (userMd.techStack) {
    const techText = userMd.techStack.join(' ');
    for (const [regex, category] of TECH_CATEGORY_MAP) {
      if (regex.test(techText)) {
        categories.add(category);
      }
    }
  }

  return Array.from(categories);
}

// ─── Dimension nudges from USER.md ───────────────────────────────────────

function calculateDimensionNudges(userMd: UserMdSignals): {
  conviction: number;
  intuition: number;
  contribution: number;
  learning?: number;
  decision?: number;
  novelty?: number;
  risk?: number;
} {
  let conviction = 0;
  let intuition = 0;
  let contribution = 0;
  let learning = 0;
  let decision = 0;
  let novelty = 0;
  let risk = 0;

  // Working style nudges (original dimensions)
  if (userMd.workingStyle === 'deep-focus') {
    conviction += 15;
    learning += 10; // deep-focus → study-first
    novelty += 10;  // deep-focus → wait-and-see
  } else if (userMd.workingStyle === 'explorer' || userMd.workingStyle === 'multitasker') {
    conviction -= 10;
    intuition += 10;
    novelty -= 10;  // explorer → early-adopter
  }

  // Role nudges
  if (userMd.role) {
    const roleLower = userMd.role.toLowerCase();
    if (/research/i.test(roleLower)) {
      intuition += 10;
      learning += 10;  // researcher → study-first
      decision += 10;  // researcher → deliberate
      risk += 10;      // researcher → cautious
    }
    if (/community|bd|business dev|ambassador/i.test(roleLower)) {
      contribution += 10;
    }
    if (/founder|cto|ceo|co-founder/i.test(roleLower)) {
      conviction += 10;
      risk -= 10;      // founder → bold
    }
  }

  // Current focus → taste nudges
  if (userMd.currentFocus) {
    const focusText = userMd.currentFocus.join(' ').toLowerCase();
    if (/build|ship|launch|prototype/i.test(focusText)) {
      learning -= 10;  // builder → try-first
      decision -= 10;  // builder → gut
    }
    if (/research|study|learn|academic/i.test(focusText)) {
      learning += 10;  // researcher → study-first
      decision += 10;  // researcher → deliberate
    }
  }

  // Clamp each nudge to [-15, +15]
  return {
    conviction: clamp(conviction, -15, 15),
    intuition: clamp(intuition, -15, 15),
    contribution: clamp(contribution, -15, 15),
    learning: clamp(learning, -15, 15) || undefined,
    decision: clamp(decision, -15, 15) || undefined,
    novelty: clamp(novelty, -15, 15) || undefined,
    risk: clamp(risk, -15, 15) || undefined,
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
