import * as provision from "./tools/provision";
import * as earnings from "./tools/earnings";
import * as withdraw from "./tools/withdraw";
import type { CreateToolsOptions } from "./types";

export { provision, earnings, withdraw };
export type { CreateToolsOptions } from "./types";
export { GATEX402_BOUNDARY, wrapAgentResponse } from "./types";

export interface X402Tools {
  provision_api: (params: provision.ProvisionParams) => Promise<string>;
  get_earnings: () => Promise<string>;
  withdraw_funds: (params: withdraw.WithdrawParams) => Promise<string>;
}

/**
 * Create tools with credentials injected by the host. Use this so the agent
 * never receives wallet private keys or management tokens.
 */
export function createTools(options: CreateToolsOptions): X402Tools {
  return {
    provision_api: (params) =>
      provision.provisionApi(params, {
        getWalletPrivateKey: options.getWalletPrivateKey,
        storeManagementToken: options.storeManagementToken,
      }),
    get_earnings: () =>
      earnings.getEarnings({
        getManagementToken:
          options.getManagementToken ?? (async () => ""),
      }),
    withdraw_funds: (params) =>
      withdraw.withdrawFunds(params, {
        getManagementToken:
          options.getManagementToken ?? (async () => ""),
        getWalletPrivateKey: options.getWalletPrivateKey,
      }),
  };
}
