/**
 * ES6 Refactor Skill - TypeScript Definitions
 * Provides type definitions for the refactoring engine and CLI
 */

// ============================================
// Core Types
// ============================================

/**
 * Represents the source language version/target compatibility
 */
export type LanguageTarget =
  | 'es5'
  | 'es2015'
  | 'es2016'
  | 'es2017'
  | 'es2018'
  | 'es2019'
  | 'es2020'
  | 'es2021'
  | 'es2022'
  | 'esnext';

/**
 * Transformation confidence level (0-1)
 */
export type ConfidenceLevel = number;

/**
 * Refactoring pattern category
 */
export type PatternCategory =
  | 'variable-declarations'
  | 'functions'
  | 'strings'
  | 'loops'
  | 'destructuring'
  | 'objects'
  | 'arrays'
  | 'modules'
  | 'classes'
  | 'async'
  | 'literals';

/**
 * Conditions that must be met for a pattern to apply
 */
export interface PatternConditions {
  /** Whether variable is reassigned */
  reassigns?: boolean;
  /** Whether scope is block-level */
  scope?: 'block' | 'function' | 'global';
  /** Whether this binding needs to be preserved */
  preservesThis?: boolean;
  /** Whether it's a function expression */
  isExpression?: boolean;
  /** Whether function contains single return statement */
  singleReturn?: boolean;
  /** Whether function has side effects */
  noSideEffects?: boolean;
  /** Whether object properties match their values */
  keyMatchesValue?: boolean;
  /** Whether string contains concatenation */
  containsConcatenation?: boolean;
  /** Whether interpolation is needed */
  hasInterpolation?: boolean;
  /** Whether for loop only uses index for array access */
  usesIndexOnlyForAccess?: boolean;
  /** Whether loop modifies the array */
  noModifications?: boolean;
  /** Whether accessing sequential array indices */
  sequentialAccess?: boolean;
  /** Whether multiple extractions from same source */
  multipleExtractions?: boolean;
  /** Whether source object is same for all properties */
  sameSourceObject?: boolean;
  /** Number of properties to extract */
  propertyCount?: 'single' | 'multiple';
  /** Whether has default assignment */
  hasDefaultAssignment?: boolean;
  /** Whether uses arguments object */
  usesArguments?: boolean;
  /** Whether performing object merging */
  objectMerging?: boolean;
  /** Whether creates new object (vs mutation) */
  createsNewObject?: boolean;
  /** Whether it's a Node.js builtin */
  nodeBuiltin?: boolean;
  /** Whether it's a callback file */
  isModuleFile?: boolean;
  /** Whether it's a single export */
  singleExport?: boolean;
  /** Whether assignment is simple (no computation) */
  simpleAssignment?: boolean;
  /** Whether key is computed/dynamic */
  dynamicKey?: boolean;
  /** Whether it's a literal value */
  literalValue?: boolean;
  /** Whether using hasOwnProperty check */
  hasOwnCheck?: boolean;
  /** Whether iterating over object */
  objectIteration?: boolean;
}

/**
 * A single transformation pattern
 */
export interface Pattern {
  /** Unique pattern identifier */
  id: string;
  /** Human-readable description */
  description: string;
  /** Pattern category */
  category: PatternCategory;
  /** Legacy code pattern (may contain placeholders) */
  legacy: string;
  /** Modern replacement pattern */
  modern: string;
  /** Conditions for pattern matching */
  conditions: PatternConditions;
  /** Confidence score 0-1 */
  confidence: ConfidenceLevel;
  /** Lower numbers applied first */
  priority: number;
}

/**
 * Complete pattern library
 */
export interface PatternLibrary {
  patterns: Record<string, Pattern>;
}

// ============================================
// Feature Compatibility Types
// ============================================

/**
 * Browser compatibility info
 */
export interface BrowserCompatibility {
  chrome: string;
  firefox: string;
  safari: string;
  edge: string;
  ie: string | 'no';
}

