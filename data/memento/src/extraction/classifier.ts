/**
 * Visibility Classifier
 *
 * Determines whether a fact should be private, shared, or secret.
 * The LLM suggestion is trusted but overridden by hard keyword/category rules.
 *
 * Visibility levels:
 *   shared  — user preferences, family info, general knowledge (default)
 *   private — agent-specific operational details
 *   secret  — credentials, medical info, financial details (never propagated)
 */

// ---------------------------------------------------------------------------
// Secret rules (hard overrides — never trust LLM with these)
// ---------------------------------------------------------------------------

const SECRET_CATEGORIES = new Set([
  "credentials",
  "medical",
  "financial",
]);

const SECRET_KEYWORDS = [
  "password",
  "passwd",
  "passphrase",
  "secret",
  "api key",
  "apikey",
  "api_key",
  "access token",
  "access_token",
  "auth token",
  "auth_token",
  "private key",
  "private_key",
  "ssh key",
  "ssh_key",
  "credential",
  "secret key",
  "client secret",
  "diagnosis",
  "medical",
  "prescription",
  "medication",
  "symptom",
  "disease",
  "illness",
  "ssn",
  "social security",
  "credit card",
  "card number",
  "bank account",
  "routing number",
  "iban",
  "pin code",
  "pin number",
];

// ---------------------------------------------------------------------------
// Private rules
// ---------------------------------------------------------------------------

const PRIVATE_CATEGORIES = new Set([
  "operational",
  "workflow",
  "internal",
]);

const PRIVATE_KEYWORDS = [
  "workflow",
  "operational",
  "internal process",
  "internal procedure",
  "pipeline step",
  "agent instruction",
  "system prompt",
];

// ---------------------------------------------------------------------------
// Classifier
// ---------------------------------------------------------------------------

/**
 * Classify the visibility of a fact.
 *
 * @param category   - The LLM-assigned category (e.g. "preference", "medical")
 * @param content    - The full fact text
 * @param llmSuggested - The visibility level the LLM proposed
 * @returns "private" | "shared" | "secret"
 */
export function classifyVisibility(
  category: string,
  content: string,
  llmSuggested: string,
): "private" | "shared" | "secret" {
  const lowerContent = content.toLowerCase();
  const lowerCategory = category.toLowerCase();

  // Secret: hard category match
  if (SECRET_CATEGORIES.has(lowerCategory)) return "secret";

  // Secret: keyword match in content
  if (SECRET_KEYWORDS.some((kw) => lowerContent.includes(kw))) return "secret";

  // Private: hard category match
  if (PRIVATE_CATEGORIES.has(lowerCategory)) return "private";

  // Private: keyword match
  if (PRIVATE_KEYWORDS.some((kw) => lowerContent.includes(kw))) return "private";

  // Trust LLM suggestion if it's a valid value
  if (
    llmSuggested === "private" ||
    llmSuggested === "shared" ||
    llmSuggested === "secret"
  ) {
    return llmSuggested;
  }

  // Default
  return "shared";
}
