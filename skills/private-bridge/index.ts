export { RelayClient } from "./relayClient";
export { validateConfig } from "./config";
export type { RemoteRelayConfig } from "./config";
export type {
  IncomingMessage,
  HeartbeatPayload,
  TokenChunk,
  DoneMessage,
  StatusResponse,
  ErrorResponse,
  OutgoingMessage,
  OpenClawRuntime,
} from "./capabilities";

import { RelayClient } from "./relayClient";
import type { RemoteRelayConfig } from "./config";
import type { OpenClawRuntime } from "./capabilities";

let client: RelayClient | null = null;

/**
 * Initialize and connect the PrivateBridge skill.
 * Call this once from your OpenClaw boot sequence.
 */
export function init(
  config: Partial<RemoteRelayConfig>,
  runtime: OpenClawRuntime
): RelayClient {
  if (client) {
    client.disconnect();
  }
  client = new RelayClient(config, runtime);
  client.connect();
  return client;
}

/**
 * Disconnect and clean up the relay client.
 */
export function shutdown(): void {
  if (client) {
    client.disconnect();
    client = null;
  }
}
