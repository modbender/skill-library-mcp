# Custom Commands — Cypress

## Essential Commands

### Login with Session
```typescript
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session(
    [email, password],
    () => {
      cy.visit('/login')
      cy.getByTestId('email').type(email)
      cy.getByTestId('password').type(password)
      cy.getByTestId('submit').click()
      cy.url().should('include', '/dashboard')
    },
    {
      validate: () => {
        cy.getCookie('session').should('exist')
      },
    }
  )
})
```

### API Login (Faster)
```typescript
Cypress.Commands.add('loginViaApi', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: { email, password },
    }).then((response) => {
      window.localStorage.setItem('token', response.body.token)
    })
  })
})
```

### Get by Test ID
```typescript
Cypress.Commands.add('getByTestId', (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`)
})

Cypress.Commands.add('findByTestId', { prevSubject: true }, (subject, testId: string) => {
  return cy.wrap(subject).find(`[data-testid="${testId}"]`)
})
```

## TypeScript Declarations

```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Login via UI with session caching
       */
      login(email: string, password: string): Chainable<void>
      
      /**
       * Login via API (faster, for most tests)
       */
      loginViaApi(email: string, password: string): Chainable<void>
      
      /**
       * Get element by data-testid
       */
      getByTestId(testId: string): Chainable<JQuery<HTMLElement>>
      
      /**
       * Find child element by data-testid
       */
      findByTestId(testId: string): Chainable<JQuery<HTMLElement>>
    }
  }
}
```

## Utility Commands

### Drag and Drop
```typescript
Cypress.Commands.add('dragTo', { prevSubject: true }, (subject, targetSelector: string) => {
  cy.wrap(subject).trigger('dragstart')
  cy.get(targetSelector).trigger('drop')
  cy.wrap(subject).trigger('dragend')
})

// Usage
cy.getByTestId('draggable-item').dragTo('[data-testid="drop-zone"]')
```

### File Upload
```typescript
Cypress.Commands.add('uploadFile', { prevSubject: true }, (subject, fileName: string, mimeType: string) => {
  cy.fixture(fileName, 'base64').then((content) => {
    const blob = Cypress.Blob.base64StringToBlob(content, mimeType)
    const file = new File([blob], fileName, { type: mimeType })
    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(file)
    
    cy.wrap(subject).trigger('drop', { dataTransfer })
  })
})
```

### Wait for API
```typescript
Cypress.Commands.add('waitForApi', (method: string, url: string) => {
  const alias = `api-${Date.now()}`
  cy.intercept(method, url).as(alias)
  return cy.wrap(alias)
})

// Usage
cy.waitForApi('GET', '/api/users').then((alias) => {
  cy.getByTestId('load-users').click()
  cy.wait(`@${alias}`)
})
```

## Command Patterns

### Overwriting Existing Commands
```typescript
Cypress.Commands.overwrite('visit', (originalFn, url, options) => {
  // Add auth header to all visits
  const token = window.localStorage.getItem('token')
  return originalFn(url, {
    ...options,
    onBeforeLoad: (win) => {
      if (token) {
        win.localStorage.setItem('token', token)
      }
      options?.onBeforeLoad?.(win)
    },
  })
})
```

### Query Commands (Retry-able)
```typescript
// Query commands auto-retry, action commands don't
Cypress.Commands.addQuery('getVisible', (selector: string) => {
  return () => Cypress.$(selector).filter(':visible')
})
```

## Organization

Keep commands organized by domain:
```
cypress/support/
├── commands.ts          # Re-exports all
├── commands/
│   ├── auth.ts          # login, logout, register
│   ├── navigation.ts    # goTo, waitForPage
│   ├── forms.ts         # fillForm, submitForm
│   └── utils.ts         # getByTestId, dragTo
└── e2e.ts               # Imports commands.ts
```

```typescript
// cypress/support/commands.ts
import './commands/auth'
import './commands/navigation'
import './commands/forms'
import './commands/utils'
```
