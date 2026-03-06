// Copy this to config.js and fill in your keys
module.exports = {
  instantly: {
    apiKey: "YOUR_INSTANTLY_V2_BEARER_TOKEN",
  },
  hunter: {
    apiKey: "YOUR_HUNTER_API_KEY",
  },
  apollo: {
    apiKey: "YOUR_APOLLO_API_KEY",  // Only needed for pipeline.js (API scrape mode)
  },
  target: {
    industries: ["ecommerce", "retail", "online retail"],
    countries: ["AE", "SA", "EG", "KW", "QA", "BH", "OM"],  // ISO-2 codes
    titles: [
      "Founder", "Co-Founder", "CEO", "Owner", "Director",
      "Head of E-commerce", "E-commerce Manager", "Operations Manager"
    ],
    perPage: 25,
    maxLeads: 200,
  },
  sequence: {
    name: "Your Campaign Name",
    campaignId: "YOUR_INSTANTLY_CAMPAIGN_ID",
    dailyLimit: 40,  // per inbox
    delayBetweenEmails: { min: 5, max: 15 },  // minutes
  }
};
