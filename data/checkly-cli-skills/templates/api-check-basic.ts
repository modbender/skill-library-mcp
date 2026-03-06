// Basic API Check Template
import { ApiCheck, AssertionBuilder } from 'checkly/constructs'

new ApiCheck('api-status-check', {
  name: 'API Status Check',
  frequency: 5,
  locations: ['us-east-1', 'eu-west-1'],
  tags: ['api', 'production'],
  request: {
    url: 'https://api.example.com/status',
    method: 'GET',
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.responseTime().lessThan(500),
      AssertionBuilder.jsonBody('$.status').equals('ok'),
    ],
  },
})
