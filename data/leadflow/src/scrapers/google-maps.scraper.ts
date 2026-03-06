/**
 * Google Places API scraper
 *
 * Uses the Google Places API (New) - $200 free credit/month
 * https://developers.google.com/maps/documentation/places/web-service
 */

import { BaseScraper } from './base.scraper.js';
import { createApiClient } from '../core/http/client.js';
import { createRateLimiter } from '../core/http/rate-limiter.js';
import { requireApiKey } from '../config/index.js';
import { ConfigurationError } from '../errors/index.js';
import {
  Trade,
  type ScrapeQuery,
  type RawLead,
  type LeadSource,
} from '../types/index.js';

/**
 * Google Places API response types (Text Search)
 */
interface PlacesTextSearchResponse {
  places?: GooglePlace[];
  nextPageToken?: string;
}

interface GooglePlace {
  id: string;
  displayName?: {
    text: string;
    languageCode?: string;
  };
  formattedAddress?: string;
  addressComponents?: AddressComponent[];
  nationalPhoneNumber?: string;
  internationalPhoneNumber?: string;
  websiteUri?: string;
  googleMapsUri?: string;
  rating?: number;
  userRatingCount?: number;
  types?: string[];
  primaryType?: string;
  primaryTypeDisplayName?: {
    text: string;
  };
  location?: {
    latitude: number;
    longitude: number;
  };
}

interface AddressComponent {
  longText: string;
  shortText: string;
  types: string[];
}

/**
 * Search terms for each trade
 */
const TRADE_SEARCH_TERMS: Partial<Record<Trade, string[]>> = {
  // Home Services
  [Trade.HVAC]: ['HVAC contractor', 'heating and cooling', 'air conditioning repair'],
  [Trade.PLUMBING]: ['plumber', 'plumbing contractor', 'emergency plumber'],
  [Trade.ELECTRICAL]: ['electrician', 'electrical contractor'],
  [Trade.ROOFING]: ['roofing contractor', 'roof repair', 'roofer'],
  [Trade.GENERAL]: ['general contractor', 'home services'],
  [Trade.LANDSCAPING]: ['landscaping company', 'lawn care service'],
  [Trade.PEST_CONTROL]: ['pest control', 'exterminator'],
  [Trade.CLEANING]: ['cleaning service', 'house cleaning', 'janitorial service'],
  [Trade.PAINTING]: ['painting contractor', 'house painter'],
  [Trade.FLOORING]: ['flooring contractor', 'hardwood floor installer'],
  [Trade.FENCING]: ['fence company', 'fence contractor'],
  [Trade.TREE_SERVICE]: ['tree service', 'tree removal'],
  [Trade.POOL]: ['pool service', 'pool contractor'],
  [Trade.WINDOWS]: ['window replacement', 'window installer', 'door installer'],
  [Trade.GARAGE_DOOR]: ['garage door repair', 'garage door installer'],
  [Trade.CONCRETE]: ['concrete contractor', 'concrete company'],
  [Trade.SIDING]: ['siding contractor', 'siding installer'],
  [Trade.INSULATION]: ['insulation contractor', 'spray foam insulation'],
  [Trade.SOLAR]: ['solar panel installer', 'solar company'],
  [Trade.HANDYMAN]: ['handyman', 'handyman service'],
  [Trade.APPLIANCE]: ['appliance repair', 'appliance service'],
  [Trade.LOCKSMITH]: ['locksmith', 'locksmith service'],
  [Trade.MOVING]: ['moving company', 'movers'],
  // Auto
  [Trade.AUTO_REPAIR]: ['auto repair shop', 'mechanic', 'car repair'],
  [Trade.AUTO_BODY]: ['auto body shop', 'collision repair'],
  [Trade.AUTO_DETAILING]: ['auto detailing', 'car detailing', 'car wash'],
  [Trade.TOWING]: ['towing service', 'tow truck'],
  // Healthcare
  [Trade.DENTAL]: ['dentist', 'dental office', 'family dentistry'],
  [Trade.MEDICAL]: ['doctor', 'medical practice', 'family physician'],
  [Trade.CHIROPRACTIC]: ['chiropractor', 'chiropractic office'],
  [Trade.VETERINARY]: ['veterinarian', 'animal hospital', 'vet clinic'],
  [Trade.PHARMACY]: ['pharmacy', 'drugstore'],
  // Professional Services
  [Trade.LEGAL]: ['lawyer', 'law firm', 'attorney'],
  [Trade.ACCOUNTING]: ['accountant', 'CPA', 'tax preparation', 'bookkeeper'],
  [Trade.REAL_ESTATE]: ['real estate agent', 'realtor', 'real estate broker'],
  [Trade.INSURANCE]: ['insurance agent', 'insurance broker', 'insurance agency'],
  [Trade.MARKETING]: ['marketing agency', 'digital marketing', 'advertising agency'],
  [Trade.IT_SERVICES]: ['IT services', 'managed IT', 'computer repair', 'IT consulting'],
  [Trade.CONSULTING]: ['business consultant', 'consulting firm', 'management consulting'],
  // Food & Hospitality
  [Trade.RESTAURANT]: ['restaurant', 'dining', 'cafe'],
  [Trade.CATERING]: ['catering company', 'catering service'],
  [Trade.BAKERY]: ['bakery', 'cake shop'],
  [Trade.HOTEL]: ['hotel', 'inn', 'bed and breakfast'],
  // Retail
  [Trade.RETAIL]: ['retail store', 'shop'],
  [Trade.ECOMMERCE]: ['online store', 'ecommerce business'],
  // Personal Services
  [Trade.SALON]: ['hair salon', 'beauty salon', 'spa', 'barber shop'],
  [Trade.FITNESS]: ['gym', 'fitness center', 'personal trainer', 'yoga studio'],
  [Trade.PHOTOGRAPHY]: ['photographer', 'photography studio', 'wedding photographer'],
  [Trade.PET_SERVICES]: ['pet grooming', 'dog walker', 'pet sitter'],
  // Education
  [Trade.TUTORING]: ['tutoring service', 'tutor', 'learning center'],
  [Trade.DAYCARE]: ['daycare', 'childcare', 'preschool'],
  // Other
  [Trade.MANUFACTURING]: ['manufacturer', 'manufacturing company'],
  [Trade.CONSTRUCTION]: ['construction company', 'building contractor'],
  [Trade.TRANSPORTATION]: ['transportation service', 'logistics company'],
  [Trade.NONPROFIT]: ['nonprofit organization', 'charity'],
  [Trade.UNKNOWN]: ['business'],
};

