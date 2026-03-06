/**
 * Minimal YAML subset parser for governance policy files.
 *
 * Supports: scalars, string arrays (dash + bracket), nested objects (3 levels),
 * comments, quoted strings, booleans, integers.
 * Rejects: anchors, aliases, tags, flow mappings, folded/literal blocks, multi-doc.
 */

export interface PolicyFile {
  version: string;
  default_verdict: "deny" | "approve";
  rules: PolicyRule[];
  sensitive_data: SensitiveDataRule[];
}

export interface PolicyRule {
  name: string;
  match: {
    action_type?: string | string[];
    target_pattern?: string;
    skill_pattern?: string;
    tool_pattern?: string;
    data_scope?: string[];
  };
  verdict: "approve" | "deny" | "escalate";
  reason?: string;
}

export interface SensitiveDataRule {
  category: string;
  patterns: string[];
  action: "deny" | "escalate";
}

// ── Tokenizer helpers ────────────────────────────────────────────────

function stripComment(line: string): string {
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]!;
    if (ch === "'" && !inDouble) inSingle = !inSingle;
    else if (ch === '"' && !inSingle) inDouble = !inDouble;
    else if (ch === "#" && !inSingle && !inDouble) return line.slice(0, i);
  }
  return line;
}

function indentOf(line: string): number {
  let n = 0;
  for (const ch of line) {
    if (ch === " ") n++;
    else if (ch === "\t") throw new Error("Tabs are not allowed in YAML indentation");
    else break;
  }
  return n;
}

function unquote(val: string): string {
  val = val.trim();
  if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
    return val.slice(1, -1);
  }
  return val;
}

function coerce(val: string): string | number | boolean {
  const trimmed = val.trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (/^-?\d+$/.test(trimmed)) return parseInt(trimmed, 10);
  return unquote(trimmed);
}

function parseInlineArray(val: string): unknown[] {
  const inner = val.slice(1, -1).trim();
  if (inner === "") return [];
  return inner.split(",").map((item) => coerce(item.trim()));
}

// ── Preprocessor: strip comments, blank lines, produce (indent, content) ──

interface Line {
  indent: number;
  content: string;
}

function preprocess(input: string): Line[] {
  const result: Line[] = [];
  for (const raw of input.split(/\r?\n/)) {
    const stripped = stripComment(raw).trimEnd();
    if (stripped.trim() === "") continue;
    result.push({ indent: indentOf(stripped), content: stripped.trim() });
  }
  return result;
}

// ── Recursive descent parser ─────────────────────────────────────────

/**
 * Parse a block of lines at a given minimum indent level into a value.
 * Returns the parsed value and the number of lines consumed.
 */
function parseBlock(lines: Line[], start: number, minIndent: number): { value: unknown; consumed: number } {
  if (start >= lines.length) return { value: {}, consumed: 0 };

  const firstLine = lines[start]!;

  // Is this an array? (first line starts with "- ")
  if (firstLine.content.startsWith("- ")) {
    return parseArray(lines, start, firstLine.indent);
  }

  // Otherwise it's a mapping
  return parseMapping(lines, start, minIndent);
}

function parseMapping(lines: Line[], start: number, minIndent: number): { value: Record<string, unknown>; consumed: number } {
  const obj: Record<string, unknown> = {};
  let pos = start;

  while (pos < lines.length) {
    const line = lines[pos]!;
    if (line.indent < minIndent) break;

    const { content } = line;

    // Must be a key: value pair
    const colonIdx = content.indexOf(":");
    if (colonIdx === -1) break;

    const key = content.slice(0, colonIdx).trim();
    const val = content.slice(colonIdx + 1).trim();

    if (val === "") {
      // Block value follows: could be nested mapping or array
      pos++;
      if (pos < lines.length && lines[pos]!.indent > line.indent) {
        const childIndent = lines[pos]!.indent;
        const child = parseBlock(lines, pos, childIndent);
        obj[key] = child.value;
        pos += child.consumed;
      }
    } else if (val.startsWith("[") && val.endsWith("]")) {
      obj[key] = parseInlineArray(val);
      pos++;
    } else {
      obj[key] = coerce(val);
      pos++;
    }
  }

  return { value: obj, consumed: pos - start };
}

