import type { ExecuteJobResult, ValidationResult } from "../../../runtime/offeringTypes.js";

// Required: implement your service logic here
export async function executeJob(request: any): Promise<ExecuteJobResult> {
  // TODO: Implement your service
  return { deliverable: "TODO: Return your result" };
}

// Optional: validate incoming requests
export function validateRequirements(request: any): ValidationResult {
  // Return { valid: true } to accept, or { valid: false, reason: "explanation" } to reject
  return { valid: true };
}

// Optional: provide custom payment request message
export function requestPayment(request: any): string {
  // Return a custom message/reason for the payment request
  return "Request accepted";
}
