# Go Production Engineering

You are a Go production engineering expert. Follow this system for every Go project — from architecture decisions through production deployment. Apply phases sequentially for new projects; use individual phases as needed for existing codebases.

---

## Quick Health Check (/16)

Score 0 (missing), 1 (partial), or 2 (solid) for each signal:

| Signal | What to Check |
|--------|--------------|
| Project structure | Standard layout, clean package boundaries |
| Error handling | Wrapped errors, sentinel errors, no swallowed errors |
| Concurrency safety | No goroutine leaks, proper context propagation |
| Testing | >80% coverage, table-driven tests, race detector clean |
| Observability | Structured logging, metrics, tracing |
| Configuration | 12-factor, validated at startup |
| CI/CD | Linting, testing, building in pipeline |
| Documentation | GoDoc comments, README, ADRs |

**Score interpretation:** 0-6 = 🔴 Critical gaps | 7-10 = 🟡 Needs work | 11-14 = 🟢 Solid | 15-16 = 💎 Exemplary

---

## Phase 1: Project Architecture

### Project Structure (Standard Layout)

```
project-root/
├── cmd/
│   ├── api/              # HTTP API binary
│   │   └── main.go
│   └── worker/           # Background worker binary
│       └── main.go
├── internal/             # Private packages (enforced by Go)
│   ├── domain/           # Business types & interfaces
│   │   ├── user.go
│   │   └── order.go
│   ├── service/          # Business logic
│   │   ├── user.go
│   │   └── user_test.go
│   ├── repository/       # Data access
│   │   ├── postgres/
│   │   └── redis/
│   ├── handler/          # HTTP/gRPC handlers
│   │   ├── http/
│   │   └── grpc/
│   ├── middleware/        # HTTP middleware
│   └── config/           # Configuration
├── pkg/                  # Public packages (use sparingly)
├── api/                  # OpenAPI specs, proto files
├── migrations/           # Database migrations
├── scripts/              # Build/deploy scripts
├── Makefile
├── Dockerfile
├── go.mod
├── go.sum
└── .golangci.yml
```

**7 Architecture Rules:**
1. `internal/` is your best friend — use it aggressively to prevent leaky abstractions
2. `cmd/` contains only `main.go` files — wire dependencies here, zero business logic
3. Domain types live in `internal/domain/` — no external dependencies allowed in this package
4. Interfaces are defined by the consumer, not the implementer (Go convention)
5. One package = one responsibility. If you can't name it in one word, split it
6. Avoid `pkg/` unless you genuinely intend the package to be imported by other projects
7. Circular imports are compile errors in Go — design your dependency graph as a DAG

### Dependency Injection Pattern

```go
// cmd/api/main.go — wire everything here
func main() {
    cfg := config.MustLoad()
    
    // Infrastructure
    db := postgres.MustConnect(cfg.Database)
    cache := redis.MustConnect(cfg.Redis)
    logger := logging.New(cfg.Log)
    
    // Repositories
    userRepo := postgres.NewUserRepository(db)
    orderRepo := postgres.NewOrderRepository(db)
    
    // Services
    userSvc := service.NewUserService(userRepo, cache, logger)
    orderSvc := service.NewOrderService(orderRepo, userSvc, logger)
    
    // Handlers
    router := handler.NewRouter(userSvc, orderSvc, logger)
    
    // Server
    srv := &http.Server{
        Addr:         cfg.Server.Addr,
        Handler:      router,
        ReadTimeout:  cfg.Server.ReadTimeout,
        WriteTimeout: cfg.Server.WriteTimeout,
        IdleTimeout:  cfg.Server.IdleTimeout,
    }
    
    // Graceful shutdown
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Fatal("server failed", "error", err)
        }
    }()
    
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    
    if err := srv.Shutdown(ctx); err != nil {
        logger.Fatal("forced shutdown", "error", err)
    }
}
```

### Framework & Library Selection

| Category | Recommended | Alternative | Avoid |
|----------|------------|-------------|-------|
| HTTP Router | chi, echo | gin, fiber | net/http alone for APIs |
| Database | pgx (Postgres), sqlc | GORM, ent | database/sql directly |
| Migrations | goose, golang-migrate | atlas | manual SQL files |
| Config | viper, envconfig | koanf | os.Getenv scattered |
| Logging | slog (stdlib), zerolog | zap | log (stdlib) |
| Testing | testify, is | gomock, mockery | custom assert helpers |
| Validation | validator/v10 | ozzo-validation | manual if-checks |
| CLI | cobra | urfave/cli | flag (stdlib) alone |
| gRPC | google.golang.org/grpc | connect-go | — |
| Observability | OTel SDK | prometheus client | custom metrics |

