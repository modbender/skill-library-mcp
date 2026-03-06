/** Jest config for OTE integration tests only. Run via: npm run test:ote */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/ote-integration.test.ts'],
  testTimeout: 30000,
};
