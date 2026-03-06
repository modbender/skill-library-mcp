# Code Review Checklist

## Security Issues
- [ ] Input validation implemented
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (proper escaping)
- [ ] Authentication and authorization checks
- [ ] Secure handling of sensitive data
- [ ] Proper encryption for stored/transported data

## Performance
- [ ] Efficient algorithms and data structures
- [ ] Database query optimization
- [ ] Proper indexing strategies
- [ ] Resource cleanup (memory, file handles, connections)
- [ ] Caching strategies where appropriate
- [ ] Lazy loading for expensive operations

## Code Quality
- [ ] Clear, descriptive variable/function names
- [ ] Functions are focused and single-purpose
- [ ] Code follows language conventions
- [ ] Proper error handling in place
- [ ] Appropriate logging levels and messages
- [ ] DRY (Don't Repeat Yourself) principle applied

## Maintainability
- [ ] Code is well-commented where needed
- [ ] Complex logic is explained
- [ ] Appropriate abstraction levels
- [ ] Modular design with clear interfaces
- [ ] Easy to modify without breaking other parts
- [ ] Dependencies are properly managed

## Testing
- [ ] Unit tests cover main functionality
- [ ] Edge cases are tested
- [ ] Error conditions are handled
- [ ] Integration tests for complex workflows
- [ ] Test coverage is adequate
- [ ] Tests are maintainable and readable

## Architecture
- [ ] Clear separation of concerns
- [ ] Proper layering (presentation, business, data)
- [ ] Configuration management
- [ ] Error propagation strategy
- [ ] Logging strategy
- [ ] Monitoring and observability considerations

## Documentation
- [ ] API endpoints documented
- [ ] Public functions/methods documented
- [ ] Architecture decisions recorded
- [ ] Deployment instructions clear
- [ ] Environment setup documented
- [ ] Known limitations noted