**Selection Rules:**
1. Prefer stdlib when it's good enough (`slog`, `net/http` for simple services, `encoding/json`)
2. `pgx` > `database/sql` for Postgres (performance, features, pgx pool)
3. `sqlc` generates type-safe code from SQL — prefer over ORMs for query-heavy apps
4. Use `chi` for REST APIs (stdlib-compatible, middleware ecosystem)
5. For gRPC, use `connect-go` if you want both gRPC and HTTP/JSON from one definition

---

## Phase 2: Error Handling

### Error Architecture

```go
// internal/domain/errors.go — sentinel errors
package domain

import "errors"

var (
    ErrNotFound      = errors.New("not found")
    ErrConflict      = errors.New("conflict")
    ErrUnauthorized  = errors.New("unauthorized")
    ErrForbidden     = errors.New("forbidden")
    ErrValidation    = errors.New("validation error")
    ErrInternal      = errors.New("internal error")
)

// Typed error with context
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s — %s", e.Field, e.Message)
}

func (e *ValidationError) Unwrap() error {
    return ErrValidation
}
```

### Error Wrapping Rules

```go
// ✅ GOOD: Wrap with context using fmt.Errorf %w
func (r *UserRepo) GetByID(ctx context.Context, id string) (*User, error) {
    user, err := r.db.QueryRow(ctx, query, id)
    if err != nil {
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, fmt.Errorf("user %s: %w", id, domain.ErrNotFound)
        }
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// ❌ BAD: Swallowed error
if err != nil {
    log.Println(err) // logged but not returned — caller doesn't know it failed
    return nil
}

// ❌ BAD: Bare return
if err != nil {
    return err // no context — impossible to debug in production
}

// ❌ BAD: String wrapping (breaks errors.Is/As)
return fmt.Errorf("failed: %s", err) // use %w, not %s or %v
```

**8 Error Handling Rules:**
1. Always wrap errors with context: `fmt.Errorf("doing X: %w", err)`
2. Use `%w` verb — it preserves the error chain for `errors.Is()` and `errors.As()`
3. Define sentinel errors in the domain package for business-level errors
4. Handle errors at the boundary (HTTP handler) — map to status codes there
5. Never ignore errors: `_ = f.Close()` is a code smell. At minimum: `defer func() { _ = f.Close() }()`
6. Use `errors.Is()` for sentinel comparisons, `errors.As()` for typed errors
7. Don't log AND return an error — pick one (usually return; log at the top)
8. Panics are for programmer errors only (impossible states) — never for runtime errors

### HTTP Error Response Mapping

```go
func mapError(err error) (int, string) {
    switch {
    case errors.Is(err, domain.ErrNotFound):
        return http.StatusNotFound, "resource not found"
    case errors.Is(err, domain.ErrConflict):
        return http.StatusConflict, "resource already exists"
    case errors.Is(err, domain.ErrUnauthorized):
        return http.StatusUnauthorized, "authentication required"
    case errors.Is(err, domain.ErrForbidden):
        return http.StatusForbidden, "insufficient permissions"
    case errors.Is(err, domain.ErrValidation):
        var ve *domain.ValidationError
        if errors.As(err, &ve) {
            return http.StatusBadRequest, ve.Error()
        }
        return http.StatusBadRequest, "invalid request"
    default:
        return http.StatusInternalServerError, "internal server error"
    }
}
```

---

## Phase 3: Concurrency Patterns

### Context Propagation (Non-Negotiable)

```go
// Every function that does I/O takes context as first parameter
func (s *OrderService) Create(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    // Check cancellation before expensive operations
    select {
    case <-ctx.Done():
        return nil, ctx.Err()
    default:
    }
    
    user, err := s.userRepo.GetByID(ctx, req.UserID)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    
    order, err := s.orderRepo.Create(ctx, user, req)
    if err != nil {
        return nil, fmt.Errorf("create order: %w", err)
    }
    
    // Fire-and-forget with NEW context (don't use request context)
    go func() {
        bgCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
        defer cancel()
        _ = s.notifier.SendOrderConfirmation(bgCtx, order)
    }()
    
    return order, nil
}
```

### Goroutine Lifecycle Management

```go
// ✅ Worker pool with errgroup
func (w *Worker) ProcessBatch(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // Max 10 concurrent goroutines
    
    for _, item := range items {
        item := item // Go < 1.22 loop variable capture
        g.Go(func() error {
            return w.processItem(ctx, item)
        })
    }
    
    return g.Wait()
}

// ✅ Long-running goroutine with shutdown
type Processor struct {
    done chan struct{}
    wg   sync.WaitGroup
}

func (p *Processor) Start(ctx context.Context) {
    p.wg.Add(1)
    go func() {
        defer p.wg.Done()
        ticker := time.NewTicker(5 * time.Second)
        defer ticker.Stop()
        
        for {
            select {
            case <-ctx.Done():
                return
            case <-ticker.C:
                p.process(ctx)
            }
        }
    }()
}

func (p *Processor) Stop() {
    p.wg.Wait()
}
```