/**
 * Google Places API scraper
 */
export class GoogleMapsScraper extends BaseScraper {
  readonly name = 'Google Maps' as LeadSource;

  private apiKey: string | null = null;
  private apiClient;
  private readonly API_BASE = 'https://places.googleapis.com/v1';
  private readonly MAX_RESULTS_PER_REQUEST = 20; // Google limit

  constructor() {
    super();

    // Create dedicated API client with rate limiting
    // Google allows 100 QPS with billing enabled
    const rateLimiter = createRateLimiter('google-places-api', 10, 1000);
    this.apiClient = createApiClient(this.API_BASE, rateLimiter);
  }

  /**
   * Initialize API key lazily
   */
  private getApiKey(): string {
    if (!this.apiKey) {
      try {
        this.apiKey = requireApiKey('GOOGLE_PLACES_API_KEY');
      } catch {
        throw new ConfigurationError(
          'Google Places API key not configured. Set GOOGLE_PLACES_API_KEY in your .env file.',
          'GOOGLE_PLACES_API_KEY'
        );
      }
    }
    return this.apiKey;
  }

  /**
   * Test connection to Google Places API
   */
  async testConnection(): Promise<boolean> {
    try {
      const apiKey = this.getApiKey();

      // Simple search to test API
      await this.apiClient.post<PlacesTextSearchResponse>(
        '/places:searchText',
        {
          textQuery: 'plumber in New York',
          maxResultCount: 1,
        },
        {
          headers: {
            'X-Goog-Api-Key': apiKey,
            'X-Goog-FieldMask': 'places.id',
          },
        }
      );

      this.logger.info('Google Places API connection successful');
      return true;
    } catch (error) {
      this.logger.error(`Google Places API connection failed: ${error}`);
      return false;
    }
  }

