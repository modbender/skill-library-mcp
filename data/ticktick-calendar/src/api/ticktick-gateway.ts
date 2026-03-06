import { ContractValidationError } from "../common/contract-validation.js";
import {
  filterProjectsForQuery,
  parseTickTickProjectList,
  type TickTickListProjectsQuery,
  type TickTickProject,
} from "../domain/project-contract.js";
import {
  parseListTasksQuery,
  parseTickTickTask,
  parseTickTickTaskList,
  toCreateTaskPayload,
  toUpdateTaskPayload,
  validateCompleteTaskInput,
  validateCreateTaskInput,
  validateUpdateTaskInput,
  type TickTickCompleteTaskInput,
  type TickTickCreateTaskInput,
  type TickTickListTasksQuery,
  type TickTickTask,
  type TickTickUpdateTaskInput,
} from "../domain/task-contract.js";
import {
  categorizeHttpStatus,
  isRetriableCategory,
  TickTickDomainError,
  type TickTickErrorCategory,
  type TickTickErrorContext,
} from "../shared/error-categories.js";
import { TickTickApiClient, TickTickApiError, TickTickApiTimeoutError } from "./ticktick-api-client.js";

const TASK_PATH = "/task";
const PROJECT_PATH = "/project";

export interface TickTickGateway {
  createTask(input: TickTickCreateTaskInput): Promise<TickTickTask>;
  listTasks(query?: TickTickListTasksQuery): Promise<TickTickTask[]>;
  updateTask(input: TickTickUpdateTaskInput): Promise<TickTickTask>;
  completeTask(input: TickTickCompleteTaskInput): Promise<TickTickTask>;
  listProjects(query?: TickTickListProjectsQuery): Promise<TickTickProject[]>;
}

export class TickTickApiGateway implements TickTickGateway {
  private readonly apiClient: TickTickApiClient;

  constructor(apiClient: TickTickApiClient) {
    this.apiClient = apiClient;
  }

  async createTask(input: TickTickCreateTaskInput): Promise<TickTickTask> {
    try {
      const validated = validateCreateTaskInput(input);
      const payload = toCreateTaskPayload(validated);
      const response = await this.apiClient.post<unknown, Record<string, unknown>>(TASK_PATH, payload);

      return parseTickTickTask(response);
    } catch (error: unknown) {
      throw mapGatewayError("createTask", error);
    }
  }

  async listTasks(query?: TickTickListTasksQuery): Promise<TickTickTask[]> {
    try {
      const parsedQuery = query === undefined ? {} : parseListTasksQuery(query);
      const tasks =
        parsedQuery.projectId === undefined
          ? await this.fetchTasksAcrossProjects()
          : await this.fetchTasksByProjectId(parsedQuery.projectId);

      return applyTaskFilters(tasks, parsedQuery);
    } catch (error: unknown) {
      throw mapGatewayError("listTasks", error);
    }
  }

  async updateTask(input: TickTickUpdateTaskInput): Promise<TickTickTask> {
    try {
      const validated = validateUpdateTaskInput(input);
      const payload = toUpdateTaskPayload(validated);
      const path = `${TASK_PATH}/${encodeURIComponent(validated.taskId)}`;
      const response = await this.apiClient.post<unknown, Record<string, unknown>>(path, payload);

      return parseTickTickTask(response);
    } catch (error: unknown) {
      throw mapGatewayError("updateTask", error);
    }
  }

  async completeTask(input: TickTickCompleteTaskInput): Promise<TickTickTask> {
    try {
      const validated = validateCompleteTaskInput(input);
      const taskId = encodeURIComponent(validated.taskId);
      const completePath = `${TASK_PATH}/${taskId}/complete`;
      const completePayload = buildCompleteTaskPayload(validated);

      let completionResponse: unknown;
      if (completePayload === undefined) {
        completionResponse = await this.apiClient.post<unknown>(completePath);
      } else {
        completionResponse = await this.apiClient.post<unknown, Record<string, unknown>>(completePath, completePayload);
      }

      const completedTask = tryParseTaskResponse(completionResponse);
      if (completedTask !== undefined) {
        return completedTask;
      }

      const fetchResponse = await this.apiClient.get<unknown>(`${TASK_PATH}/${taskId}`);
      return parseTickTickTask(fetchResponse);
    } catch (error: unknown) {
      throw mapGatewayError("completeTask", error);
    }
  }

  async listProjects(query?: TickTickListProjectsQuery): Promise<TickTickProject[]> {
    try {
      validateListProjectsQuery(query);
      const response = await this.apiClient.get<unknown>(PROJECT_PATH);
      const projects = parseTickTickProjectList(response);

      return filterProjectsForQuery(projects, query);
    } catch (error: unknown) {
      throw mapGatewayError("listProjects", error);
    }
  }

  private async fetchTasksAcrossProjects(): Promise<TickTickTask[]> {
    const projects = await this.listProjects({ includeClosed: true });
    if (projects.length === 0) {
      return [];
    }

    const allTasks: TickTickTask[] = [];
    for (const project of projects) {
      try {
        const tasks = await this.fetchTasksByProjectId(project.id);
        allTasks.push(...tasks);
        // Small delay to respect TickTick API rate limits for sequential project fetches
        await new Promise((resolve) => setTimeout(resolve, 100));
      } catch (error: unknown) {
        // Log individual project failures gracefully during aggregate fetch
        console.error(
          `[ticktick-gateway] Warning: Failed to fetch tasks for project ${project.id} (${project.name}). Skipping.`
        );
      }
    }

    return dedupeTasks(allTasks);
  }

