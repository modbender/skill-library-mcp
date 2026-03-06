# Reference: 09 - Documentation

Code is read more often than it is written. Good documentation is not an afterthought; it is a core part of a maintainable and scalable project.

## The Delegate/Review/Own Model for Documentation

- **Delegate**: Use AI to generate the first draft of all documentation. This includes API reference documentation from OpenAPI specs, README files from `spec.md`, and code comments.
- **Review**: A human must review all AI-generated documentation for accuracy, clarity, and tone. The goal is to make the documentation helpful and easy to understand.
- **Own**: The development team owns the quality and completeness of the documentation.

## Types of Documentation

### 1. API Documentation

- **Source**: The `openapi.yaml` file is the single source of truth.
- **Generation**: Use a tool like **Redoc** or **Swagger UI** to automatically generate a beautiful, interactive API reference website from your OpenAPI spec.
- **CI/CD**: This generation and deployment should be part of your CI/CD pipeline.

### 2. Developer Documentation

- **README.md**: The root `README.md` should be a concise entry point to the project. It should explain what the project is, why it exists, and how to get it running locally. Use the `templates/readme-template.md` as a starting point.
- **Architectural Decision Records (ADRs)**: For significant architectural decisions (e.g., choosing a database, deciding on a microservices pattern), create a short markdown file in a `/docs/adr` directory. This provides context for future developers on *why* a decision was made.

### 3. User Documentation

- **Source**: The `spec.md` file, which contains the user journeys and goals.
- **Format**: Can be a simple set of markdown files, a GitBook, or a dedicated knowledge base.
- **Content**: Should be written for a non-technical audience. Focus on how to use the application to solve their problems.

### 4. Code Comments

- **Good Code is Self-Documenting**: Strive to write code that is so clear it doesn't need comments.
- **Comment the *Why*, not the *What***: Do not write comments that explain what the code is doing. A developer can read the code to understand that. Write comments to explain *why* the code is doing something, especially if the reason is not obvious (e.g., a workaround for a library bug, a specific business rule).

    ```typescript
    // Bad comment: what
    // Increment i by 1
    i++;

    // Good comment: why
    // We need to increment the counter here to account for the off-by-one
    // error in the legacy data import script.
    i++;
    ```
