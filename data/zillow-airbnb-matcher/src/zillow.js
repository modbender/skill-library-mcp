/**
 * Zillow data fetcher
 * Uses RapidAPI US Property Market API (free: 600 requests/month)
 * https://rapidapi.com/SwongF/api/us-property-market1
 */

const axios = require('axios');

const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY;
const RAPIDAPI_ZILLOW_HOST = 'us-property-market1.p.rapidapi.com';

/**
 * Fetch Zillow for-sale listings by ZIP code
 * @param {string} zip - ZIP code or city string
 * @param {object} options
 * @returns {Array} Zillow listing objects
 */
async function fetchZillowListings(zip, options = {}) {
  if (!RAPIDAPI_KEY) {
    throw new Error(
      'RAPIDAPI_KEY not configured.\n\n' +
      'Get a free key (no credit card):\n' +
      '  1. Sign up: https://rapidapi.com\n' +
      '  2. Subscribe: https://rapidapi.com/SwongF/api/us-property-market1\n' +
      '  3. Add to .env: RAPIDAPI_KEY=your_key_here'
    );
  }

  const { maxResults = 40 } = options;

  process.stderr.write(`  📡 Fetching Zillow listings for ${zip} via RapidAPI...\n`);

  try {
    const searchResponse = await axios.get(`https://${RAPIDAPI_ZILLOW_HOST}/search`, {
      params: {
        location: zip,
        status: 'forSale'
      },
      headers: {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_ZILLOW_HOST
      },
      timeout: 15000
    });

    const results = searchResponse.data?.props || searchResponse.data?.results || searchResponse.data?.data || [];
    const resultArray = Array.isArray(results) ? results : (searchResponse.data?.props ? Object.values(searchResponse.data.props) : []);
    process.stderr.write(`  ✅ Found ${resultArray.length} Zillow listings\n`);

    return resultArray.slice(0, maxResults).map(normalizeListing);

  } catch (err) {
    if (err.response?.status === 429) {
      throw new Error('RapidAPI rate limit hit. Free tier = 600 requests/month.\n' +
        'Upgrade at: https://rapidapi.com/SwongF/api/us-property-market1');
    }
    if (err.response?.status === 403 || err.response?.status === 401) {
      throw new Error('RapidAPI auth failed. Subscribe to US Property Market API (free):\n' +
        'https://rapidapi.com/SwongF/api/us-property-market1');
    }
    if (err.response?.data) {
      process.stderr.write(`  ⚠️ API response: ${JSON.stringify(err.response.data).slice(0, 200)}\n`);
    }
    throw new Error(`Zillow fetch failed: ${err.message}`);
  }
}

/**
 * Normalize a RapidAPI Zillow result to standard format
 */
function normalizeListing(item) {
  let city = item.city || '';
  let state = item.state || '';
  let zip = item.zipcode || item.zip || '';

  if (!city && item.address) {
    const parts = item.address.split(',').map(s => s.trim());
    if (parts.length >= 2) {
      city = parts[parts.length - 2] || '';
      const stateZip = (parts[parts.length - 1] || '').split(' ');
      state = stateZip[0] || '';
      zip = stateZip[1] || zip;
    }
  }

  return {
    zpid: item.zpid,
    address: item.address,
    city,
    state,
    zip,
    price: item.price,
    beds: item.bedrooms,
    baths: item.bathrooms,
    sqft: item.livingArea,
    yearBuilt: item.yearBuilt,
    propertyType: item.homeType || item.propertyType || 'Residential',
    daysOnMarket: item.daysOnZillow || item.daysOnMarket,
    zestimate: item.zestimate,
    listingUrl: item.detailUrl ? `https://zillow.com${item.detailUrl}` : `https://zillow.com/homes/${item.zpid}_zpid`,
    lat: item.latitude,
    lng: item.longitude,
    pricePerSqft: item.price && item.livingArea ? Math.round(item.price / item.livingArea) : null
  };
}

module.exports = { fetchZillowListings };
