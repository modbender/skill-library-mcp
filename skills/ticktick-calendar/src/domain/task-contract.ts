import {
  ContractValidationError,
  ensureRecord,
  readIsoDateString,
  readOptionalBoolean,
  readOptionalNumber,
  readOptionalString,
  readOptionalStringArray,
  readRequiredString,
  UnknownRecord,
} from "../common/contract-validation.js";

const TASK_CONTRACT = "ticktick-task";
const TASK_INPUT_CONTRACT = "ticktick-task-input";

export const TICKTICK_TASK_PRIORITIES = [0, 1, 3, 5] as const;

export type TickTickTaskPriority = (typeof TICKTICK_TASK_PRIORITIES)[number];
export type TickTickTaskStatus = "active" | "completed";

export interface TickTickTask {
  id: string;
  projectId: string;
  title: string;
  content?: string;
  description?: string;
  startDate?: string;
  dueDate?: string;
  isAllDay?: boolean;
  priority?: TickTickTaskPriority;
  status: TickTickTaskStatus;
  tags?: string[];
  completedAt?: string;
  timeZone?: string;
}

export interface TickTickCreateTaskInput {
  projectId: string;
  title: string;
  content?: string;
  description?: string;
  startDate?: string;
  dueDate?: string;
  isAllDay?: boolean;
  priority?: TickTickTaskPriority;
  tags?: string[];
}

export interface TickTickListTasksQuery {
  projectId?: string;
  from?: string;
  to?: string;
  includeCompleted?: boolean;
  limit?: number;
}

export interface TickTickUpdateTaskInput {
  taskId: string;
  title?: string;
  content?: string;
  description?: string;
  startDate?: string | null;
  dueDate?: string | null;
  isAllDay?: boolean;
  priority?: TickTickTaskPriority;
  tags?: string[];
}

export interface TickTickCompleteTaskInput {
  taskId: string;
  completedAt?: string;
}

export function parseTickTickTask(value: unknown): TickTickTask {
  const record = ensureRecord(value, TASK_CONTRACT);

  const id = readRequiredString(record, "id", TASK_CONTRACT);
  const projectId = readRequiredString(record, "projectId", TASK_CONTRACT);
  const title = readStringFromAliases(record, ["title", "content"], TASK_CONTRACT);
  const content = readOptionalString(record, "content", TASK_CONTRACT);
  const description = readOptionalStringFromAliases(record, ["description", "desc"], TASK_CONTRACT);
  const startDate = readIsoDateString(record, "startDate", TASK_CONTRACT);
  const dueDate = readIsoDateString(record, "dueDate", TASK_CONTRACT);
  const isAllDay = readOptionalBoolean(record, "isAllDay", TASK_CONTRACT);
  const priority = readTaskPriority(record, "priority", TASK_CONTRACT);
  const tags = readOptionalStringArray(record, "tags", TASK_CONTRACT);
  const completedAt = readIsoDateStringFromAliases(record, ["completedAt", "completedTime"], TASK_CONTRACT);
  const timeZone = readOptionalString(record, "timeZone", TASK_CONTRACT);

  const task: TickTickTask = {
    id,
    projectId,
    title,
    status: readTaskStatus(record),
  };

  if (content !== undefined) {
    task.content = content;
  }
  if (description !== undefined) {
    task.description = description;
  }
  if (startDate !== undefined) {
    task.startDate = startDate;
  }
  if (dueDate !== undefined) {
    task.dueDate = dueDate;
  }
  if (isAllDay !== undefined) {
    task.isAllDay = isAllDay;
  }
  if (priority !== undefined) {
    task.priority = priority;
  }
  if (tags !== undefined) {
    task.tags = tags;
  }
  if (completedAt !== undefined) {
    task.completedAt = completedAt;
  }
  if (timeZone !== undefined) {
    task.timeZone = timeZone;
  }

  return task;
}

export function parseTickTickTaskList(value: unknown): TickTickTask[] {
  if (!Array.isArray(value)) {
    throw new ContractValidationError(TASK_CONTRACT, "Expected a task list array.");
  }

  return value.map((item, index) => {
    try {
      return parseTickTickTask(item);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      throw new ContractValidationError(TASK_CONTRACT, `Invalid task at index ${index}: ${message}`);
    }
  });
}

export function validateCreateTaskInput(input: TickTickCreateTaskInput): TickTickCreateTaskInput {
  assertNonEmpty(input.projectId, "projectId");
  assertNonEmpty(input.title, "title");
  assertOptionalIsoDate(input.startDate, "startDate");
  assertOptionalIsoDate(input.dueDate, "dueDate");
  assertPriority(input.priority, "priority");
  assertDateOrder(input.startDate, input.dueDate);

  return input;
}

export function toCreateTaskPayload(input: TickTickCreateTaskInput): Record<string, unknown> {
  validateCreateTaskInput(input);

  return compactObject({
    projectId: input.projectId,
    title: input.title,
    content: input.content,
    desc: input.description,
    startDate: input.startDate,
    dueDate: input.dueDate,
    isAllDay: input.isAllDay,
    priority: input.priority,
    tags: input.tags,
  });
}