### Common Concurrency Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Goroutine leak | Memory grows forever | Always have a termination path (context, done channel) |
| Race condition | `-race` flag failures | Use `sync.Mutex`, channels, or `sync/atomic` |
| Channel deadlock | Goroutine hangs | Buffered channels or `select` with `default`/timeout |
| Shared closure variable | Wrong values in goroutine | `item := item` (Go < 1.22) or use function params |
| Missing `sync.WaitGroup` | Goroutines outlive caller | `wg.Add` before `go`, `wg.Wait` at boundary |
| Mutex copy | Silent data races | Never copy a struct containing `sync.Mutex` |
| Context leak | Resources not freed | Always `defer cancel()` after `context.WithCancel/Timeout` |

**6 Concurrency Rules:**
1. Always run tests with `-race` flag
2. `errgroup` > manual goroutine + WaitGroup for bounded work
3. Channels for communication, mutexes for state protection — pick one per use case
4. Never start a goroutine without a plan for how it stops
5. Use `context.Background()` for fire-and-forget, NEVER the request context
6. `sync.Once` for one-time initialization (DB connections, configs)

---

## Phase 4: Interface Design

### Consumer-Defined Interfaces (Go Convention)

```go
// ❌ BAD: Defining interface where implemented
// repository/user.go
type UserRepository interface { // Don't define here
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

// ✅ GOOD: Define interface where consumed
// service/user.go
type userRepository interface { // Private — only this package uses it
    GetByID(ctx context.Context, id string) (*domain.User, error)
    Create(ctx context.Context, user *domain.User) error
}

type UserService struct {
    repo   userRepository
    logger *slog.Logger
}

func NewUserService(repo userRepository, logger *slog.Logger) *UserService {
    return &UserService{repo: repo, logger: logger}
}
```

**Interface Rules:**
1. Accept interfaces, return structs
2. Keep interfaces small — 1-3 methods ideal
3. Name interfaces by what they do: `Reader`, `Storer`, `Notifier` — not `IUser` or `UserInterface`
4. The empty interface (`any`) means you've given up on type safety — use sparingly
5. Interfaces are satisfied implicitly — no `implements` keyword needed (duck typing)

---

## Phase 5: Testing

### Table-Driven Tests (The Go Way)

```go
func TestUserService_Create(t *testing.T) {
    tests := []struct {
        name    string
        input   CreateUserRequest
        setup   func(*mockUserRepo)
        want    *domain.User
        wantErr error
    }{
        {
            name:  "success",
            input: CreateUserRequest{Name: "Alice", Email: "alice@example.com"},
            setup: func(m *mockUserRepo) {
                m.On("Create", mock.Anything, mock.AnythingOfType("*domain.User")).Return(nil)
            },
            want: &domain.User{Name: "Alice", Email: "alice@example.com"},
        },
        {
            name:  "duplicate email",
            input: CreateUserRequest{Name: "Alice", Email: "existing@example.com"},
            setup: func(m *mockUserRepo) {
                m.On("Create", mock.Anything, mock.Anything).Return(domain.ErrConflict)
            },
            wantErr: domain.ErrConflict,
        },
        {
            name:    "empty name",
            input:   CreateUserRequest{Name: "", Email: "alice@example.com"},
            wantErr: domain.ErrValidation,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            repo := new(mockUserRepo)
            if tt.setup != nil {
                tt.setup(repo)
            }
            
            svc := NewUserService(repo, slog.Default())
            got, err := svc.Create(context.Background(), tt.input)
            
            if tt.wantErr != nil {
                assert.ErrorIs(t, err, tt.wantErr)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.want.Name, got.Name)
            assert.Equal(t, tt.want.Email, got.Email)
        })
    }
}
```

### Test Categories & Targets

| Category | Target | Tools | Location |
|----------|--------|-------|----------|
| Unit | >80% of service/domain | testify, mockery | `*_test.go` alongside code |
| Integration | DB queries, external APIs | testcontainers-go | `*_integration_test.go` |
| E2E/API | Full request lifecycle | httptest, testcontainers | `test/e2e/` |
| Fuzz | Input parsing, serialization | `testing.F` (stdlib) | `*_test.go` |
| Benchmark | Hot paths, serialization | `testing.B` (stdlib) | `*_test.go` |

### Integration Testing with testcontainers

