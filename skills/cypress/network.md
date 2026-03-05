# Network & API Testing — Cypress

## Intercepting Requests

### Basic Intercept
```typescript
// Intercept and stub response
cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers')

// Intercept and modify
cy.intercept('GET', '/api/users', (req) => {
  req.reply((res) => {
    res.body.users = res.body.users.slice(0, 5)
  })
}).as('getUsers')

// Wait for request
cy.visit('/users')
cy.wait('@getUsers')
```

### URL Patterns
```typescript
// Exact match
cy.intercept('GET', '/api/users')

// Glob pattern
cy.intercept('GET', '/api/users/*')
cy.intercept('GET', '/api/users/*/posts')

// Regex
cy.intercept('GET', /\/api\/users\/\d+/)

// With query params
cy.intercept('GET', '/api/users?page=*')
cy.intercept({ method: 'GET', pathname: '/api/users', query: { page: '1' } })
```

### Stubbing Responses
```typescript
// Static response
cy.intercept('GET', '/api/users', {
  statusCode: 200,
  body: [{ id: 1, name: 'John' }],
  headers: { 'x-custom': 'value' },
})

// From fixture
cy.intercept('GET', '/api/users', { fixture: 'users.json' })

// Dynamic response
cy.intercept('GET', '/api/users', (req) => {
  req.reply({
    statusCode: 200,
    body: generateUsers(10),
  })
})

// Delay response
cy.intercept('GET', '/api/users', {
  body: [],
  delay: 2000,
})
```

### Error Responses
```typescript
// 404
cy.intercept('GET', '/api/users/999', { statusCode: 404 })

// 500 Server Error
cy.intercept('POST', '/api/users', {
  statusCode: 500,
  body: { error: 'Internal Server Error' },
})

// Network failure
cy.intercept('GET', '/api/users', { forceNetworkError: true })

// Timeout simulation
cy.intercept('GET', '/api/slow', (req) => {
  req.on('response', (res) => {
    res.setDelay(30000)  // 30s delay
  })
})
```

## Assertions on Requests

```typescript
cy.intercept('POST', '/api/users').as('createUser')

cy.getByTestId('name').type('John')
cy.getByTestId('submit').click()

cy.wait('@createUser').then((interception) => {
  // Assert request body
  expect(interception.request.body).to.deep.equal({ name: 'John' })
  
  // Assert request headers
  expect(interception.request.headers).to.have.property('authorization')
  
  // Assert response
  expect(interception.response.statusCode).to.equal(201)
  expect(interception.response.body).to.have.property('id')
})
```

## API Testing (cy.request)

```typescript
describe('API Tests', () => {
  it('creates a user', () => {
    cy.request({
      method: 'POST',
      url: '/api/users',
      body: { name: 'John', email: 'john@example.com' },
      headers: { Authorization: `Bearer ${Cypress.env('API_TOKEN')}` },
    }).then((response) => {
      expect(response.status).to.eq(201)
      expect(response.body).to.have.property('id')
    })
  })

  it('handles auth flow', () => {
    cy.request('POST', '/api/login', { email: 'test@test.com', password: 'pass' })
      .its('body.token')
      .then((token) => {
        cy.request({
          url: '/api/profile',
          headers: { Authorization: `Bearer ${token}` },
        }).its('body.name').should('eq', 'Test User')
      })
  })
})
```

## Fixtures

### Structure
```
cypress/fixtures/
├── users.json
├── products.json
├── api/
│   ├── login-success.json
│   └── login-error.json
└── images/
    └── avatar.png
```

### Usage
```typescript
// Load fixture
cy.fixture('users.json').then((users) => {
  cy.intercept('GET', '/api/users', users)
})

// Shorthand
cy.intercept('GET', '/api/users', { fixture: 'users.json' })

// Modify fixture data
cy.fixture('users.json').then((users) => {
  users[0].name = 'Modified Name'
  cy.intercept('GET', '/api/users', users)
})
```

### Dynamic Fixtures
```typescript
// cypress/fixtures/factory.ts
export const createUser = (overrides = {}) => ({
  id: Math.random().toString(36).substr(2, 9),
  name: 'Test User',
  email: 'test@example.com',
  ...overrides,
})

// In test
import { createUser } from '../fixtures/factory'

cy.intercept('GET', '/api/users/1', createUser({ name: 'Custom Name' }))
```

## Spying (Without Stubbing)

```typescript
// Spy on real requests
cy.intercept('POST', '/api/analytics').as('analytics')

cy.visit('/page')
cy.wait('@analytics').then((interception) => {
  expect(interception.request.body.event).to.eq('page_view')
})
```

## Common Patterns

### Wait for Multiple Requests
```typescript
cy.intercept('GET', '/api/users').as('users')
cy.intercept('GET', '/api/products').as('products')
cy.intercept('GET', '/api/settings').as('settings')

cy.visit('/dashboard')
cy.wait(['@users', '@products', '@settings'])
```

### Conditional Response
```typescript
let callCount = 0
cy.intercept('GET', '/api/data', (req) => {
  callCount++
  if (callCount === 1) {
    req.reply({ body: { loading: true } })
  } else {
    req.reply({ body: { data: 'loaded' } })
  }
})
```