export function parseListTasksQuery(value: unknown): TickTickListTasksQuery {
  const record = ensureRecord(value, "ticktick-list-tasks-query");

  const projectId = readOptionalString(record, "projectId", "ticktick-list-tasks-query");
  const from = readIsoDateString(record, "from", "ticktick-list-tasks-query");
  const to = readIsoDateString(record, "to", "ticktick-list-tasks-query");
  const includeCompleted = readOptionalBoolean(record, "includeCompleted", "ticktick-list-tasks-query");
  const limit = readOptionalNumber(record, "limit", "ticktick-list-tasks-query");

  if (limit !== undefined && (!Number.isInteger(limit) || limit <= 0)) {
    throw new ContractValidationError("ticktick-list-tasks-query", "limit must be a positive integer.");
  }

  assertDateOrder(from, to);

  const parsedQuery: TickTickListTasksQuery = {};
  if (projectId !== undefined) {
    parsedQuery.projectId = projectId;
  }
  if (from !== undefined) {
    parsedQuery.from = from;
  }
  if (to !== undefined) {
    parsedQuery.to = to;
  }
  if (includeCompleted !== undefined) {
    parsedQuery.includeCompleted = includeCompleted;
  }
  if (limit !== undefined) {
    parsedQuery.limit = limit;
  }

  return parsedQuery;
}

export function validateUpdateTaskInput(input: TickTickUpdateTaskInput): TickTickUpdateTaskInput {
  assertNonEmpty(input.taskId, "taskId");
  assertNullableIsoDate(input.startDate, "startDate");
  assertNullableIsoDate(input.dueDate, "dueDate");
  assertPriority(input.priority, "priority");

  const hasMutableField =
    input.title !== undefined ||
    input.content !== undefined ||
    input.description !== undefined ||
    input.startDate !== undefined ||
    input.dueDate !== undefined ||
    input.isAllDay !== undefined ||
    input.priority !== undefined ||
    input.tags !== undefined;

  if (!hasMutableField) {
    throw new ContractValidationError(TASK_INPUT_CONTRACT, "Update input must include at least one mutable field.");
  }

  return input;
}

export function toUpdateTaskPayload(input: TickTickUpdateTaskInput): Record<string, unknown> {
  validateUpdateTaskInput(input);

  return compactObject({
    title: input.title,
    content: input.content,
    desc: input.description,
    startDate: input.startDate,
    dueDate: input.dueDate,
    isAllDay: input.isAllDay,
    priority: input.priority,
    tags: input.tags,
  });
}

export function validateCompleteTaskInput(input: TickTickCompleteTaskInput): TickTickCompleteTaskInput {
  assertNonEmpty(input.taskId, "taskId");
  assertOptionalIsoDate(input.completedAt, "completedAt");
  return input;
}

function readTaskStatus(record: UnknownRecord): TickTickTaskStatus {
  const value = record.status;

  if (typeof value === "string") {
    if (value === "completed" || value === "done") {
      return "completed";
    }
    if (value === "active" || value === "open") {
      return "active";
    }
  }

  if (typeof value === "number") {
    if (value === 2) {
      return "completed";
    }
    if (value === 0) {
      return "active";
    }
  }

  return "active";
}

function readTaskPriority(record: UnknownRecord, key: string, contract: string): TickTickTaskPriority | undefined {
  const value = readOptionalNumber(record, key, contract);
  if (value === undefined) {
    return undefined;
  }

  assertPriority(value, key);
  return value as TickTickTaskPriority;
}

function readStringFromAliases(record: UnknownRecord, keys: string[], contract: string): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }

  throw new ContractValidationError(contract, `Missing required string in aliases: ${keys.join(", ")}.`);
}

function readOptionalStringFromAliases(record: UnknownRecord, keys: string[], contract: string): string | undefined {
  for (const key of keys) {
    const value = record[key];
    if (value === undefined || value === null) {
      continue;
    }
    if (typeof value !== "string") {
      throw new ContractValidationError(contract, `Expected '${key}' to be a string.`);
    }
    return value;
  }

  return undefined;
}

function readIsoDateStringFromAliases(record: UnknownRecord, keys: string[], contract: string): string | undefined {
  for (const key of keys) {
    const value = record[key];
    if (value === undefined || value === null) {
      continue;
    }
    if (typeof value !== "string") {
      throw new ContractValidationError(contract, `Expected '${key}' to be a string.`);
    }
    const parsed = Date.parse(value);
    if (Number.isNaN(parsed)) {
      throw new ContractValidationError(contract, `Expected '${key}' to be an ISO date string.`);
    }
    return value;
  }

  return undefined;
}

function assertNonEmpty(value: string, key: string): void {
  if (value.trim().length === 0) {
    throw new ContractValidationError(TASK_INPUT_CONTRACT, `${key} must be a non-empty string.`);
  }
}

function assertOptionalIsoDate(value: string | undefined, key: string): void {
  if (value === undefined) {
    return;
  }

  if (Number.isNaN(Date.parse(value))) {
    throw new ContractValidationError(TASK_INPUT_CONTRACT, `${key} must be a valid ISO date string.`);
  }
}

function assertNullableIsoDate(value: string | null | undefined, key: string): void {
  if (value === undefined || value === null) {
    return;
  }

  assertOptionalIsoDate(value, key);
}

function assertDateOrder(startDate: string | undefined, dueDate: string | undefined): void {
  if (startDate === undefined || dueDate === undefined) {
    return;
  }

  if (Date.parse(startDate) > Date.parse(dueDate)) {
    throw new ContractValidationError(TASK_INPUT_CONTRACT, "startDate cannot be later than dueDate.");
  }
}

function assertPriority(value: number | undefined, key: string): void {
  if (value === undefined) {
    return;
  }

  if (!TICKTICK_TASK_PRIORITIES.includes(value as TickTickTaskPriority)) {
    throw new ContractValidationError(
      TASK_INPUT_CONTRACT,
      `${key} must be one of: ${TICKTICK_TASK_PRIORITIES.join(", ")}.`
    );
  }
}

function compactObject(record: Record<string, unknown>): Record<string, unknown> {
  const compacted: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(record)) {
    if (value !== undefined) {
      compacted[key] = value;
    }
  }

  return compacted;
}
