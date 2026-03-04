---
name: clangd-lsp
description: C/C++ language server (clangd) providing code intelligence, diagnostics, and formatting for .c, .h, .cpp, .cc, .cxx, .hpp, .hxx files. Use when working with C or C++ code that needs autocomplete, go-to-definition, find references, error detection, or refactoring support.
---

# clangd LSP

C/C++ language server integration providing comprehensive code intelligence through clangd (part of LLVM).

## Capabilities

- **Code intelligence**: Autocomplete, go-to-definition, find references
- **Error detection**: Real-time diagnostics for compilation errors
- **Formatting**: Code formatting with clang-format
- **Refactoring**: Rename symbols, extract function
- **Supported extensions**: `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.C`, `.H`

## Installation

### Via Homebrew (macOS)
```bash
brew install llvm
# Add to PATH
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"
```

### Via package manager (Linux)
```bash
# Ubuntu/Debian
sudo apt install clangd

# Fedora
sudo dnf install clang-tools-extra

# Arch Linux
sudo pacman -S clang
```

### Windows
```bash
winget install LLVM.LLVM
```

Or download from [LLVM releases](https://github.com/llvm/llvm-project/releases).

Verify installation:
```bash
clangd --version
```

## Usage

The language server runs automatically in LSP-compatible editors. For manual operations:

### Compile
```bash
gcc file.c -o output      # C
g++ file.cpp -o output    # C++
clang file.c -o output    # with clang
```

### Format code
```bash
clang-format -i file.cpp
```

### Static analysis
```bash
clang-tidy file.cpp -- -std=c++17
```

## Configuration

Create `.clangd` in project root:

```yaml
CompileFlags:
  Add: [-std=c++17, -Wall, -Wextra]
  Remove: [-W*]
Diagnostics:
  UnusedIncludes: Strict
  MissingIncludes: Strict
```

Or `compile_commands.json` for complex projects:
```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON .
# or
bear -- make
```

## Integration Pattern

When editing C/C++ code:
1. clangd uses `compile_commands.json` for project understanding
2. Run `clang-format` to format code
3. Use `clang-tidy` for static analysis
4. Compile with warnings enabled (`-Wall -Wextra`)

## Common Flags

**Compile flags:**
- `-std=c++17` - C++17 standard
- `-Wall -Wextra` - Enable warnings
- `-O2` - Optimization level
- `-g` - Debug symbols
- `-I<path>` - Include path
- `-L<path>` - Library path

**clang-tidy checks:**
```bash
clang-tidy file.cpp --checks='*' --
clang-tidy file.cpp --fix --  # Auto-fix
```

## More Information

- [clangd Website](https://clangd.llvm.org/)
- [Getting Started Guide](https://clangd.llvm.org/installation)
- [LLVM Project](https://llvm.org/)