  private async fetchTasksByProjectId(projectId: string): Promise<TickTickTask[]> {
    if (projectId.trim().length === 0) {
      throw new ContractValidationError("ticktick-gateway", "projectId must be a non-empty string.");
    }

    const path = `${PROJECT_PATH}/${encodeURIComponent(projectId)}/data`;
    const response = await this.apiClient.get<unknown>(path);
    const tasksPayload = extractTaskCollection(response);
    return parseTickTickTaskList(tasksPayload);
  }
}

export function createTickTickGateway(apiClient: TickTickApiClient): TickTickGateway {
  return new TickTickApiGateway(apiClient);
}

function validateListProjectsQuery(query: TickTickListProjectsQuery | undefined): void {
  if (query === undefined) {
    return;
  }

  if (query.includeClosed !== undefined && typeof query.includeClosed !== "boolean") {
    throw new ContractValidationError("ticktick-list-projects-query", "includeClosed must be a boolean when provided.");
  }
}

function buildCompleteTaskPayload(input: TickTickCompleteTaskInput): Record<string, unknown> | undefined {
  if (input.completedAt === undefined) {
    return undefined;
  }

  return {
    completedTime: input.completedAt,
  };
}

function tryParseTaskResponse(value: unknown): TickTickTask | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }

  try {
    return parseTickTickTask(value);
  } catch {
    const nested = extractNestedTask(value);
    if (nested === undefined) {
      return undefined;
    }

    return parseTickTickTask(nested);
  }
}

function extractNestedTask(value: unknown): unknown | undefined {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return undefined;
  }

  const record = value as Record<string, unknown>;
  const keys = ["task", "item", "data", "result"];
  for (const key of keys) {
    const nested = record[key];
    if (nested !== undefined && nested !== null) {
      return nested;
    }
  }

  return undefined;
}

function extractTaskCollection(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value;
  }

  if (typeof value !== "object" || value === null) {
    return value;
  }

  const record = value as Record<string, unknown>;
  const directTaskArrays = ["tasks", "items", "data", "taskList"];
  for (const key of directTaskArrays) {
    const candidate = record[key];
    if (Array.isArray(candidate)) {
      return candidate;
    }
  }

  const nestedContainers = ["project", "result"];
  for (const key of nestedContainers) {
    const nested = record[key];
    if (typeof nested !== "object" || nested === null || Array.isArray(nested)) {
      continue;
    }

    const nestedRecord = nested as Record<string, unknown>;
    for (const nestedKey of directTaskArrays) {
      const candidate = nestedRecord[nestedKey];
      if (Array.isArray(candidate)) {
        return candidate;
      }
    }
  }

  return value;
}

function dedupeTasks(tasks: TickTickTask[]): TickTickTask[] {
  const dedupedById = new Map<string, TickTickTask>();

  for (const task of tasks) {
    if (!dedupedById.has(task.id)) {
      dedupedById.set(task.id, task);
    }
  }

  return [...dedupedById.values()];
}

function applyTaskFilters(tasks: TickTickTask[], query: TickTickListTasksQuery): TickTickTask[] {
  const fromTime = query.from === undefined ? undefined : Date.parse(query.from);
  const toTime = query.to === undefined ? undefined : Date.parse(query.to);
  const includeCompleted = query.includeCompleted === true;

  const filtered = tasks.filter((task) => {
    if (!includeCompleted && task.status === "completed") {
      return false;
    }

    if (fromTime === undefined && toTime === undefined) {
      return true;
    }

    const referenceDate = task.dueDate ?? task.startDate ?? task.completedAt;
    if (referenceDate === undefined) {
      return false;
    }

    const time = Date.parse(referenceDate);
    if (Number.isNaN(time)) {
      return false;
    }

    if (fromTime !== undefined && time < fromTime) {
      return false;
    }
    if (toTime !== undefined && time > toTime) {
      return false;
    }

    return true;
  });

  if (query.limit === undefined) {
    return filtered;
  }

  return filtered.slice(0, query.limit);
}

function mapGatewayError(operation: string, error: unknown): TickTickDomainError {
  if (error instanceof TickTickDomainError) {
    return error;
  }

  if (error instanceof ContractValidationError) {
    return new TickTickDomainError({
      category: "validation",
      message: `[${operation}] ${error.message}`,
      retriable: false,
      cause: error,
    });
  }

  if (error instanceof TickTickApiError) {
    const category = categorizeHttpStatus(error.status);
    const context: TickTickErrorContext = {
      category,
      message: `[${operation}] ${error.message}`,
      retriable: error.retryable || isRetriableCategory(category),
      cause: error,
      status: error.status,
    };
    if (error.body !== undefined) {
      context.responseBody = error.body;
    }

    return new TickTickDomainError(context);
  }

  if (error instanceof TickTickApiTimeoutError) {
    return new TickTickDomainError({
      category: "network",
      message: `[${operation}] ${error.message}`,
      retriable: true,
      cause: error,
    });
  }

  if (error instanceof Error) {
    const category: TickTickErrorCategory = isNetworkLikeError(error) ? "network" : "unknown";
    return new TickTickDomainError({
      category,
      message: `[${operation}] ${error.message}`,
      retriable: category === "network",
      cause: error,
    });
  }

  return new TickTickDomainError({
    category: "unknown",
    message: `[${operation}] Unexpected error occurred while calling TickTick API.`,
    retriable: false,
    cause: error,
  });
}

function isNetworkLikeError(error: Error): boolean {
  return error.name === "AbortError" || error.name === "TypeError";
}