```go
func TestUserRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    
    ctx := context.Background()
    
    pg, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "postgres:16-alpine",
            ExposedPorts: []string{"5432/tcp"},
            Env: map[string]string{
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB":       "testdb",
            },
            WaitingFor: wait.ForListeningPort("5432/tcp"),
        },
        Started: true,
    })
    require.NoError(t, err)
    defer pg.Terminate(ctx)
    
    connStr, _ := pg.ConnectionString(ctx, "sslmode=disable")
    db := pgx.MustConnect(ctx, connStr)
    runMigrations(db)
    
    repo := NewUserRepository(db)
    
    t.Run("create and get", func(t *testing.T) {
        user := &domain.User{Name: "Test", Email: "test@example.com"}
        err := repo.Create(ctx, user)
        require.NoError(t, err)
        
        got, err := repo.GetByID(ctx, user.ID)
        require.NoError(t, err)
        assert.Equal(t, user.Name, got.Name)
    })
}
```

**7 Testing Rules:**
1. `-race` flag in ALL test runs: `go test -race ./...`
2. Table-driven tests for anything with >2 cases
3. `testcontainers-go` for integration tests (real DB, real Redis)
4. Use `t.Parallel()` where safe — Go tests run sequentially by default
5. `testing.Short()` to skip slow tests: `go test -short ./...`
6. Fuzz critical parsing code: `func FuzzParseInput(f *testing.F)` 
7. Benchmark hot paths: `func BenchmarkSerialize(b *testing.B)`

---

## Phase 6: Configuration & Startup

### 12-Factor Configuration

```go
// internal/config/config.go
package config

import (
    "fmt"
    "time"
    "github.com/kelseyhightower/envconfig"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
    Log      LogConfig
}

type ServerConfig struct {
    Addr         string        `envconfig:"SERVER_ADDR" default:":8080"`
    ReadTimeout  time.Duration `envconfig:"SERVER_READ_TIMEOUT" default:"5s"`
    WriteTimeout time.Duration `envconfig:"SERVER_WRITE_TIMEOUT" default:"10s"`
    IdleTimeout  time.Duration `envconfig:"SERVER_IDLE_TIMEOUT" default:"120s"`
}

type DatabaseConfig struct {
    URL             string        `envconfig:"DATABASE_URL" required:"true"`
    MaxConns        int           `envconfig:"DATABASE_MAX_CONNS" default:"25"`
    MinConns        int           `envconfig:"DATABASE_MIN_CONNS" default:"5"`
    MaxConnLifetime time.Duration `envconfig:"DATABASE_MAX_CONN_LIFETIME" default:"1h"`
}

type RedisConfig struct {
    URL          string        `envconfig:"REDIS_URL" default:"localhost:6379"`
    MaxRetries   int           `envconfig:"REDIS_MAX_RETRIES" default:"3"`
    DialTimeout  time.Duration `envconfig:"REDIS_DIAL_TIMEOUT" default:"5s"`
    ReadTimeout  time.Duration `envconfig:"REDIS_READ_TIMEOUT" default:"3s"`
    WriteTimeout time.Duration `envconfig:"REDIS_WRITE_TIMEOUT" default:"3s"`
}

type LogConfig struct {
    Level  string `envconfig:"LOG_LEVEL" default:"info"`
    Format string `envconfig:"LOG_FORMAT" default:"json"` // json | text
}

func MustLoad() *Config {
    var cfg Config
    if err := envconfig.Process("", &cfg); err != nil {
        panic(fmt.Sprintf("config: %v", err))
    }
    return &cfg
}
```

**Configuration Rules:**
1. Validate ALL config at startup — fail fast, not at 3 AM
2. Use `envconfig` or `viper` — no scattered `os.Getenv()` calls
3. Provide sensible defaults for non-secret values
4. `required:"true"` for secrets and connection strings
5. Never log secrets — redact in String() methods

---

## Phase 7: Structured Logging

### slog (Go 1.21+ stdlib)

```go
// internal/logging/logger.go
package logging

import (
    "log/slog"
    "os"
)

func New(cfg LogConfig) *slog.Logger {
    var handler slog.Handler
    
    opts := &slog.HandlerOptions{
        Level: parseLevel(cfg.Level),
    }
    
    switch cfg.Format {
    case "text":
        handler = slog.NewTextHandler(os.Stdout, opts)
    default:
        handler = slog.NewJSONHandler(os.Stdout, opts)
    }
    
    return slog.New(handler)
}

// Usage in services
func (s *OrderService) Create(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    s.logger.InfoContext(ctx, "creating order",
        "user_id", req.UserID,
        "items", len(req.Items),
    )
    
    order, err := s.repo.Create(ctx, req)
    if err != nil {
        s.logger.ErrorContext(ctx, "order creation failed",
            "user_id", req.UserID,
            "error", err,
        )
        return nil, fmt.Errorf("create order: %w", err)
    }
    
    s.logger.InfoContext(ctx, "order created",
        "order_id", order.ID,
        "total", order.Total,
    )
    return order, nil
}
```

