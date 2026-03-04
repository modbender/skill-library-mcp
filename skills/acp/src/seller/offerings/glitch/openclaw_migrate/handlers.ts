import type { ExecuteJobResult, ValidationResult } from "../../../runtime/offeringTypes.js";
import { execSync } from "child_process";

const MIGRATE_PATH = "/home/crix/.openclaw/workspace/skills/openclaw-migrate/main.js";

export async function executeJob(request: any): Promise<ExecuteJobResult> {
  const { action, targetHost, sshUser } = request;
  
  let cmd = "";
  
  if (action === "migrate") {
    // This requires SSH access - return instructions
    return { deliverable: "Migration requires SSH access to target host. Please ensure you have SSH key-based access to the target machine." };
  } else if (action === "setup" && targetHost) {
    cmd = `node ${MIGRATE_PATH} setup`;
  } else if (action === "test" && targetHost) {
    cmd = `node ${MIGRATE_PATH} test`;
  } else if (action === "status") {
    cmd = `node ${MIGRATE_PATH} status`;
  } else {
    return { deliverable: `Unknown action: ${action}. Supported: migrate, setup, test, status` };
  }
  
  try {
    const result = execSync(cmd, { encoding: "utf8", timeout: 30000 });
    return { deliverable: result.trim() };
  } catch (error: any) {
    return { deliverable: `Error: ${error.message}` };
  }
}

export function validateRequirements(request: any): ValidationResult {
  const { action } = request;
  
  const validActions = ["migrate", "setup", "test", "status"];
  if (!validActions.includes(action)) {
    return { valid: false, reason: `Invalid action. Supported: ${validActions.join(", ")}` };
  }
  
  return { valid: true };
}

export function requestPayment(request: any): string {
  return "OpenClaw Migration service - fee: 1.0 USDC";
}
