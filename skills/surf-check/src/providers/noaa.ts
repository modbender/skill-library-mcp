/**
 * NOAA NDBC Buoy Data Provider
 * 
 * Fetches real-time buoy data from NOAA's National Data Buoy Center.
 * Useful for cross-referencing Surfline forecasts with actual conditions.
 * 
 * Relevant buoy for Monmouth County, NJ:
 * - Station 44091 (Barnegat, NJ)
 */

import { NOAABuoyReading, NOAA_BUOYS } from '../types.js';

const NDBC_BASE_URL = 'https://www.ndbc.noaa.gov/data/realtime2';

/**
 * Parse NDBC realtime2 text format
 * 
 * Format example:
 * #YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE
 * 2026 02 19 00 00  MM   MM   MM   1.4    13   7.7 100     MM   3.1   3.3    MM   MM   MM    MM
 */
function parseNDBCData(text: string): NOAABuoyReading[] {
  const lines = text.trim().split('\n');
  const readings: NOAABuoyReading[] = [];

  for (const line of lines) {
    // Skip header lines
    if (line.startsWith('#')) continue;

    const parts = line.trim().split(/\s+/);
    if (parts.length < 13) continue;

    const [year, month, day, hour, minute, _wdir, _wspd, _gst, wvht, dpd, apd, mwd, _pres, _atmp, wtmp] = parts;

    // Parse timestamp
    const timestamp = new Date(
      parseInt(year),
      parseInt(month) - 1,
      parseInt(day),
      parseInt(hour),
      parseInt(minute)
    );

    // Parse values (MM = missing)
    const parseValue = (val: string): number | null => {
      return val === 'MM' ? null : parseFloat(val);
    };

    readings.push({
      timestamp,
      waveHeight: parseValue(wvht),
      dominantPeriod: parseValue(dpd),
      averagePeriod: parseValue(apd),
      meanDirection: parseValue(mwd),
      waterTemp: wtmp ? parseValue(wtmp) : null,
    });
  }

  return readings;
}

/**
 * Fetch current buoy readings
 */
export async function fetchBuoyData(stationId: string): Promise<NOAABuoyReading[]> {
  const url = `${NDBC_BASE_URL}/${stationId}.txt`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch buoy data: ${response.status} ${response.statusText}`);
  }

  const text = await response.text();
  return parseNDBCData(text);
}

/**
 * Get latest buoy reading
 */
export async function getLatestBuoyReading(stationId: string): Promise<NOAABuoyReading | null> {
  const readings = await fetchBuoyData(stationId);
  return readings.length > 0 ? readings[0] : null;
}

/**
 * Format buoy reading for display
 */
export function formatBuoyReading(reading: NOAABuoyReading): string {
  const lines: string[] = [];
  
  lines.push(`📡 Buoy Reading (${reading.timestamp.toLocaleString()})`);
  
  if (reading.waveHeight !== null) {
    // Convert meters to feet
    const heightFt = (reading.waveHeight * 3.28084).toFixed(1);
    lines.push(`🌊 Wave Height: ${heightFt}ft (${reading.waveHeight.toFixed(1)}m)`);
  }
  
  if (reading.dominantPeriod !== null) {
    lines.push(`⏱️ Period: ${reading.dominantPeriod}s`);
  }
  
  if (reading.meanDirection !== null) {
    const dir = getDirectionName(reading.meanDirection);
    lines.push(`🧭 Direction: ${dir} (${reading.meanDirection}°)`);
  }
  
  if (reading.waterTemp !== null) {
    const tempF = (reading.waterTemp * 9/5 + 32).toFixed(1);
    lines.push(`🌡️ Water Temp: ${tempF}°F (${reading.waterTemp}°C)`);
  }

  return lines.join('\n');
}

/**
 * Convert degrees to compass direction
 */
function getDirectionName(degrees: number): string {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
}

/**
 * Fetch data for Barnegat buoy (default for Monmouth County)
 */
export async function fetchBarnegatBuoyData(): Promise<NOAABuoyReading[]> {
  return fetchBuoyData(NOAA_BUOYS.BARNEGAT.stationId);
}

/**
 * Compare buoy data with Surfline forecast
 * 
 * Useful for:
 * - Validating forecast accuracy
 * - Real-time conditions vs predicted
 */
export interface BuoyComparison {
  buoyReading: NOAABuoyReading;
  surflineForecast: {
    waveMin: number;
    waveMax: number;
    period?: number;
  } | null;
  comparison: {
    heightMatch: boolean;
    heightDelta: number | null;
    periodMatch: boolean;
    periodDelta: number | null;
  };
}

export function compareBuoyToForecast(
  buoyReading: NOAABuoyReading,
  forecastWaveMin: number,
  forecastWaveMax: number
): BuoyComparison {
  const buoyHeightFt = buoyReading.waveHeight !== null
    ? buoyReading.waveHeight * 3.28084
    : null;

  const heightDelta = buoyHeightFt !== null
    ? buoyHeightFt - (forecastWaveMin + forecastWaveMax) / 2
    : null;

  // Consider it a match if within 1ft of forecast range
  const heightMatch = buoyHeightFt !== null
    ? buoyHeightFt >= forecastWaveMin - 1 && buoyHeightFt <= forecastWaveMax + 1
    : false;

  return {
    buoyReading,
    surflineForecast: {
      waveMin: forecastWaveMin,
      waveMax: forecastWaveMax,
    },
    comparison: {
      heightMatch,
      heightDelta,
      periodMatch: false, // TODO: Compare periods when available
      periodDelta: null,
    },
  };
}
