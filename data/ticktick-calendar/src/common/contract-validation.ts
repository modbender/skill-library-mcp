export class ContractValidationError extends Error {
  readonly contract: string;

  constructor(contract: string, message: string) {
    super(`[${contract}] ${message}`);
    this.name = "ContractValidationError";
    this.contract = contract;
  }
}

export type UnknownRecord = Record<string, unknown>;

export function ensureRecord(value: unknown, contract: string): UnknownRecord {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new ContractValidationError(contract, "Expected an object payload.");
  }

  return value as UnknownRecord;
}

export function readRequiredString(record: UnknownRecord, key: string, contract: string): string {
  const value = record[key];
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new ContractValidationError(contract, `Expected '${key}' to be a non-empty string.`);
  }

  return value;
}

export function readOptionalString(record: UnknownRecord, key: string, contract: string): string | undefined {
  const value = record[key];
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "string") {
    throw new ContractValidationError(contract, `Expected '${key}' to be a string when provided.`);
  }

  return value;
}

export function readOptionalBoolean(record: UnknownRecord, key: string, contract: string): boolean | undefined {
  const value = record[key];
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "boolean") {
    throw new ContractValidationError(contract, `Expected '${key}' to be a boolean when provided.`);
  }

  return value;
}

export function readOptionalNumber(record: UnknownRecord, key: string, contract: string): number | undefined {
  const value = record[key];
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new ContractValidationError(contract, `Expected '${key}' to be a finite number when provided.`);
  }

  return value;
}

export function readOptionalStringArray(record: UnknownRecord, key: string, contract: string): string[] | undefined {
  const value = record[key];
  if (value === undefined || value === null) {
    return undefined;
  }
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
    throw new ContractValidationError(contract, `Expected '${key}' to be an array of strings when provided.`);
  }

  return value;
}

export function readIsoDateString(record: UnknownRecord, key: string, contract: string): string | undefined {
  const value = readOptionalString(record, key, contract);
  if (value === undefined) {
    return undefined;
  }

  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) {
    throw new ContractValidationError(contract, `Expected '${key}' to be a valid ISO date string.`);
  }

  return value;
}
