/**
 * Speckit Swarm - Ultrawork & Auto-Parallelization
 * 
 * Detecta automaticamente tarefas complexas e executa em paralelo.
 * Não precisa de palavras-chave - analisa a complexidade da tarefa.
 * 
 * Uso:
 * 1. Quando receber mensagem do usuário, chamar shouldAutoParallelize(task)
 * 2. Se true, chamar prepareUltrawork(task)
 * 3. Executar com parallel_spawn
 */

import { planTask, shouldUseUltrawork, PERSONAS, getPersonaConfig } from './src/planner.js';
import type { TaskChunk } from './src/planner.js';

// Re-implementação simples sem imports para evitar issues de módulos
const PERSONAS_MAP = {
  sisyphus: { 
    prompt: "You are Sisyphus, the main orchestration agent. Complete tasks relentlessly.", 
    config: { model: "minimax-coding-plan/MiniMax-M2.5", thinking: "high" } 
  },
  hephaestus: { 
    prompt: "You are Hephaestus, autonomous deep worker. Complete tasks without hand-holding.", 
    config: { model: "minimax-coding-plan/MiniMax-M2.5", thinking: "high" } 
  },
  oracle: { 
    prompt: "You are Oracle, design and debugging specialist. Think deeply.", 
    config: { model: "minimax-coding-plan/MiniMax-M2.5", thinking: "high" } 
  },
  librarian: { 
    prompt: "You are Librarian, research specialist. Find information.", 
    config: { model: "minimax-coding-plan/MiniMax-M2.1", thinking: "medium" } 
  },
  explore: { 
    prompt: "You are Explore, fast scout. Move quickly.", 
    config: { model: "minimax-coding-plan/MiniMax-M2.5-highspeed", thinking: "low" } 
  },
};

/**
 * Verifica se a tarefa é complexa (detecção automática)
 * Substitui containsUltrawork - agora não precisa de "ulw"
 */
export function shouldAutoParallelize(task: string): boolean {
  const keywords = ['ulw', 'ultrawork', 'parallel'];
  const hasKeyword = keywords.some(k => task.toLowerCase().includes(k));
  
  // Also detect by complexity
  const complexPatterns = [
    /criar\s+(um?\s+)?(novo|nova)/i,
    /implementar/i,
    /construir/i,
    /refatorar/i,
    /reescrever/i,
    /migrar/i,
    /criar\s+.*api/i,
    /criar\s+.*cli/i,
    /criar\s+.*projeto/i,
    /criar\s+.*app/i,
    /build\s+/i,
    /corrigir\s+o?\s*bug/i,
    /fix\s+(the\s+)?bug/i,
    /consertar/i,
  ];
  
  const isComplex = complexPatterns.some(p => p.test(task.toLowerCase()));
  
  return hasKeyword || isComplex;
}

/**
 * Detecta e limpa o prefixo ulw da tarefa
 */
export function cleanUltraworkTask(task: string): string {
  return task.replace(/^(ulw|ultrawork)\s*/i, '').trim();
}

/**
 * Executa tarefa com parallelização automática
 * 
 * Retorna um objeto pronto para usar com parallel_spawn
 */
export function prepareParallelExecution(task: string): {
  shouldExecute: boolean;
  chunks: Array<{
    label: string;
    task: string;
    model?: string;
    thinking?: string;
  }>;
  cleanedTask: string;
  reason: string;
} {
  // Usar detecção automática de complexidade
  if (!shouldAutoParallelize(task)) {
    return {
      shouldExecute: false,
      chunks: [],
      cleanedTask: task,
      reason: 'Task is simple, single agent execution',
    };
  }

  // Detectar se tem prefixo ulw para limpar
  const cleanedTask = task.replace(/^(ulw|ultrawork)\s*/i, '').trim();
  
  // Execute o planner
  const plan = planSimpleTask(cleanedTask);
  
  // Adiciona config de persona a cada chunk
  const chunksWithConfig = plan.chunks.map(chunk => {
    const personaName = chunk.persona || 'hephaestus';
    const persona = PERSONAS_MAP[personaName as keyof typeof PERSONAS_MAP];
    
    return {
      label: chunk.label,
      task: chunk.task,
      model: persona?.config.model,
      thinking: persona?.config.thinking,
    };
  });

  return {
    shouldExecute: true,
    chunks: chunksWithConfig,
    cleanedTask,
    reason: 'Task is complex - using parallel execution',
  };
}

/**
 * Versão simplificada do planner para evitar dependências
 */
function planSimpleTask(task: string): { mainTask: string; chunks: TaskChunk[] } {
  const lower = task.toLowerCase();
  
  if (lower.includes('create') || lower.includes('build') || lower.includes('implement')) {
    return {
      mainTask: task,
      chunks: [
        { label: 'spec', task: `Create SPEC.md for: ${task}. Define overview, features, file structure.`, persona: 'oracle' },
        { label: 'setup', task: `Initialize project for: ${task}. Create package.json, dependencies, directory structure.`, persona: 'hephaestus' },
        { label: 'core', task: `Implement core functionality for: ${task}. Write all source files per spec.`, persona: 'hephaestus' },
        { label: 'test', task: `Verify implementation: ${task}. Test that it works.`, persona: 'explore' },
      ],
    };
  }
  
  if (lower.includes('refactor')) {
    return {
      mainTask: task,
      chunks: [
        { label: 'analyze', task: `Analyze: ${task}. Find files to change, dependencies, issues.`, persona: 'explore' },
        { label: 'plan', task: `Create refactoring plan for: ${task}. Define changes and order.`, persona: 'oracle' },
        { label: 'implement', task: `Execute refactoring: ${task}.`, persona: 'hephaestus' },
      ],
    };
  }
  
  if (lower.includes('fix') || lower.includes('bug')) {
    return {
      mainTask: task,
      chunks: [
        { label: 'debug', task: `Find and understand bug: ${task}. Find root cause.`, persona: 'oracle' },
        { label: 'fix', task: `Fix bug: ${task}.`, persona: 'hephaestus' },
        { label: 'verify', task: `Verify fix: ${task}.`, persona: 'explore' },
      ],
    };
  }
  
  // Default
  return {
    mainTask: task,
    chunks: [
      { label: 'research', task: `Research: ${task}. Find relevant docs and patterns.`, persona: 'librarian' },
      { label: 'execute', task: task, persona: 'hephaestus' },
    ],
  };
}

/**
 * Exemplo de como usar com parallel_spawn
 * 
 * // Detecção automática - não precisa de "ulw"
 * const result = prepareParallelExecution("criar um novo CLI");
 * 
 * // Ou com "ulw" (ainda funciona)
 * const result = prepareParallelExecution("ulw create a new API");
 * 
 * if (result.shouldExecute) {
 *   parallel_spawn({
 *     tasks: result.chunks,
 *     wait: "all"
 *   });
 * }
 */