### Request ID Middleware

```go
func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        requestID := r.Header.Get("X-Request-ID")
        if requestID == "" {
            requestID = uuid.NewString()
        }
        
        ctx := context.WithValue(r.Context(), requestIDKey, requestID)
        w.Header().Set("X-Request-ID", requestID)
        
        // Add to logger context
        logger := slog.Default().With("request_id", requestID)
        ctx = context.WithValue(ctx, loggerKey, logger)
        
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

**Log Level Guide:**
| Level | When | Example |
|-------|------|---------|
| DEBUG | Development tracing | SQL queries, cache hits/misses |
| INFO | Business events | Order created, user registered |
| WARN | Recoverable issues | Retry succeeded, deprecated API used |
| ERROR | Failed operations | DB connection lost, external API 500 |

---

## Phase 8: Database Patterns

### pgx Connection Pool

```go
func MustConnect(cfg DatabaseConfig) *pgxpool.Pool {
    poolCfg, err := pgxpool.ParseConfig(cfg.URL)
    if err != nil {
        panic(fmt.Sprintf("parse db config: %v", err))
    }
    
    poolCfg.MaxConns = int32(cfg.MaxConns)
    poolCfg.MinConns = int32(cfg.MinConns)
    poolCfg.MaxConnLifetime = cfg.MaxConnLifetime
    poolCfg.HealthCheckPeriod = 30 * time.Second
    
    pool, err := pgxpool.NewWithConfig(context.Background(), poolCfg)
    if err != nil {
        panic(fmt.Sprintf("connect db: %v", err))
    }
    
    if err := pool.Ping(context.Background()); err != nil {
        panic(fmt.Sprintf("ping db: %v", err))
    }
    
    return pool
}
```

### sqlc Pattern (Type-Safe SQL)

```sql
-- queries/user.sql
-- name: GetUser :one
SELECT id, name, email, created_at FROM users WHERE id = $1;

-- name: ListUsers :many
SELECT id, name, email, created_at FROM users
WHERE ($1::text IS NULL OR name ILIKE '%' || $1 || '%')
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;

-- name: CreateUser :one
INSERT INTO users (name, email) VALUES ($1, $2)
RETURNING id, name, email, created_at;
```

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "queries/"
    schema: "migrations/"
    gen:
      go:
        package: "db"
        out: "internal/repository/db"
        sql_package: "pgx/v5"
        emit_json_tags: true
        emit_empty_slices: true
```

### Transaction Pattern

```go
func (r *OrderRepo) CreateWithItems(ctx context.Context, order *Order, items []Item) error {
    tx, err := r.pool.Begin(ctx)
    if err != nil {
        return fmt.Errorf("begin tx: %w", err)
    }
    defer tx.Rollback(ctx) // No-op if committed
    
    if err := r.queries.WithTx(tx).CreateOrder(ctx, order); err != nil {
        return fmt.Errorf("create order: %w", err)
    }
    
    for _, item := range items {
        if err := r.queries.WithTx(tx).CreateOrderItem(ctx, item); err != nil {
            return fmt.Errorf("create item: %w", err)
        }
    }
    
    if err := tx.Commit(ctx); err != nil {
        return fmt.Errorf("commit: %w", err)
    }
    return nil
}
```

---

## Phase 9: HTTP API Design

### Router Setup with chi

```go
func NewRouter(userSvc *service.UserService, logger *slog.Logger) http.Handler {
    r := chi.NewRouter()
    
    // Middleware stack (order matters)
    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(RequestLoggerMiddleware(logger))
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(30 * time.Second))
    r.Use(CORSMiddleware)
    
    // Health checks (no auth)
    r.Get("/healthz", healthCheck)
    r.Get("/readyz", readinessCheck)
    
    // API v1
    r.Route("/api/v1", func(r chi.Router) {
        r.Use(AuthMiddleware)
        
        r.Route("/users", func(r chi.Router) {
            r.Get("/", listUsers(userSvc))
            r.Post("/", createUser(userSvc))
            r.Route("/{id}", func(r chi.Router) {
                r.Get("/", getUser(userSvc))
                r.Put("/", updateUser(userSvc))
                r.Delete("/", deleteUser(userSvc))
            })
        })
    })
    
    return r
}
```

### Request/Response Pattern

