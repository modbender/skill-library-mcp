/**
 * Smart Directions Router
 * Uses Directions5 by default, switches to Directions15 only when waypoints >= 5
 */

import { getDirections } from "./directions";
import { getDirections5 } from "./directions5";
import type { DirectionsParams } from "./directions";
import type { ResultOutput } from "./directions";

export interface SmartDirectionsParams {
  start: string;
  goal: string;
  apiKeyId: string;
  apiKey: string;
  waypoints?: string;
  option?: string;
  cartype?: number;
  fueltype?: string;
  mileage?: number;
  lang?: string;
}

/**
 * Smart routing: defaults to Directions5, uses Directions15 only when waypoints >= 5
 */
export async function getSmartDirections(params: SmartDirectionsParams): Promise<ResultOutput> {
  // Count waypoints
  const waypointCount = params.waypoints 
    ? params.waypoints.split("|").length 
    : 0;

  // If 5 or more waypoints, use Directions15; otherwise use Directions5
  const useDirections15 = waypointCount >= 5;

  console.log(`\n📊 경유지 개수: ${waypointCount}개`);
  console.log(`🚀 사용 API: ${useDirections15 ? "Directions15 (15개 경유지 지원)" : "Directions5 (기본값)"}\n`);

  if (useDirections15) {
    return getDirections(params as DirectionsParams);
  } else {
    return getDirections5(params as SmartDirectionsParams);
  }
}
