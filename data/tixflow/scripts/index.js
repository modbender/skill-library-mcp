// TixFlow - AI Event Assistant
// Functions for event discovery, booking, and coordination

// Mock event data for demo mode
const mockEvents = [
  {
    id: "1",
    name: "Classical Symphony Orchestra",
    date: "2026-02-25",
    venue: "Royal Albert Hall, London",
    price: { min: 45, max: 120, currency: "GBP" },
    image: "https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=400&q=80",
    available: true,
    category: "classical"
  },
  {
    id: "2",
    name: "Jazz Night Live",
    date: "2026-03-01",
    venue: "Blue Note, NYC",
    price: { min: 35, max: 80, currency: "USD" },
    image: "https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=400&q=80",
    available: true,
    category: "jazz"
  },
  {
    id: "3",
    name: "Electronic Music Festival",
    date: "2026-03-15",
    venue: "Brooklyn Warehouse",
    price: { min: 50, max: 150, currency: "USD" },
    image: "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=400&q=80",
    available: false,
    category: "electronic"
  }
];

/**
 * Find events based on criteria
 * @param {Object} params - Search parameters
 * @param {string} params.type - Event type (concert, theater, sports)
 * @param {string} params.location - Location
 * @param {string} params.date - Date or date range
 * @param {number} params.budget - Maximum budget
 */
async function findEvents(params = {}) {
  const { type, location, date, budget } = params;
  
  // In demo mode, return mock events
  // In production, this would call KYD Labs API
  let results = [...mockEvents];
  
  if (type) {
    results = results.filter(e => e.category.toLowerCase().includes(type.toLowerCase()));
  }
  
  if (location) {
    results = results.filter(e => e.venue.toLowerCase().includes(location.toLowerCase()));
  }
  
  if (budget) {
    results = results.filter(e => e.price.min <= budget);
  }
  
  return {
    success: true,
    count: results.length,
    events: results
  };
}

/**
 * Get detailed information about a specific event
 * @param {string} eventId - Event ID
 */
async function getEventDetails(eventId) {
  const event = mockEvents.find(e => e.id === eventId);
  
  if (!event) {
    return { success: false, error: "Event not found" };
  }
  
  return {
    success: true,
    event: {
      ...event,
      description: "An evening of classical masterpieces conducted by renowned artists.",
      seatingChart: "https://example.com/seating.jpg",
      policies: {
        refundable: false,
        transferAllowed: true
      }
    }
  };
}

/**
 * Purchase tickets for an event
 * @param {Object} params - Purchase parameters
 * @param {string} params.eventId - Event ID
 * @param {number} params.quantity - Number of tickets
 * @param {string} params.walletAddress - Wallet address for NFT ticket
 */
async function purchaseTicket(params) {
  const { eventId, quantity, walletAddress } = params;
  
  const event = mockEvents.find(e => e.id === eventId);
  
  if (!event) {
    return { success: false, error: "Event not found" };
  }
  
  if (!event.available) {
    return { success: false, error: "Event is sold out. Added to waitlist." };
  }
  
  // In demo mode, return mock transaction
  // In production, this would call KYD Labs protocol
  return {
    success: true,
    demo: true,
    message: "Demo mode: Ticket would be minted as cNFT on Solana",
    transactionId: "mock_tx_" + Date.now(),
    ticketId: "mock_nft_" + Date.now()
  };
}

/**
 * Sync event to Google Calendar
 * @param {Object} params - Sync parameters
 * @param {string} params.eventId - Event ID
 * @param {string} params.userEmail - User email for calendar
 */
async function syncToCalendar(params) {
  const { eventId, userEmail } = params;
  
  const event = mockEvents.find(e => e.id === eventId);
  
  if (!event) {
    return { success: false, error: "Event not found" };
  }
  
  // In demo mode, return mock calendar event
  // In production, this would call Google Calendar API
  return {
    success: true,
    demo: true,
    message: "Demo mode: Would sync to Google Calendar",
    calendarEventId: "mock_calendar_" + Date.now(),
    eventLink: "https://calendar.google.com/calendar/event?eid=mock"
  };
}

/**
 * Add user to event waitlist
 * @param {Object} params - Waitlist parameters
 * @param {string} params.eventId - Event ID
 * @param {string} params.walletAddress - User wallet
 * @param {string} params.notificationMethod - email, telegram, or discord
 */
async function addToWaitlist(params) {
  const { eventId, walletAddress, notificationMethod } = params;
  
  const event = mockEvents.find(e => e.id === eventId);
  
  if (!event) {
    return { success: false, error: "Event not found" };
  }
  
  // In production, this would store in database and monitor for availability
  return {
    success: true,
    waitlistPosition: Math.floor(Math.random() * 100) + 1,
    message: `Added to waitlist for ${event.name}. We'll notify you when tickets are available.`
  };
}

/**
 * Check prices across platforms
 * @param {string} eventId - Event ID
 */
async function checkPrices(eventId) {
  const event = mockEvents.find(e => e.id === eventId);
  
  if (!event) {
    return { success: false, error: "Event not found" };
  }
  
  // Mock price comparison across platforms
  return {
    success: true,
    eventId,
    prices: [
      { platform: "Ticketmaster", price: event.price.max, fees: 12, total: event.price.max + 12 },
      { platform: "StubHub", price: event.price.max + 10, fees: 8, total: event.price.max + 18 },
      { platform: "KYD Protocol", price: event.price.min, fees: 0, total: event.price.min }
    ],
    recommendation: "KYD Protocol offers the best price with no fees"
  };
}

module.exports = {
  findEvents,
  getEventDetails,
  purchaseTicket,
  syncToCalendar,
  addToWaitlist,
  checkPrices
};
