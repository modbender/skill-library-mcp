import { chromium, FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const API_URL = process.env.API_URL || 'http://localhost:8000';
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';

async function globalSetup(config: FullConfig) {
  console.log(`Running global setup...`);
  console.log(`  BASE_URL: ${BASE_URL}`);
  console.log(`  API_URL:  ${API_URL}`);

  // Health check - in production, /health is not proxied through nginx,
  // so we check the API via /api/campaigns which is always available.
  // In dev, we check /health directly on the API server.
  const isProduction = !API_URL.includes('localhost');
  const healthUrl = isProduction ? `${API_URL}/api/campaigns?per_page=1` : `${API_URL}/health`;
  
  try {
    const healthCheck = await fetch(healthUrl, { 
      method: 'GET',
      signal: AbortSignal.timeout(10000),
    });
    if (!healthCheck.ok) {
      console.warn(`⚠ Backend not available at ${healthUrl} (${healthCheck.status}), skipping global setup`);
      return;
    }
    console.log(`✓ Backend is reachable`);
  } catch (error) {
    console.warn(`⚠ Backend not available at ${healthUrl}, skipping global setup`);
    return;
  }

  // Create test user and get auth token
  const email = `test-setup-${Date.now()}@example.com`;
  
  try {
    // Request magic link
    const magicLinkResponse = await fetch(`${API_URL}/api/auth/magic-link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    
    if (!magicLinkResponse.ok) {
      const errorText = await magicLinkResponse.text();
      throw new Error(`Magic link request failed: ${magicLinkResponse.status} ${errorText}`);
    }
    
    const magicLinkData = await magicLinkResponse.json();

    // Extract token from message (dev mode shows token directly)
    const tokenMatch = magicLinkData.message?.match(/Token: ([^\s]+)/);
    if (!tokenMatch) {
      // In production, token is not exposed - this is expected
      console.warn('⚠ Token not in magic link response (expected in production mode)');
      console.warn('⚠ Authenticated tests will use their own login flow');
      return;
    }
    const token = tokenMatch[1];

    // Verify token to get JWT
    const verifyResponse = await fetch(`${API_URL}/api/auth/verify?token=${encodeURIComponent(token)}`);
    
    if (!verifyResponse.ok) {
      const errorText = await verifyResponse.text();
      throw new Error(`Token verification failed: ${verifyResponse.status} ${errorText}`);
    }
    
    const verifyData = await verifyResponse.json();

    if (!verifyData.success || !verifyData.access_token) {
      throw new Error('Failed to verify token and get access token');
    }

    const jwtToken = verifyData.access_token;

    // Save auth state for authenticated tests
    // Use the actual BASE_URL as the origin so localStorage is set for the correct domain
    const authState = {
      cookies: [],
      origins: [
        {
          origin: BASE_URL,
          localStorage: [
            {
              name: 'moltfundme_token',
              value: jwtToken,
            },
            {
              name: 'moltfundme_user',
              value: JSON.stringify({ id: 'test-user-id', email }),
            },
          ],
        },
      ],
    };

    const authStatePath = path.join(__dirname, 'auth-state.json');
    fs.writeFileSync(authStatePath, JSON.stringify(authState, null, 2));
    console.log('✓ Auth state saved for authenticated tests');

  } catch (error) {
    console.error('Error during global setup:', error);
    // Don't throw - allow tests to run without global setup
    console.warn('⚠ Continuing without global setup auth state');
  }
}

export default globalSetup;
