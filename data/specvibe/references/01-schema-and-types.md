# Reference: 01 - Schema, Types, and API Contracts

This guide covers the principles of defining data models and API contracts, which form the blueprint of the application.

## 1. Data Modeling: The Single Source of Truth

All data structures MUST be defined before any implementation. A shared `schema.ts` or similar file is the single source of truth for the entire application's data model.

### Principles

- **Clarity and Precision**: Use clear, descriptive names for interfaces, types, and enums.
- **Normalization**: Avoid data duplication. Use relationships to link entities.
- **Scalability**: Consider future needs when designing models.

### Best Practices

1.  **Use TypeScript Interfaces**: Define each database table or logical entity as a TypeScript `interface`.

    ```typescript
    // Example: A User entity
    export interface User {
      id: string; // UUID
      email: string; // Unique
      name: string | null;
      role: UserRole;
      createdAt: Date;
    }
    ```

2.  **Use Enums for Controlled Vocabularies**: For fields with a fixed set of possible values, always use an `enum`.

    ```typescript
    export enum UserRole {
      ADMIN = 'ADMIN',
      JUDGE = 'JUDGE',
      VIEWER = 'VIEWER',
    }
    ```

3.  **Document JSON/unstructured Columns**: If using a JSON/JSONB column, define its structure with a dedicated interface.

    ```typescript
    export interface UserPreferences {
      theme: 'dark' | 'light';
      notifications: {
        email: boolean;
        push: boolean;
      };
    }

    export interface User {
      // ... other fields
      preferences: UserPreferences; // Stored in a JSONB column
    }
    ```

## 2. API Contract: OpenAPI Specification

The API contract is a formal, machine-readable definition of your API. We use the **OpenAPI 3.0** standard.

### Principles

- **Contract-First**: The OpenAPI spec is written *before* the API code.
- **Consumer-Centric**: Design the API from the perspective of the frontend or third-party developer who will use it.
- **Completeness**: The spec must define all endpoints, parameters, request bodies, responses (including errors), and authentication methods.

### Best Practices

1.  **Use the Template**: Start with the `templates/openapi-template.yaml` file provided in this skill.

2.  **Define Reusable Components**: For common data structures like `User`, `Error`, or paginated responses, define them once in the `components/schemas` section and reference them using `$ref`.

    ```yaml
    components:
      schemas:
        Error:
          type: object
          properties:
            code: { type: string }
            message: { type: string }
    paths:
      /users/{userId}:
        get:
          responses:
            '404':
              description: User not found
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Error'
    ```

3.  **Clearly Document Responses**: Define all possible HTTP status code responses for each endpoint, especially common errors like `400` (Validation Error), `401` (Unauthorized), `403` (Forbidden), and `404` (Not Found).

## 3. API Versioning

APIs evolve. A clear versioning strategy is mandatory to avoid breaking changes for consumers.

- **Method**: Use **URL-based versioning** (e.g., `/api/v1/users`, `/api/v2/users`). It is the most explicit and widely understood method.
- **When to Version**: Increment the version number only for **breaking changes** (e.g., removing a field, changing a data type, altering an endpoint's path). Adding new fields or endpoints is non-breaking and does not require a version bump.
- **Deprecation Policy**: Clearly document your deprecation policy. When a new version (e.g., `v2`) is released, the old version (`v1`) should be maintained for a documented period (e.g., 6 months) before being decommissioned.

## 4. Type Safety Across Stacks

To eliminate an entire class of bugs, we ensure type safety from the database to the UI.

- **Backend**: Use an ORM like Prisma that generates type-safe clients from your database schema.
- **Frontend**: **Do not write API fetching code by hand.** Use a tool like `openapi-typescript-codegen` to automatically generate a fully-typed API client from your `openapi.yaml` file. This ensures that if the backend API changes, the frontend code will fail to compile, catching errors at build time, not runtime.
