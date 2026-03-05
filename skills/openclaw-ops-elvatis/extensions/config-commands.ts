/**
 * openclaw-ops-elvatis Config Commands
 *
 * /config [plugin] - Configuration viewer/validator
 *   - Show current config (all or by plugin)
 *   - Validate against schema
 *   - Diff against defaults
 *   - Environment variable resolution
 *   - Secret masking
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { expandHome, readJsonSafe } from "../src/utils.js";

/** Patterns that indicate a value should be masked in output. */
const SECRET_KEY_PATTERNS = [
  /api[_-]?key/i,
  /secret/i,
  /token/i,
  /password/i,
  /credential/i,
  /auth/i,
  /private[_-]?key/i,
];

/** Check whether a key name looks like it holds a secret. */
function isSecretKey(key: string): boolean {
  return SECRET_KEY_PATTERNS.some((re) => re.test(key));
}

/** Mask a string value, showing only the first 4 chars if long enough. */
function maskValue(value: string): string {
  if (value.length <= 4) return "****";
  return value.slice(0, 4) + "****";
}

/**
 * Recursively walk a config object and mask values whose keys match
 * secret patterns. Returns a new object (does not mutate the original).
 */
function maskSecrets(obj: any): any {
  if (obj === null || obj === undefined) return obj;
  if (typeof obj !== "object") return obj;
  if (Array.isArray(obj)) return obj.map((v) => maskSecrets(v));

  const result: Record<string, any> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (isSecretKey(key) && typeof value === "string" && value.length > 0) {
      result[key] = maskValue(value);
    } else if (typeof value === "object" && value !== null) {
      result[key] = maskSecrets(value);
    } else {
      result[key] = value;
    }
  }
  return result;
}

/**
 * Extract default values from a JSON Schema `properties` block.
 * Returns a flat object of { propertyName: defaultValue }.
 */
function extractDefaults(properties: Record<string, any>): Record<string, any> {
  const defaults: Record<string, any> = {};
  for (const [key, schema] of Object.entries(properties)) {
    if (schema && "default" in schema) {
      defaults[key] = schema.default;
    }
  }
  return defaults;
}

/**
 * Compare actual config values against schema defaults and return
 * lines describing each property's state (default, overridden, or extra).
 */
function diffAgainstDefaults(
  config: Record<string, any>,
  defaults: Record<string, any>,
  schemaProps: Record<string, any>,
): string[] {
  const lines: string[] = [];
  const allKeys = new Set([...Object.keys(defaults), ...Object.keys(config)]);

  for (const key of [...allKeys].sort()) {
    const hasDefault = key in defaults;
    const hasValue = key in config;
    const inSchema = key in schemaProps;

    if (hasValue && hasDefault) {
      const actual = config[key];
      const def = defaults[key];
      if (JSON.stringify(actual) === JSON.stringify(def)) {
        lines.push(`  ${key}: ${JSON.stringify(actual)} (default)`);
      } else {
        lines.push(`  ${key}: ${JSON.stringify(actual)} (overridden, default: ${JSON.stringify(def)})`);
      }
    } else if (hasValue && !hasDefault && inSchema) {
      lines.push(`  ${key}: ${JSON.stringify(config[key])} (no default in schema)`);
    } else if (hasValue && !inSchema) {
      lines.push(`  ${key}: ${JSON.stringify(config[key])} (extra - not in schema)`);
    } else if (!hasValue && hasDefault) {
      lines.push(`  ${key}: (not set, default: ${JSON.stringify(defaults[key])})`);
    }
  }

  return lines;
}

/**
 * Validate config against schema properties. Returns a list of warnings.
 * This is a lightweight check - validates types and required-ness, not a
 * full JSON Schema validator.
 */
