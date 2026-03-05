---
name: ngamux
description: Build and modify web services using ngamux, a simple HTTP router for Go. Define routes, apply middleware, handle requests, and send responses efficiently.
---

## When to use this skill
Use this skill when the user needs to:
- **Define HTTP endpoints**: Create new routes for various HTTP methods (e.g., `mux.Get("/users/:id", getUserHandler)`) including dynamic path segments (`/users/{id}`) and wildcards (`/files/*filePath`).
- **Implement request preprocessing/postprocessing**: Add global middlewares (e.g., for authentication, logging, CORS) or group-specific middlewares to handle requests before they reach the main handler or after they are processed. For example, `mux.Use(authMiddleware)` or `apiGroup.Use(loggingMiddleware)`.
- **Extract incoming data from requests**:
    - **URL Parameters**: Retrieve values from dynamic path segments (e.g., `req.Params("id")`).
    - **Query Parameters**: Access query string values (e.g., `req.Query("name", "Guest")`).
    - **Form Data**: Parse `application/x-www-form-urlencoded` or `multipart/form-data` (e.g., `req.FormValue("username")`, `req.FormFile("image")`).
    - **JSON Payloads**: Decode `application/json` request bodies into Go structs (e.g., `req.JSON(&user)`).
- **Construct and send various response types**:
    - **JSON Responses**: Send structured data as JSON (e.g., `ngamux.Res(rw).Status(http.StatusOK).Json(data)`).
    - **Text Responses**: Send plain text (e.g., `ngamux.Res(rw).Status(http.StatusOK).Text("Hello, World!")`).
    - **HTML Responses**: Render HTML templates (e.g., `ngamux.Res(rw).Status(http.StatusOK).HTML("template.html", data)`).
    - **Custom Status Codes**: Set specific HTTP status codes for responses.
- **Configure router behavior**: Adjust global settings like automatically removing trailing slashes (`ngamux.WithTrailingSlash()`), setting the logging verbosity (`ngamux.WithLogLevel(slog.LevelDebug)`), or providing custom `json.Marshal`/`json.Unmarshal` functions for specific serialization needs.
- **Organize routes with grouping**: Create nested route groups to apply common path prefixes and middlewares to a set of routes (e.g., `/api/v1`).
- **Debug routing or handler issues**: Inspect route definitions, middleware chains, request context, and logging output to diagnose and resolve problems.

## Key Functionality
-   **Route Definition**: `ngamux` provides methods like `mux.Get()`, `mux.Post()`, `mux.Put()`, `mux.Delete()`, `mux.Patch()`, `mux.Head()`, and `mux.All()` to register `http.HandlerFunc`s for specific HTTP methods and paths. It supports path parameters (e.g., `/{id}`) and wildcards (`/*filePath`). Routes are efficiently stored and matched using a tree-like structure, leveraging the `mapping` package for optimized key-value storage.
-   **Middleware Application**: The `mux.Use()` method allows global middleware registration, while `mux.Group()` and `mux.With()` enable group-specific middlewares. Middlewares are `MiddlewareFunc` types that wrap `http.HandlerFunc`s, allowing for a chain of responsibility pattern. The `WithMiddlewares` utility from `common.go` handles the functional chaining.
-   **Request Handling**: The `Request` struct (wrapped `*http.Request`) offers convenience methods:
    -   `Req().Params(key string)`: Retrieves URL path parameters parsed during routing.
    -   `Req().Query(key string, fallback ...string)`: Accesses URL query string parameters.
    -   `Req().QueriesParser(data any)`: Automatically binds query parameters to a Go struct using `query` tags and reflection.
    -   `Req().FormValue(key string)`: Gets form field values.
    -   `Req().FormFile(key string, maxFileSize ...int64)`: Handles file uploads from multipart forms.
    -   `Req().JSON(store any)`: Decodes JSON request bodies into a provided Go interface.
    -   `Req().Locals(key any, value ...any)`: Manages request-scoped data in the context.
-   **Response Handling**: The `Response` struct (wrapped `http.ResponseWriter`) provides a fluent API for crafting responses:
    -   `Res(rw).Status(code int)`: Sets the HTTP status code.
    -   `Res(rw).Text(data string)`: Sends `text/plain` content.
    -   `Res(rw).JSON(data any)`: Sends `application/json` content, using the configured JSON marshaller.
    -   `Res(rw).HTML(path string, data any)`: Renders HTML templates using `html/template`.
-   **Configuration**: Global `Config` options are set via `ngamux.New()` and functional options like `ngamux.WithTrailingSlash()` and `ngamux.WithLogLevel()`. Custom JSON marshalling/unmarshalling can be provided.
-   **Route Grouping**: The `mux.Group(path string)` and `mux.GroupFunc(path string, router func(mux *Ngamux))` methods allow hierarchical organization of routes, where child groups inherit path prefixes and can apply their own set of middlewares, leading to cleaner code organization and shared logic.

