// ============================================================================
// Context injection budget allocator
// Controls how much memory context gets injected per agent turn.
// ============================================================================

/** Total chars allowed per injection. ~1000 tokens at 4 chars/token. */
export const DEFAULT_BUDGET = 4000;

/** Max chars for a single fact value in injection output. */
export const MAX_ITEM_VALUE_LENGTH = 150;

/** Budget allocation weights by section (must sum to 1.0). */
export const SECTION_WEIGHTS = {
  permanent: 0.30,  // identity + stable prefs
  fts: 0.30,        // query-relevant recall
  recent: 0.20,     // recency signal
  vector: 0.20,     // semantic expansion
};

/**
 * Truncate a string to maxLen, appending "..." if truncated.
 * @param {string} value
 * @param {number} maxLen
 * @returns {string}
 */
export function truncateValue(value, maxLen = MAX_ITEM_VALUE_LENGTH) {
  if (!value || typeof value !== "string") return "";
  if (value.length <= maxLen) return value;
  return value.substring(0, maxLen - 3) + "...";
}

/**
 * Format a database row into a display line with truncated values.
 * @param {object} row - Database row with entity/fact_key/fact_value or description/category
 * @param {number} maxValueLen - Max value length for truncation
 * @returns {string|null} Formatted line or null if row is empty
 */
export function formatFactLine(row, maxValueLen = MAX_ITEM_VALUE_LENGTH) {
  if (row.entity && row.fact_key) {
    const val = truncateValue(row.fact_value, maxValueLen);
    return `- **${row.entity}**.${row.fact_key} = ${val}`;
  }
  if (row.description) {
    const desc = truncateValue(row.description, maxValueLen);
    return `- [${row.category || "general"}] ${desc}`;
  }
  return null;
}

/**
 * Create a budget tracker for a single injection cycle.
 * Sections fill in priority order; underflow from one section
 * rolls into the next.
 *
 * @param {number} totalChars - Total character budget
 * @returns {object} Budget tracker
 */
export function createBudget(totalChars = DEFAULT_BUDGET) {
  let remaining = totalChars;
  const allocations = {};

  return {
    get remaining() { return remaining; },
    get total() { return totalChars; },

    /**
     * Attempt to consume chars from the budget.
     * @param {string} section - Section name (permanent, fts, recent, vector)
     * @param {number} chars - Characters to consume
     * @returns {boolean} true if budget allows, false if exhausted
     */
    tryAdd(section, chars) {
      if (chars > remaining) return false;
      remaining -= chars;
      allocations[section] = (allocations[section] || 0) + chars;
      return true;
    },

    /**
     * Get the initial allocation for a section (before any spending).
     * @param {string} section
     * @returns {number}
     */
    sectionBudget(section) {
      const weight = SECTION_WEIGHTS[section] || 0.25;
      return Math.floor(totalChars * weight);
    },

    /**
     * Get a summary of how the budget was spent.
     * @returns {object}
     */
    report() {
      return {
        total: totalChars,
        remaining,
        used: totalChars - remaining,
        allocations: { ...allocations },
      };
    },
  };
}
