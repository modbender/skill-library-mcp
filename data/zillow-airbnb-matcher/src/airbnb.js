/**
 * Airbnb listing data fetcher
 * Uses RapidAPI airbnb13 API (free: 100 requests/month)
 * https://rapidapi.com/3b-data-3b-data-default/api/airbnb13
 */

const axios = require('axios');

const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY;

/**
 * Fetch Airbnb listings for a location
 * @param {string} location - ZIP code or city
 * @param {object} options
 * @returns {Array} Airbnb listing objects
 */
async function fetchAirbnbListings(location, options = {}) {
  const { maxResults = 50 } = options;

  if (!RAPIDAPI_KEY) {
    throw new Error(
      'RAPIDAPI_KEY not configured.\n\n' +
      'Get a free key (no credit card):\n' +
      '  1. Sign up: https://rapidapi.com\n' +
      '  2. Subscribe: https://rapidapi.com/3b-data-3b-data-default/api/airbnb13\n' +
      '  3. Add to .env: RAPIDAPI_KEY=your_key_here\n\n' +
      'Run with --demo to see the tool without API keys'
    );
  }

  const { checkIn, checkOut } = options;

  // Default dates (next available weekend)
  const today = new Date();
  const nextFriday = new Date(today);
  nextFriday.setDate(today.getDate() + (5 - today.getDay() + 7) % 7 + 7);
  const nextSunday = new Date(nextFriday);
  nextSunday.setDate(nextFriday.getDate() + 2);

  const checkinDate = checkIn || nextFriday.toISOString().split('T')[0];
  const checkoutDate = checkOut || nextSunday.toISOString().split('T')[0];

  process.stderr.write(`  📡 Fetching Airbnb listings for ${location} via RapidAPI...\n`);

  try {
    const response = await axios.get('https://airbnb13.p.rapidapi.com/search-location', {
      params: {
        location,
        checkin: checkinDate,
        checkout: checkoutDate,
        adults: 2,
        currency: 'USD',
        page: 1
      },
      headers: {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': 'airbnb13.p.rapidapi.com'
      },
      timeout: 20000
    });

    const results = response.data?.results || [];
    process.stderr.write(`  ✅ Found ${results.length} Airbnb listings via RapidAPI\n`);

    return results.slice(0, maxResults).map(normalizeListing);

  } catch (err) {
    if (err.response?.status === 403 || err.response?.status === 429) {
      throw new Error('RapidAPI rate limit hit or subscription needed.\n' +
        'Free tier = 100 requests/month.\n' +
        'Subscribe at: https://rapidapi.com/3b-data-3b-data-default/api/airbnb13');
    }
    if (err.response?.status === 401) {
      throw new Error('Invalid RapidAPI key. Check RAPIDAPI_KEY in .env');
    }
    throw new Error(`Airbnb fetch failed: ${err.message}`);
  }
}

/**
 * Normalize a RapidAPI airbnb13 listing to standard format
 */
function normalizeListing(item) {
  const nightlyRate = item.price?.rate || item.price?.total;
  const estimatedOccupancy = 0.70;
  const monthlyRevenue = nightlyRate ? Math.round(nightlyRate * 30 * estimatedOccupancy) : null;

  return {
    id: `rapidapi-${item.id}`,
    address: item.name || item.title,
    city: item.city || '',
    state: '',
    zip: '',
    title: item.name || item.title,
    beds: item.bedrooms || item.beds,
    baths: item.bathrooms,
    maxGuests: item.persons || item.guests,
    nightly_rate: nightlyRate,
    monthly_revenue_avg: monthlyRevenue,
    annual_revenue_est: monthlyRevenue ? monthlyRevenue * 12 : null,
    occupancy_rate: estimatedOccupancy,
    total_reviews: item.reviewsCount || item.numberOfReviews,
    avg_rating: item.rating,
    host_status: item.isSuperhost ? 'Superhost' : 'Regular',
    airbnbUrl: item.url || item.deeplink || `https://airbnb.com/rooms/${item.id}`,
    lat: item.lat || item.coordinate?.latitude,
    lng: item.lng || item.coordinate?.longitude,
    roomType: item.type || item.roomType,
    _note: monthlyRevenue ? 'Revenue estimated at 70% occupancy from nightly rate' : 'Nightly rate unavailable'
  };
}

module.exports = { fetchAirbnbListings };
