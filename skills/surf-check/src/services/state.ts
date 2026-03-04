/**
 * State Management
 * 
 * Tracks which alerts have been sent to avoid duplicates.
 * State is stored in data/state.json
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { DayForecast, Alert } from '../types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STATE_FILE = path.join(__dirname, '..', '..', 'data', 'state.json');

export interface AlertState {
  lastCheck: string;
  alertsSent: Record<string, string>; // "spotId:YYYY-MM-DD" -> ISO timestamp sent
}

const DEFAULT_STATE: AlertState = {
  lastCheck: new Date().toISOString(),
  alertsSent: {},
};

/**
 * Load state from disk
 */
export async function loadState(): Promise<AlertState> {
  try {
    const data = await fs.readFile(STATE_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return { ...DEFAULT_STATE };
  }
}

/**
 * Save state to disk
 */
export async function saveState(state: AlertState): Promise<void> {
  const dir = path.dirname(STATE_FILE);
  await fs.mkdir(dir, { recursive: true });
  await fs.writeFile(STATE_FILE, JSON.stringify(state, null, 2));
}

/**
 * Generate key for a forecast alert
 */
function getAlertKey(spotId: string, forecastDate: Date): string {
  const dateStr = forecastDate.toISOString().split('T')[0];
  return `${spotId}:${dateStr}`;
}

/**
 * Check if alert was already sent for this forecast
 */
export function wasAlertSent(
  state: AlertState,
  spotId: string,
  forecastDate: Date
): boolean {
  const key = getAlertKey(spotId, forecastDate);
  return key in state.alertsSent;
}

/**
 * Mark alert as sent
 */
export function markAlertSent(
  state: AlertState,
  spotId: string,
  forecastDate: Date
): void {
  const key = getAlertKey(spotId, forecastDate);
  state.alertsSent[key] = new Date().toISOString();
}

/**
 * Filter alerts to only new ones (not already sent)
 */
export function filterNewAlerts(
  alert: Alert,
  state: AlertState
): Alert | null {
  const newForecasts = alert.forecasts.filter(
    (f) => !wasAlertSent(state, alert.spot.id, f.date)
  );

  if (newForecasts.length === 0) {
    return null;
  }

  return {
    ...alert,
    forecasts: newForecasts,
  };
}

/**
 * Clean up old alerts (older than 7 days)
 */
export function cleanupOldAlerts(state: AlertState): void {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 7);
  const cutoffStr = cutoff.toISOString().split('T')[0];

  for (const key of Object.keys(state.alertsSent)) {
    const dateStr = key.split(':')[1];
    if (dateStr < cutoffStr) {
      delete state.alertsSent[key];
    }
  }
}

/**
 * Update state after checking
 */
export async function updateStateAfterCheck(
  state: AlertState,
  sentAlerts: Alert[]
): Promise<void> {
  state.lastCheck = new Date().toISOString();

  // Mark all sent alerts
  for (const alert of sentAlerts) {
    for (const forecast of alert.forecasts) {
      markAlertSent(state, alert.spot.id, forecast.date);
    }
  }

  // Cleanup old entries
  cleanupOldAlerts(state);

  await saveState(state);
}
