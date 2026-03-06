# Selectors — Cypress

## Priority Order

| Priority | Selector Type | Example | Resilience |
|----------|--------------|---------|------------|
| 1 | data-testid | `[data-testid="submit"]` | ⭐⭐⭐⭐⭐ |
| 2 | data-cy | `[data-cy="submit"]` | ⭐⭐⭐⭐⭐ |
| 3 | aria-label | `[aria-label="Submit form"]` | ⭐⭐⭐⭐ |
| 4 | role + name | `button:contains("Submit")` | ⭐⭐⭐ |
| 5 | text content | `.contains("Submit")` | ⭐⭐⭐ |
| 6 | CSS class | `.btn-submit` | ⭐⭐ |
| 7 | CSS structure | `form > button:last` | ⭐ |

## Helper Command

```typescript
// cypress/support/commands.ts
Cypress.Commands.add('getByTestId', (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`)
})

Cypress.Commands.add('findByTestId', { prevSubject: true }, (subject, testId: string) => {
  return cy.wrap(subject).find(`[data-testid="${testId}"]`)
})
```

## Common Patterns

### Form Elements
```typescript
// Input by label
cy.contains('label', 'Email').find('input')

// Input by testid (preferred)
cy.getByTestId('email-input').type('user@example.com')

// Select dropdown
cy.getByTestId('country-select').select('US')

// Checkbox
cy.getByTestId('agree-checkbox').check()
```

### Lists and Tables
```typescript
// All items
cy.getByTestId('todo-item').should('have.length', 3)

// Specific item
cy.getByTestId('todo-item').eq(0).should('contain', 'First task')

// Item containing text
cy.getByTestId('todo-item').contains('Buy milk').click()

// Within a row
cy.getByTestId('user-row')
  .contains('john@example.com')
  .parents('[data-testid="user-row"]')
  .findByTestId('delete-btn')
  .click()
```

### Dynamic Elements
```typescript
// Wait for element to appear
cy.getByTestId('loading').should('not.exist')
cy.getByTestId('results').should('be.visible')

// Dynamic testid
const userId = '123'
cy.get(`[data-testid="user-${userId}"]`)
```

## Anti-Patterns

```typescript
// ❌ Brittle CSS path
cy.get('#app > div.container > form > div:nth-child(2) > input')

// ❌ Class that might change
cy.get('.MuiButton-containedPrimary')

// ❌ Index without context
cy.get('button').eq(3).click()

// ❌ Timeout instead of assertion
cy.wait(1000)
cy.get('.results')
```

## Adding data-testid to Components

### React
```tsx
<button data-testid="submit-btn" onClick={handleSubmit}>
  Submit
</button>
```

### Vue
```vue
<button data-testid="submit-btn" @click="handleSubmit">
  Submit
</button>
```

### Strip in Production (Optional)
```javascript
// babel.config.js
module.exports = {
  env: {
    production: {
      plugins: [
        ['react-remove-properties', { properties: ['data-testid'] }]
      ]
    }
  }
}
```
