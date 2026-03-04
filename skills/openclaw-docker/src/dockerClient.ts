import Docker from "dockerode";
import { PluginConfig } from "./types";
import { resolveTlsMaterial } from "./config";

export function createDockerClient(config: PluginConfig): Docker {
  const tls = resolveTlsMaterial(config);

  if (config.host && config.port) {
    return new Docker({
      host: config.host,
      port: config.port,
      ca: tls.ca,
      cert: tls.cert,
      key: tls.key,
      protocol: tls.ca || tls.cert || tls.key ? "https" : "http"
    });
  }

  return new Docker({ socketPath: config.socketPath });
}
