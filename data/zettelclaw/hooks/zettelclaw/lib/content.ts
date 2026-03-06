export function contentToText(value: unknown): string {
  if (typeof value === "string") {
    return value.trim()
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => contentToText(item))
      .filter((item) => item.length > 0)
      .join("\n")
      .trim()
  }

  if (!value || typeof value !== "object") {
    return ""
  }

  const record = value as Record<string, unknown>
  const directText = typeof record.text === "string" ? record.text : ""
  if (directText.trim().length > 0) {
    return directText.trim()
  }

  for (const key of ["content", "value"]) {
    if (!(key in record)) {
      continue
    }

    const nested = contentToText(record[key])
    if (nested.length > 0) {
      return nested
    }
  }

  return ""
}
