# Reference: 07 - Error Handling and Observability

Robust error handling and clear observability are critical for maintaining a healthy production application. This guide also addresses **OWASP A10:2025 (Mishandling of Exceptional Conditions)** [1].

## 1. Error Handling

- **Fail Gracefully, Fail Securely**: Never let an unexpected error crash the entire application. Use `try...catch` blocks for operations that can fail. When an error occurs, the system should **fail closed** (deny access, return a generic error) rather than **fail open** (grant access, expose internal details).
- **Custom Error Classes**: Create custom error classes that extend the base `Error` class.

  ```typescript
  class AppError extends Error {
    constructor(public statusCode: number, public code: string, message: string) {
      super(message);
      this.name = 'AppError';
    }
  }
  class NotFoundError extends AppError {
    constructor(resource: string) {
      super(404, 'NOT_FOUND', `${resource} not found`);
    }
  }
  class ValidationError extends AppError {
    constructor(details: string[]) {
      super(400, 'VALIDATION_ERROR', details.join(', '));
    }
  }
  ```

- **Standardized Error Responses**: Your API should return errors in a consistent, predictable format. Refer to the `Error` schema in your `openapi.yaml`.

  ```json
  {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email address",
    "details": ["The email field must be a valid email."]
  }
  ```

- **Never Expose Internal Details**: Error messages returned to the client must NEVER include stack traces, internal file paths, database query details, or any other information that could be exploited by an attacker. Log the full details server-side, but return a generic message to the client.

## 2. Structured Logging

Logging is the most fundamental tool for understanding what is happening inside your application.

- **Structured Logging**: Do not log plain text strings. Log JSON objects. This makes your logs machine-readable and allows you to easily search, filter, and analyze them.

  ```javascript
  // Bad
  logger.info('User ' + userId + ' logged in.');

  // Good
  logger.info({ userId, event: 'USER_LOGIN', traceId: req.traceId }, 'User logged in.');
  ```

- **Log Levels**: Use different log levels to indicate the severity of an event:
    - **`DEBUG`**: Detailed information for debugging during development.
    - **`INFO`**: Normal application behavior (e.g., user login, API request).
    - **`WARN`**: A potential problem that does not prevent the application from functioning.
    - **`ERROR`**: An error that caused an operation to fail. This requires attention.
    - **`FATAL`**: An error that is causing the application to crash.
- **Correlation IDs**: Assign a unique `traceId` (or `requestId`) to every incoming request and include it in all log entries for that request. This allows you to trace a single user action through all the services and log entries it touches. This is a core concept of **distributed tracing** in OpenTelemetry.
- **Security Logging (OWASP A09)**: Log all security-relevant events: successful and failed logins, access control failures, input validation failures, and administrative actions. Ensure logs do NOT contain sensitive data (passwords, tokens, PII).

## 3. Error Reporting

- **Automated Error Reporting**: Integrate an error reporting service (like Sentry or Bugsnag) into your application. This will automatically capture all unhandled exceptions, group them, and notify you.
- **Include Context**: When reporting an error, include as much context as possible, such as the user ID, request ID, and application version. This makes debugging much easier.

---

### References

[1] OWASP. (2025). *OWASP Top 10:2025 - A10: Mishandling of Exceptional Conditions*. OWASP Foundation.
