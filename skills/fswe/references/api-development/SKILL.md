# API Development

## Overview
Clean controller architecture, validation strategy, error standardization, authentication & authorization, dan API documentation standards.

## Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                              │
│   Routes → Controllers → Validation → Error Handling        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                            │
│   Business Logic → Orchestration → Transactions            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   REPOSITORY LAYER                          │
│   Database Queries → Caching → External APIs               │
└─────────────────────────────────────────────────────────────┘
```

## Controller Pattern

```typescript
// routes/user.routes.ts
import { Router, Request, Response, NextFunction } from 'express'
import { UserService } from '../services/user.service'
import { validateRequest } from '../middleware/validation'
import { authenticate } from '../middleware/auth'

const router = Router()
const userService = new UserService()

// GET /users
router.get('/users', 
  authenticate,
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const users = await userService.findAll(req.query)
      res.json(users)
    } catch (err) {
      next(err)
    }
  }
)

// GET /users/:id
router.get('/users/:id', 
  authenticate,
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const user = await userService.findById(req.params.id)
      if (!user) {
        return res.status(404).json({ error: 'User not found' })
      }
      res.json(user)
    } catch (err) {
      next(err)
    }
  }
)

// POST /users
router.post('/users',
  validateRequest(createUserSchema),
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const user = await userService.create(req.body)
      res.status(201).json(user)
    } catch (err) {
      next(err)
    }
  }
)

// PATCH /users/:id
router.patch('/users/:id',
  authenticate,
  validateRequest(updateUserSchema),
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const user = await userService.update(req.params.id, req.body)
      res.json(user)
    } catch (err) {
      next(err)
    }
  }
)

// DELETE /users/:id
router.delete('/users/:id',
  authenticate,
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      await userService.delete(req.params.id)
      res.status(204).send()
    } catch (err) {
      next(err)
    }
  }
)

export default router
```

## Validation Strategy (Zod)

```typescript
// schemas/user.schema.ts
import { z } from 'zod'

export const createUserSchema = z.object({
  body: z.object({
    email: z.string().email('Invalid email format'),
    name: z.string().min(1, 'Name is required').max(100),
    password: z.string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain uppercase')
      .regex(/[0-9]/, 'Password must contain number'),
    role: z.enum(['user', 'admin']).default('user'),
  }),
})

export const updateUserSchema = z.object({
  body: z.object({
    name: z.string().min(1).max(100).optional(),
    email: z.string().email().optional(),
    avatar: z.string().url().optional(),
  }),
  params: z.object({
    id: z.string().uuid(),
  }),
})

export const userIdSchema = z.object({
  params: z.object({
    id: z.string().uuid(),
  }),
})

// Type inference
export type CreateUserInput = z.infer<typeof createUserSchema>
export type UpdateUserInput = z.infer<typeof updateUserSchema>
```

## Error Standardization

```typescript
// errors/app.error.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: unknown
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public validationErrors: ValidationDetail[]) {
    super(message, 'VALIDATION_ERROR', 400)
    this.name = 'ValidationError'
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404)
    this.name = 'NotFoundError'
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401)
    this.name = 'UnauthorizedError'
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super(message, 'FORBIDDEN', 403)
    this.name = 'ForbiddenError'
  }
}

// Standard error response format
interface ErrorResponse {
  error: {
    code: string
    message: string
    details?: ValidationDetail[]
    requestId?: string
  }
}
```

## Authentication & Authorization

```typescript
// middleware/auth.ts
import { Request, Response, NextFunction } from 'express'
import jwt from 'jsonwebtoken'
import { UnauthorizedError } from '../errors/app.error'

interface JwtPayload {
  userId: string
  email: string
  role: string
}

export const authenticate = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const authHeader = req.headers.authorization
  
  if (!authHeader?.startsWith('Bearer ')) {
    throw new UnauthorizedError('No token provided')
  }

  const token = authHeader.substring(7)

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload
    req.user = payload
    next()
  } catch {
    throw new UnauthorizedError('Invalid token')
  }
}

export const authorize = (...roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      throw new UnauthorizedError()
    }

    if (!roles.includes(req.user.role)) {
      throw new ForbiddenError('Insufficient permissions')
    }

    next()
  }
}
```

## API Documentation (OpenAPI)

```yaml
# openapi.yaml
openapi: 3.0.3
info:
  title: EazyCam API
  version: 1.0.0
  description: API for EazyCam webcam service

servers:
  - url: https://api.eazycam.com/v1
  - url: http://localhost:3000/v1

paths:
  /users:
    get:
      summary: List users
      tags: [Users]
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  meta:
                    $ref: '#/components/schemas/Pagination'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
```

## Checklist

### Controller Layer
- [ ] Use middleware for cross-cutting concerns
- [ ] Keep controllers thin (no business logic)
- [ ] Return proper HTTP status codes
- [ ] Add request validation
- [ ] Include pagination for list endpoints

### Error Handling
- [ ] Create custom error classes
- [ ] Standardize error response format
- [ ] Add request ID for tracing
- [ ] Don't leak internal details in production

### Security
- [ ] Implement authentication
- [ ] Add role-based authorization
- [ ] Validate all inputs
- [ ] Rate limit endpoints
- [ ] Use HTTPS only

### Documentation
- [ ] Document with OpenAPI/Swagger
- [ ] Include example responses
- [ ] Document error codes
- [ ] Add authentication requirements
