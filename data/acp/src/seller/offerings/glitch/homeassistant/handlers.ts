import type { ExecuteJobResult, ValidationResult } from "../../../runtime/offeringTypes.js";
import { execSync } from "child_process";

const HA_CLI_PATH = "/home/crix/.openclaw/workspace/skills/homeassistant/ha-cli";

export async function executeJob(request: any): Promise<ExecuteJobResult> {
  const { action, entity, value } = request;
  
  let cmd = "";
  
  if (action === "on" || action === "off") {
    cmd = `${HA_CLI_PATH} ${action} "${entity}"`;
  } else if (action === "brightness" && value) {
    cmd = `${HA_CLI_PATH} brightness ${value} "${entity}"`;
  } else if (action === "rgb" && value) {
    cmd = `${HA_CLI_PATH} rgb ${value} "${entity}"`;
  } else if (action === "temperature" && value) {
    cmd = `${HA_CLI_PATH} ${value} "${entity}"`;
  } else if (action === "scene") {
    cmd = `${HA_CLI_PATH} scene "${entity}"`;
  } else if (action === "script") {
    cmd = `${HA_CLI_PATH} script run "${entity}"`;
  } else {
    return { deliverable: `Unknown action: ${action}. Supported: on, off, brightness, rgb, temperature, scene, script` };
  }
  
  try {
    const result = execSync(cmd, { encoding: "utf8", timeout: 30000 });
    return { deliverable: result.trim() };
  } catch (error: any) {
    return { deliverable: `Error: ${error.message}` };
  }
}

export function validateRequirements(request: any): ValidationResult {
  const { action, entity } = request;
  
  if (!action) {
    return { valid: false, reason: "action is required" };
  }
  
  const validActions = ["on", "off", "brightness", "rgb", "temperature", "scene", "script"];
  if (!validActions.includes(action)) {
    return { valid: false, reason: `Invalid action. Supported: ${validActions.join(", ")}` };
  }
  
  return { valid: true };
}

export function requestPayment(request: any): string {
  return "Home Assistant control service - fee: 0.5 USDC";
}
