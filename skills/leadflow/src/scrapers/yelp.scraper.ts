/**
 * Yelp Fusion API scraper
 *
 * Uses the official Yelp Fusion API (5,000 calls/day free)
 * https://www.yelp.com/developers/documentation/v3
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
 * Yelp API response types
 */
interface YelpBusinessSearchResponse {
  businesses: YelpBusiness[];
  total: number;
  region?: {
    center: {
      latitude: number;
      longitude: number;
    };
  };
}

interface YelpBusiness {
  id: string;
  alias: string;
  name: string;
  image_url?: string;
  is_closed: boolean;
  url: string;
  review_count: number;
  categories: YelpCategory[];
  rating: number;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  transactions: string[];
  price?: string;
  location: YelpLocation;
  phone: string;
  display_phone: string;
  distance?: number;
}

interface YelpCategory {
  alias: string;
  title: string;
}

interface YelpLocation {
  address1: string | null;
  address2: string | null;
  address3: string | null;
  city: string;
  zip_code: string;
  country: string;
  state: string;
  display_address: string[];
}

/**
 * Map trade to Yelp categories
 */
const TRADE_TO_CATEGORIES: Partial<Record<Trade, string[]>> = {
  // Home Services
  [Trade.HVAC]: ['hvac', 'heating', 'airconditioning'],
  [Trade.PLUMBING]: ['plumbing', 'waterheaterinstallation'],
  [Trade.ELECTRICAL]: ['electricians', 'lighting'],
  [Trade.ROOFING]: ['roofing', 'gutterservices'],
  [Trade.GENERAL]: ['contractors', 'homeservices'],
  [Trade.LANDSCAPING]: ['landscaping', 'lawnservices', 'gardeners'],
  [Trade.PEST_CONTROL]: ['pestcontrol', 'exterminators'],
  [Trade.CLEANING]: ['homecleaning', 'officecleaning', 'janitorial'],
  [Trade.PAINTING]: ['painters', 'housepainters'],
  [Trade.FLOORING]: ['flooring', 'carpetinstallation', 'tiling'],
  [Trade.FENCING]: ['fences', 'fencesandgates'],
  [Trade.TREE_SERVICE]: ['treeservices', 'treeremovals'],
  [Trade.POOL]: ['swimmingpools', 'poolservice', 'poolcleaners'],
  [Trade.WINDOWS]: ['windows_installation', 'doorinstallation'],
  [Trade.GARAGE_DOOR]: ['garagedoorservices'],
  [Trade.CONCRETE]: ['masonry_concrete'],
  [Trade.SIDING]: ['siding'],
  [Trade.INSULATION]: ['insulation_installation'],
  [Trade.SOLAR]: ['solarinstallation', 'solarpanelcleaning'],
  [Trade.HANDYMAN]: ['handyman'],
  [Trade.APPLIANCE]: ['appliancesrepair'],
  [Trade.LOCKSMITH]: ['locksmiths'],
  [Trade.MOVING]: ['movers', 'localmovers'],
  // Auto
  [Trade.AUTO_REPAIR]: ['autorepair', 'mechanics', 'oilchange'],
  [Trade.AUTO_BODY]: ['autobodyshops', 'collisionrepair'],
  [Trade.AUTO_DETAILING]: ['autodetailing', 'carwash'],
  [Trade.TOWING]: ['towing', 'roadsideassistance'],
  // Healthcare
  [Trade.DENTAL]: ['dentists', 'cosmeticdentists', 'generaldentistry'],
  [Trade.MEDICAL]: ['doctors', 'familypractice', 'internalmed'],
  [Trade.CHIROPRACTIC]: ['chiropractors'],
  [Trade.VETERINARY]: ['vet', 'animalhospitals', 'veterinarians'],
  [Trade.PHARMACY]: ['pharmacy'],
  // Professional Services
  [Trade.LEGAL]: ['lawyers', 'personalinjurylaw', 'divorcelawyers', 'estateplanninglaw'],
  [Trade.ACCOUNTING]: ['accountants', 'taxservices', 'bookkeepers'],
  [Trade.REAL_ESTATE]: ['realestateagents', 'realestateservices'],
  [Trade.INSURANCE]: ['insurance', 'autoinsurance', 'homeinsurance'],
  [Trade.MARKETING]: ['marketing', 'advertisingagencies', 'graphicdesign'],
  [Trade.IT_SERVICES]: ['itservices', 'computerrepair', 'datarecovery'],
  [Trade.CONSULTING]: ['businessconsulting', 'managementconsulting'],
  // Food & Hospitality
  [Trade.RESTAURANT]: ['restaurants', 'newamerican', 'italian', 'mexican'],
  [Trade.CATERING]: ['catering', 'eventplanning'],
  [Trade.BAKERY]: ['bakeries', 'customcakes'],
  [Trade.HOTEL]: ['hotels', 'bedbreakfast'],
  // Retail
  [Trade.RETAIL]: ['shopping', 'fashion', 'giftshops'],
  [Trade.ECOMMERCE]: ['shopping'],
  // Personal Services
  [Trade.SALON]: ['hair', 'hairsalons', 'spas', 'barbers', 'nailsalons'],
  [Trade.FITNESS]: ['gyms', 'personaltrainers', 'yoga', 'pilates'],
  [Trade.PHOTOGRAPHY]: ['photographers', 'eventphotography'],
  [Trade.PET_SERVICES]: ['petgroomers', 'dogwalkers', 'petsitting'],
  // Education
  [Trade.TUTORING]: ['tutoring', 'testprep', 'educationalservices'],
  [Trade.DAYCARE]: ['childcare', 'preschools'],
  // Other
  [Trade.MANUFACTURING]: ['manufacturing'],
  [Trade.CONSTRUCTION]: ['contractors', 'constructioncompanies'],
  [Trade.TRANSPORTATION]: ['couriers', 'transportation'],
  [Trade.NONPROFIT]: ['nonprofit'],
  [Trade.UNKNOWN]: ['localservices'],
};

