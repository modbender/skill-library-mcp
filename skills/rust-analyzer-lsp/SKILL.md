---
name: rust-analyzer-lsp
description: Rust language server (rust-analyzer) providing code intelligence and analysis for .rs files. Use when working with Rust code that needs autocomplete, go-to-definition, find references, error detection, or refactoring support.
---

# rust-analyzer LSP

Rust language server integration providing comprehensive code intelligence through rust-analyzer.

## Capabilities

- **Code intelligence**: Autocomplete, go-to-definition, find references
- **Error detection**: Real-time diagnostics for compilation errors
- **Refactoring**: Rename symbols, extract function/variable
- **Analysis**: Macro expansion, type hints, inlay hints
- **Supported extensions**: `.rs`

## Installation

### Via rustup (recommended)
```bash
rustup component add rust-analyzer
```

### Via Homebrew (macOS)
```bash
brew install rust-analyzer
```

### Via package manager (Linux)
```bash
# Ubuntu/Debian
sudo apt install rust-analyzer

# Arch Linux
sudo pacman -S rust-analyzer
```

### Manual download
Download pre-built binaries from the [releases page](https://github.com/rust-lang/rust-analyzer/releases).

Verify installation:
```bash
rust-analyzer --version
```

## Usage

The language server runs automatically in LSP-compatible editors. For manual operations:

### Format code
```bash
cargo fmt
```

### Run linter
```bash
cargo clippy
```

### Build and test
```bash
cargo build
cargo test
```

### Check without building
```bash
cargo check
```

## Configuration

Create `.rust-analyzer.json` in project root:

```json
{
  "checkOnSave": {
    "command": "clippy"
  },
  "inlayHints": {
    "typeHints": true,
    "parameterHints": true
  }
}
```

## Integration Pattern

When editing Rust code:
1. rust-analyzer provides real-time diagnostics
2. Run `cargo fmt` to format code
3. Use `cargo clippy` for linting
4. Run `cargo test` before committing

## Common Cargo Commands

- `cargo new <name>` - Create new project
- `cargo build` - Compile project
- `cargo run` - Build and run
- `cargo test` - Run tests
- `cargo check` - Fast compile check
- `cargo clippy` - Run linter
- `cargo fmt` - Format code
- `cargo doc --open` - Generate and open docs

## More Information

- [rust-analyzer Website](https://rust-analyzer.github.io/)
- [GitHub Repository](https://github.com/rust-lang/rust-analyzer)
- [Rust Official Documentation](https://doc.rust-lang.org/)
