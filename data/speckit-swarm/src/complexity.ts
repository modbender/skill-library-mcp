/**
 * Task Complexity Analyzer
 * 
 * Detects if a task is complex enough to warrant parallel execution.
 * No keywords needed - just analyze the task itself.
 */

export interface ComplexityResult {
  isComplex: boolean;
  reason: string;
  recommendedStrategy: 'single' | 'parallel' | 'ultrawork';
  estimatedChunks: number;
}

/**
 * Analyze task complexity
 */
export function analyzeComplexity(task: string): ComplexityResult {
  const lower = task.toLowerCase();
  
  // Clear indicators of complex tasks
  const multiStepIndicators = [
    /criar\s+(um?\s+)?(novo|nova)/i,
    /implementar/i,
    /construir/i,
    /build\s+/i,
    /refatorar/i,
    /reescrever/i,
    /migrar/i,
    /criar\s+.*api/i,
    /criar\s+.*cli/i,
    /criar\s+.*projeto/i,
    /criar\s+.*app/i,
    /criar\s+.*site/i,
    /criar\s+.*blog/i,
    /criar\s+.*sistema/i,
    /fix\s+.*and\s+/i,
    /add\s+.*and\s+/i,
    /\be2e\b/i,
    /integra[rção]*\s+(com|entre)/i,
    /múltiplos?\s+(arquivos|módulos|arquivos)/i,
  ];
  
  // Check for multi-step indicators
  for (const pattern of multiStepIndicators) {
    if (pattern.test(lower)) {
      return {
        isComplex: true,
        reason: `Task matches complex pattern: ${pattern.source}`,
        recommendedStrategy: 'ultrawork',
        estimatedChunks: 4,
      };
    }
  }
  
  // Check for explicit multi-step language
  const multiStepPhrases = [
    ' e depois ',
    ' e também ',
    ' e então ',
    ' e em seguida ',
    ' além disso ',
    ' também ',
    ' primeiramente ',
    ' primeiro ',
    ' segundo ',
    ' terceiro ',
    ', depois ',
  ];
  
  let stepCount = 1;
  for (const phrase of multiStepPhrases) {
    if (lower.includes(phrase)) {
      stepCount++;
    }
  }
  
  if (stepCount >= 3) {
    return {
      isComplex: true,
      reason: `Task has ${stepCount} explicit steps`,
      recommendedStrategy: 'parallel',
      estimatedChunks: stepCount,
    };
  }
  
  // Check for multiple deliverables
  const deliverables = [
    /múltiplos?\s+(arquivos|arquivos|pastas)/i,
    /vários?\s+arquivos/i,
    /criar\s+\d+\s+arquivos/i,
    /criar\s+(\w+,\s*)+e\s+(\w+)/i,
  ];
  
  for (const pattern of deliverables) {
    if (pattern.test(lower)) {
      return {
        isComplex: true,
        reason: 'Task involves multiple deliverables',
        recommendedStrategy: 'ultrawork',
        estimatedChunks: 3,
      };
    }
  }
  
  // Default - simple task
  return {
    isComplex: false,
    reason: 'Task is straightforward',
    recommendedStrategy: 'single',
    estimatedChunks: 1,
  };
}

/**
 * Should automatically use parallel execution
 */
export function shouldAutoParallelize(task: string): boolean {
  const result = analyzeComplexity(task);
  return result.isComplex;
}

/**
 * Get the appropriate execution strategy
 */
export function getExecutionStrategy(task: string): ComplexityResult {
  return analyzeComplexity(task);
}
