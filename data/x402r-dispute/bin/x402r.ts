#!/usr/bin/env tsx

/**
 * x402r CLI — Agent-friendly dispute resolution tool
 *
 * Usage:
 *   x402r config --key 0x... --operator 0x...
 *   x402r pay <url>
 *   x402r dispute "reason" --evidence "details"
 *   x402r status
 *   x402r verify
 *   x402r list
 *   x402r show
 */

import { Command } from "commander";
import { config as dotenvConfig } from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { registerConfigCommand } from "../src/commands/config.js";
import { registerDisputeCommand } from "../src/commands/dispute.js";
import { registerStatusCommand } from "../src/commands/status.js";
import { registerVerifyCommand } from "../src/commands/verify.js";
import { registerListCommand } from "../src/commands/list.js";
import { registerShowCommand } from "../src/commands/show.js";
import { registerPayCommand } from "../src/commands/pay.js";

// Load .env from cli/ directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenvConfig({ path: join(__dirname, "..", ".env") });

const program = new Command();

program
  .name("x402r")
  .description("Agent-friendly CLI for x402r dispute resolution")
  .version("0.1.0");

registerConfigCommand(program);
registerPayCommand(program);
registerDisputeCommand(program);
registerStatusCommand(program);
registerVerifyCommand(program);
registerListCommand(program);
registerShowCommand(program);

program.parse();
