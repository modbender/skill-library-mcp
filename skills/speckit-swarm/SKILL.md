# Speckit Swarm - Agent Orchestration System

## Overview

Native implementation of oh-my-opencode-style orchestration using OpenClaw's tools.

## Architecture

### Core Components

1. **Ultrawork Detector** - Detects "ulw"/"ultrawork" keywords and triggers parallel execution
2. **Agent Personas** - Specialized system prompts for different tasks
3. **Task Planner** - Breaks complex tasks into parallel chunks
4. **Continuation Enforcer** - Ensures tasks complete fully

## File Structure

```
skills/speckit-swarm/
├── SKILL.md                      # This file
├── src/
│   ├── ultrawork.ts              # Ultrawork detection & trigger
│   ├── personas/
│   │   ├── mod.ts               # Persona exports
│   │   ├── sisyphus.ts          # Main orchestrator
│   │   ├── hephaestus.ts        # Deep worker
│   │   ├── oracle.ts            # Design/debug
│   │   ├── librarian.ts         # Research/docs
│   │   └── explore.ts            # Fast scout
│   ├── planner.ts               # Task decomposition
│   └── index.ts                 # Main entry
```

## Usage

### Manual Mode
```bash
# Use personas directly
sessions_spawn task:"..." model:"minimax-m2.5" thinking:"high"
```

### Ultrawork Mode
When user includes "ulw" or "ultrawork":
1. Detect keyword
2. Decompose task into parallel chunks
3. Execute with parallel_spawn
4. Aggregate results

## Personas

### Sisyphus (Main Orchestrator)
- Model: minimax-m2.5
- Thinking: high
- Behavior: Relentless execution, parallel coordination, todo tracking

### Hephaestus (Deep Worker)
- Model: minimax-m2.5
- Thinking: high
- Behavior: Autonomous execution, no hand-holding, completes full scope

### Oracle (Design/Debug)
- Model: minimax-m2.5
- Thinking: high
- Behavior: Architecture decisions, bug hunting, code review

### Librarian (Research)
- Model: minimax-m2.1
- Thinking: medium
- Behavior: Docs lookup, code exploration, pattern finding

### Explore (Scout)
- Model: minimax-m2.5-highspeed
- Thinking: low
- Behavior: Fast grep, file finding, quick analysis

## How to Use

### 1. Direct Persona Usage
```typescript
import { PERSONAS, buildTaskPrompt } from './speckit-swarm';

const persona = PERSONAS.hephaestus;
const task = "Fix the login bug in auth.ts";

sessions_spawn({
  task: buildTaskPrompt({ task, persona: 'hephaestus' }),
  model: persona.config.model,
  thinking: persona.config.thinking
});
```

### 2. Ultrawork Mode (auto-detected)
When user includes "ulw" or "ultrawork":
```typescript
import { planTask, shouldUseUltrawork } from './speckit-swarm';

const task = "ulw refactor the auth module";
if (shouldUseUltrawork(task)) {
  const plan = planTask(task);
  // Execute plan.chunks with parallel_spawn
}
```

### 3. Task Decomposition
```typescript
import { planTask } from './speckit-swarm';

const plan = planTask("Create a new API endpoint");
// plan.chunks = [{ label: 'spec', ... }, { label: 'setup', ... }, ...]
```

## Ultrawork Handler

O handler detecta "ulw" automaticamente e prepara tarefas para parallel_spawn.

### Funções Exportadas

```typescript
// Verifica se contém keyword ulw
containsUltrawork(task: string): boolean

// Limpa o prefixo ulw da tarefa
cleanUltraworkTask(task: string): string

// Prepara execução ultrawork
prepareUltrawork(task: string): {
  shouldExecute: boolean;
  chunks: Array<{
    label: string;
    task: string;
    model?: string;
    thinking?: string;
  }>;
  cleanedTask: string;
}
```

### Exemplo de Uso

```typescript
// Na minha resposta, quando receber mensagem com "ulw":

const ultrawork = prepareUltrawork("ulw create a new API");

if (ultrawork.shouldExecute) {
  // Executar com parallel_spawn
  parallel_spawn({
    tasks: ultrawork.chunks,
    wait: "all"
  });
}
```

### Como Eu Detecto e Executo

### Análise de Segurança de Concorrência

Antes de paralelizar, verifico se não há conflitos:

| Tipo de Tarefa | Estratégia |
|----------------|------------|
| Criar novo projeto/CLI/API | **PARALLEL** ✓ |
| Múltiplos arquivos novos | **PARALLEL** ✓ |
| Refatorar módulo | CAUTIOUS (verifica dependências) |
| Corrigir bug | **SEQUENTIAL** ✗ |
| Editar mesmo arquivo | **SEQUENTIAL** ✗ |
| Tarefa simples | SINGLE |

### Fluxo de Decisão

1. **Analiso complexidade** - É uma tarefa grande?
2. **Verifico conflitos** - Vai mexer no mesmo arquivo?
3. **Decido estratégia** - parallel / sequential / single

Isso evita problemas de concorrência quando múltiplos agentes tentam modificar o mesmo arquivo.

### Exemplo de Uso

```typescript
// Detecção automática
const result = prepareParallelExecution("criar um novo CLI");
// result.shouldExecute = true (detectou complexidade)

if (result.shouldExecute) {
  parallel_spawn({
    tasks: result.chunks,
    wait: "all"
  });
}
```
