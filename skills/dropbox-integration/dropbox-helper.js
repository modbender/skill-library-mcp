/**
 * Dropbox Helper with Auto-Refresh
 * Automatically refreshes access tokens when they expire
 */

const { Dropbox } = require('dropbox');
const fs = require('fs').promises;
const path = require('path');

const CREDENTIALS_PATH = path.join(__dirname, 'credentials.json');
const TOKEN_PATH = path.join(__dirname, 'token.json');

// Buffer time: refresh 5 minutes before actual expiration
const REFRESH_BUFFER_MS = 5 * 60 * 1000;

class DropboxHelper {
  constructor() {
    this.dbx = null;
    this.tokenData = null;
    this.credentials = null;
    this.tokenExpiresAt = null;
  }

  /**
   * Initialize and return a valid Dropbox instance
   * Automatically refreshes token if needed
   */
  async getClient() {
    // Load credentials and tokens on first use
    if (!this.credentials) {
      this.credentials = JSON.parse(await fs.readFile(CREDENTIALS_PATH, 'utf8'));
    }
    
    if (!this.tokenData) {
      this.tokenData = JSON.parse(await fs.readFile(TOKEN_PATH, 'utf8'));
      // Calculate when token expires (current time would be when token.json was last written)
      // Since we don't have that, we'll check on first API call and refresh if needed
      this.tokenExpiresAt = Date.now(); // Will trigger immediate check
    }

    // Check if token needs refresh
    if (this.needsRefresh()) {
      await this.refreshAccessToken();
    }

    // Create or update Dropbox client
    if (!this.dbx || this.dbx.auth.getAccessToken() !== this.tokenData.access_token) {
      this.dbx = new Dropbox({
        accessToken: this.tokenData.access_token,
        clientId: this.credentials.app_key,
        clientSecret: this.credentials.app_secret,
        refreshToken: this.tokenData.refresh_token
      });
    }

    return this.dbx;
  }

  /**
   * Check if token needs refresh
   */
  needsRefresh() {
    if (!this.tokenExpiresAt) return true;
    return Date.now() >= (this.tokenExpiresAt - REFRESH_BUFFER_MS);
  }

  /**
   * Refresh the access token using the refresh token
   */
  async refreshAccessToken() {
    console.error('Refreshing Dropbox access token...');
    
    const response = await fetch('https://api.dropboxapi.com/oauth2/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: this.tokenData.refresh_token,
        client_id: this.credentials.app_key,
        client_secret: this.credentials.app_secret
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Token refresh failed: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    
    // Update token data
    this.tokenData.access_token = data.access_token;
    this.tokenData.expires_in = data.expires_in;
    
    // Note: refresh_token is NOT returned in refresh response - it stays the same
    // Calculate expiration time
    this.tokenExpiresAt = Date.now() + (data.expires_in * 1000);

    // Save updated token
    await fs.writeFile(TOKEN_PATH, JSON.stringify(this.tokenData, null, 2));
    
    console.error(`Token refreshed! Valid for ${data.expires_in} seconds`);
  }

  /**
   * Force a token refresh (useful for testing)
   */
  async forceRefresh() {
    this.tokenExpiresAt = 0; // Force immediate refresh
    await this.getClient();
  }
}

// Singleton instance
let helperInstance = null;

/**
 * Get the Dropbox helper singleton
 */
function getDropboxHelper() {
  if (!helperInstance) {
    helperInstance = new DropboxHelper();
  }
  return helperInstance;
}

/**
 * Quick function to get a ready-to-use Dropbox client
 */
async function getDropboxClient() {
  const helper = getDropboxHelper();
  return await helper.getClient();
}

module.exports = {
  getDropboxHelper,
  getDropboxClient
};
