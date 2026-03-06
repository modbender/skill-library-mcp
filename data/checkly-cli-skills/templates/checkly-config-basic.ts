// Basic Checkly Configuration Template
import { defineConfig } from 'checkly'

export default defineConfig({
  projectName: 'My Application Monitoring',
  logicalId: 'my-app-prod',
  repoUrl: 'https://github.com/your-org/your-repo',
  checks: {
    frequency: 5,
    locations: ['us-east-1', 'eu-west-1'],
    tags: ['production'],
    runtimeId: '2025.04',
    checkMatch: '**/__checks__/**/*.check.{js,ts}',
    browserChecks: {
      testMatch: '**/__checks__/**/*.spec.{js,ts}',
    },
  },
})
