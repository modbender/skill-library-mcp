import 'dotenv/config';

export function getPicqerConfig() {
  const subdomain = process.env.PICQER_SUBDOMAIN;
  const apiKey = process.env.PICQER_API_KEY;
  
  if (!subdomain || !apiKey) {
    throw new Error('Picqer API not configured. Set PICQER_SUBDOMAIN and PICQER_API_KEY in .env');
  }
  
  return { subdomain, apiKey };
}
