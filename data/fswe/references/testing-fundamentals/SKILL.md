# Testing Fundamentals

## Test Pyramid

```
        ╱╲
       ╱  ╲      E2E (few)
      ╱────╲
     ╱      ╲    Integration (some)
    ╱────────╲
   ╱          ╲  Unit (many)
  ╱────────────╲
```

## Unit Testing

```typescript
// user.service.test.ts
import { describe, it, expect, vi } from 'vitest'
import { UserService } from './user.service'

describe('UserService', () => {
  it('should create user', async () => {
    const mockRepo = {
      create: vi.fn().mockResolvedValue({ id: '1', email: 'test@test.com' })
    }
    const service = new UserService(mockRepo)
    
    const user = await service.create({ email: 'test@test.com', name: 'Test' })
    
    expect(user.email).toBe('test@test.com')
    expect(mockRepo.create).toHaveBeenCalled()
  })
})
```

## Integration Testing

```typescript
// api/users.test.ts
import { describe, it, expect, beforeAll } from 'vitest'
import request from 'supertest'
import { app } from '../src/index'

describe('POST /users', () => {
  it('should create user', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'test@test.com', name: 'Test' })
    
    expect(res.status).toBe(201)
    expect(res.body.email).toBe('test@test.com')
  })
})
```

## Checklist

- [ ] Set up test framework (Vitest/Jest)
- [ ] Write unit tests for services
- [ ] Add integration tests for API
- [ ] Use test fixtures
- [ ] Mock external services
- [ ] Aim for 80% coverage on core logic
