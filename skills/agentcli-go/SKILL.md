---
name: agentcli-go
description: "agentcli-go framework reference for building Go CLI tools. Use when working on agentcli-go itself, scaffolding new CLI projects, adding commands, integrating the library, or debugging framework behavior. Triggers on: agentcli-go, scaffold new CLI, add command, cobrax, configx, AppContext, RunLifecycle, agentcli."
version: "1.0"
last_updated: 2026-02-23
---

# agentcli-go

Shared Go CLI helpers and framework modules.

**Module:** `github.com/gh-xj/agentcli-go`
**Repo:** `github.com/gh-xj/agentcli-go` | **Versioning:** `v0.x.y` (pre-1.0)

---

## API Surface

| File | Exported Symbols |
|------|-----------------|
| `log.go` | `InitLogger()` — zerolog setup, respects `-v`/`--verbose` |
| `args.go` | `ParseArgs(args)`, `RequireArg(args, name)`, `GetArg(args, name)`, `HasFlag(args, name)` |
| `exec.go` | `RunCommand(name, args...)`, `RunOsascript(script)`, `Which(bin)`, `CheckDependency(bin)` |
| `fs.go` | `FileExists(path)`, `EnsureDir(path)`, `GetBaseName(path)` |
| `core_context.go` | `AppContext{Meta, Values}`, `NewAppContext(ctx)` |
| `lifecycle.go` | `Hook` interface (`Preflight`, `Postflight`), `RunLifecycle(app, hook, run)` |
| `errors.go` | `CLIError`, `ResolveExitCode(err)`, `ExitSuccess`, `ExitUsage` |
| `scaffold.go` | `ScaffoldNew(baseDir, name, module)`, `ScaffoldAddCommand(rootDir, name, desc, preset)`, `Doctor(rootDir) DoctorReport` |
| `cobrax/cobrax.go` | `Execute(RootSpec, args) int`, `NewRoot(RootSpec) *cobra.Command`, `CommandSpec`, `RootSpec` |
| `configx/configx.go` | `Load(Options) map[string]any`, `Decode[T](raw)`, `NormalizeEnv(prefix, environ)` |

---

## Scaffold Workflows

### New project
```bash
agentcli new --name my-tool --module github.com/me/my-tool
# or programmatically:
agentcli.ScaffoldNew(".", "my-tool", "github.com/me/my-tool")
```
Generates: `main.go`, `cmd/root.go`, `internal/app/`, `internal/config/`, `internal/io/`, `internal/tools/smokecheck/`, `pkg/version/`, `test/`, `Taskfile.yml`, `README.md`

### Add command
```bash
agentcli add command --name sync --preset file-sync
agentcli add command --name deploy --desc "run deploy checks"
```
Presets: `file-sync`, `http-client`, `deploy-helper`

### Doctor check
```bash
agentcli doctor [--dir ./my-tool]
# returns DoctorReport JSON with findings
```

---

## Golden Project Layout

```
my-tool/
├── main.go                          # os.Exit(cmd.Execute(os.Args[1:]))
├── cmd/
│   ├── root.go                      # cobrax.Execute(RootSpec{...})
│   └── <command>.go                 # func <Name>Command() command
├── internal/
│   ├── app/{bootstrap,lifecycle,errors}.go
│   ├── config/{schema,load}.go
│   ├── io/output.go
│   └── tools/smokecheck/main.go
├── pkg/version/version.go
├── test/
│   ├── e2e/cli_test.go
│   └── smoke/version.schema.json
└── Taskfile.yml
```

---

## cobrax Pattern

```go
// cmd/root.go
return cobrax.Execute(cobrax.RootSpec{
    Use:   "my-tool",
    Short: "my-tool CLI",
    Meta:  agentcli.AppMeta{Name: "my-tool", Version: version.Version},
    Commands: []cobrax.CommandSpec{
        {Use: "sync", Short: "sync files", Run: SyncCommand().Run},
    },
}, args)
```

Persistent flags auto-wired: `--verbose/-v`, `--config`, `--json`, `--no-color`
Values accessible via `app.Values["json"]`, `app.Values["config"]`, etc.

---

## configx Pattern

```go
raw, err := configx.Load(configx.Options{
    Defaults: map[string]any{"env": "default"},
    FilePath: configPath,   // optional JSON file
    Env:      configx.NormalizeEnv("MYTOOL_", os.Environ()),
    Flags:    map[string]string{"env": flagVal},
})
cfg, err := configx.Decode[config.Config](raw)
// Precedence: Defaults < File < Env < Flags
```

---

## Taskfile Tasks

| Task | Purpose |
|------|---------|
| `task ci` | Canonical CI: preflight + lint + test + build + smoke + schema checks |
| `task verify` | Local aggregate (wraps ci) |
| `task lint` | go vet + golangci-lint |
| `task smoke` | Deterministic smoke tests (subset of unit tests) |
| `task schema:check` | Validate JSON contracts against schemas |
| `task docs:check` | Ensure skill docs match CLI help signatures |
| `task fmt` | Format all Go files |

---

## Rules

- **Flat package** — everything in `package agentcli`, no sub-packages (except `cobrax`, `configx`)
- **Exported only** — all functions PascalCase; this is a library
- **No business logic** — generic utilities only; must be reused across 2+ projects to qualify
- **`log.Fatal` allowed** in `RequireArg`, `CheckDependency` (CLI-oriented helpers)
- **Minimal deps** — zerolog, lo, cobra only; justify new additions

## Out of Scope

- Project-specific logic (put that in consuming projects)
- Adding functions used by only one project
