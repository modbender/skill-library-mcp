# Pre-Deployment Checklist

Before deploying to production, review the entire codebase against this checklist.

## Security
- [ ] All API keys, database credentials, and other secrets are loaded from environment variables (or a secret manager) and are NOT in version control.
- [ ] All API endpoints are protected by authentication and authorization middleware.
- [ ] Row-Level Security is implemented and tested to prevent data leakage between tenants.
- [ ] All user input is validated on the backend using a schema library (e.g., Zod).
- [ ] Dependencies have been scanned for known vulnerabilities (`npm audit`).

## Testing
- [ ] All unit and integration tests pass in the CI pipeline.
- [ ] Test coverage for critical business logic is above 80%.
- [ ] E2E tests for the main user journeys pass reliably.

## Performance
- [ ] Database queries are optimized with appropriate indexes.
- [ ] N+1 query problems have been identified and fixed.
- [ ] Frontend bundle size has been analyzed and code-splitting is implemented for large components/routes.
- [ ] Images are optimized and served in modern formats.

## Observability & Error Handling
- [ ] Structured logging is implemented for all key events and errors.
- [ ] An error reporting service (e.g., Sentry) is integrated.
- [ ] A `/health` check endpoint is implemented.

## Environment & Configuration
- [ ] A `.env.example` file exists and is up-to-date.
- [ ] The production environment has been configured with all necessary environment variables.
- [ ] Database migrations are handled automatically by the deployment script/pipeline.