/**
 * Mobile browser compatibility
 */
export interface MobileCompatibility {
  ios_safari: string;
  android_chrome: string;
}

/**
 * Complete feature compatibility data
 */
export interface FeatureCompatibility {
  browsers: BrowserCompatibility;
  node: string;
  mobile?: MobileCompatibility;
}

/**
 * ES6+ Feature definition
 */
export interface Feature {
  /** Feature name */
  name: string;
  /** ECMAScript version */
  ecmaVersion: 'ES2015' | 'ES2016' | 'ES2017' | 'ES2018' | 'ES2019' | 'ES2020' | 'ES2021' | 'ES2022' | 'ES2023';
  /** Brief description */
  description: string;
  /** Compatibility matrix */
  compatibility: FeatureCompatibility;
  /** Usage recommendations */
  usage: {
    recommended: boolean | 'modern_only' | 'with_bundler';
    notes: string[];
  };
  /** Related transformation patterns */
  patterns?: string[];
}

/**
 * Complete features database
 */
export interface FeatureDatabase {
  features: Record<string, Feature>;
  compatibility_guidelines: {
    [target: string]: {
      description: string;
      allowed_features: string[];
      needs_transpilation: boolean;
      tooling: string[] | null;
    };
  };
  deprecation_timeline: Record<
    string,
    {
      deprecated: boolean;
      recommended_replacement: string;
      reason: string;
      migration_difficulty: 'easy' | 'moderate' | 'hard';
    }
  >;
}

// ============================================
// AST and Transformation Types
// ============================================

/**
 * AST Node types we handle
 */
export type ASTNodeType =
  | 'VariableDeclaration'
  | 'FunctionExpression'
  | 'ArrowFunctionExpression'
  | 'CallExpression'
  | 'BinaryExpression'
  | 'MemberExpression'
  | 'ObjectExpression'
  | 'ArrayExpression'
  | 'ForStatement'
  | 'ForInStatement'
  | 'ForOfStatement'
  | 'TemplateLiteral'
  | 'ImportDeclaration'
  | 'ExportDefaultDeclaration'
  | 'ExportNamedDeclaration'
  | 'ClassDeclaration'
  | 'ClassExpression'
  | 'MethodDefinition'
  | 'Property';

/**
 * Position in source code
 */
export interface SourcePosition {
  line: number;
  column: number;
  offset: number;
}

/**
 * AST Node structure (simplified)
 */
export interface ASTNode {
  type: ASTNodeType;
  start: SourcePosition;
  end: SourcePosition;
  raw?: string;
  children?: ASTNode[];
  [key: string]: unknown;
}

/**
 * Transformation result for a single node
 */
export interface TransformationResult {
  original: ASTNode;
  transformed: ASTNode | ASTNode[];
  patternId: string;
  confidence: ConfidenceLevel;
  edits?: CodeEdit[];
}

/**
 * Code edit (for patch generation)
 */
export interface CodeEdit {
  start: SourcePosition;
  end: SourcePosition;
  replacement: string;
}

/**
 * Complete refactoring result
 */
export interface RefactoringResult {
  success: boolean;
  output: string;
  appliedPatterns: Array<{
    patternId: string;
    location: SourcePosition;
    confidence: ConfidenceLevel;
  }>;
  errors: string[];
  warnings: string[];
  stats: {
    patternsApplied: number;
    nodesTransformed: number;
    linesChanged: number;
  };
}

// ============================================
// CLI Types
// ============================================

/**
 * CLI configuration
 */
export interface CLIConfig {
  /** Source file path */
  from?: string;
  /** Output file path (defaults to stdout) */
  to?: string;
  /** Target language version */
  target?: LanguageTarget;
  /** Input format */
  type?: 'javascript' | 'typescript';
  /** Show diff output */
  diff?: boolean;
  /** Verbose logging */
  verbose?: boolean;
  /** Pattern filter */
  only?: string[];
  /** Exclude patterns */
  exclude?: string[];
  /** Confidence threshold */
  threshold?: number;
  /** Generate source maps */
  sourceMaps?: boolean;
  /** Lint after refactoring */
  lint?: boolean;
}