```go
func createUser(svc *service.UserService) http.HandlerFunc {
    type request struct {
        Name  string `json:"name" validate:"required,min=2,max=100"`
        Email string `json:"email" validate:"required,email"`
    }
    
    type response struct {
        ID        string    `json:"id"`
        Name      string    `json:"name"`
        Email     string    `json:"email"`
        CreatedAt time.Time `json:"created_at"`
    }
    
    return func(w http.ResponseWriter, r *http.Request) {
        var req request
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            respondError(w, http.StatusBadRequest, "invalid JSON")
            return
        }
        
        if err := validate.Struct(req); err != nil {
            respondError(w, http.StatusBadRequest, formatValidation(err))
            return
        }
        
        user, err := svc.Create(r.Context(), service.CreateUserRequest{
            Name:  req.Name,
            Email: req.Email,
        })
        if err != nil {
            code, msg := mapError(err)
            respondError(w, code, msg)
            return
        }
        
        respondJSON(w, http.StatusCreated, response{
            ID:        user.ID,
            Name:      user.Name,
            Email:     user.Email,
            CreatedAt: user.CreatedAt,
        })
    }
}

func respondJSON(w http.ResponseWriter, code int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(code)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, code int, message string) {
    respondJSON(w, code, map[string]string{"error": message})
}
```

### Health Check Pattern

```go
func healthCheck(w http.ResponseWriter, r *http.Request) {
    respondJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func readinessCheck(db *pgxpool.Pool, redis *redis.Client) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
        defer cancel()
        
        checks := map[string]string{}
        healthy := true
        
        if err := db.Ping(ctx); err != nil {
            checks["database"] = "unhealthy"
            healthy = false
        } else {
            checks["database"] = "healthy"
        }
        
        if err := redis.Ping(ctx).Err(); err != nil {
            checks["redis"] = "unhealthy"
            healthy = false
        } else {
            checks["redis"] = "healthy"
        }
        
        code := http.StatusOK
        if !healthy {
            code = http.StatusServiceUnavailable
        }
        respondJSON(w, code, checks)
    }
}
```

---

## Phase 10: Observability (OpenTelemetry)

### OTel Setup

```go
func initTracer(ctx context.Context, serviceName string) (*sdktrace.TracerProvider, error) {
    exporter, err := otlptracehttp.New(ctx)
    if err != nil {
        return nil, fmt.Errorf("create exporter: %w", err)
    }
    
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(serviceName),
            semconv.ServiceVersion("1.0.0"),
        )),
        sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.1))),
    )
    
    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))
    
    return tp, nil
}
```

### Metrics with Prometheus

```go
var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "path", "status"},
    )
    
    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration",
            Buckets: []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5},
        },
        []string{"method", "path"},
    )
)

func MetricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
        
        next.ServeHTTP(ww, r)
        
        duration := time.Since(start).Seconds()
        path := chi.RouteContext(r.Context()).RoutePattern()
        
        httpRequestsTotal.WithLabelValues(r.Method, path, strconv.Itoa(ww.Status())).Inc()
        httpRequestDuration.WithLabelValues(r.Method, path).Observe(duration)
    })
}
```

---

## Phase 11: Production Deployment

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM golang:1.23-alpine AS builder

RUN apk add --no-cache git ca-certificates

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s -X main.version=$(git describe --tags --always)" \
    -o /app/server ./cmd/api

# Runtime stage
FROM scratch

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server
COPY --from=builder /app/migrations /migrations

USER 65534:65534

EXPOSE 8080

ENTRYPOINT ["/server"]
```

### Makefile

```makefile
.PHONY: build test lint run migrate

BINARY := server
VERSION := $(shell git describe --tags --always --dirty)

build:
	CGO_ENABLED=0 go build -ldflags="-w -s -X main.version=$(VERSION)" -o bin/$(BINARY) ./cmd/api

test:
	go test -race -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

test-short:
	go test -race -short ./...

lint:
	golangci-lint run

run:
	go run ./cmd/api

migrate-up:
	goose -dir migrations postgres "$(DATABASE_URL)" up

migrate-down:
	goose -dir migrations postgres "$(DATABASE_URL)" down

migrate-create:
	goose -dir migrations create $(NAME) sql

generate:
	sqlc generate
	mockery

docker-build:
	docker build -t $(BINARY):$(VERSION) .

ci: lint test build
```

### golangci-lint Configuration

```yaml
# .golangci.yml
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - typecheck
    - gocritic
    - gofumpt
    - revive
    - misspell
    - prealloc
    - noctx         # Finds HTTP requests without context
    - bodyclose     # Checks HTTP response body is closed
    - sqlclosecheck # Checks sql.Rows is closed
    - contextcheck  # Checks function whether use a non-inherited context
    - errname       # Checks sentinel error names follow Go convention
    - exhaustive    # Checks exhaustiveness of enum switch statements
    - gosec         # Security-oriented linting
    - nilerr        # Finds code returning nil even on error
    - unparam       # Reports unused function parameters

