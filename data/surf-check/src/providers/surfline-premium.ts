/**
 * Surfline Premium API Client
 * 
 * Uses saved session cookies to access premium features:
 * - 16-day forecasts (vs 6-day free)
 * - Extended analysis and expert reports
 * 
 * Requires running login-surfline.ts first to save session cookies.
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { fileURLToPath } from 'url';
import {
  SpotConfig,
  SurflineWaveResponse,
  SurflineRatingResponse,
  SurflineConditionsResponse,
  DayForecast,
  RatingKey,
  RATING_VALUES,
  RATING_DISPLAY,
} from '../types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SESSION_DIR = path.join(__dirname, '..', '..', 'data', 'session');
const COOKIES_FILE = path.join(SESSION_DIR, 'cookies.json');

const BASE_URL = 'https://services.surfline.com/kbyg/spots/forecasts';

interface Cookie {
  name: string;
  value: string;
  domain: string;
  path: string;
}

/**
 * Load saved session cookies
 */
async function loadCookies(): Promise<Cookie[]> {
  try {
    const data = await fs.readFile(COOKIES_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    throw new Error(
      'Session cookies not found. Run "npx ts-node scripts/login-surfline.ts" first.'
    );
  }
}

/**
 * Format cookies for fetch header
 */
function formatCookieHeader(cookies: Cookie[]): string {
  return cookies
    .filter((c) => c.domain.includes('surfline.com'))
    .map((c) => `${c.name}=${c.value}`)
    .join('; ');
}

/**
 * Check if session is valid
 */
export async function checkSession(): Promise<boolean> {
  try {
    const cookies = await loadCookies();
    
    // Try to fetch a minimal request with auth
    const response = await fetch(
      `${BASE_URL}/wave?spotId=5842041f4e65fad6a7708a01&days=1`,
      {
        headers: {
          Cookie: formatCookieHeader(cookies),
        },
      }
    );

    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Make authenticated request to Surfline API
 */
async function authenticatedFetch<T>(url: string): Promise<T> {
  const cookies = await loadCookies();
  
  const response = await fetch(url, {
    headers: {
      Cookie: formatCookieHeader(cookies),
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error('Session expired. Run login-surfline.ts to refresh.');
    }
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export interface PremiumFetchOptions {
  days?: number;
  intervalHours?: number;
}

/**
 * Fetch premium wave forecast (up to 16 days)
 */
export async function fetchPremiumWaveForecast(
  spotId: string,
  options: PremiumFetchOptions = {}
): Promise<SurflineWaveResponse> {
  const { days = 16, intervalHours = 6 } = options;
  const url = `${BASE_URL}/wave?spotId=${spotId}&days=${days}&intervalHours=${intervalHours}`;
  return authenticatedFetch(url);
}

/**
 * Fetch premium rating forecast (up to 16 days)
 */
export async function fetchPremiumRatingForecast(
  spotId: string,
  options: PremiumFetchOptions = {}
): Promise<SurflineRatingResponse> {
  const { days = 16, intervalHours = 6 } = options;
  const url = `${BASE_URL}/rating?spotId=${spotId}&days=${days}&intervalHours=${intervalHours}`;
  return authenticatedFetch(url);
}

/**
 * Fetch premium conditions forecast
 */
export async function fetchPremiumConditionsForecast(
  spotId: string,
  options: PremiumFetchOptions = {}
): Promise<SurflineConditionsResponse> {
  const { days = 16 } = options;
  const url = `${BASE_URL}/conditions?spotId=${spotId}&days=${days}`;
  return authenticatedFetch(url);
}

/**
 * Helper: Get day of week name
 */
function getDayOfWeek(date: Date): string {
  return date.toLocaleDateString('en-US', { weekday: 'long' });
}

/**
 * Helper: Check if date is a weekend (Friday, Saturday, Sunday)
 */
function isWeekend(date: Date): boolean {
  const day = date.getDay();
  return day === 0 || day === 5 || day === 6;
}

/**
 * Helper: Format date as string
 */
function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Fetch premium daily forecasts with full 16-day range
 */
export async function fetchPremiumDailyForecasts(
  spot: SpotConfig,
  days: number = 16
): Promise<DayForecast[]> {
  const [waveData, ratingData] = await Promise.all([
    fetchPremiumWaveForecast(spot.id, { days, intervalHours: 24 }),
    fetchPremiumRatingForecast(spot.id, { days, intervalHours: 24 }),
  ]);

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
          key: RatingKey.FAIR,
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

  return Array.from(forecastsByDate.values()).sort(
    (a, b) => a.date.getTime() - b.date.getTime()
  );
}
