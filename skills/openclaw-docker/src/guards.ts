import { DockerOperation, PluginConfig } from "./types";

const READ_ONLY_ALLOWED: DockerOperation[] = ["ps", "logs", "inspect", "compose_ps"];

export function assertOperationAllowed(operation: DockerOperation, config: PluginConfig): void {
  if (config.readOnly && !READ_ONLY_ALLOWED.includes(operation)) {
    throw new Error(`Operation '${operation}' is blocked in readOnly mode.`);
  }

  if (Array.isArray(config.allowedOperations) && config.allowedOperations.length > 0) {
    if (!config.allowedOperations.includes(operation)) {
      throw new Error(`Operation '${operation}' is not listed in allowedOperations.`);
    }
  }
}
