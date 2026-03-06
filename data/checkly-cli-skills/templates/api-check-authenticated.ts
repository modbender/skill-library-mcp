// Authenticated API Check Template
import { ApiCheck, AssertionBuilder } from 'checkly/constructs'

new ApiCheck('authenticated-api-check', {
  name: 'Authenticated API Check',
  frequency: 5,
  locations: ['us-east-1'],
  request: {
    url: 'https://api.example.com/user/profile',
    method: 'GET',
    headers: [
      { key: 'Authorization', value: 'Bearer {{API_TOKEN}}' },
      { key: 'Content-Type', value: 'application/json' },
    ],
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.jsonBody('$.user.id').isNotNull(),
      AssertionBuilder.header('Content-Type').contains('application/json'),
    ],
  },
  environmentVariables: [
    { key: 'API_TOKEN', value: process.env.API_TOKEN!, locked: true },
  ],
})
