import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { parse, stringify } from "yaml";
import { getStateRoot } from "./paths";
import { type ConfigPatch, DEFAULT_CONFIG, type SecDigestConfig } from "./schema";

function sanitizeConfig(raw: unknown): ConfigPatch {
  if (!raw || typeof raw !== "object") {
    return {};
  }

  const obj = raw as Record<string, unknown>;
  const patch: ConfigPatch = {};

  if (obj.provider === "openai" || obj.provider === "gemini" || obj.provider === "claude" || obj.provider === "ollama") {
    patch.provider = obj.provider;
  }

  if (obj.opml_profile === "tiny" || obj.opml_profile === "full") {
    patch.opml_profile = obj.opml_profile;
  }

  if (typeof obj.time_range_hours === "number" && Number.isFinite(obj.time_range_hours)) {
    patch.time_range_hours = Math.max(1, Math.floor(obj.time_range_hours));
  }

  if (typeof obj.top_n === "number" && Number.isFinite(obj.top_n)) {
    patch.top_n = Math.max(1, Math.floor(obj.top_n));
  }

  if (obj.output_language === "bilingual_zh_en") {
    patch.output_language = obj.output_language;
  }

  if (obj.weights && typeof obj.weights === "object") {
    const weights = obj.weights as Record<string, unknown>;
    if (typeof weights.security === "number" && typeof weights.ai === "number") {
      patch.weights = {
        security: weights.security,
        ai: weights.ai,
      };
    }
  }

  return patch;
}

export async function loadConfig(cliPatch: ConfigPatch, env: NodeJS.ProcessEnv): Promise<SecDigestConfig> {
  const root = getStateRoot(env);
  await mkdir(root, { recursive: true });

  const filePath = path.join(root, "config.yaml");
  let filePatch: ConfigPatch = {};

  try {
    const content = await readFile(filePath, "utf8");
    filePatch = sanitizeConfig(parse(content));
  } catch {
    // Missing or invalid YAML falls back to defaults + CLI patch.
  }

  const merged: SecDigestConfig = {
    ...DEFAULT_CONFIG,
    ...filePatch,
    ...sanitizeConfig(cliPatch),
    weights: {
      security: sanitizeConfig(cliPatch).weights?.security ?? filePatch.weights?.security ?? DEFAULT_CONFIG.weights.security,
      ai: sanitizeConfig(cliPatch).weights?.ai ?? filePatch.weights?.ai ?? DEFAULT_CONFIG.weights.ai,
    },
  };

  await writeFile(filePath, stringify(merged), "utf8");
  return merged;
}
