// Check Group Pattern Template
import { CheckGroup, EmailAlertChannel } from 'checkly/constructs'

// Define alert channels
const emailChannel = new EmailAlertChannel('team-email', {
  address: 'team@example.com',
})

// Create check groups
export const criticalChecks = new CheckGroup('critical-checks', {
  name: 'Critical Services',
  activated: true,
  locations: ['us-east-1', 'eu-west-1'],
  frequency: 1,
  tags: ['critical', 'p0'],
  alertChannels: [emailChannel],
  environmentVariables: [
    { key: 'ENV', value: 'production' },
  ],
})

export const apiChecks = new CheckGroup('api-checks', {
  name: 'API Monitoring',
  activated: true,
  locations: ['us-east-1'],
  frequency: 5,
  tags: ['api', 'backend'],
  environmentVariables: [
    { key: 'API_BASE_URL', value: 'https://api.example.com' },
  ],
})

export const e2eChecks = new CheckGroup('e2e-checks', {
  name: 'E2E Flows',
  activated: true,
  locations: ['us-east-1'],
  frequency: 10,
  tags: ['e2e', 'browser'],
})
