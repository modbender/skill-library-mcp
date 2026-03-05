module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts', '**/*.test.ts'],
  testPathIgnorePatterns: ['/node_modules/', 'ote-integration\\.test\\.ts$'],
};
