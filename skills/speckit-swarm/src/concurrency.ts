/**
 * Task Concurrency Safety Checker
 * 
 * Verifica se uma tarefa pode ser executada em paralelo sem conflitos.
 */

export interface ConcurrencyResult {
  isSafe: boolean;
  conflicts: string[];
  recommendedStrategy: 'parallel' | 'sequential' | 'cautious';
  reason: string;
}

/**
 * Analisa se a tarefa tem conflitos potenciais de concurrency
 */
export function checkConcurrencySafety(task: string): ConcurrencyResult {
  const lower = task.toLowerCase();
  const conflicts: string[] = [];
  
  // Patterns que indicam potencial conflito
  const conflictPatterns = [
    {
      pattern: /mesmo\s+arquivo/i,
      message: "Task mentions 'same file' - may cause conflicts",
    },
    {
      pattern: /arquivo\s+único/i,
      message: "Task mentions 'single file' - may cause conflicts",
    },
    {
      pattern: /um\s+arquivo/i,
      message: "Task mentions 'one file' - sequential execution safer",
    },
    {
      pattern: /editar\s+o\s+mesmo/i,
      message: "Editing same resource - sequential recommended",
    },
    {
      pattern: /modificar\s+o\s+mesmo/i,
      message: "Modifying same resource - sequential recommended",
    },
    {
      pattern: /refatorar\s+o\s+módulo/i,
      message: "Refactoring same module - check for dependencies",
    },
    {
      pattern: /corrigir\s+o\s+bug/i,
      message: "Fixing bug - usually single file, sequential safer",
    },
    {
      pattern: /consertar\s+o\s+bug/i,
      message: "Fixing bug - usually single file, sequential safer",
    },
  ];
  
  for (const { pattern, message } of conflictPatterns) {
    if (pattern.test(lower)) {
      conflicts.push(message);
    }
  }
  
  // Safe patterns - claramente não têm conflitos
  const safePatterns = [
    /criar\s+(um\s+)?novo/i,
    /implementar\s+(um\s+)?novo/i,
    /construir\s+(um\s+)?projeto/i,
    /criar\s+(vários|múltiplos)\s+arquivos/i,
    /separar\s+em\s+arquivos/i,
    /múltiplos?\s+arquivos/i,
  ];
  
  const isSafe = conflicts.length === 0 && safePatterns.some(p => p.test(lower));
  
  // Se tem "criar novo" sem menção de editar existente, é seguro
  if (isSafe) {
    return {
      isSafe: true,
      conflicts: [],
      recommendedStrategy: 'parallel',
      reason: 'Creating new files - no conflicts expected',
    };
  }
  
  // Se tem conflitos potenciais
  if (conflicts.length > 0) {
    return {
      isSafe: false,
      conflicts,
      recommendedStrategy: 'cautious',
      reason: 'Potential conflicts detected - recommend sequential or careful parallel',
    };
  }
  
  // Default: cautious
  return {
    isSafe: true,
    conflicts: [],
    recommendedStrategy: 'cautious',
    reason: 'Default to cautious - analyze specific case',
  };
}

/**
 * Wrapper que combina complexity + concurrency
 */
export interface TaskAnalysis {
  shouldParallel: boolean;
  strategy: 'parallel' | 'sequential' | 'cautious';
  reason: string;
  chunks?: string[];
}

export function analyzeTask(task: string): TaskAnalysis {
  // Primeiro verifica complexidade
  const complexPatterns = [
    /criar\s+(um?\s+)?(novo|nova)/i,
    /implementar/i,
    /construir/i,
    /refatorar/i,
    /reescrever/i,
    /migrar/i,
    /build\s+/i,
    /corrigir\s+o?\s*bug/i,
    /fix\s+(the\s+)?bug/i,
  ];
  
  const isComplex = complexPatterns.some(p => p.test(task.toLowerCase()));
  
  // Se não é complexo, executa normalmente
  if (!isComplex) {
    return {
      shouldParallel: false,
      strategy: 'sequential',
      reason: 'Simple task - single agent sufficient',
    };
  }
  
  // Se é complexo, verifica concurrency
  const concurrency = checkConcurrencySafety(task);
  
  return {
    shouldParallel: concurrency.isSafe && concurrency.recommendedStrategy === 'parallel',
    strategy: concurrency.recommendedStrategy,
    reason: concurrency.reason,
  };
}
