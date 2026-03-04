import { readFileSync } from "node:fs";
import { ComposeProjectConfig, PluginConfig } from "./types";

const DEFAULT_ALLOWED_READ_ONLY = ["ps", "logs", "inspect"] as const;

function loadPemIfSet(path?: string): string | undefined {
  if (!path) {
    return undefined;
  }
  return readFileSync(path, "utf8");
}

function isValidComposeProjects(value: unknown): value is ComposeProjectConfig[] {
  if (!Array.isArray(value)) {
    return false;
  }
  return value.every(
    (entry) =>
      typeof entry === "object" &&
      entry !== null &&
      typeof (entry as { name?: unknown }).name === "string" &&
      typeof (entry as { path?: unknown }).path === "string"
  );
}

export function normalizeConfig(raw: unknown): PluginConfig {
  const input = (raw ?? {}) as Record<string, unknown>;

  const socketPath =
    typeof input.socketPath === "string" && input.socketPath.trim().length > 0
      ? input.socketPath
      : "/var/run/docker.sock";

  const host = typeof input.host === "string" ? input.host : undefined;
  const port = typeof input.port === "number" ? input.port : undefined;
  const readOnly = input.readOnly === true;
  const timeoutMs =
    typeof input.timeoutMs === "number" && input.timeoutMs > 0 ? input.timeoutMs : 15000;

  const allowedOperations = Array.isArray(input.allowedOperations)
    ? (input.allowedOperations.filter((x) => typeof x === "string") as PluginConfig["allowedOperations"])
    : undefined;

  const composeProjects = isValidComposeProjects(input.composeProjects)
    ? input.composeProjects
    : [];

  const tlsInput =
    typeof input.tls === "object" && input.tls !== null
      ? (input.tls as Record<string, unknown>)
      : undefined;

  const tls = tlsInput
    ? {
        caPath: typeof tlsInput.caPath === "string" ? tlsInput.caPath : undefined,
        certPath: typeof tlsInput.certPath === "string" ? tlsInput.certPath : undefined,
        keyPath: typeof tlsInput.keyPath === "string" ? tlsInput.keyPath : undefined,
        rejectUnauthorized:
          typeof tlsInput.rejectUnauthorized === "boolean"
            ? tlsInput.rejectUnauthorized
            : undefined
      }
    : undefined;

  return {
    socketPath,
    host,
    port,
    tls,
    readOnly,
    allowedOperations: readOnly
      ? [...DEFAULT_ALLOWED_READ_ONLY]
      : (allowedOperations as PluginConfig["allowedOperations"]),
    composeProjects,
    timeoutMs
  };
}

export function resolveTlsMaterial(config: PluginConfig): {
  ca?: string;
  cert?: string;
  key?: string;
  rejectUnauthorized?: boolean;
} {
  if (!config.tls) {
    return {};
  }

  return {
    ca: loadPemIfSet(config.tls.caPath),
    cert: loadPemIfSet(config.tls.certPath),
    key: loadPemIfSet(config.tls.keyPath),
    rejectUnauthorized: config.tls.rejectUnauthorized
  };
}
