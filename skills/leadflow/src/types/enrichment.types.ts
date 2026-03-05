/**
 * Enrichment API types
 */

/**
 * Result from email enrichment
 */
export interface EnrichmentResult {
  email?: string;
  firstName?: string;
  lastName?: string;
  position?: string;
  confidence: number; // 0-100
  verificationStatus: EmailVerificationStatus;
  provider: EnrichmentProvider;
  raw?: Record<string, unknown>;
}

export type EmailVerificationStatus =
  | 'valid'
  | 'invalid'
  | 'accept_all'
  | 'unknown'
  | 'pending';

export type EnrichmentProvider = 'hunter' | 'apollo' | 'dropcontact' | 'scraper' | 'manual';

/**
 * Dropcontact API response types
 */
export interface DropcontactEnrichResponse {
  request_id: string;
  error: boolean;
  data: DropcontactContact[];
}

export interface DropcontactContact {
  email: { email: string; qualification: string } | null;
  first_name: string | null;
  last_name: string | null;
  full_name: string | null;
  phone: string | null;
  mobile_phone: string | null;
  company: string | null;
  website: string | null;
  linkedin: string | null;
  job: string | null;
}

/**
 * ZeroBounce verification response
 */
export interface ZeroBounceValidateResponse {
  address: string;
  status: 'valid' | 'invalid' | 'catch-all' | 'unknown' | 'spamtrap' | 'abuse' | 'do_not_mail';
  sub_status: string;
  free_email: boolean;
  did_you_mean: string | null;
  account: string | null;
  domain: string | null;
  domain_age_days: string | null;
  smtp_provider: string | null;
  mx_found: string;
  mx_record: string | null;
  firstname: string | null;
  lastname: string | null;
  gender: string | null;
  processed_at: string;
}

/**
 * Twilio Lookup v2 response
 */
export interface TwilioLookupResponse {
  calling_country_code: string;
  country_code: string;
  phone_number: string;
  national_format: string;
  valid: boolean;
  line_type_intelligence?: {
    carrier_name: string | null;
    type: 'mobile' | 'landline' | 'fixedVoip' | 'nonFixedVoip' | 'tollFree' | 'voip' | null;
    error_code: number | null;
    mobile_country_code: string | null;
    mobile_network_code: string | null;
  };
}

/**
 * Hunter.io API response types
 */
export interface HunterDomainSearchResponse {
  data: {
    domain: string;
    disposable: boolean;
    webmail: boolean;
    accept_all: boolean;
    pattern: string | null;
    organization: string | null;
    emails: HunterEmail[];
  };
  meta: {
    results: number;
    limit: number;
    offset: number;
  };
}

export interface HunterEmail {
  value: string;
  type: 'personal' | 'generic';
  confidence: number;
  first_name: string | null;
  last_name: string | null;
  position: string | null;
  seniority: string | null;
  department: string | null;
  linkedin: string | null;
  twitter: string | null;
  phone_number: string | null;
  verification: {
    date: string | null;
    status: 'valid' | 'invalid' | 'accept_all' | 'unknown';
  };
}

export interface HunterEmailFinderResponse {
  data: {
    first_name: string;
    last_name: string;
    email: string;
    score: number;
    domain: string;
    accept_all: boolean;
    position: string | null;
    twitter: string | null;
    linkedin_url: string | null;
    phone_number: string | null;
    company: string | null;
    verification: {
      date: string | null;
      status: 'valid' | 'invalid' | 'accept_all' | 'unknown';
    };
  };
}

export interface HunterEmailVerifierResponse {
  data: {
    status: 'valid' | 'invalid' | 'accept_all' | 'unknown';
    result: 'deliverable' | 'undeliverable' | 'risky' | 'unknown';
    score: number;
    email: string;
    regexp: boolean;
    gibberish: boolean;
    disposable: boolean;
    webmail: boolean;
    mx_records: boolean;
    smtp_server: boolean;
    smtp_check: boolean;
    accept_all: boolean;
    block: boolean;
  };
}

/**
 * Apollo.io API response types
 */
export interface ApolloPersonSearchResponse {
  people: ApolloPerson[];
  pagination: {
    page: number;
    per_page: number;
    total_entries: number;
    total_pages: number;
  };
}

export interface ApolloPerson {
  id: string;
  first_name: string;
  last_name: string;
  name: string;
  email: string | null;
  email_status: 'verified' | 'guessed' | 'unavailable' | null;
  title: string | null;
  linkedin_url: string | null;
  organization: {
    id: string;
    name: string;
    website_url: string | null;
    phone: string | null;
  } | null;
  phone_numbers: {
    raw_number: string;
    sanitized_number: string;
    type: string;
  }[];
}

/**
 * Enrichment job for the queue
 */
export interface EnrichmentJob {
  id: string;
  leadId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  provider: EnrichmentProvider;
  attempts: number;
  error?: string;
  createdAt: Date;
  completedAt?: Date;
}

/**
 * Options for enrichment
 */
export interface EnrichmentOptions {
  provider?: EnrichmentProvider;
  skipVerification?: boolean;
  maxCreditsPerLead?: number;
}