function validateConfig(
  config: Record<string, any>,
  schemaProps: Record<string, any>,
  additionalProperties: boolean,
): string[] {
  const warnings: string[] = [];

  // Check for unknown keys (when additionalProperties is false)
  if (!additionalProperties) {
    for (const key of Object.keys(config)) {
      if (!(key in schemaProps)) {
        warnings.push(`Unknown property "${key}" (not in schema)`);
      }
    }
  }

  // Type-check known properties
  for (const [key, schema] of Object.entries(schemaProps)) {
    if (!(key in config)) continue;
    const value = config[key];
    const expectedType = (schema as any)?.type;
    if (!expectedType) continue;

    const actualType = Array.isArray(value) ? "array" : typeof value;
    if (expectedType !== actualType) {
      warnings.push(`"${key}": expected ${expectedType}, got ${actualType}`);
    }
  }

  return warnings;
}

/**
 * Find and read the plugin config for a given plugin name.
 * Searches the openclaw config directory for plugin configs.
 */
function loadPluginConfig(
  pluginName: string,
  workspace: string,
): { config: Record<string, any> | null; source: string } {
  // Check the main openclaw config file
  const mainConfigPath = expandHome("~/.openclaw/config.json");
  const mainConfig = readJsonSafe<Record<string, any> | null>(mainConfigPath, null);

  if (mainConfig?.plugins?.[pluginName]) {
    return { config: mainConfig.plugins[pluginName], source: mainConfigPath };
  }

  // Check plugin's own config
  const pluginDir = path.join(workspace, pluginName);
  const pluginConfigPath = path.join(pluginDir, "openclaw.plugin.json");
  if (fs.existsSync(pluginConfigPath)) {
    const manifest = readJsonSafe<Record<string, any>>(pluginConfigPath, {});
    return { config: manifest, source: pluginConfigPath };
  }

  return { config: null, source: "(not found)" };
}

/**
 * Load the plugin manifest (openclaw.plugin.json) for a specific plugin
 * from the workspace.
 */
function loadPluginManifest(
  pluginName: string,
  workspace: string,
): Record<string, any> | null {
  // Direct match
  const direct = path.join(workspace, pluginName, "openclaw.plugin.json");
  if (fs.existsSync(direct)) {
    return readJsonSafe<Record<string, any> | null>(direct, null);
  }

  // Scan workspace for matching plugin
  try {
    const dirs = fs.readdirSync(workspace).filter((d) => d.startsWith("openclaw-"));
    for (const dir of dirs) {
      const manifestPath = path.join(workspace, dir, "openclaw.plugin.json");
      if (!fs.existsSync(manifestPath)) continue;
      const manifest = readJsonSafe<Record<string, any> | null>(manifestPath, null);
      if (manifest?.id === pluginName || dir === pluginName) {
        return manifest;
      }
    }
  } catch {
    // workspace not readable
  }

  return null;
}

