/**
 * OpenCLAW Tour Planner — Public API
 *
 * Main entry point for the skill. Use these functions from your agent
 * to provide AI-powered travel planning capabilities.
 *
 * @example
 * ```ts
 * import { planTrip } from 'openclaw-tour-planner';
 *
 * const itinerary = await planTrip({
 *   destination: 'Tokyo',
 *   durationDays: 5,
 *   budgetLevel: 'mid-range',
 *   travelers: { adults: 2 },
 * });
 *
 * console.log(itinerary); // Markdown-formatted itinerary
 * ```
 */

import { nominatim } from './apis/nominatim';
import { weatherClient } from './apis/weather';
import { wikivoyage } from './apis/wikivoyage';
import { buildItinerary } from './planners/itinerary';
import { formatItinerary, formatWeatherSummary, formatBudget } from './utils/formatter';
import { buildBudget } from './planners/budget';
import { cache, TTL } from './utils/cache';
import { PlanRequest, Destination, WeatherForecast } from './types';

export { PlanRequest } from './types';

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Generate a complete, formatted travel itinerary.
 * Returns Markdown ready for display to end-users.
 */
export async function planTrip(request: PlanRequest): Promise<string> {
  log(`Planning ${request.durationDays}-day trip to ${request.destination}...`);

  const destination = await resolveDestination(request.destination);
  log(`✓ Geocoded: ${destination.name}, ${destination.country} (${destination.coordinates.lat}, ${destination.coordinates.lon})`);

  const [weather, guide] = await Promise.all([
    getWeatherData(destination, request.durationDays),
    getGuideData(destination.name),
  ]);
  log(`✓ Weather: ${weather.summary}`);
  log(`✓ Guide: ${guide.attractions.length} attractions found`);

  const itinerary = await buildItinerary(request, destination, weather, guide);
  log(`✓ Generated ${itinerary.days.length}-day itinerary`);

  return formatItinerary(itinerary);
}

/**
 * Get a weather forecast for a destination.
 * Returns a Markdown-formatted forecast table.
 */
export async function getWeather(destination: string, days: number = 7): Promise<string> {
  log(`Fetching weather for ${destination}...`);
  const dest = await resolveDestination(destination);
  const forecast = await getWeatherData(dest, days);
  return formatWeatherSummary(forecast);
}

/**
 * Get a travel guide summary for a destination.
 * Returns Markdown with overview, attractions, and cultural tips.
 */
export async function getGuide(destination: string): Promise<string> {
  log(`Fetching travel guide for ${destination}...`);
  const guide = await getGuideData(destination);

  const lines = [
    `# 🌍 ${destination} Travel Guide`,
    '',
    '## Overview',
    guide.overview || '_No overview available._',
    '',
  ];

  if (guide.attractions.length) {
    lines.push('## Top Attractions');
    guide.attractions.slice(0, 10).forEach(a => {
      lines.push(`- **${a.name}** — ${a.description.slice(0, 120)}`);
    });
    lines.push('');
  }

  if (guide.culturalTips.length) {
    lines.push('## Cultural Tips');
    guide.culturalTips.forEach(t => lines.push(`- ${t}`));
    lines.push('');
  }

  if (guide.practicalInfo) {
    lines.push('## Practical Info', guide.practicalInfo, '');
  }

  return lines.join('\n');
}

/**
 * Estimate a trip budget without building a full itinerary.
 */
export async function estimateBudget(
  destination: string,
  durationDays: number,
  travelers: number = 1,
  level: 'budget' | 'mid-range' | 'luxury' = 'mid-range',
): Promise<string> {
  log(`Estimating budget for ${destination}...`);
  const dest = await resolveDestination(destination);
  const budget = buildBudget(dest, durationDays, travelers, level);
  return formatBudget(budget);
}

// ── Internals ─────────────────────────────────────────────────────────────────

async function resolveDestination(query: string): Promise<Destination> {
  const cacheKey = `geo:${query.toLowerCase().trim()}`;
  const cached = cache.get<Destination>(cacheKey);
  if (cached) return cached;

  const results = await nominatim.search(query, 1);
  if (!results.length) {
    throw new Error(`Could not find "${query}". Try a more specific name, e.g. "Tokyo, Japan".`);
  }

  const dest = results[0];
  cache.set(cacheKey, dest, TTL.GEOCODING);
  return dest;
}

async function getWeatherData(dest: Destination, days: number): Promise<WeatherForecast> {
  const cacheKey = `weather:${dest.coordinates.lat.toFixed(2)}:${dest.coordinates.lon.toFixed(2)}:${days}`;
  const cached = cache.get<WeatherForecast>(cacheKey);
  if (cached) return cached;

  try {
    const forecast = await weatherClient.getForecast(
      dest.name, dest.coordinates.lat, dest.coordinates.lon, days,
    );
    cache.set(cacheKey, forecast, TTL.WEATHER);
    return forecast;
  } catch (err) {
    log(`⚠ Weather unavailable: ${(err as Error).message}`);
    // Return an empty forecast rather than crashing
    return {
      destination: dest.name,
      days: [],
      summary: 'Weather data currently unavailable — check a local forecast before travelling.',
    };
  }
}

async function getGuideData(destinationName: string) {
  const cacheKey = `wv:${destinationName.toLowerCase().trim()}`;
  const cached = cache.get<ReturnType<typeof wikivoyage.getGuide> extends Promise<infer T> ? T : never>(cacheKey);
  if (cached) return cached;

  const guide = await wikivoyage.getGuide(destinationName);
  cache.set(cacheKey, guide, TTL.WIKIVOYAGE);
  return guide;
}

function log(msg: string): void {
  process.stderr.write(`[tour-planner] ${msg}\n`);
}
