// Mock openclaw-config for testing
const config = {
  get: jest.fn((key) => {
    const mockConfig = {
      "helpscout.API_KEY": "mock-api-key",
      "helpscout.APP_SECRET": "mock-app-secret",
      "helpscout.INBOX_IDS": ["mock-inbox-id-1", "mock-inbox-id-2"]
    };
    return mockConfig[key];
  })
};

module.exports = config;