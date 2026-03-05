#!/usr/bin/env npx tsx
/**
 * Check Surfline Forecast
 * 
 * Manual script to check current forecast for configured spots.
 * 
 * Usage:
 *   npx tsx scripts/check-forecast.ts           # Show forecast + alerts
 *   npx tsx scripts/check-forecast.ts --debug   # Show alert evaluation reasoning
 *   npx tsx scripts/check-forecast.ts --json    # JSON output
 *   npx tsx scripts/check-forecast.ts --cron    # Cron mode: only new alerts, update state
 *   npx tsx scripts/check-forecast.ts --cron --force  # Bypass quiet hours
 */

import { fetchDailyForecasts, formatForecast } from '../src/providers/surfline.js';
import {
  generateAlert,
  formatAlertMessage,
  formatMultiSpotSummary,
  debugEvaluations,
  shouldSuppressNotification,
} from '../src/services/alerts.js';
import {
  loadState,
  filterNewAlerts,
  updateStateAfterCheck,
} from '../src/services/state.js';
import { loadConfig, getConfigPath } from '../src/config.js';

async function main() {
  const jsonOutput = process.argv.includes('--json');
  const debugMode = process.argv.includes('--debug');
  const cronMode = process.argv.includes('--cron');
  const forceMode = process.argv.includes('--force');
  
  // Load config (from file or defaults)
  const config = loadConfig();
  const spotsToCheck = config.spots;
  const alertConfig = config.alertConfig;
  const now = new Date();

  // Load state for deduplication
  const state = await loadState();

  if (!cronMode && !jsonOutput) {
    const configPath = getConfigPath();
    if (configPath) {
      console.log(`🏄 Checking Surfline forecasts (config: ${configPath})...\n`);
    } else {
      console.log('🏄 Checking Surfline forecasts (using defaults)...\n');
    }
  }

  const allAlerts = [];
  const newAlerts = [];

  for (const spot of spotsToCheck) {
    if (!cronMode && !jsonOutput) {
      console.log(`📍 ${spot.name}`);
      console.log('-'.repeat(40));
    }

    try {
      const forecasts = await fetchDailyForecasts(spot, 6);

      if (!cronMode && !jsonOutput) {
        for (const forecast of forecasts) {
          console.log(formatForecast(forecast));
        }
      }

      if (debugMode) {
        console.log('\nAlert evaluation:');
        console.log(debugEvaluations(forecasts, alertConfig, now));
      }

      const alert = generateAlert(spot, forecasts, alertConfig, now);
      if (alert) {
        allAlerts.push(alert);
        
        // Filter to only new alerts (not already sent)
        const newAlert = filterNewAlerts(alert, state);
        if (newAlert) {
          newAlerts.push(newAlert);
        }
      }

      if (!cronMode && !jsonOutput) {
        console.log('');
      }
    } catch (error) {
      console.error(`Error fetching ${spot.name}:`, error);
    }
  }

  if (cronMode) {
    // Check quiet hours before sending notifications (unless --force)
    if (!forceMode) {
      const quietCheck = shouldSuppressNotification(alertConfig, now);
      
      if (quietCheck.suppress) {
        // During quiet hours: don't output anything, don't mark as sent
        // Alerts will be sent on next check outside quiet hours
        return;
      }
    }
    
    // Cron mode: only output if there are NEW alerts
    if (newAlerts.length > 0) {
      console.log(formatMultiSpotSummary(newAlerts));
      
      // Update state to mark these as sent
      await updateStateAfterCheck(state, newAlerts);
    }
    // Silent if no new alerts
  } else if (jsonOutput) {
    console.log(JSON.stringify({ allAlerts, newAlerts }, null, 2));
  } else {
    console.log('='.repeat(40));
    console.log('ALERTS');
    console.log('='.repeat(40));

    if (allAlerts.length === 0) {
      console.log('No alerts - conditions not meeting criteria.');
    } else {
      console.log(formatMultiSpotSummary(allAlerts));
      
      if (newAlerts.length < allAlerts.length) {
        const alreadySent = allAlerts.reduce((n, a) => n + a.forecasts.length, 0) - 
                           newAlerts.reduce((n, a) => n + a.forecasts.length, 0);
        console.log(`(${alreadySent} alert(s) already sent previously)`);
      }
    }
  }
}

main().catch(console.error);
