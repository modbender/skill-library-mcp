import axios, { AxiosInstance } from 'axios';
import { Destination } from '../types';

/**
 * Nominatim API client for geocoding
 * Free, no API key required, 1 request per second limit
 * https://nominatim.org/release-docs/develop/api/Search/
 */
export class NominatimClient {
  private client: AxiosInstance;
  private lastRequestTime: number = 0;
  private readonly minRequestInterval = 1100; // 1.1 seconds to be safe

  constructor() {
    this.client = axios.create({
      baseURL: 'https://nominatim.openstreetmap.org',
      headers: {
        'User-Agent': 'OpenCLAW-TourPlanner/1.0 (openclaw.tours)',
      },
    });
  }

  /**
   * Rate limiter to respect Nominatim's 1 req/sec policy
   */
  private async rateLimit(): Promise<void> {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    if (timeSinceLastRequest < this.minRequestInterval) {
      const delay = this.minRequestInterval - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    this.lastRequestTime = Date.now();
  }

  /**
   * Search for a location and return geocoded results
   */
  async search(query: string, limit: number = 1): Promise<Destination[]> {
    await this.rateLimit();

    try {
      const response = await this.client.get('/search', {
        params: {
          q: query,
          format: 'json',
          limit: limit,
          addressdetails: 1,
          extratags: 1,
          namedetails: 1,
        },
      });

      return response.data.map((item: any) => this.parseResult(item));
    } catch (error) {
      console.error('Nominatim search error:', error);
      throw new Error(`Failed to geocode "${query}". Please try again.`);
    }
  }

  /**
   * Reverse geocode: coordinates to address
   */
  async reverse(lat: number, lon: number): Promise<Destination> {
    await this.rateLimit();

    try {
      const response = await this.client.get('/reverse', {
        params: {
          lat: lat,
          lon: lon,
          format: 'json',
          addressdetails: 1,
        },
      });

      return this.parseResult(response.data);
    } catch (error) {
      console.error('Nominatim reverse geocode error:', error);
      throw new Error(`Failed to reverse geocode coordinates (${lat}, ${lon}).`);
    }
  }

  /**
   * Parse Nominatim API response into Destination object
   */
  private parseResult(item: any): Destination {
    const address = item.address || {};
    
    return {
      name: item.namedetails?.name || item.name || item.display_name.split(',')[0],
      country: address.country || '',
      coordinates: {
        lat: parseFloat(item.lat),
        lon: parseFloat(item.lon),
      },
      boundingBox: item.boundingbox 
        ? [
            parseFloat(item.boundingbox[0]),
            parseFloat(item.boundingbox[1]),
            parseFloat(item.boundingbox[2]),
            parseFloat(item.boundingbox[3]),
          ]
        : undefined,
      timezone: item.extratags?.timezone,
      currency: undefined, // Will be populated from RestCountries
      language: address.country_code 
        ? this.getLanguageFromCountryCode(address.country_code)
        : undefined,
    };
  }

  /**
   * Simple mapping of country codes to primary language
   * In production, this should use RestCountries API
   */
  private getLanguageFromCountryCode(code: string): string | undefined {
    const languageMap: Record<string, string> = {
      'jp': 'Japanese',
      'fr': 'French',
      'es': 'Spanish',
      'de': 'German',
      'it': 'Italian',
      'cn': 'Chinese',
      'kr': 'Korean',
      'th': 'Thai',
      'vn': 'Vietnamese',
      'in': 'Hindi/English',
      'gb': 'English',
      'us': 'English',
      'au': 'English',
      'ca': 'English/French',
      'br': 'Portuguese',
      'mx': 'Spanish',
      'ru': 'Russian',
      'tr': 'Turkish',
      'ae': 'Arabic/English',
    };
    
    return languageMap[code.toLowerCase()];
  }
}

// Export singleton instance
export const nominatim = new NominatimClient();