  /**
   * Scrape leads from Google Places
   */
  async *scrape(query: ScrapeQuery): AsyncGenerator<RawLead, void, unknown> {
    const apiKey = this.getApiKey();

    // Build location string
    const location = this.buildLocationString(query);

    // Track seen place IDs to avoid duplicates
    const seenIds = new Set<string>();
    let totalYielded = 0;

    // Scrape each trade
    for (const trade of query.trades) {
      const searchTerms = TRADE_SEARCH_TERMS[trade] ?? ['contractor'];

      for (const term of searchTerms) {
        const textQuery = `${term} in ${location}`;
        this.logger.info(`Searching: "${textQuery}"`);

        let pageToken: string | undefined;
        let hasMore = true;

        while (hasMore) {
          try {
            // Convert miles to meters for Google API
          const radiusMeters = query.location.radius
            ? Math.round(query.location.radius * 1609.34)
            : undefined;

          const response = await this.withRetry(() =>
              this.searchPlaces(apiKey, textQuery, pageToken, radiusMeters)
            );

            if (!response.places || response.places.length === 0) {
              hasMore = false;
              break;
            }

            // Convert to RawLead and yield
            for (const place of response.places) {
              // Skip if we've seen this place
              if (seenIds.has(place.id)) {
                continue;
              }
              seenIds.add(place.id);

              const lead = this.placeToLead(place, trade);
              if (lead) {
                yield lead;
                totalYielded++;

                // Check max results
                if (query.maxResults && totalYielded >= query.maxResults) {
                  return;
                }
              }
            }

            // Check pagination
            pageToken = response.nextPageToken;
            hasMore = !!pageToken;

            this.logger.debug(
              `Found ${response.places.length} places for "${term}" (total: ${totalYielded})`
            );
          } catch (error) {
            this.logger.error(`Error searching Google Places: ${error}`);
            hasMore = false;
          }
        }
      }
    }

    this.logger.info(`Scraped ${totalYielded} total places from Google Maps`);
  }

  /**
   * Search places using Text Search
   */
  private async searchPlaces(
    apiKey: string,
    textQuery: string,
    pageToken?: string,
    radiusMeters?: number
  ): Promise<PlacesTextSearchResponse> {
    const body: Record<string, unknown> = {
      textQuery,
      maxResultCount: this.MAX_RESULTS_PER_REQUEST,
      languageCode: 'en',
      regionCode: 'US',
    };

    // Add location bias with radius if specified
    if (radiusMeters) {
      body.locationBias = {
        circle: {
          radius: radiusMeters,
        },
      };
    }

    if (pageToken) {
      body.pageToken = pageToken;
    }

    const response = await this.apiClient.post<PlacesTextSearchResponse>(
      '/places:searchText',
      body,
      {
        headers: {
          'X-Goog-Api-Key': apiKey,
          'X-Goog-FieldMask': [
            'places.id',
            'places.displayName',
            'places.formattedAddress',
            'places.addressComponents',
            'places.nationalPhoneNumber',
            'places.internationalPhoneNumber',
            'places.websiteUri',
            'places.googleMapsUri',
            'places.rating',
            'places.userRatingCount',
            'places.types',
            'places.primaryType',
            'nextPageToken',
          ].join(','),
        },
      }
    );

    return response.data;
  }

  /**
   * Convert Google Place to RawLead
   */
  private placeToLead(place: GooglePlace, trade: Trade): RawLead | null {
    if (!place.displayName?.text) {
      return null;
    }

    // Parse address components
    const addressParts = this.parseAddressComponents(place.addressComponents);

    return {
      companyName: place.displayName.text,
      phone: place.nationalPhoneNumber || place.internationalPhoneNumber || undefined,
      website: place.websiteUri || undefined,
      address: addressParts.streetAddress || place.formattedAddress || undefined,
      city: addressParts.city,
      state: addressParts.state,
      zipCode: addressParts.zipCode,
      trade,
      source: 'Google Maps' as LeadSource,
      sourceUrl: place.googleMapsUri || undefined,
      sourceId: place.id,
      rating: place.rating,
      reviewCount: place.userRatingCount,
      scrapedAt: new Date(),
    };
  }

  /**
   * Parse address components from Google Places
   */
  private parseAddressComponents(
    components?: AddressComponent[]
  ): {
    streetAddress?: string;
    city?: string;
    state?: string;
    zipCode?: string;
  } {
    if (!components) {
      return {};
    }

    const result: {
      streetNumber?: string;
      route?: string;
      city?: string;
      state?: string;
      zipCode?: string;
    } = {};

    for (const component of components) {
      if (component.types.includes('street_number')) {
        result.streetNumber = component.longText;
      } else if (component.types.includes('route')) {
        result.route = component.longText;
      } else if (component.types.includes('locality')) {
        result.city = component.longText;
      } else if (component.types.includes('administrative_area_level_1')) {
        result.state = component.shortText;
      } else if (component.types.includes('postal_code')) {
        result.zipCode = component.longText;
      }
    }

    const streetAddress =
      result.streetNumber && result.route
        ? `${result.streetNumber} ${result.route}`
        : result.route;

    return {
      streetAddress,
      city: result.city,
      state: result.state,
      zipCode: result.zipCode,
    };
  }

  /**
   * Build location string from query
   */
  private buildLocationString(query: ScrapeQuery): string {
    const parts: string[] = [];

    if (query.location.city) {
      parts.push(query.location.city);
    }

    if (query.location.county) {
      parts.push(query.location.county);
    }

    if (query.location.state) {
      parts.push(query.location.state);
    }

    return parts.join(', ') || 'Westchester County, NY';
  }
}
