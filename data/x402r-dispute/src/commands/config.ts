/**
 * config command — Save/load CLI configuration
 */

import type { Command } from "commander";
import { saveConfigFile, printConfig, type CliConfigFile } from "../config.js";

export function registerConfigCommand(program: Command): void {
  program
    .command("config")
    .description("Save or view CLI configuration")
    .option("-k, --key <privateKey>", "Set private key")
    .option("-o, --operator <address>", "Set operator address")
    .option("-a, --arbiter-url <url>", "Set arbiter server URL")
    .option("-c, --court-url <url>", "Set court UI URL (for independent verification)")
    .option("-n, --network <networkId>", "Set network ID (e.g., eip155:84532)")
    .option("-r, --rpc <url>", "Set RPC URL")
    .option("--pinata-jwt <jwt>", "Set Pinata JWT token")
    .action(async (options) => {
      const updates: CliConfigFile = {};
      let hasUpdates = false;

      if (options.key) {
        updates.privateKey = options.key;
        hasUpdates = true;
      }
      if (options.operator) {
        updates.operatorAddress = options.operator;
        hasUpdates = true;
      }
      if (options.arbiterUrl) {
        updates.arbiterUrl = options.arbiterUrl;
        hasUpdates = true;
      }
      if (options.courtUrl) {
        updates.courtUrl = options.courtUrl;
        hasUpdates = true;
      }
      if (options.network) {
        updates.networkId = options.network;
        hasUpdates = true;
      }
      if (options.rpc) {
        updates.rpcUrl = options.rpc;
        hasUpdates = true;
      }
      if (options.pinataJwt) {
        updates.pinataJwt = options.pinataJwt;
        hasUpdates = true;
      }

      if (hasUpdates) {
        saveConfigFile(updates);
        console.log("Config updated.");
      }

      await printConfig();
    });
}
