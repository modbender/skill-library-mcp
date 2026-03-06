/**
 * Task Planner
 * 
 * Decomposes complex tasks into parallel chunks for ultrawork mode.
 */

export interface TaskChunk {
  label: string;
  task: string;
  persona?: string;
  dependsOn?: string[];
}

export interface PlanResult {
  chunks: TaskChunk[];
  mainTask: string;
}

/**
 * Analyze task and decompose into parallel chunks
 */
export function planTask(userTask: string): PlanResult {
  const task = userTask.toLowerCase();
  
  // Common patterns that suggest parallelization
  if (task.includes('refactor') || task.includes('restructure')) {
    return {
      mainTask: userTask,
      chunks: [
        {
          label: 'analyze',
          task: `Analyze the current structure. Find all files that need changes, dependencies, and potential issues. Report findings.`,
          persona: 'explore',
        },
        {
          label: 'plan',
          task: `Create a refactoring plan based on the analysis. Define what files to change, in what order, and any risks.`,
          persona: 'oracle',
        },
        {
          label: 'implement',
          task: `Execute the refactoring. Make the code changes according to the plan.`,
          persona: 'hephaestus',
        },
        {
          label: 'verify',
          task: `Verify the refactoring worked. Check for errors, run tests if available.`,
          persona: 'oracle',
        },
      ],
    };
  }

  if (task.includes('create') || task.includes('build') || task.includes('implement')) {
    // Create from scratch
    return {
      mainTask: userTask,
      chunks: [
        {
          label: 'spec',
          task: `Create a SPEC.md for this project. Define: overview, features, file structure, data models, API if applicable.`,
          persona: 'oracle',
        },
        {
          label: 'setup',
          task: `Initialize the project: package.json, dependencies, directory structure, config files.`,
          persona: 'hephaestus',
        },
        {
          label: 'core',
          task: `Implement the core functionality based on the spec. Write all source files.`,
          persona: 'hephaestus',
        },
        {
          label: 'test',
          task: `Verify the implementation works. Run the app, check for errors.`,
          persona: 'explore',
        },
      ],
    };
  }

  if (task.includes('fix') || task.includes('bug')) {
    return {
      mainTask: userTask,
      chunks: [
        {
          label: 'reproduce',
          task: `Find and understand the bug. Look at the code, find the root cause.`,
          persona: 'oracle',
        },
        {
          label: 'fix',
          task: `Implement the fix for the bug.`,
          persona: 'hephaestus',
        },
        {
          label: 'verify',
          task: `Verify the fix works. Test the solution.`,
          persona: 'explore',
        },
      ],
    };
  }

  // Default: single task with research
  return {
    mainTask: userTask,
    chunks: [
      {
        label: 'research',
        task: `Research this task. Find relevant docs, examples, and patterns.`,
        persona: 'librarian',
      },
      {
        label: 'execute',
        task: userTask,
        persona: 'hephaestus',
      },
    ],
  };
}

/**
 * Check if task should use ultrawork mode
 */
export function shouldUseUltrawork(task: string): boolean {
  const keywords = ['ulw', 'ultrawork', 'parallel', 'multi', 'refactor', 'create project', 'build'];
  const lower = task.toLowerCase();
  return keywords.some(k => lower.includes(k));
}
