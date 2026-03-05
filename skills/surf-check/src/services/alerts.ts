/**
 * Alert Evaluation Logic
 * 
 * Determines whether to send surf alerts based on forecast conditions.
 * 
 * Tiered confidence based on forecast accuracy:
 * - 4+ days out: Fair-Good+ only (forecasts are fuzzy)
 * - 1-3 days out: Fair+ (good confidence)
 * - Day of: Good+ only, and only before dawn patrol cutoff
 */

import {
  DayForecast,
  AlertConfig,
  AlertDecision,
  Alert,
  SpotConfig,
  RatingKey,
  RATING_VALUES,
  DEFAULT_ALERT_CONFIG,
  QuietHours,
} from '../types.js';

/**
 * Get days until forecast date (0 = today, 1 = tomorrow, etc.)
 */
function getDaysOut(forecastDate: Date, now: Date = new Date()): number {
  const forecastDay = new Date(forecastDate);
  forecastDay.setHours(0, 0, 0, 0);
  
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);
  
  const diffMs = forecastDay.getTime() - today.getTime();
  return Math.round(diffMs / (24 * 60 * 60 * 1000));
}

/**
 * Get minimum rating required based on days out
 */
function getMinRatingForDaysOut(daysOut: number): RatingKey {
  if (daysOut >= 4) {
    // 4+ days: need Fair-Good or better (forecasts are fuzzy)
    return RatingKey.FAIR_TO_GOOD;
  } else if (daysOut >= 1) {
    // 1-3 days: Fair or better
    return RatingKey.FAIR;
  } else {
    // Day of: Good or better only
    return RatingKey.GOOD;
  }
}

/**
 * Check if it's too late to alert for same-day surf
 * Dawn patrol cutoff: 8am
 */
function isPastDawnPatrol(now: Date = new Date()): boolean {
  return now.getHours() >= 8;
}

/**
 * Check if current time is within quiet hours
 * Handles overnight ranges (e.g., 22:00 - 06:00)
 */
function isQuietHours(quietHours: QuietHours, now: Date = new Date()): boolean {
  if (!quietHours.enabled) {
    return false;
  }

  const hour = now.getHours();
  const { start, end } = quietHours;

  // Handle overnight range (e.g., 22:00 - 06:00)
  if (start > end) {
    return hour >= start || hour < end;
  }
  
  // Handle same-day range (e.g., 14:00 - 18:00)
  return hour >= start && hour < end;
}

/**
 * Evaluate a single forecast against alert criteria
 */
export function evaluateForecast(
  forecast: DayForecast,
  config: AlertConfig = DEFAULT_ALERT_CONFIG,
  now: Date = new Date()
): AlertDecision {
  const daysOut = getDaysOut(forecast.date, now);

  // Skip past dates
  if (daysOut < 0) {
    return {
      shouldAlert: false,
      forecast,
      reason: 'Date is in the past',
    };
  }

  // Skip same-day alerts if past dawn patrol
  if (daysOut === 0 && isPastDawnPatrol(now)) {
    return {
      shouldAlert: false,
      forecast,
      reason: 'Too late for same-day alert (past 8am)',
    };
  }

  // Check wave height range
  if (forecast.wave.max < config.waveMin) {
    return {
      shouldAlert: false,
      forecast,
      reason: `Wave height too small (${Math.round(forecast.wave.max)}ft < ${config.waveMin}ft)`,
    };
  }

  if (forecast.wave.min > config.waveMax) {
    return {
      shouldAlert: false,
      forecast,
      reason: `Wave height too big (${Math.round(forecast.wave.min)}ft > ${config.waveMax}ft)`,
    };
  }

  // Get minimum rating based on days out
  const minRating = getMinRatingForDaysOut(daysOut);
  const ratingValue = RATING_VALUES[forecast.rating.key] ?? 0;
  const minRatingValue = RATING_VALUES[minRating] ?? 2;

  if (ratingValue < minRatingValue) {
    const minDisplay = minRating.replace(/_/g, '-').toLowerCase();
    return {
      shouldAlert: false,
      forecast,
      reason: `Rating ${forecast.rating.display} below ${minDisplay} (${daysOut} days out)`,
    };
  }

  // Weekend bonus for Fair conditions (1-3 days out)
  // Fair on weekdays is fine, but worth noting weekends are preferred
  const weekendNote = forecast.isWeekend ? ' (weekend!)' : '';

  // All criteria met!
  return {
    shouldAlert: true,
    forecast,
    reason: `${forecast.rating.display} conditions${weekendNote} - ${daysOut} day${daysOut === 1 ? '' : 's'} out`,
  };
}

/**
 * Evaluate multiple forecasts and return alerts
 */
export function evaluateForecasts(
  forecasts: DayForecast[],
  config: AlertConfig = DEFAULT_ALERT_CONFIG,
  now: Date = new Date()
): AlertDecision[] {
  // Only consider forecasts within the configured window
  const maxDate = new Date(now.getTime() + config.forecastDays * 24 * 60 * 60 * 1000);

  return forecasts
    .filter((f) => f.date <= maxDate)
    .map((f) => evaluateForecast(f, config, now));
}

