/**
 * Surfline API Client
 * 
 * Fetches forecast data from Surfline's public KBYG (Know Before You Go) API.
 * Note: Free tier is limited to 6 days of forecast data.
 */

import {
  SpotConfig,
  SurflineWaveResponse,
  SurflineRatingResponse,
  SurflineConditionsResponse,
  SurflineWindResponse,
  DayForecast,
  RatingKey,
  RATING_VALUES,
  RATING_DISPLAY,
} from '../types.js';

const BASE_URL = 'https://services.surfline.com/kbyg/spots/forecasts';

export interface FetchOptions {
  days?: number;
  intervalHours?: number;
}

/**
 * Fetch wave forecast data for a spot
 */
export async function fetchWaveForecast(
  spotId: string,
  options: FetchOptions = {}
): Promise<SurflineWaveResponse> {
  const { days = 6, intervalHours = 6 } = options;
  const url = `${BASE_URL}/wave?spotId=${spotId}&days=${days}&intervalHours=${intervalHours}`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch wave forecast: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch rating forecast data for a spot
 */
export async function fetchRatingForecast(
  spotId: string,
  options: FetchOptions = {}
): Promise<SurflineRatingResponse> {
  const { days = 6, intervalHours = 6 } = options;
  const url = `${BASE_URL}/rating?spotId=${spotId}&days=${days}&intervalHours=${intervalHours}`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch rating forecast: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch conditions forecast data for a spot
 */
export async function fetchConditionsForecast(
  spotId: string,
  options: FetchOptions = {}
): Promise<SurflineConditionsResponse> {
  const { days = 6 } = options;
  const url = `${BASE_URL}/conditions?spotId=${spotId}&days=${days}`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch conditions forecast: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch wind forecast data for a spot
 */
export async function fetchWindForecast(
  spotId: string,
  options: FetchOptions = {}
): Promise<SurflineWindResponse> {
  const { days = 6, intervalHours = 3 } = options;
  const url = `${BASE_URL}/wind?spotId=${spotId}&days=${days}&intervalHours=${intervalHours}`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch wind forecast: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Get day of week name
 */
function getDayOfWeek(date: Date): string {
  return date.toLocaleDateString('en-US', { weekday: 'long' });
}

/**
 * Check if date is a weekend (Friday, Saturday, Sunday)
 */
function isWeekend(date: Date): boolean {
  const day = date.getDay();
  return day === 0 || day === 5 || day === 6; // Sun, Fri, Sat
}

/**
 * Format date as string
 */
function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Aggregate wave and rating data into daily forecasts
 */
export async function fetchDailyForecasts(
  spot: SpotConfig,
  days: number = 6
): Promise<DayForecast[]> {
  // Fetch all data in parallel
  const [waveData, ratingData, windData] = await Promise.all([
    fetchWaveForecast(spot.id, { days, intervalHours: 24 }),
    fetchRatingForecast(spot.id, { days, intervalHours: 24 }),
    fetchWindForecast(spot.id, { days, intervalHours: 12 }),
  ]);

  // Group by date
  const forecastsByDate = new Map<string, DayForecast>();

  // Process wave data
  for (const item of waveData.data.wave) {
    const date = new Date(item.timestamp * 1000);
    const dateKey = date.toISOString().split('T')[0];

    if (!forecastsByDate.has(dateKey)) {
      forecastsByDate.set(dateKey, {
        date,
        dateString: formatDate(date),
        dayOfWeek: getDayOfWeek(date),
        isWeekend: isWeekend(date),
        spot,
        wave: {
          min: item.surf.min,
          max: item.surf.max,
          humanRelation: item.surf.humanRelation,
        },
        rating: {
          key: RatingKey.FAIR, // Will be updated
          value: 2,
          display: 'Fair',
        },
        wind: null,
        swells: item.swells,
      });
    }
  }

  // Process rating data
  for (const item of ratingData.data.rating) {
    const date = new Date(item.timestamp * 1000);
    const dateKey = date.toISOString().split('T')[0];

    const forecast = forecastsByDate.get(dateKey);
    if (forecast) {
      forecast.rating = {
        key: item.rating.key,
        value: RATING_VALUES[item.rating.key] || item.rating.value,
        display: RATING_DISPLAY[item.rating.key] || item.rating.key,
      };
    }
  }

  // Process wind data (take first reading of day)
  const windByDate = new Map<string, typeof windData.data.wind[0]>();
  for (const item of windData.data.wind) {
    const date = new Date(item.timestamp * 1000);
    const dateKey = date.toISOString().split('T')[0];
    
    if (!windByDate.has(dateKey)) {
      windByDate.set(dateKey, item);
    }
  }

  for (const [dateKey, windItem] of windByDate) {
    const forecast = forecastsByDate.get(dateKey);
    if (forecast) {
      forecast.wind = {
        speed: windItem.speed,
        direction: windItem.direction,
        directionType: windItem.directionType,
      };
    }
  }

  // Sort by date and return
  return Array.from(forecastsByDate.values()).sort(
    (a, b) => a.date.getTime() - b.date.getTime()
  );
}

/**
 * Format forecast for display
 */
export function formatForecast(forecast: DayForecast): string {
  const waveRange = `${Math.round(forecast.wave.min)}-${Math.round(forecast.wave.max)}ft`;
  const rating = forecast.rating.display;
  
  let wind = '';
  if (forecast.wind) {
    wind = ` | ${forecast.wind.directionType} ${Math.round(forecast.wind.speed)}mph`;
  }

  return `${forecast.dateString}: ${waveRange} | ${rating}${wind}`;
}