/**
 * Yelp Fusion API scraper
 */
export class YelpScraper extends BaseScraper {
  readonly name = 'Yelp' as LeadSource;

  private apiKey: string | null = null;
  private apiClient;
  private readonly API_BASE = 'https://api.yelp.com/v3';
  private readonly MAX_RESULTS_PER_REQUEST = 50; // Yelp limit
  private readonly MAX_OFFSET = 1000; // Yelp limit

  constructor() {
    super();

    // Create dedicated API client with rate limiting
    const rateLimiter = createRateLimiter('yelp-api', 5, 1000); // 5 QPS
    this.apiClient = createApiClient(this.API_BASE, rateLimiter);
  }

  /**
   * Initialize API key lazily
   */
  private getApiKey(): string {
    if (!this.apiKey) {
      try {
        this.apiKey = requireApiKey('YELP_API_KEY');
      } catch {
        throw new ConfigurationError(
          'Yelp API key not configured. Set YELP_API_KEY in your .env file.',
          'YELP_API_KEY'
        );
      }
    }
    return this.apiKey;
  }

  /**
   * Test connection to Yelp API
   */
  async testConnection(): Promise<boolean> {
    try {
      const apiKey = this.getApiKey();

      // Simple autocomplete request to test API
      await this.apiClient.get('/autocomplete', {
        params: { text: 'plumber' },
        headers: { Authorization: `Bearer ${apiKey}` },
      });

      this.logger.info('Yelp API connection successful');
      return true;
    } catch (error) {
      this.logger.error(`Yelp API connection failed: ${error}`);
      return false;
    }
  }

  /**
   * Scrape leads from Yelp
   */
  async *scrape(query: ScrapeQuery): AsyncGenerator<RawLead, void, unknown> {
    const apiKey = this.getApiKey();

    // Build location string
    const location = this.buildLocationString(query);

    // Scrape each trade
    for (const trade of query.trades) {
      const categories = TRADE_TO_CATEGORIES[trade] ?? [];

      this.logger.info(`Scraping ${trade} businesses in ${location}`);

      let offset = 0;
      let hasMore = true;

      while (hasMore && offset < this.MAX_OFFSET) {
        try {
          // Convert miles to meters for Yelp API (max 40000m ~= 25 miles)
          const radiusMeters = query.location.radius
            ? Math.min(Math.round(query.location.radius * 1609.34), 40000)
            : undefined;

          const response = await this.withRetry(() =>
            this.searchBusinesses(apiKey, {
              location,
              categories: categories.join(','),
              limit: this.MAX_RESULTS_PER_REQUEST,
              offset,
              radius: radiusMeters,
            })
          );

          if (response.businesses.length === 0) {
            hasMore = false;
            break;
          }

          // Convert to RawLead and yield
          for (const business of response.businesses) {
            if (!business.is_closed) {
              yield this.businessToLead(business, trade);
            }
          }

          // Check if we should continue
          offset += response.businesses.length;
          hasMore = offset < response.total && offset < this.MAX_OFFSET;

          if (query.maxResults && offset >= query.maxResults) {
            hasMore = false;
          }

          this.logger.debug(
            `Scraped ${offset}/${Math.min(response.total, this.MAX_OFFSET)} ${trade} businesses`
          );
        } catch (error) {
          this.logger.error(`Error scraping Yelp: ${error}`);
          hasMore = false;
        }
      }
    }
  }

  /**
   * Search Yelp businesses
   */
  private async searchBusinesses(
    apiKey: string,
    params: {
      location: string;
      categories?: string;
      limit?: number;
      offset?: number;
      term?: string;
      radius?: number;
    }
  ): Promise<YelpBusinessSearchResponse> {
    const response = await this.apiClient.get<YelpBusinessSearchResponse>(
      '/businesses/search',
      {
        params,
        headers: { Authorization: `Bearer ${apiKey}` },
      }
    );

    return response.data;
  }

  /**
   * Convert Yelp business to RawLead
   */
  private businessToLead(business: YelpBusiness, trade: Trade): RawLead {
    return {
      companyName: business.name,
      phone: business.phone || undefined,
      website: undefined, // Yelp API doesn't provide website directly
      address: business.location.address1 || undefined,
      city: business.location.city,
      state: business.location.state,
      zipCode: business.location.zip_code,
      trade,
      source: 'Yelp' as LeadSource,
      sourceUrl: business.url,
      sourceId: business.id,
      rating: business.rating,
      reviewCount: business.review_count,
      scrapedAt: new Date(),
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

    if (query.location.zipCode) {
      parts.push(query.location.zipCode);
    }

    return parts.join(', ') || 'Westchester County, NY';
  }
}