/**
 * Generate alerts for a spot
 */
export function generateAlert(
  spot: SpotConfig,
  forecasts: DayForecast[],
  config: AlertConfig = DEFAULT_ALERT_CONFIG,
  now: Date = new Date()
): Alert | null {
  const decisions = evaluateForecasts(forecasts, config, now);
  const alertForecasts = decisions
    .filter((d) => d.shouldAlert)
    .map((d) => d.forecast);

  if (alertForecasts.length === 0) {
    return null;
  }

  return {
    spot,
    forecasts: alertForecasts,
    generatedAt: now,
  };
}

/**
 * Format alert for Telegram/notification
 */
export function formatAlertMessage(alert: Alert): string {
  const lines: string[] = [];
  
  lines.push(`🏄 **Surf Alert: ${alert.spot.name}**`);
  lines.push('');

  for (const forecast of alert.forecasts) {
    const waveRange = `${Math.round(forecast.wave.min)}-${Math.round(forecast.wave.max)}ft`;
    const emoji = getConditionEmoji(forecast.rating.key);
    const daysOut = getDaysOut(forecast.date, alert.generatedAt);
    const daysLabel = daysOut === 0 ? 'Today' : daysOut === 1 ? 'Tomorrow' : forecast.dateString;
    
    lines.push(`📅 **${daysLabel}**`);
    lines.push(`🌊 ${waveRange} | ${emoji} ${forecast.rating.display}`);
    
    if (forecast.wind) {
      const windDir = getWindDirection(forecast.wind.direction);
      lines.push(`💨 ${windDir} ${Math.round(forecast.wind.speed)}mph`);
    }
    
    lines.push('');
  }

  lines.push(`[View Forecast](${alert.spot.url})`);

  return lines.join('\n');
}

/**
 * Get emoji for condition rating
 */
function getConditionEmoji(rating: RatingKey): string {
  switch (rating) {
    case RatingKey.EPIC:
    case RatingKey.GOOD_TO_EPIC:
      return '🔥';
    case RatingKey.GOOD:
      return '✨';
    case RatingKey.FAIR_TO_GOOD:
      return '👍';
    case RatingKey.FAIR:
      return '👌';
    default:
      return '🌊';
  }
}

/**
 * Convert wind direction degrees to compass direction
 */
function getWindDirection(degrees: number): string {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
}

/**
 * Format a summary of all alerts for multiple spots
 */
export function formatMultiSpotSummary(alerts: Alert[]): string {
  if (alerts.length === 0) {
    return '🏄 No surf alerts for the upcoming week. Conditions not meeting criteria.';
  }

  const lines: string[] = [];
  lines.push('🏄 **Surf Forecast Summary**');
  lines.push('');

  for (const alert of alerts) {
    lines.push(`**${alert.spot.name}**`);
    for (const forecast of alert.forecasts) {
      const waveRange = `${Math.round(forecast.wave.min)}-${Math.round(forecast.wave.max)}ft`;
      const daysOut = getDaysOut(forecast.date, alert.generatedAt);
      const dayLabel = daysOut === 0 ? 'Today' : daysOut === 1 ? 'Tomorrow' : forecast.dayOfWeek;
      lines.push(`• ${dayLabel}: ${waveRange} (${forecast.rating.display})`);
    }
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Check if notifications should be suppressed due to quiet hours
 */
export function shouldSuppressNotification(
  config: AlertConfig = DEFAULT_ALERT_CONFIG,
  now: Date = new Date()
): { suppress: boolean; reason?: string } {
  if (isQuietHours(config.quietHours, now)) {
    const hour = now.getHours();
    const ampm = hour >= 12 ? 'pm' : 'am';
    const displayHour = hour % 12 || 12;
    return {
      suppress: true,
      reason: `Quiet hours active (${displayHour}${ampm} is between ${formatHour(config.quietHours.start)} and ${formatHour(config.quietHours.end)})`,
    };
  }
  return { suppress: false };
}

/**
 * Format hour for display (e.g., 22 -> "10pm", 6 -> "6am")
 */
function formatHour(hour: number): string {
  const ampm = hour >= 12 ? 'pm' : 'am';
  const displayHour = hour % 12 || 12;
  return `${displayHour}${ampm}`;
}

/**
 * Debug: Show evaluation for all forecasts
 */
export function debugEvaluations(
  forecasts: DayForecast[],
  config: AlertConfig = DEFAULT_ALERT_CONFIG,
  now: Date = new Date()
): string {
  const decisions = evaluateForecasts(forecasts, config, now);
  
  const lines = decisions.map((d) => {
    const status = d.shouldAlert ? '✅' : '❌';
    const daysOut = getDaysOut(d.forecast.date, now);
    return `${status} ${d.forecast.dayOfWeek} (${daysOut}d): ${d.forecast.rating.display} - ${d.reason}`;
  });

  return lines.join('\n');
}
