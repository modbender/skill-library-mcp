import { httpGetJson } from "./http.js";
import { Candidate } from "../types.js";
import { logger } from "../logger.js";

/**
 * NOTE: Pump.fun endpoints can change.
 * Treat this module as a stub. Replace URL(s) with your actual source.
 */
export async function fetchPumpfunCandidates(): Promise<Candidate[]> {
  // Placeholder: return empty unless you wire a valid endpoint.
  // You can implement:
  // - new tokens
  // - trending
  // - graduating
  logger.debug("pumpfun: fetch candidates (stub)");
  return [];
}