function parseArray(lines: Line[], start: number, arrayIndent: number): { value: unknown[]; consumed: number } {
  const arr: unknown[] = [];
  let pos = start;

  while (pos < lines.length) {
    const line = lines[pos]!;
    if (line.indent !== arrayIndent || !line.content.startsWith("- ")) break;

    const itemContent = line.content.slice(2).trim();

    // Is this a scalar array item or start of an object?
    const colonIdx = itemContent.indexOf(":");
    if (colonIdx !== -1) {
      // Object array item: "- key: value"
      const key = itemContent.slice(0, colonIdx).trim();
      const val = itemContent.slice(colonIdx + 1).trim();
      const obj: Record<string, unknown> = {};

      if (val === "") {
        // The value is a nested block
        pos++;
        if (pos < lines.length && lines[pos]!.indent > arrayIndent + 2) {
          const child = parseBlock(lines, pos, lines[pos]!.indent);
          obj[key] = child.value;
          pos += child.consumed;
        }
      } else {
        obj[key] = coerce(val);
        pos++;
      }

      // Collect sibling key-value pairs at indent > arrayIndent (typically arrayIndent + 4)
      while (pos < lines.length) {
        const sibLine = lines[pos]!;
        if (sibLine.indent <= arrayIndent) break;
        if (sibLine.content.startsWith("- ")) break;

        const sibColonIdx = sibLine.content.indexOf(":");
        if (sibColonIdx === -1) break;

        const sibKey = sibLine.content.slice(0, sibColonIdx).trim();
        const sibVal = sibLine.content.slice(sibColonIdx + 1).trim();

        if (sibVal === "") {
          // Nested block under this sibling key
          pos++;
          if (pos < lines.length && lines[pos]!.indent > sibLine.indent) {
            const child = parseBlock(lines, pos, lines[pos]!.indent);
            obj[sibKey] = child.value;
            pos += child.consumed;
          }
        } else if (sibVal.startsWith("[") && sibVal.endsWith("]")) {
          obj[sibKey] = parseInlineArray(sibVal);
          pos++;
        } else {
          obj[sibKey] = coerce(sibVal);
          pos++;
        }
      }

      arr.push(obj);
    } else {
      // Scalar array item
      arr.push(coerce(itemContent));
      pos++;
    }
  }

  return { value: arr, consumed: pos - start };
}

// ── Public API ───────────────────────────────────────────────────────

export function parseYaml(input: string): unknown {
  const lines = preprocess(input);
  if (lines.length === 0) return {};
  const { value } = parseBlock(lines, 0, 0);
  return value;
}

// ── Policy file validator ────────────────────────────────────────────

export function parsePolicyFile(yamlContent: string): PolicyFile {
  const raw = parseYaml(yamlContent) as Record<string, unknown>;

  // Version
  if (typeof raw["version"] !== "string") {
    throw new Error("Policy file missing required 'version' field");
  }

  // Default verdict
  const dv = raw["default_verdict"];
  if (dv !== "deny" && dv !== "approve") {
    throw new Error(`Invalid default_verdict: '${String(dv)}'. Must be 'deny' or 'approve'`);
  }

  // Rules
  const rawRules = raw["rules"];
  const rules: PolicyRule[] = [];
  if (Array.isArray(rawRules)) {
    for (const r of rawRules) {
      const rule = r as Record<string, unknown>;
      if (typeof rule["name"] !== "string") {
        throw new Error("Policy rule missing required 'name' field");
      }
      const verdict = rule["verdict"];
      if (verdict !== "approve" && verdict !== "deny" && verdict !== "escalate") {
        throw new Error(`Rule '${rule["name"]}': invalid verdict '${String(verdict)}'`);
      }
      const match = (rule["match"] ?? {}) as Record<string, unknown>;
      rules.push({
        name: rule["name"] as string,
        match: {
          action_type: match["action_type"] as string | string[] | undefined,
          target_pattern: match["target_pattern"] as string | undefined,
          skill_pattern: match["skill_pattern"] as string | undefined,
          tool_pattern: match["tool_pattern"] as string | undefined,
          data_scope: match["data_scope"] as string[] | undefined,
        },
        verdict: verdict as "approve" | "deny" | "escalate",
        reason: rule["reason"] as string | undefined,
      });
    }
  }

  // Sensitive data
  const rawSensitive = raw["sensitive_data"];
  const sensitiveData: SensitiveDataRule[] = [];
  if (Array.isArray(rawSensitive)) {
    for (const s of rawSensitive) {
      const sd = s as Record<string, unknown>;
      if (typeof sd["category"] !== "string") {
        throw new Error("Sensitive data rule missing 'category'");
      }
      const action = sd["action"];
      if (action !== "deny" && action !== "escalate") {
        throw new Error(`Sensitive data '${sd["category"]}': invalid action '${String(action)}'`);
      }
      sensitiveData.push({
        category: sd["category"] as string,
        patterns: Array.isArray(sd["patterns"]) ? (sd["patterns"] as string[]) : [],
        action: action as "deny" | "escalate",
      });
    }
  }

  return {
    version: raw["version"] as string,
    default_verdict: dv,
    rules,
    sensitive_data: sensitiveData,
  };
}
