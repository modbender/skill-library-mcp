/**
 * Core lead data types for the scraper
 */

export enum Trade {
  // Home Services
  HVAC = 'HVAC',
  PLUMBING = 'Plumbing',
  ELECTRICAL = 'Electrical',
  ROOFING = 'Roofing',
  GENERAL = 'General Contractor',
  LANDSCAPING = 'Landscaping',
  PAINTING = 'Painting',
  FLOORING = 'Flooring',
  PEST_CONTROL = 'Pest Control',
  CLEANING = 'Cleaning',
  WINDOWS = 'Windows & Doors',
  GARAGE_DOOR = 'Garage Door',
  FENCING = 'Fencing',
  CONCRETE = 'Concrete',
  SIDING = 'Siding',
  INSULATION = 'Insulation',
  SOLAR = 'Solar',
  POOL = 'Pool & Spa',
  TREE_SERVICE = 'Tree Service',
  HANDYMAN = 'Handyman',
  APPLIANCE = 'Appliance Repair',
  LOCKSMITH = 'Locksmith',
  MOVING = 'Moving',
  // Auto
  AUTO_REPAIR = 'Auto Repair',
  AUTO_BODY = 'Auto Body',
  AUTO_DETAILING = 'Auto Detailing',
  TOWING = 'Towing',
  // Healthcare
  DENTAL = 'Dental',
  MEDICAL = 'Medical',
  CHIROPRACTIC = 'Chiropractic',
  VETERINARY = 'Veterinary',
  PHARMACY = 'Pharmacy',
  // Professional Services
  LEGAL = 'Legal',
  ACCOUNTING = 'Accounting',
  INSURANCE = 'Insurance',
  REAL_ESTATE = 'Real Estate',
  MARKETING = 'Marketing',
  IT_SERVICES = 'IT Services',
  CONSULTING = 'Consulting',
  // Food & Hospitality
  RESTAURANT = 'Restaurant',
  CATERING = 'Catering',
  BAKERY = 'Bakery',
  HOTEL = 'Hotel',
  // Retail
  RETAIL = 'Retail',
  ECOMMERCE = 'E-commerce',
  // Personal Services
  SALON = 'Salon & Spa',
  FITNESS = 'Fitness',
  PHOTOGRAPHY = 'Photography',
  PET_SERVICES = 'Pet Services',
  // Education
  TUTORING = 'Tutoring',
  DAYCARE = 'Daycare',
  // Other
  MANUFACTURING = 'Manufacturing',
  CONSTRUCTION = 'Construction',
  TRANSPORTATION = 'Transportation',
  NONPROFIT = 'Nonprofit',
  OTHER = 'Other',
  UNKNOWN = 'Unknown',
}

export enum LeadSource {
  GOOGLE_MAPS = 'Google Maps',
  YELP = 'Yelp',
  LINKEDIN = 'LinkedIn',
  HOMEADVISOR = 'HomeAdvisor',
  ANGI = 'Angi',
  THUMBTACK = 'Thumbtack',
  BBB = 'BBB',
  MANUAL = 'Manual',
}

export enum LeadStatus {
  NEW = 'New',
  ENRICHED = 'Enriched',
  VERIFIED = 'Verified',
  EXPORTED = 'Exported',
  INVALID = 'Invalid',
  DUPLICATE = 'Duplicate',
}

/**
 * Raw lead data from scraping before processing
 */
export interface RawLead {
  companyName: string;
  contactName?: string;
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  trade: Trade;
  source: LeadSource;
  sourceUrl?: string;
  sourceId?: string; // Unique ID from the source (e.g., Google Place ID)
  rating?: number;
  reviewCount?: number;
  scrapedAt: Date;
}

/**
 * Processed lead with normalization and deduplication metadata
 */
export interface Lead extends RawLead {
  id: string; // UUID
  normalizedName: string; // Lowercase, no suffixes, for deduplication
  normalizedPhone?: string; // E.164 format (+1XXXXXXXXXX)
  normalizedAddress?: string; // Standardized format
  enrichedAt?: Date;
  verifiedAt?: Date;
  status: LeadStatus;
  notes: string;
  duplicateOf?: string; // ID of canonical lead if this is a duplicate
  confidence: number; // 0-1 match confidence for enrichment
  metadata: LeadMetadata;
  // Verification fields
  emailVerified?: boolean;
  emailVerificationStatus?: EmailVerificationTag;
  phoneVerified?: boolean;
  phoneType?: PhoneLineType;
  phoneCarrier?: string;
  // Scoring
  leadScore?: number; // Composite 0-100
}

export type EmailVerificationTag =
  | 'valid'
  | 'invalid'
  | 'catch_all'
  | 'disposable'
  | 'spam_trap'
  | 'abuse'
  | 'do_not_mail'
  | 'unknown';

export type PhoneLineType = 'mobile' | 'landline' | 'voip' | 'unknown';

export interface LeadMetadata {
  mergedFrom?: string[]; // IDs of leads merged into this one
  enrichmentProvider?: string;
  enrichmentRaw?: Record<string, unknown>;
  scrapeAttempts?: number;
  lastError?: string;
  [key: string]: unknown;
}

/**
 * Lead export format matching OnCall template
 */
export interface ExportLead {
  'Company Name': string;
  'Contact Name': string;
  Email: string;
  Phone: string;
  Website: string;
  Address: string;
  Trade: string;
  Source: string;
  Notes: string;
  Status: string;
}

/**
 * Filters for querying leads
 */
export interface LeadFilters {
  status?: LeadStatus | LeadStatus[];
  trade?: Trade | Trade[];
  source?: LeadSource | LeadSource[];
  hasEmail?: boolean;
  hasPhone?: boolean;
  hasWebsite?: boolean;
  needsEnrichment?: boolean; // Has website but no email
  minConfidence?: number;
  limit?: number;
  offset?: number;
}