export function registerConfigCommands(api: any, workspace: string) {
  // ========================================
  // /config [plugin] - Configuration viewer/validator
  // ========================================
  api.registerCommand({
    name: "config",
    description: "Show and validate configuration (usage: /config [plugin-name])",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (args: string) => {
      const pluginName = (args ?? "").trim();
      const lines: string[] = [];

      if (pluginName) {
        // ── Single plugin config ─────────────────────────────────────
        return showPluginConfig(pluginName, workspace, lines);
      }

      // ── Overview: all plugin configs ───────────────────────────────
      lines.push("Configuration Overview");
      lines.push("");

      // 1. Environment info
      lines.push("ENVIRONMENT");
      lines.push(`  Platform: ${os.platform()} ${os.arch()}`);
      lines.push(`  Node: ${process.version}`);
      lines.push(`  Home: ${os.homedir()}`);
      lines.push(`  Workspace: ${workspace}`);

      const openclawDir = expandHome("~/.openclaw");
      lines.push(`  OpenClaw dir: ${openclawDir}`);
      lines.push(`  Config file: ${path.join(openclawDir, "config.json")}`);

      // 2. Main config file
      lines.push("");
      lines.push("MAIN CONFIG");
      const mainConfigPath = path.join(openclawDir, "config.json");
      const mainConfig = readJsonSafe<Record<string, any> | null>(mainConfigPath, null);

      if (mainConfig) {
        const masked = maskSecrets(mainConfig);
        const configStr = JSON.stringify(masked, null, 2);
        for (const line of configStr.split("\n")) {
          lines.push(`  ${line}`);
        }
      } else {
        lines.push("  (not found or unreadable)");
      }

      // 3. Per-plugin configs from workspace
      lines.push("");
      lines.push("PLUGIN CONFIGS");

      try {
        const dirs = fs
          .readdirSync(workspace)
          .filter(
            (d) =>
              d.startsWith("openclaw-") &&
              fs.existsSync(path.join(workspace, d, "openclaw.plugin.json")),
          )
          .sort();

        if (dirs.length === 0) {
          lines.push("  (no plugins found in workspace)");
        }

        for (const dir of dirs) {
          const manifest = readJsonSafe<Record<string, any>>(
            path.join(workspace, dir, "openclaw.plugin.json"),
            {},
          );
          const pluginId = manifest.id ?? dir;
          const version = manifest.version ?? "?";

          // Check if main config has overrides for this plugin
          const overrides = mainConfig?.plugins?.[pluginId];
          const hasOverrides = overrides && Object.keys(overrides).length > 0;

          const schema = manifest.configSchema;
          const hasSchema = schema?.properties && Object.keys(schema.properties).length > 0;

          let status = "OK";
          if (hasSchema && hasOverrides) {
            const warnings = validateConfig(
              overrides,
              schema.properties,
              schema.additionalProperties !== false ? true : false,
            );
            status = warnings.length > 0 ? `${warnings.length} warning(s)` : "OK";
          }

          lines.push(`  ${pluginId} v${version} [${status}]`);
          if (hasOverrides) {
            lines.push(`    Overrides: ${JSON.stringify(maskSecrets(overrides))}`);
          }
        }
      } catch {
        lines.push("  (workspace not readable)");
      }

      // 4. Relevant environment variables
      lines.push("");
      lines.push("ENV VARS");
      const relevantEnvPrefixes = ["OPENCLAW", "OPENAI", "ANTHROPIC", "AZURE"];
      const envVars: string[] = [];
      for (const [key, value] of Object.entries(process.env)) {
        if (relevantEnvPrefixes.some((prefix) => key.toUpperCase().startsWith(prefix))) {
          const masked = isSecretKey(key) && value ? maskValue(value) : (value ?? "");
          envVars.push(`  ${key}=${masked}`);
        }
      }
      if (envVars.length > 0) {
        for (const v of envVars.sort()) lines.push(v);
      } else {
        lines.push("  (none detected)");
      }

      lines.push("");
      lines.push("Use /config <plugin-name> for detailed plugin config and validation");

      return { text: lines.join("\n") };
    },
  });
}

/**
 * Show detailed config for a single plugin: config values, schema validation,
 * diff against defaults, and resolved paths.
 */