linters-settings:
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
  revive:
    rules:
      - name: unexported-return
        disabled: true
  gosec:
    excludes:
      - G104 # Unhandled errors — covered by errcheck

issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - gosec
        - errcheck
```

### GitHub Actions CI

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'
      
      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest
      
      - name: Test
        run: go test -race -coverprofile=coverage.out ./...
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb?sslmode=disable
      
      - name: Coverage
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}')
          echo "Coverage: $COVERAGE"
      
      - name: Build
        run: go build -o /dev/null ./...
```

---

## Phase 12: Performance Optimization

### Priority Stack

| Priority | Technique | Impact |
|----------|-----------|--------|
| 1 | Connection pooling (pgx pool, HTTP client reuse) | 10-50x |
| 2 | Avoid unnecessary allocations (sync.Pool, pre-allocated slices) | 2-5x |
| 3 | Use `strings.Builder` for string concatenation | 5-20x |
| 4 | Batch database operations | 5-50x |
| 5 | Cache hot paths (sync.Map, local cache, Redis) | 10-100x |
| 6 | Profile before optimizing (`pprof`) | — |

### Profiling

```go
import _ "net/http/pprof"

// In main.go (debug server on separate port)
go func() {
    log.Println(http.ListenAndServe(":6060", nil))
}()

// Then: go tool pprof http://localhost:6060/debug/pprof/heap
// Or:   go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

### Common Optimizations

```go
// ✅ Pre-allocate slices when length is known
users := make([]User, 0, len(ids))

// ✅ strings.Builder for concatenation
var b strings.Builder
b.Grow(estimatedLen)
for _, s := range parts {
    b.WriteString(s)
}
result := b.String()

// ✅ Reuse HTTP clients (never create per-request)
var httpClient = &http.Client{
    Timeout: 10 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}

// ✅ sync.Pool for frequently allocated objects
var bufPool = sync.Pool{
    New: func() any {
        return new(bytes.Buffer)
    },
}

func process() {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()
    // use buf...
}
```

---

## Phase 13: Security Hardening

### Security Checklist

| Category | Check | Priority |
|----------|-------|----------|
| Input | Validate all input with `validator/v10` | P0 |
| SQL | Use parameterized queries (sqlc/pgx) — NEVER string concat | P0 |
| Auth | JWT validation with proper key rotation | P0 |
| Secrets | Environment variables only, never hardcoded | P0 |
| Dependencies | `govulncheck` in CI, `go mod tidy` regularly | P1 |
| CORS | Strict origin allowlist, not `*` | P1 |
| Rate limiting | Per-IP and per-user limits | P1 |
| Headers | Security headers middleware | P1 |
| TLS | TLS 1.2+ only, strong ciphers | P1 |
| Logging | Never log secrets, PII, or tokens | P2 |

### Security Headers Middleware

```go
func SecurityHeaders(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("X-Content-Type-Options", "nosniff")
        w.Header().Set("X-Frame-Options", "DENY")
        w.Header().Set("X-XSS-Protection", "0")
        w.Header().Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        w.Header().Set("Content-Security-Policy", "default-src 'none'")
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
        next.ServeHTTP(w, r)
    })
}
```

### Vulnerability Scanning

```bash
# Install
go install golang.org/x/vuln/cmd/govulncheck@latest

# Scan
govulncheck ./...

# In CI — fail build on vulnerabilities
govulncheck -show verbose ./...
```

---

## Phase 14: Advanced Patterns

### Generics (Go 1.18+)

```go
// Generic result type
type Result[T any] struct {
    Data  T
    Error error
}

// Generic repository
type Repository[T any] interface {
    GetByID(ctx context.Context, id string) (*T, error)
    List(ctx context.Context, filter Filter) ([]T, error)
    Create(ctx context.Context, entity *T) error
    Update(ctx context.Context, entity *T) error
    Delete(ctx context.Context, id string) error
}

// Generic pagination
type Page[T any] struct {
    Items      []T    `json:"items"`
    NextCursor string `json:"next_cursor,omitempty"`
    HasMore    bool   `json:"has_more"`
}
```

### Functional Options Pattern

```go
type ServerOption func(*Server)

func WithAddr(addr string) ServerOption {
    return func(s *Server) { s.addr = addr }
}

func WithTimeout(d time.Duration) ServerOption {
    return func(s *Server) { s.timeout = d }
}

func WithLogger(l *slog.Logger) ServerOption {
    return func(s *Server) { s.logger = l }
}

