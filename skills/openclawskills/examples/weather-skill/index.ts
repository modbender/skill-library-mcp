/**
 * Weather Skill
 * Fetches weather data from OpenWeatherMap API
 */

interface WeatherConfig {
  apiKey: string;
  defaultLocation?: string;
  units?: 'metric' | 'imperial' | 'kelvin';
}

interface SkillContext {
  userId: string;
  memory: MemoryStore;
  logger: Logger;
  http: HttpClient;
}

interface MemoryStore {
  get(key: string): Promise<any>;
  set(key: string, value: any): Promise<void>;
}

interface Logger {
  debug(msg: string): void;
  info(msg: string): void;
  error(msg: string): void;
}

interface HttpClient {
  get(url: string, options?: any): Promise<any>;
}

interface WeatherData {
  location: string;
  temperature: number;
  feelsLike: number;
  humidity: number;
  description: string;
  windSpeed: number;
  timestamp: string;
}

export class WeatherSkill {
  private config: WeatherConfig;
  private context: SkillContext;
  private baseUrl = 'https://api.openweathermap.org/data/2.5';

  constructor(config: WeatherConfig, context: SkillContext) {
    this.config = config;
    this.context = context;
  }

  /**
   * Get current weather for a location
   */
  async getCurrentWeather(location?: string): Promise<WeatherData> {
    const targetLocation = location || this.config.defaultLocation || 'London';
    
    this.context.logger.debug(`Fetching weather for: ${targetLocation}`);

    try {
      const response = await this.context.http.get(
        `${this.baseUrl}/weather?q=${encodeURIComponent(targetLocation)}&appid=${this.config.apiKey}&units=${this.config.units || 'metric'}`
      );

      const weather: WeatherData = {
        location: `${response.name}, ${response.sys.country}`,
        temperature: response.main.temp,
        feelsLike: response.main.feels_like,
        humidity: response.main.humidity,
        description: response.weather[0].description,
        windSpeed: response.wind.speed,
        timestamp: new Date().toISOString()
      };

      // Cache in memory
      await this.context.memory.set(
        `weather:last:${this.context.userId}`,
        weather
      );

      return weather;
    } catch (error) {
      this.context.logger.error(`Weather fetch failed: ${error}`);
      throw new Error(`Could not fetch weather for ${targetLocation}`);
    }
  }

  /**
   * Get 5-day forecast
   */
  async getForecast(location?: string): Promise<any> {
    const targetLocation = location || this.config.defaultLocation || 'London';
    
    this.context.logger.debug(`Fetching forecast for: ${targetLocation}`);

    try {
      const response = await this.context.http.get(
        `${this.baseUrl}/forecast?q=${encodeURIComponent(targetLocation)}&appid=${this.config.apiKey}&units=${this.config.units || 'metric'}`
      );

      // Simplify forecast data
      const dailyForecasts = response.list
        .filter((item: any, index: number) => index % 8 === 0) // One per day
        .slice(0, 5)
        .map((item: any) => ({
          date: new Date(item.dt * 1000).toDateString(),
          temp: item.main.temp,
          description: item.weather[0].description,
          humidity: item.main.humidity
        }));

      return {
        location: `${response.city.name}, ${response.city.country}`,
        forecast: dailyForecasts
      };
    } catch (error) {
      this.context.logger.error(`Forecast fetch failed: ${error}`);
      throw new Error(`Could not fetch forecast for ${targetLocation}`);
    }
  }

  /**
   * Get last cached weather
   */
  async getLastWeather(): Promise<WeatherData | null> {
    return await this.context.memory.get(`weather:last:${this.context.userId}`);
  }
}

export default function createSkill(config: WeatherConfig, context: SkillContext) {
  return new WeatherSkill(config, context);
}

export type { WeatherConfig, WeatherData };
