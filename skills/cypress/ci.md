# CI/CD Configuration — Cypress

## GitHub Actions

### Basic Workflow
```yaml
# .github/workflows/cypress.yml
name: Cypress Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  cypress:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run Cypress tests
        uses: cypress-io/github-action@v6
        with:
          build: npm run build
          start: npm start
          wait-on: 'http://localhost:3000'
          wait-on-timeout: 120
      
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
          retention-days: 7
```

### Parallel Testing
```yaml
jobs:
  cypress:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        containers: [1, 2, 3, 4]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          record: true
          parallel: true
          group: 'E2E Tests'
        env:
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Component Testing
```yaml
- name: Run Component Tests
  uses: cypress-io/github-action@v6
  with:
    component: true
```

## GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test

cypress:
  stage: test
  image: cypress/browsers:node-20.18.0-chrome-130.0.6723.69-1-ff-131.0.3-edge-130.0.2849.52-1
  
  script:
    - npm ci
    - npm run build
    - npm start &
    - npx wait-on http://localhost:3000
    - npx cypress run --browser chrome
  
  artifacts:
    when: on_failure
    paths:
      - cypress/screenshots
      - cypress/videos
    expire_in: 1 week
  
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
      - ~/.cache/Cypress/
```

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  cypress: cypress-io/cypress@3

workflows:
  test:
    jobs:
      - cypress/run:
          start-command: npm start
          wait-on: 'http://localhost:3000'
          cypress-command: npx cypress run --browser chrome
          post-steps:
            - store_artifacts:
                path: cypress/screenshots
            - store_artifacts:
                path: cypress/videos
```

## Docker

### Dockerfile for CI
```dockerfile
FROM cypress/included:13.6.0

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

CMD ["npx", "cypress", "run"]
```

### Docker Compose
```yaml
# docker-compose.cypress.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
  
  cypress:
    image: cypress/included:13.6.0
    depends_on:
      - app
    environment:
      - CYPRESS_baseUrl=http://app:3000
    working_dir: /e2e
    volumes:
      - ./cypress:/e2e/cypress
      - ./cypress.config.ts:/e2e/cypress.config.ts
      - ./package.json:/e2e/package.json
```

```bash
docker-compose -f docker-compose.cypress.yml run cypress
```

## Configuration for CI

### cypress.config.ts
```typescript
export default defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:3000',
    
    // CI-specific settings
    retries: {
      runMode: 2,      // Retry failed tests in CI
      openMode: 0,     // No retries in interactive mode
    },
    
    video: process.env.CI === 'true',
    screenshotOnRunFailure: true,
    
    // Longer timeouts for CI
    defaultCommandTimeout: process.env.CI ? 15000 : 10000,
    requestTimeout: process.env.CI ? 15000 : 10000,
    
    // Reporter for CI
    reporter: 'mochawesome',
    reporterOptions: {
      reportDir: 'cypress/results',
      overwrite: false,
      html: true,
      json: true,
    },
  },
})
```

### Environment Variables
```bash
# .env.ci
CYPRESS_BASE_URL=http://localhost:3000
CYPRESS_RECORD_KEY=your-dashboard-key
```

## Best Practices

### Caching
```yaml
# GitHub Actions
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/Cypress
      node_modules
    key: cypress-${{ runner.os }}-${{ hashFiles('package-lock.json') }}

# GitLab CI
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - ~/.cache/Cypress/
```

### Artifacts on Failure
Always save screenshots and videos when tests fail:
```yaml
artifacts:
  when: on_failure
  paths:
    - cypress/screenshots
    - cypress/videos
```

### Wait for App
```yaml
# Using wait-on
- run: npx wait-on http://localhost:3000 --timeout 120000

# Or start-server-and-test
- run: npx start-server-and-test 'npm start' http://localhost:3000 'npx cypress run'
```

### Browser Selection
```yaml
# Use Chrome for consistency
- run: npx cypress run --browser chrome

# Or test multiple browsers
strategy:
  matrix:
    browser: [chrome, firefox, edge]
steps:
  - run: npx cypress run --browser ${{ matrix.browser }}
```
