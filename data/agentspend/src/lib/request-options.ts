const METHOD_TOKEN_PATTERN = /^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/;

export function normalizeMethod(method: string | undefined): string {
  const normalized = (method ?? "GET").trim().toUpperCase();

  if (!normalized || !METHOD_TOKEN_PATTERN.test(normalized)) {
    throw new Error(`Invalid HTTP method: ${method ?? ""}`);
  }

  return normalized;
}

export function parseHeaders(rawHeaders: string[] | undefined): Record<string, string> {
  const parsed: Record<string, string> = {};

  for (const header of rawHeaders ?? []) {
    const separator = header.indexOf(":");
    if (separator === -1) {
      throw new Error(`Invalid header format: ${header}. Expected key:value.`);
    }

    const key = header.slice(0, separator).trim();
    const value = header.slice(separator + 1).trim();

    if (!key || !value) {
      throw new Error(`Invalid header format: ${header}. Expected key:value.`);
    }

    parsed[key] = value;
  }

  return parsed;
}

export function parseBody(rawBody: string | undefined): unknown {
  if (rawBody === undefined) {
    return undefined;
  }

  try {
    return JSON.parse(rawBody);
  } catch {
    return rawBody;
  }
}