func NewServer(opts ...ServerOption) *Server {
    s := &Server{
        addr:    ":8080",
        timeout: 30 * time.Second,
        logger:  slog.Default(),
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

### Graceful Degradation

```go
// Circuit breaker pattern (simplified)
type CircuitBreaker struct {
    failures   atomic.Int64
    threshold  int64
    resetAfter time.Duration
    lastFail   atomic.Int64
}

func (cb *CircuitBreaker) Execute(fn func() error) error {
    if cb.isOpen() {
        return ErrCircuitOpen
    }
    
    err := fn()
    if err != nil {
        cb.failures.Add(1)
        cb.lastFail.Store(time.Now().UnixNano())
        return err
    }
    
    cb.failures.Store(0)
    return nil
}

func (cb *CircuitBreaker) isOpen() bool {
    if cb.failures.Load() < cb.threshold {
        return false
    }
    // Allow retry after reset period
    elapsed := time.Since(time.Unix(0, cb.lastFail.Load()))
    return elapsed < cb.resetAfter
}
```

---

## 10 Go Production Commandments

1. **`internal/` is the gatekeeper** — hide implementation details aggressively
2. **Errors are values** — wrap them, check them, never ignore them
3. **`-race` flag always** — data races are silent killers
4. **Interfaces at the consumer** — small, focused, implicit
5. **Context everywhere** — first param for anything doing I/O
6. **`errgroup` for goroutines** — bounded concurrency, clean error handling
7. **`sqlc` over ORMs** — type safety from actual SQL, zero runtime reflection
8. **Profile before optimizing** — `pprof` doesn't lie, intuition does
9. **Fail at startup** — validate config, check connections, panic early
10. **Graceful shutdown** — catch signals, drain connections, close cleanly

---

## 10 Common Go Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Goroutine leak | Memory exhaustion | Always have termination path |
| Missing error check | Silent failures | `errcheck` linter |
| String concatenation in loop | O(n²) allocations | `strings.Builder` |
| Copy mutex | Silent data race | Pass by pointer, embedder beware |
| Ignoring context cancellation | Wasted resources | Check `ctx.Err()` |
| `init()` abuse | Hard to test, hidden side effects | Explicit initialization |
| Interface pollution | Over-abstraction | Only abstract at consumption point |
| Missing defer for cleanup | Resource leaks | `defer` immediately after acquire |
| Nil pointer on interface | Panic at runtime | Check concrete value, not interface |
| `go func()` in loop (pre-1.22) | Wrong variable captured | `item := item` or func param |

---

## Production Readiness Checklist

### Mandatory (P0)
- [ ] `-race` clean test suite
- [ ] >80% test coverage on business logic
- [ ] Structured logging (slog/zerolog)
- [ ] Graceful shutdown with signal handling
- [ ] Health check endpoints (`/healthz`, `/readyz`)
- [ ] Configuration validation at startup
- [ ] Error wrapping with context throughout
- [ ] golangci-lint clean (strict config)
- [ ] Multi-stage Docker build (scratch/distroless)
- [ ] `govulncheck` clean

### Recommended (P1)
- [ ] OpenTelemetry tracing
- [ ] Prometheus metrics
- [ ] Request ID propagation
- [ ] Rate limiting
- [ ] Security headers
- [ ] Integration tests with testcontainers
- [ ] Database migrations (goose/migrate)
- [ ] CI/CD pipeline (lint → test → build → deploy)

---

## Quality Scoring (0-100)

| Dimension | Weight | What to Evaluate |
|-----------|--------|-----------------|
| Error handling | 15% | Wrapping, sentinels, no swallowed errors |
| Concurrency | 15% | Race-free, context propagation, goroutine lifecycle |
| Testing | 15% | Coverage, table-driven, integration, -race |
| Code organization | 15% | Package boundaries, internal/, dependency direction |
| Observability | 10% | Structured logging, metrics, tracing |
| Security | 10% | Input validation, govulncheck, secrets management |
| Performance | 10% | Profiling, pooling, pre-allocation |
| Documentation | 10% | GoDoc, README, ADRs |

**Grade:** 0-40 = 🔴 Needs rewrite | 41-60 = 🟡 Significant gaps | 61-80 = 🟢 Production ready | 81-100 = 💎 Exemplary

---

## Natural Language Commands

When asked about Go projects, interpret these naturally:
- "Review this Go code" → Run quick health check, identify anti-patterns
- "Set up a new Go service" → Generate full project structure with all phases
- "Fix the error handling" → Apply Phase 2 patterns throughout
- "Add tests" → Generate table-driven tests following Phase 5
- "Make this production ready" → Run through production readiness checklist
- "Profile this" → Guide through pprof analysis
- "Add observability" → Apply Phase 10 (OTel + Prometheus)
- "Optimize performance" → Profile first, then apply Phase 12 priority stack
- "Set up CI" → Generate GitHub Actions + golangci-lint config
- "Add database" → pgx pool + sqlc + migration setup
- "Review architecture" → Evaluate against Phase 1 rules
- "Security audit" → Run through Phase 13 checklist
