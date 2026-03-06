/**
 * Configuration loader with Zod validation
 */

import { z } from 'zod';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Environment configuration schema
 */
const envSchema = z.object({
  // General
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .default('development'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),

  // Database
  DATABASE_PATH: z.string().default('./data/leads.db'),

  // Google APIs
  GOOGLE_PLACES_API_KEY: z.string().optional(),

  // Yelp
  YELP_API_KEY: z.string().optional(),

  // LinkedIn/Proxycurl
  PROXYCURL_API_KEY: z.string().optional(),

  // Email Enrichment
  HUNTER_API_KEY: z.string().optional(),
  APOLLO_API_KEY: z.string().optional(),
  DROPCONTACT_API_KEY: z.string().optional(),

  // Email Verification
  ZEROBOUNCE_API_KEY: z.string().optional(),

  // Phone Validation
  TWILIO_ACCOUNT_SID: z.string().optional(),
  TWILIO_AUTH_TOKEN: z.string().optional(),

  // Proxy Configuration
  PROXY_PROVIDER: z.enum(['brightdata', 'oxylabs', 'iproyal', 'custom']).optional(),
  PROXY_USERNAME: z.string().optional(),
  PROXY_PASSWORD: z.string().optional(),
  PROXY_LIST_PATH: z.string().optional(),

  // Scraping Settings
  MAX_CONCURRENT_SCRAPERS: z.coerce.number().default(2),
  REQUEST_TIMEOUT_MS: z.coerce.number().default(30000),

  // Export
  EXPORT_PATH: z.string().default('./data/exports'),
});

/**
 * Parse and validate environment
 */
function loadConfig() {
  const result = envSchema.safeParse(process.env);

  if (!result.success) {
    console.error('Invalid environment configuration:');
    console.error(result.error.format());
    throw new Error('Invalid environment configuration');
  }

  return result.data;
}

export const config = loadConfig();

export type Config = z.infer<typeof envSchema>;

/**
 * Check if an API key is configured
 */
export function hasApiKey(key: keyof Config): boolean {
  const value = config[key];
  return typeof value === 'string' && value.length > 0;
}

/**
 * Get required API key or throw
 */
export function requireApiKey(key: keyof Config): string {
  const value = config[key];
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`Missing required API key: ${key}`);
  }
  return value;
}
