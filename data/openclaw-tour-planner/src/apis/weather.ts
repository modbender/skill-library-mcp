import axios from 'axios';
import { WeatherForecast, WeatherDay } from '../types';

/**
 * WMO Weather interpretation codes → human-readable conditions
 * https://open-meteo.com/en/docs#weathervariables
 */
const WMO_CODES: Record<number, string> = {
  0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
  45: 'Fog', 48: 'Icy fog',
  51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
  61: 'Light rain', 63: 'Moderate rain', 65: 'Heavy rain',
  71: 'Light snow', 73: 'Moderate snow', 75: 'Heavy snow',
  77: 'Snow grains',
  80: 'Light showers', 81: 'Moderate showers', 82: 'Violent showers',
  85: 'Snow showers', 86: 'Heavy snow showers',
  95: 'Thunderstorm', 96: 'Thunderstorm with hail', 99: 'Thunderstorm with heavy hail',
};

function wmoToCondition(code: number): string {
  return WMO_CODES[code] ?? 'Unknown';
}

/**
 * Open-Meteo weather client — free, no API key required
 * https://api.open-meteo.com
 */
export class WeatherClient {
  private readonly openMeteoBase = 'https://api.open-meteo.com/v1/forecast';
  private readonly visualCrossingBase =
    'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline';

  /**
   * Get weather forecast for coordinates
   * Primary: Open-Meteo (free, no key)
   * Fallback: Visual Crossing (requires VISUAL_CROSSING_API_KEY env var)
   */
  async getForecast(
    destinationName: string,
    lat: number,
    lon: number,
    days: number = 7,
  ): Promise<WeatherForecast> {
    try {
      return await this.fetchOpenMeteo(destinationName, lat, lon, days);
    } catch (primaryErr) {
      const vcKey = process.env.VISUAL_CROSSING_API_KEY;
      if (vcKey) {
        try {
          return await this.fetchVisualCrossing(destinationName, lat, lon, days, vcKey);
        } catch {
          // fall through to error
        }
      }
      throw new Error(
        `Weather data unavailable for ${destinationName}. ` +
          `Set VISUAL_CROSSING_API_KEY for a fallback source. (${(primaryErr as Error).message})`,
      );
    }
  }

  private async fetchOpenMeteo(
    destinationName: string,
    lat: number,
    lon: number,
    days: number,
  ): Promise<WeatherForecast> {
    const response = await axios.get(this.openMeteoBase, {
      params: {
        latitude: lat,
        longitude: lon,
        daily: [
          'weathercode',
          'temperature_2m_max',
          'temperature_2m_min',
          'precipitation_probability_max',
          'windspeed_10m_max',
          'relative_humidity_2m_max',
        ].join(','),
        timezone: 'auto',
        forecast_days: Math.min(days, 16),
      },
      timeout: 8000,
    });

    const d = response.data.daily;
    const weatherDays: WeatherDay[] = d.time.map((date: string, i: number) => ({
      date,
      tempMax: Math.round(d.temperature_2m_max[i]),
      tempMin: Math.round(d.temperature_2m_min[i]),
      conditions: wmoToCondition(d.weathercode[i]),
      precipitationChance: d.precipitation_probability_max[i] ?? 0,
      humidity: d.relative_humidity_2m_max[i] ?? 0,
      windSpeed: Math.round(d.windspeed_10m_max[i]),
    }));

    return {
      destination: destinationName,
      days: weatherDays,
      summary: this.buildSummary(weatherDays),
    };
  }

  private async fetchVisualCrossing(
    destinationName: string,
    lat: number,
    lon: number,
    days: number,
    apiKey: string,
  ): Promise<WeatherForecast> {
    const url = `${this.visualCrossingBase}/${lat},${lon}/next${days}days`;
    const response = await axios.get(url, {
      params: { unitGroup: 'metric', key: apiKey, contentType: 'json' },
      timeout: 8000,
    });

    const weatherDays: WeatherDay[] = response.data.days
      .slice(0, days)
      .map((day: any) => ({
        date: day.datetime,
        tempMax: Math.round(day.tempmax),
        tempMin: Math.round(day.tempmin),
        conditions: day.conditions ?? 'Unknown',
        precipitationChance: Math.round((day.precipprob ?? 0)),
        humidity: Math.round(day.humidity ?? 0),
        windSpeed: Math.round(day.windspeed ?? 0),
      }));

    return {
      destination: destinationName,
      days: weatherDays,
      summary: this.buildSummary(weatherDays),
    };
  }

  private buildSummary(days: WeatherDay[]): string {
    if (!days.length) return 'No forecast available.';
    const avgHigh = Math.round(days.reduce((s, d) => s + d.tempMax, 0) / days.length);
    const avgLow  = Math.round(days.reduce((s, d) => s + d.tempMin, 0) / days.length);
    const rainyDays = days.filter(d => d.precipitationChance > 40).length;
    const conditions = days[0]?.conditions ?? 'variable';
    return (
      `${avgLow}–${avgHigh}°C, ${conditions.toLowerCase()}` +
      (rainyDays > 0 ? `, ${rainyDays} day(s) with rain likely` : ', low rain chance')
    );
  }
}

export const weatherClient = new WeatherClient();
