/**
 * Canonical Category List
 *
 * Single source of truth for category names used across:
 * - Personality analyzer (detectCategories)
 * - CategoryMapper (fallback)
 * - GitHub recommendations (topic mapping)
 * - Recommendation grouping (findBestCategory)
 *
 * Categories represent WHAT the user is interested in (detected from conversation).
 * They are independent of personality type (which represents HOW the user thinks).
 */

export const CANONICAL_CATEGORIES = [
  'AI Tools',
  'Productivity',
  'Wellness',
  'Education',
  'Crypto',
  'Lifestyle',
  'Design',
  'Development',
  'Marketing',
  'Finance',
] as const;

export type CanonicalCategory = (typeof CANONICAL_CATEGORIES)[number];

/**
 * Keyword lists for detecting categories from conversation text.
 * Used by personality-analyzer's detectCategories() and by findBestCategory().
 */
export const CATEGORY_KEYWORDS: Record<CanonicalCategory, string[]> = {
  'AI Tools': ['ai', 'gpt', 'llm', 'machine learning', 'neural', 'model', 'chatbot', 'openai', 'anthropic', 'claude', 'copilot', 'prompt', 'inference', 'transformer', 'agent', 'gemini', 'image gen', 'text-to'],
  'Productivity': ['productivity', 'workflow', 'automation', 'efficiency', 'task management', 'notion', 'calendar', 'time tracking', 'optimize', 'systematic', 'slide', 'template', 'formatter', 'compress'],
  'Wellness': ['wellness', 'health', 'fitness', 'meditation', 'mindfulness', 'mental health', 'yoga', 'sleep', 'nutrition', 'self-care', 'wellbeing'],
  'Education': ['education', 'learning', 'course', 'teach', 'knowledge', 'tutorial', 'study', 'mentor', 'curriculum', 'workshop', 'training', 'comic', 'explainer'],
  'Crypto': ['crypto', 'defi', 'web3', 'blockchain', 'token', 'dao', 'nft', 'onchain', 'smart contract', 'wallet', 'protocol', 'ethereum', 'solana', 'base'],
  'Lifestyle': ['lifestyle', 'fashion', 'travel', 'personal brand', 'food', 'photography'],
  'Design': ['design', 'ui', 'ux', 'figma', 'creative', 'visual', 'typography', 'layout', 'prototype', 'infographic', 'illustration', 'cover image', 'graphic'],
  'Development': ['development', 'coding', 'programming', 'software', 'engineering', 'code', 'developer', 'api', 'framework', 'architecture', 'debugging', 'typescript', 'python', 'rust', 'markdown', 'html', 'cli', 'url-to', 'converter', 'formatter'],
  'Marketing': ['marketing', 'growth', 'seo', 'content strategy', 'advertising', 'brand', 'conversion', 'funnel', 'campaign', 'audience', 'copywriting', 'copy editing', 'cro', 'landing page', 'onboarding', 'churn', 'referral', 'email sequence', 'cold email', 'drip', 'pricing', 'paywall', 'popup', 'a/b test', 'split test', 'analytics', 'tracking', 'ads', 'ad creative', 'competitor', 'launch', 'social content', 'social media', 'wechat', 'xiaohongshu', 'post to x'],
  'Finance': ['finance', 'investing', 'trading', 'portfolio', 'wealth', 'stock', 'market', 'budget', 'revenue'],
};

/**
 * GitHub search topics for each canonical category.
 * Used by GitHubRecommendations to build search queries.
 */
export const CATEGORY_GITHUB_TOPICS: Record<CanonicalCategory, string[]> = {
  'AI Tools': ['ai', 'artificial-intelligence', 'machine-learning', 'llm', 'chatgpt', 'gpt'],
  'Productivity': ['productivity', 'automation', 'workflow', 'tools', 'utilities'],
  'Wellness': ['health', 'fitness', 'wellness', 'meditation', 'mindfulness', 'mental-health'],
  'Education': ['education', 'learning', 'tutorial', 'course', 'teaching'],
  'Crypto': ['blockchain', 'web3', 'crypto', 'ethereum', 'solana', 'defi', 'smart-contracts'],
  'Lifestyle': ['lifestyle', 'travel', 'food', 'photography', 'personal'],
  'Design': ['design', 'ui', 'ux', 'figma', 'design-tools', 'creative'],
  'Development': ['developer-tools', 'devtools', 'cli', 'sdk', 'library', 'framework'],
  'Marketing': ['marketing', 'seo', 'analytics', 'growth', 'content'],
  'Finance': ['finance', 'fintech', 'trading', 'investing', 'budgeting'],
};

/**
 * Default fallback categories when conversation analysis detects nothing.
 * These are the broadest, most universally populated categories across all sources.
 */
export const DEFAULT_FALLBACK_CATEGORIES: CanonicalCategory[] = [
  'AI Tools',
  'Development',
  'Productivity',
];

/**
 * Blocked keywords for filtering out potentially malicious or harmful repos/skills.
 * Applied to both GitHub and Claude Code recommendation pipelines.
 */
export const BLOCKED_KEYWORDS = [
  'hack', 'crack', 'exploit', 'phishing', 'drainer', 'stealer',
  'keylogger', 'malware', 'trojan', 'botnet', 'ransomware',
  'brute-force', 'password-crack', 'rat-tool', 'spyware',
  'wallet-drainer', 'token-grabber', 'cookie-stealer',
];

/**
 * Check if text contains any blocked keywords (case-insensitive).
 * Uses word-boundary matching where practical to avoid false positives.
 */
export function containsBlockedKeyword(text: string): boolean {
  const lower = text.toLowerCase();
  return BLOCKED_KEYWORDS.some(keyword => {
    // Use word boundary regex for single-word keywords, plain includes for hyphenated
    if (keyword.includes('-')) {
      return lower.includes(keyword);
    }
    const regex = new RegExp(`\\b${keyword}\\b`, 'i');
    return regex.test(lower);
  });
}