/**
 * CLI exit codes
 */
export type CLIExitCode = 0 | 1 | 2;

// ============================================
// Agent Integration Types
// ============================================

/**
 * Agent request payload
 */
export interface AgentRequest {
  /** Source code to refactor */
  code: string;
  /** Language (javascript/typescript) */
  language: 'javascript' | 'typescript';
  /** Target compatibility */
  target: LanguageTarget;
  /** Specific patterns to apply (empty = all) */
  patterns?: string[];
  /** Patterns to skip */
  skipPatterns?: string[];
  /** Confidence threshold 0-1 */
  confidence?: number;
  /** Preserve original formatting */
  preserveFormatting?: boolean;
  /** Generate comments for each change */
  annotateChanges?: boolean;
}

/**
 * Agent response payload
 */
export interface AgentResponse {
  /** Refactored code */
  code: string;
  /** Applied transformations */
  transformations: Array<{
    pattern: string;
    location: {line: number; column: number};
    before: string;
    after: string;
  }>;
  /** Errors encountered */
  errors: string[];
  /** Warnings */
  warnings: string[];
  /** Stats */
  stats: {
    totalChanges: number;
    linesAdded: number;
    linesRemoved: number;
  };
  /** Execution time in ms */
  executionTime: number;
}

// ============================================
// Internal Engine Types
// ============================================

/**
 * Refactoring engine configuration
 */
export interface EngineConfig {
  /** Loaded pattern library */
  patterns: PatternLibrary;
  /** Loaded feature database */
  features: FeatureDatabase;
  /** Target language */
  target: LanguageTarget;
  /** Confidence threshold */
  confidenceThreshold: number;
  /** Enable TypeScript-specific transformations */
  typescriptMode: boolean;
  /** Preserve comments */
  preserveComments: boolean;
  /** Maximum edit distance for pattern matching */
  maxEditDistance: number;
}

/**
 * Context for a single refactoring operation
 */
export interface RefactorContext {
  /** Source code */
  source: string;
  /** AST root */
  ast: ASTNode;
  /** Language (javascript/typescript) */
  language: 'javascript' | 'typescript';
  /** Applied patterns (to avoid conflicts) */
  appliedPatterns: Set<string>;
  /** Accumulated code edits */
  edits: CodeEdit[];
  /** Configuration */
  config: EngineConfig;
}

// ============================================
// Utility Types
// ============================================

/**
 * Deep partial type
 */
export type DeepPartial<T> = T extends object
  ? {[P in keyof T]?: DeepPartial<T[P]>}
  : T;

/**
 * Pattern match result
 */
export interface PatternMatch {
  pattern: Pattern;
  /** Node(s) that match */
  nodes: ASTNode[];
  /** Match confidence */
  confidence: ConfidenceLevel;
  /** Location of match */
  location: SourcePosition;
}

// ============================================
// Module Exports
// ============================================

export default interface RefactorModule {
  /** Main refactoring function */
  refactor(context: RefactorContext): Promise<RefactoringResult>;

  /** Parse source to AST */
  parse(source: string, language: 'javascript' | 'typescript'): ASTNode;

  /** Generate code from AST */
  generate(ast: ASTNode, options?: {minify?: boolean}): string;

  /** Load pattern library */
  loadPatterns(path: string): Promise<PatternLibrary>;

  /** Load feature database */
  loadFeatures(path: string): Promise<FeatureDatabase>;

  /** Check if pattern applies */
  matches(node: ASTNode, pattern: Pattern): PatternMatch | null;

  /** Apply transformation */
  transform(node: ASTNode, pattern: Pattern): TransformationResult;

  /** Get available patterns */
  getPatterns(category?: PatternCategory): Pattern[];

  /** Validate target compatibility */
  validateFeature(feature: string, target: LanguageTarget): boolean;
}

export {};