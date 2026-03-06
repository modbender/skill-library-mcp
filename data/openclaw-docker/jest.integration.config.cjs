module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/test'],
  testMatch: ['**/test/integration/**/*.test.ts'],
  testTimeout: 120_000,
  collectCoverageFrom: ['src/**/*.ts']
};
