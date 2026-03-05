---
name: gopls-lsp
description: Go language server (gopls) providing code intelligence, refactoring, and analysis for .go files. Use when working with Go code that needs autocomplete, go-to-definition, find references, error detection, or refactoring support.
---

# gopls LSP

Go language server integration providing comprehensive code intelligence through gopls (the official Go language server).

## Capabilities

- **Code intelligence**: Autocomplete, go-to-definition, find references
- **Error detection**: Real-time diagnostics for compilation errors and issues
- **Refactoring**: Rename symbols, extract function, organize imports
- **Analysis**: Static analysis, code suggestions, unused code detection
- **Supported extensions**: `.go`

## Installation

Install gopls using the Go toolchain:

```bash
go install golang.org/x/tools/gopls@latest
```

**Important**: Make sure `$GOPATH/bin` (or `$HOME/go/bin`) is in your PATH.

Verify installation:
```bash
gopls version
```

## Usage

The language server runs automatically in LSP-compatible editors. For manual operations:

### Format code
```bash
gofmt -w file.go
```

### Run linter
```bash
go vet ./...
```

### Build and test
```bash
go build ./...
go test ./...
```

## Configuration

Create `gopls.yaml` in your project or workspace for custom settings:

```yaml
analyses:
  unusedparams: true
  shadow: true
completeUnimported: true
staticcheck: true
```

Or configure via environment:
```bash
export GOPLS_CONFIG='{"staticcheck": true, "analyses": {"unusedparams": true}}'
```

## Integration Pattern

When editing Go code:
1. gopls provides real-time diagnostics in LSP editors
2. Run `go fmt` or `gofmt` to format code
3. Use `go vet` for additional static analysis
4. Run tests with `go test` before committing

## Common Go Commands

- `go mod init <module>` - Initialize Go module
- `go mod tidy` - Clean up dependencies
- `go get <package>` - Add dependency
- `go build` - Compile packages
- `go run main.go` - Run program
- `go test` - Run tests
- `go vet` - Report suspicious constructs

## More Information

- [gopls Documentation](https://pkg.go.dev/golang.org/x/tools/gopls)
- [GitHub Repository](https://github.com/golang/tools/tree/master/gopls)
- [Go Official Documentation](https://go.dev/doc/)
