import type { ExecuteJobResult, ValidationResult } from "../../../runtime/offeringTypes.js";
import { execSync } from "child_process";

const SKILLSTORE_PATH = "/home/crix/.openclaw/workspace/skills/skillstore/main.js";

export async function executeJob(request: any): Promise<ExecuteJobResult> {
  const { action, query } = request;
  
  let cmd = "";
  
  if (action === "search" || !action) {
    cmd = `node ${SKILLSTORE_PATH} "${query || ''}"`;
  } else if (action === "list") {
    cmd = `node ${SKILLSTORE_PATH} list`;
  } else if (action === "known") {
    cmd = `node ${SKILLSTORE_PATH} known`;
  } else if (action === "create" && query) {
    cmd = `node ${SKILLSTORE_PATH} create ${query}`;
  } else {
    return { deliverable: `Unknown action: ${action}. Supported: search, list, known, create` };
  }
  
  try {
    const result = execSync(cmd, { encoding: "utf8", timeout: 60000 });
    return { deliverable: result.trim() };
  } catch (error: any) {
    return { deliverable: `Error: ${error.message}` };
  }
}

export function validateRequirements(request: any): ValidationResult {
  const { action } = request;
  
  const validActions = ["search", "list", "known", "create"];
  if (action && !validActions.includes(action)) {
    return { valid: false, reason: `Invalid action. Supported: ${validActions.join(", ")}` };
  }
  
  return { valid: true };
}

export function requestPayment(request: any): string {
  return "SkillStore service - fee: 0.3 USDC";
}
