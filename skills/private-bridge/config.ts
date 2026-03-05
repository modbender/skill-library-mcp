export interface RemoteRelayConfig {
  relay_url: string;
  node_id: string;
  auth_token: string;
}

export function validateConfig(config: Partial<RemoteRelayConfig>): RemoteRelayConfig {
  if (!config.relay_url) throw new Error("private-bridge: relay_url is required");
  if (!config.node_id) throw new Error("private-bridge: node_id is required");
  if (!config.auth_token) throw new Error("private-bridge: auth_token is required");

  // Normalize URL: ensure wss:// for secure connections
  let url = config.relay_url.replace(/\/+$/, "");
  url = url.replace(/^https:\/\//, "wss://");
  url = url.replace(/^http:\/\//, "ws://");

  return {
    relay_url: url,
    node_id: config.node_id,
    auth_token: config.auth_token,
  };
}
