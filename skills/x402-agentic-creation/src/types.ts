/**
 * Credential injectors for use by the host/runtime. Never expose these to the agent.
 */
export interface CreateToolsOptions {
  /** Resolve wallet private key (e.g. from env or secure vault). Required for provision_api and withdraw_funds. */
  getWalletPrivateKey: () => Promise<string>;
  /** Resolve management token after provisioning. Required for get_earnings and withdraw_funds. */
  getManagementToken?: () => Promise<string>;
  /** Called when provision_api succeeds so the host can store the token. Required when using provision_api. */
  storeManagementToken?: (token: string) => void | Promise<void>;
}

/** Agent-safe response wrapper to mitigate indirect prompt injection. */
export const GATEX402_BOUNDARY = {
  start: "<!-- GATEX402_API_RESPONSE -->",
  end: "<!-- END_GATEX402_API_RESPONSE -->",
};

export function wrapAgentResponse<T extends object>(data: T): string {
  return `${GATEX402_BOUNDARY.start}\n${JSON.stringify(data)}\n${GATEX402_BOUNDARY.end}`;
}
