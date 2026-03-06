import type {
  TickTickCompleteTaskInput,
  TickTickCreateTaskInput,
  TickTickListTasksQuery,
  TickTickTask,
  TickTickUpdateTaskInput,
} from "../domain/task-contract.js";
import type { TickTickListProjectsQuery, TickTickProject } from "../domain/project-contract.js";

export interface CreateTaskUseCase {
  execute(input: TickTickCreateTaskInput): Promise<TickTickTask>;
}

export interface ListTasksUseCase {
  execute(query?: TickTickListTasksQuery): Promise<TickTickTask[]>;
}

export interface UpdateTaskUseCase {
  execute(input: TickTickUpdateTaskInput): Promise<TickTickTask>;
}

export interface CompleteTaskUseCase {
  execute(input: TickTickCompleteTaskInput): Promise<TickTickTask>;
}

export interface ListProjectsUseCase {
  execute(query?: TickTickListProjectsQuery): Promise<TickTickProject[]>;
}

export interface TickTickUseCases {
  createTask: CreateTaskUseCase;
  listTasks: ListTasksUseCase;
  updateTask: UpdateTaskUseCase;
  completeTask: CompleteTaskUseCase;
  listProjects: ListProjectsUseCase;
}

function notImplementedUseCase(name: string): never {
  throw new Error(`Use case '${name}' is not implemented yet.`);
}

export function createUnimplementedUseCases(): TickTickUseCases {
  return {
    createTask: {
      execute: async (_input) => notImplementedUseCase("createTask"),
    },
    listTasks: {
      execute: async (_query) => notImplementedUseCase("listTasks"),
    },
    updateTask: {
      execute: async (_input) => notImplementedUseCase("updateTask"),
    },
    completeTask: {
      execute: async (_input) => notImplementedUseCase("completeTask"),
    },
    listProjects: {
      execute: async (_query) => notImplementedUseCase("listProjects"),
    },
  };
}
