import { type TickTickListProjectsQuery } from "../domain/project-contract.js";
import {
  type TickTickCompleteTaskInput,
  type TickTickCreateTaskInput,
  type TickTickListTasksQuery,
  type TickTickTask,
  type TickTickUpdateTaskInput,
} from "../domain/task-contract.js";
import { categorizeHttpStatus, isRetriableCategory, TickTickDomainError } from "../shared/error-categories.js";
import {
  TickTickApiError,
  TickTickApiTimeoutError,
} from "../api/ticktick-api-client.js";
import type { TickTickUseCases } from "./usecase-contracts.js";
import type { TickTickGateway } from "../api/ticktick-gateway.js";

export function createTickTickUseCases(gateway: TickTickGateway): TickTickUseCases {
  return {
    createTask: {
      execute: async (input: TickTickCreateTaskInput): Promise<TickTickTask> => {
        try {
          return await gateway.createTask(input);
        } catch (error) {
          throw mapCoreError(error, "Failed to create TickTick task.");
        }
      },
    },
    listTasks: {
      execute: async (query?: TickTickListTasksQuery): Promise<TickTickTask[]> => {
        try {
          return await gateway.listTasks(query);
        } catch (error) {
          throw mapCoreError(error, "Failed to list TickTick tasks.");
        }
      },
    },
    updateTask: {
      execute: async (input: TickTickUpdateTaskInput): Promise<TickTickTask> => {
        try {
          return await gateway.updateTask(input);
        } catch (error) {
          throw mapCoreError(error, `Failed to update TickTick task '${input.taskId}'.`);
        }
      },
    },
    completeTask: {
      execute: async (input: TickTickCompleteTaskInput): Promise<TickTickTask> => {
        try {
          return await gateway.completeTask(input);
        } catch (error) {
          throw mapCoreError(error, `Failed to complete TickTick task '${input.taskId}'.`);
        }
      },
    },
    listProjects: {
      execute: async (query?: TickTickListProjectsQuery) => {
        try {
          return await gateway.listProjects(query);
        } catch (error) {
          throw mapCoreError(error, "Failed to list TickTick projects.");
        }
      },
    },
  };
}

function toTaskListRequestOptions(
  query: TickTickListTasksQuery | undefined
): { query: Record<string, string | number | boolean | null | undefined> } | undefined {
  if (query === undefined) {
    return undefined;
  }

  return {
    query: {
      projectId: query.projectId,
      from: query.from,
      to: query.to,
      includeCompleted: query.includeCompleted,
      limit: query.limit,
    },
  };
}

function toCompleteTaskPayload(input: TickTickCompleteTaskInput): Record<string, string> {
  if (input.completedAt === undefined) {
    return {};
  }

  return {
    completedTime: input.completedAt,
  };
}

function mapCoreError(error: unknown, fallbackMessage: string): TickTickDomainError {
  if (error instanceof TickTickDomainError) {
    return error;
  }

  if (error instanceof TickTickApiError) {
    const category = categorizeHttpStatus(error.status);
    return new TickTickDomainError({
      category,
      message: fallbackMessage,
      status: error.status,
      retriable: isRetriableCategory(category),
      cause: error,
      responseBody: error.body,
    });
  }

  if (error instanceof TickTickApiTimeoutError) {
    return new TickTickDomainError({
      category: "network",
      message: fallbackMessage,
      retriable: true,
      cause: error,
    });
  }

  if (error instanceof Error) {
    return new TickTickDomainError({
      category: "network",
      message: fallbackMessage,
      retriable: true,
      cause: error,
    });
  }

  return new TickTickDomainError({
    category: "unknown",
    message: fallbackMessage,
    retriable: false,
    cause: error,
  });
}
