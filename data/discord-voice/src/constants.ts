/**
 * Centralized constants for Discord Voice plugin
 */

/** Cooldown after bot speaks - ignore VAD events (prevents echo triggering) */
export const SPEAK_COOLDOWN_VAD_MS = 800;

/** Cooldown after bot speaks - skip processing new recordings */
export const SPEAK_COOLDOWN_PROCESSING_MS = 500;

/** RMS amplitude thresholds for filtering quiet audio (keystrokes, background noise) */
export const RMS_THRESHOLDS = {
  low: 400, // More sensitive - picks up quieter speech
  medium: 800, // Balanced default
  high: 1200, // Less sensitive - requires louder speech
} as const;

export function getRmsThreshold(sensitivity: "low" | "medium" | "high"): number {
  return RMS_THRESHOLDS[sensitivity] ?? RMS_THRESHOLDS.medium;
}
