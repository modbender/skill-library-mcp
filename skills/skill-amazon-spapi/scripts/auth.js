#!/usr/bin/env node
/**
 * Amazon SP-API Auth
 * Tests connection and lists marketplace participations.
 */

const SellingPartnerAPI = require('amazon-sp-api');
const fs = require('fs');

const CREDS_PATH = process.env.AMAZON_SPAPI_PATH || './amazon-sp-api.json';

function getCfg() { return JSON.parse(fs.readFileSync(CREDS_PATH, 'utf8')); }

function getClient() {
  const creds = getCfg();
  return new SellingPartnerAPI({
    region: creds.region || 'eu',
    refresh_token: creds.refreshToken,
    credentials: {
      SELLING_PARTNER_APP_CLIENT_ID: creds.lwaClientId,
      SELLING_PARTNER_APP_CLIENT_SECRET: creds.lwaClientSecret,
    }
  });
}

module.exports = { getClient, getCfg };

if (require.main === module) {
  (async () => {
    try {
      const sp = getClient();
      const res = await sp.callAPI({ operation: 'getMarketplaceParticipations', endpoint: 'sellers' });
      console.log('✅ SP-API Connected');
      const marketplaces = res.map(p => ({
        id: p.marketplace?.id,
        name: p.marketplace?.name,
        country: p.marketplace?.countryCode,
      }));
      console.log(JSON.stringify(marketplaces, null, 2));
    } catch (e) {
      console.error('❌ Auth failed:', e.message);
      process.exit(1);
    }
  })();
}