function showPluginConfig(
  pluginName: string,
  workspace: string,
  lines: string[],
): { text: string } {
  lines.push(`Config: ${pluginName}`);
  lines.push("");

  // Load manifest (for schema)
  const manifest = loadPluginManifest(pluginName, workspace);
  if (!manifest) {
    lines.push(`Plugin "${pluginName}" not found in workspace.`);
    lines.push("");
    lines.push("Available plugins:");
    try {
      const dirs = fs
        .readdirSync(workspace)
        .filter(
          (d) =>
            d.startsWith("openclaw-") &&
            fs.existsSync(path.join(workspace, d, "openclaw.plugin.json")),
        )
        .sort();
      for (const d of dirs) lines.push(`  - ${d}`);
      if (dirs.length === 0) lines.push("  (none)");
    } catch {
      lines.push("  (workspace not readable)");
    }
    return { text: lines.join("\n") };
  }

  // Plugin metadata
  lines.push("PLUGIN");
  lines.push(`  ID: ${manifest.id ?? pluginName}`);
  lines.push(`  Name: ${manifest.name ?? "(unnamed)"}`);
  lines.push(`  Version: ${manifest.version ?? "?"}`);
  if (manifest.description) lines.push(`  Description: ${manifest.description}`);

  // Load active config
  const { config: activeConfig, source } = loadPluginConfig(
    manifest.id ?? pluginName,
    workspace,
  );

  lines.push("");
  lines.push("ACTIVE CONFIG");
  lines.push(`  Source: ${source}`);

  if (activeConfig && Object.keys(activeConfig).length > 0) {
    const masked = maskSecrets(activeConfig);
    for (const [key, value] of Object.entries(masked)) {
      // Skip manifest-level fields that aren't config
      if (["id", "name", "version", "description", "configSchema", "$schema"].includes(key)) continue;
      lines.push(`  ${key}: ${JSON.stringify(value)}`);
    }
  } else {
    lines.push("  (using defaults)");
  }

  // Schema validation
  const schema = manifest.configSchema;
  if (schema?.properties) {
    const schemaProps = schema.properties as Record<string, any>;
    const defaults = extractDefaults(schemaProps);
    const configToValidate = activeConfig ?? {};

    // Filter out manifest-level fields for validation
    const configValues: Record<string, any> = {};
    for (const [key, value] of Object.entries(configToValidate)) {
      if (!["id", "name", "version", "description", "configSchema", "$schema"].includes(key)) {
        configValues[key] = value;
      }
    }

    lines.push("");
    lines.push("SCHEMA VALIDATION");

    const warnings = validateConfig(
      configValues,
      schemaProps,
      schema.additionalProperties !== false ? true : false,
    );

    if (warnings.length === 0) {
      lines.push("  All checks passed");
    } else {
      for (const w of warnings) {
        lines.push(`  WARNING: ${w}`);
      }
    }

    // Diff against defaults
    lines.push("");
    lines.push("DEFAULTS COMPARISON");
    const diffLines = diffAgainstDefaults(configValues, defaults, schemaProps);
    if (diffLines.length > 0) {
      for (const dl of diffLines) lines.push(dl);
    } else {
      lines.push("  (no properties defined in schema)");
    }
  } else {
    lines.push("");
    lines.push("SCHEMA");
    lines.push("  (no configSchema defined in plugin manifest)");
  }

  // Resolved paths
  lines.push("");
  lines.push("RESOLVED PATHS");
  const pluginDir = findPluginDir(pluginName, workspace);
  if (pluginDir) {
    lines.push(`  Plugin dir: ${pluginDir}`);
    lines.push(`  Manifest: ${path.join(pluginDir, "openclaw.plugin.json")}`);
    const pkgPath = path.join(pluginDir, "package.json");
    if (fs.existsSync(pkgPath)) {
      lines.push(`  package.json: ${pkgPath}`);
    }
  }

  return { text: lines.join("\n") };
}

/** Find the absolute path for a plugin directory in the workspace. */
function findPluginDir(pluginName: string, workspace: string): string | null {
  const direct = path.join(workspace, pluginName);
  if (fs.existsSync(path.join(direct, "openclaw.plugin.json"))) {
    return direct;
  }

  try {
    const dirs = fs.readdirSync(workspace).filter((d) => d.startsWith("openclaw-"));
    for (const dir of dirs) {
      const manifestPath = path.join(workspace, dir, "openclaw.plugin.json");
      if (!fs.existsSync(manifestPath)) continue;
      const manifest = readJsonSafe<Record<string, any> | null>(manifestPath, null);
      if (manifest?.id === pluginName) {
        return path.join(workspace, dir);
      }
    }
  } catch {
    // workspace not readable
  }

  return null;
}
