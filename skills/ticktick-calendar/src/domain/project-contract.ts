import {
  ContractValidationError,
  ensureRecord,
  readOptionalBoolean,
  readOptionalNumber,
  readOptionalString,
  readRequiredString,
  UnknownRecord,
} from "../common/contract-validation.js";

const PROJECT_CONTRACT = "ticktick-project";

export interface TickTickProject {
  id: string;
  name: string;
  color?: string;
  groupId?: string;
  viewMode?: string;
  sortOrder?: number;
  closed: boolean;
}

export interface TickTickListProjectsQuery {
  includeClosed?: boolean;
}

export function parseTickTickProject(value: unknown): TickTickProject {
  const record = ensureRecord(value, PROJECT_CONTRACT);

  const id = readRequiredString(record, "id", PROJECT_CONTRACT);
  const name = readStringFromAliases(record, ["name", "projectName"], PROJECT_CONTRACT);
  const color = readOptionalString(record, "color", PROJECT_CONTRACT);
  const groupId = readOptionalString(record, "groupId", PROJECT_CONTRACT);
  const viewMode = readOptionalString(record, "viewMode", PROJECT_CONTRACT);
  const sortOrder = readOptionalNumber(record, "sortOrder", PROJECT_CONTRACT);
  const closed = readClosedFlag(record);

  const project: TickTickProject = {
    id,
    name,
    closed,
  };

  if (color !== undefined) {
    project.color = color;
  }
  if (groupId !== undefined) {
    project.groupId = groupId;
  }
  if (viewMode !== undefined) {
    project.viewMode = viewMode;
  }
  if (sortOrder !== undefined) {
    project.sortOrder = sortOrder;
  }

  return project;
}

export function parseTickTickProjectList(value: unknown): TickTickProject[] {
  if (Array.isArray(value)) {
    return value.map((item, index) => parseProjectWithIndex(item, index));
  }

  const record = ensureRecord(value, PROJECT_CONTRACT);
  const projects = readArrayFromAliases(record, ["projects", "items"]);

  return projects.map((item, index) => parseProjectWithIndex(item, index));
}

export function filterProjectsForQuery(
  projects: TickTickProject[],
  query: TickTickListProjectsQuery | undefined
): TickTickProject[] {
  if (query?.includeClosed === true) {
    return projects;
  }

  return projects.filter((project) => !project.closed);
}

function parseProjectWithIndex(value: unknown, index: number): TickTickProject {
  try {
    return parseTickTickProject(value);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    throw new ContractValidationError(PROJECT_CONTRACT, `Invalid project at index ${index}: ${message}`);
  }
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

function readClosedFlag(record: UnknownRecord): boolean {
  const closed = readOptionalBoolean(record, "closed", PROJECT_CONTRACT);
  if (closed !== undefined) {
    return closed;
  }

  const status = readOptionalString(record, "status", PROJECT_CONTRACT);
  if (status === "closed" || status === "archived") {
    return true;
  }
  if (status === "open" || status === "active") {
    return false;
  }

  return false;
}

function readArrayFromAliases(record: UnknownRecord, aliases: string[]): unknown[] {
  for (const alias of aliases) {
    const value = record[alias];
    if (value === undefined || value === null) {
      continue;
    }

    if (!Array.isArray(value)) {
      throw new ContractValidationError(PROJECT_CONTRACT, `Expected '${alias}' to be an array.`);
    }

    return value;
  }

  throw new ContractValidationError(PROJECT_CONTRACT, "Expected project list array.");
}
