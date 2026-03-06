/**
 * SonarQube Rule Definitions and Solutions
 * Database of known rules with automated solutions
 */

/**
 * Rule solutions database
 * Each rule contains:
 * - title: Human-readable rule name
 * - description: Detailed explanation
 * - autoFixable: Whether the fix can be automated
 * - solution: Function that returns solution text
 * - example: Code example showing before/after
 */
const RULE_SOLUTIONS = {
  // TypeScript Rules
  'typescript:S3358': {
    title: 'Nested ternary operation',
    description: 'Extract nested ternary into an independent statement or component',
    autoFixable: false,
    solution: (issue) => `Extract the nested ternary at line ${issue.line} into a separate function or component.`,
    example: `
// ❌ Before (nested ternary):
{loading ? 'Loading...' : runs.length > 0 ? <Table /> : <p>No data</p>}

// ✅ After (extracted component):
function DataContent({ loading, runs }) {
  if (loading) return 'Loading...';
  if (runs.length === 0) return <p>No data</p>;
  return <Table />;
}
    `
  },

  'typescript:S6606': {
    title: 'Prefer nullish coalescing operator',
    description: 'Use ?? instead of || for default values to avoid bugs with falsy values',
    autoFixable: true,
    solution: (issue) => `Replace || with ?? for default value assignment.`,
    example: `
// ❌ Before:
const name = value || 'default';
const count = input || 0;

// ✅ After:
const name = value ?? 'default';
const count = input ?? 0;
    `
  },

  'typescript:S6749': {
    title: 'Redundant fragment',
    description: 'Fragment with only one child is redundant and should be removed',
    autoFixable: true,
    solution: (issue) => `Remove the unnecessary <>...</> fragment.`,
    example: `
// ❌ Before:
<><div>Content</div></>

// ✅ After:
<div>Content</div>
    `
  },

  'typescript:S6759': {
    title: 'Props should be marked as read-only',
    description: 'Component props should be marked as readonly to prevent mutations',
    autoFixable: true,
    solution: (issue) => `Add 'readonly' modifier to props type definition.`,
    example: `
// ❌ Before:
function Component({ name }: { name: string })
interface Props { name: string }

// ✅ After:
function Component({ name }: { readonly name: string })
interface Props { readonly name: string }
    `
  },

  'typescript:S3776': {
    title: 'Cognitive complexity too high',
    description: 'Function has too high cognitive complexity and should be refactored',
    autoFixable: false,
    solution: (issue) => `Extract parts of the function into smaller, focused components or functions.`,
    example: `
// Strategies to reduce complexity:
// 1. Extract logic into custom hooks
// 2. Move UI sections to separate components  
// 3. Use early returns to reduce nesting
// 4. Replace conditionals with lookup objects
    `
  },

  'typescript:S6571': {
    title: 'Redundant any in union type',
    description: 'any type already includes all types, making the union redundant',
    autoFixable: true,
    solution: (issue) => `Remove redundant union with 'any' - 'any' already includes all types.`,
    example: `
// ❌ Before:
const [data, setData] = useState<any | null>(null);
const value: string | any;

// ✅ After:
const [data, setData] = useState<any>(null);
const value: any;
    `
  },

  // JavaScript Rules
  'javascript:S3358': {
    title: 'Nested ternary operation',
    description: 'Extract nested ternary into an independent statement',
    autoFixable: false,
    solution: (issue) => `Extract the nested ternary at line ${issue.line} into a separate function.`,
    example: `
// ❌ Before:
const result = condition1 ? (condition2 ? 'a' : 'b') : 'c';

// ✅ After:
function getResult(condition1, condition2) {
  if (!condition1) return 'c';
  return condition2 ? 'a' : 'b';
}
    `
  },

  // Add more rules as needed
};

/**
 * Get solution for a specific rule
 * @param {string} ruleKey - SonarQube rule key
 * @returns {Object|null} Rule solution or null if not found
 */
function getRuleSolution(ruleKey) {
  return RULE_SOLUTIONS[ruleKey] || null;
}

/**
 * Check if a rule has an automated fix
 * @param {string} ruleKey - SonarQube rule key
 * @returns {boolean} True if auto-fixable
 */
function isAutoFixable(ruleKey) {
  const rule = RULE_SOLUTIONS[ruleKey];
  return rule ? rule.autoFixable : false;
}

/**
 * Analyze an issue and add solution information
 * @param {Object} issue - SonarQube issue
 * @returns {Object} Issue with added solution data
 */
function analyzeIssue(issue) {
  const ruleInfo = getRuleSolution(issue.rule);
  
  if (!ruleInfo) {
    return {
      ...issue,
      ruleTitle: 'Unknown Rule',
      ruleDescription: 'No automated solution available. Check SonarQube documentation.',
      solution: 'Check SonarQube documentation for this rule.',
      autoFixable: false,
      action: 'manual'
    };
  }

  return {
    ...issue,
    ruleTitle: ruleInfo.title,
    ruleDescription: ruleInfo.description,
    solution: ruleInfo.solution(issue),
    autoFixable: ruleInfo.autoFixable,
    example: ruleInfo.example,
    action: ruleInfo.autoFixable ? 'auto-fix' : 'manual-refactor'
  };
}

module.exports = {
  RULE_SOLUTIONS,
  getRuleSolution,
  isAutoFixable,
  analyzeIssue
};