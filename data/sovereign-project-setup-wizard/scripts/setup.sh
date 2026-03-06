#!/usr/bin/env bash
#
# Project Setup Wizard - setup.sh
# Interactive project scaffolding for Node.js, Python, Go, and Rust.
#
# Usage: ./setup.sh [OPTIONS]
#
# Options:
#   --name <name>           Project name (required in non-interactive mode)
#   --lang <language>       Language: nodejs, python, go, rust
#   --description <text>    Short project description
#   --author <name>         Author name
#   --email <email>         Author email
#   --license <type>        License: mit, apache2, gpl3 (default: mit)
#   --ci <provider>         CI provider: github, gitlab, circleci (default: github)
#   --docker                Include Docker files (default: on)
#   --no-docker             Disable Docker file generation
#   --git-init              Initialize git repository (default: on)
#   --no-git-init           Skip git initialization
#   --output-dir <path>     Parent directory for the project (default: .)
#   --dry-run               Show what would be created without writing files
#   --verbose               Show detailed output during generation
#   --help                  Show this help message
#
# Author: Sovereign AI (Taylor)
# License: MIT
# Version: 1.0.0

set -euo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────

PROJECT_NAME="${PSW_NAME:-}"
LANGUAGE="${PSW_LANG:-}"
DESCRIPTION=""
AUTHOR_NAME="${PSW_AUTHOR:-}"
AUTHOR_EMAIL="${PSW_EMAIL:-}"
LICENSE_TYPE="${PSW_LICENSE:-mit}"
CI_PROVIDER="${PSW_CI:-github}"
INCLUDE_DOCKER="${PSW_DOCKER:-true}"
GIT_INIT=true
OUTPUT_DIR="."
DRY_RUN=false
VERBOSE=false
INTERACTIVE=true
CURRENT_YEAR=$(date +%Y 2>/dev/null || echo "2026")
CURRENT_DATE=$(date +%Y-%m-%d 2>/dev/null || echo "2026-02-21")
FILES_CREATED=0
DIRS_CREATED=0

# ─── Argument Parsing ──────────────────────────────────────────────────────

show_help() {
    sed -n '3,/^$/s/^# \?//p' "$0"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name)        PROJECT_NAME="$2"; INTERACTIVE=false; shift 2 ;;
        --lang)        LANGUAGE="$2"; INTERACTIVE=false; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --author)      AUTHOR_NAME="$2"; shift 2 ;;
        --email)       AUTHOR_EMAIL="$2"; shift 2 ;;
        --license)     LICENSE_TYPE="$2"; shift 2 ;;
        --ci)          CI_PROVIDER="$2"; shift 2 ;;
        --docker)      INCLUDE_DOCKER=true; shift ;;
        --no-docker)   INCLUDE_DOCKER=false; shift ;;
        --git-init)    GIT_INIT=true; shift ;;
        --no-git-init) GIT_INIT=false; shift ;;
        --output-dir)  OUTPUT_DIR="$2"; shift 2 ;;
        --dry-run)     DRY_RUN=true; shift ;;
        --verbose)     VERBOSE=true; shift ;;
        --help|-h)     show_help ;;
        *)             echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ─── Helpers ────────────────────────────────────────────────────────────────

log() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "[INFO] $*"
    fi
}

create_dir() {
    local dir="$1"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [DIR]  $dir/"
    else
        mkdir -p "$dir"
        log "Created directory: $dir"
    fi
    DIRS_CREATED=$((DIRS_CREATED + 1))
}

create_file() {
    local filepath="$1"
    local content="$2"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [FILE] $filepath"
    else
        local dir
        dir=$(dirname "$filepath")
        mkdir -p "$dir"
        echo "$content" > "$filepath"
        echo "  Created: $filepath"
    fi
    FILES_CREATED=$((FILES_CREATED + 1))
}

# Convert project name to Python module name (underscores, lowercase)
to_python_module() {
    echo "$1" | tr '-' '_' | tr '[:upper:]' '[:lower:]'
}

# ─── Interactive Prompts ────────────────────────────────────────────────────

if [[ "$INTERACTIVE" == "true" ]]; then
    echo ""
    echo "  Project Setup Wizard v1.0.0"
    echo ""

    if [[ -z "$PROJECT_NAME" ]]; then
        read -rp "  ? Project name: " PROJECT_NAME
    fi
    if [[ -z "$LANGUAGE" ]]; then
        echo "  ? Language options: nodejs, python, go, rust"
        read -rp "  ? Language: " LANGUAGE
    fi
    if [[ -z "$DESCRIPTION" ]]; then
        read -rp "  ? Description: " DESCRIPTION
    fi
    if [[ -z "$AUTHOR_NAME" ]]; then
        AUTHOR_NAME=$(git config user.name 2>/dev/null || echo "")
        read -rp "  ? Author [$AUTHOR_NAME]: " input
        AUTHOR_NAME="${input:-$AUTHOR_NAME}"
    fi
    if [[ -z "$AUTHOR_EMAIL" ]]; then
        AUTHOR_EMAIL=$(git config user.email 2>/dev/null || echo "")
        read -rp "  ? Email [$AUTHOR_EMAIL]: " input
        AUTHOR_EMAIL="${input:-$AUTHOR_EMAIL}"
    fi

    read -rp "  ? License (mit/apache2/gpl3) [$LICENSE_TYPE]: " input
    LICENSE_TYPE="${input:-$LICENSE_TYPE}"

    read -rp "  ? CI/CD provider (github/gitlab/circleci) [$CI_PROVIDER]: " input
    CI_PROVIDER="${input:-$CI_PROVIDER}"

    read -rp "  ? Include Docker support? (y/n) [y]: " input
    if [[ "${input:-y}" == "n" ]]; then INCLUDE_DOCKER=false; fi

    read -rp "  ? Initialize git repository? (y/n) [y]: " input
    if [[ "${input:-y}" == "n" ]]; then GIT_INIT=false; fi

    echo ""
fi

# ─── Validation ─────────────────────────────────────────────────────────────

if [[ -z "$PROJECT_NAME" ]]; then
    echo "Error: Project name is required." >&2
    exit 1
fi

if [[ -z "$LANGUAGE" ]]; then
    echo "Error: Language is required." >&2
    exit 1
fi

case "$LANGUAGE" in
    nodejs|python|go|rust) ;;
    *)
        echo "Error: Unsupported language '$LANGUAGE'. Choose: nodejs, python, go, rust" >&2
        exit 1
        ;;
esac

PROJECT_DIR="$OUTPUT_DIR/$PROJECT_NAME"

if [[ -d "$PROJECT_DIR" ]] && [[ "$DRY_RUN" == "false" ]]; then
    echo "Error: Directory '$PROJECT_DIR' already exists." >&2
    exit 1
fi

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would create the following structure:"
    echo ""
fi

echo "  Creating project structure..."
echo ""

# ─── License File ───────────────────────────────────────────────────────────

generate_license() {
    case "$LICENSE_TYPE" in
        mit)
            cat <<EOF
MIT License

Copyright (c) $CURRENT_YEAR $AUTHOR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
            ;;
        apache2)
            cat <<EOF
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Copyright $CURRENT_YEAR $AUTHOR_NAME
EOF
            ;;
        gpl3)
            cat <<EOF
Copyright (C) $CURRENT_YEAR $AUTHOR_NAME

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
EOF
            ;;
    esac
}

# ─── .editorconfig ──────────────────────────────────────────────────────────

generate_editorconfig() {
    cat <<'EOF'
root = true

[*]
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
indent_style = space
indent_size = 4

[*.{js,jsx,ts,tsx,json,yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
EOF
}

# ─── README ─────────────────────────────────────────────────────────────────

generate_readme() {
    cat <<EOF
# $PROJECT_NAME

${DESCRIPTION:-A new $LANGUAGE project.}

## Getting Started

### Prerequisites
EOF

    case "$LANGUAGE" in
        nodejs)
            cat <<'EOF'

- Node.js >= 18
- npm >= 9

### Installation

```bash
npm install
```

### Running

```bash
npm start
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
```
EOF
            ;;
        python)
            cat <<'EOF'

- Python >= 3.10
- pip

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running

```bash
python -m src.main
```

### Testing

```bash
pytest
```

### Linting

```bash
ruff check .
black --check .
```
EOF
            ;;
        go)
            cat <<'EOF'

- Go >= 1.22

### Installation

```bash
go mod download
```

### Running

```bash
go run ./cmd/...
```

### Testing

```bash
go test ./...
```

### Linting

```bash
golangci-lint run
```
EOF
            ;;
        rust)
            cat <<'EOF'

- Rust >= 1.76 (install via https://rustup.rs)

### Installation

```bash
cargo build
```

### Running

```bash
cargo run
```

### Testing

```bash
cargo test
```

### Linting

```bash
cargo clippy
cargo fmt --check
```
EOF
            ;;
    esac

    cat <<EOF

## Project Structure

\`\`\`
$(generate_tree_preview)
\`\`\`

## License

This project is licensed under the ${LICENSE_TYPE^^} License. See [LICENSE](LICENSE) for details.

## Author

$AUTHOR_NAME ${AUTHOR_EMAIL:+<$AUTHOR_EMAIL>}
EOF
}

# ─── Tree Preview ───────────────────────────────────────────────────────────

generate_tree_preview() {
    case "$LANGUAGE" in
        nodejs)
            cat <<EOF
$PROJECT_NAME/
  src/
    index.js
    lib/
      utils.js
  tests/
    index.test.js
  .gitignore
  package.json
  README.md
EOF
            ;;
        python)
            local module
            module=$(to_python_module "$PROJECT_NAME")
            cat <<EOF
$PROJECT_NAME/
  src/
    ${module}/
      __init__.py
      main.py
      utils.py
  tests/
    __init__.py
    test_main.py
  .gitignore
  pyproject.toml
  README.md
EOF
            ;;
        go)
            cat <<EOF
$PROJECT_NAME/
  cmd/
    ${PROJECT_NAME}/
      main.go
  internal/
    app/
      app.go
  pkg/
    utils/
      utils.go
  .gitignore
  go.mod
  Makefile
  README.md
EOF
            ;;
        rust)
            cat <<EOF
$PROJECT_NAME/
  src/
    main.rs
    lib.rs
  tests/
    integration_test.rs
  .gitignore
  Cargo.toml
  README.md
EOF
            ;;
    esac
}

# ─── .gitignore ─────────────────────────────────────────────────────────────

generate_gitignore() {
    # Common entries
    cat <<'EOF'
# OS files
.DS_Store
Thumbs.db
*.swp
*.swo
*~

# IDE files
.idea/
.vscode/
*.sublime-project
*.sublime-workspace

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/
EOF

    # Language-specific
    case "$LANGUAGE" in
        nodejs)
            cat <<'EOF'

# Node.js
node_modules/
dist/
build/
coverage/
.nyc_output/
*.tgz
.npm
.eslintcache
.parcel-cache
EOF
            ;;
        python)
            cat <<'EOF'

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/
dist/
build/
*.egg-info/
*.egg
.mypy_cache/
.ruff_cache/
.pytest_cache/
htmlcov/
.coverage
.coverage.*
EOF
            ;;
        go)
            cat <<'EOF'

# Go
/vendor/
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
go.work
EOF
            ;;
        rust)
            cat <<'EOF'

# Rust
/target/
**/*.rs.bk
Cargo.lock
EOF
            ;;
    esac
}

# ─── .dockerignore ──────────────────────────────────────────────────────────

generate_dockerignore() {
    cat <<'EOF'
.git
.gitignore
.dockerignore
.env
.env.*
*.md
LICENSE
.idea/
.vscode/
EOF

    case "$LANGUAGE" in
        nodejs)  echo "node_modules/"; echo "coverage/"; echo "dist/" ;;
        python)  echo "__pycache__/"; echo ".venv/"; echo ".pytest_cache/" ;;
        go)      echo "vendor/" ;;
        rust)    echo "target/" ;;
    esac
}

# ─── CI/CD Configs ──────────────────────────────────────────────────────────

generate_github_actions() {
    case "$LANGUAGE" in
        nodejs)
            cat <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm

      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build --if-present
EOF
            ;;
        python)
            cat <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: |
          ruff check .
          black --check .

      - name: Test
        run: pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
EOF
            ;;
        go)
            cat <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        go-version: ["1.21", "1.22"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Go ${{ matrix.go-version }}
        uses: actions/setup-go@v5
        with:
          go-version: ${{ matrix.go-version }}

      - name: Lint
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest

      - name: Test
        run: go test -race -coverprofile=coverage.out ./...

      - name: Build
        run: go build -v ./...
EOF
            ;;
        rust)
            cat <<'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        rust: [stable, beta]

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust ${{ matrix.rust }}
        uses: dtolnay/rust-toolchain@master
        with:
          toolchain: ${{ matrix.rust }}
          components: clippy, rustfmt

      - name: Cache cargo
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

      - name: Format check
        run: cargo fmt --all -- --check

      - name: Clippy
        run: cargo clippy --all-targets -- -D warnings

      - name: Test
        run: cargo test --verbose

      - name: Build
        run: cargo build --verbose
EOF
            ;;
    esac
}

generate_gitlab_ci() {
    case "$LANGUAGE" in
        nodejs)
            cat <<EOF
image: node:20-alpine

stages:
  - lint
  - test
  - build

cache:
  paths:
    - node_modules/

install:
  stage: .pre
  script:
    - npm ci

lint:
  stage: lint
  script:
    - npm run lint

test:
  stage: test
  script:
    - npm test
  coverage: /All files[^|]*\|[^|]*\s+([\d\.]+)/

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
EOF
            ;;
        python)
            cat <<EOF
image: python:3.12-slim

stages:
  - lint
  - test

cache:
  paths:
    - .venv/

before_script:
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -r requirements.txt -r requirements-dev.txt

lint:
  stage: lint
  script:
    - ruff check .
    - black --check .

test:
  stage: test
  script:
    - pytest --cov --cov-report=term
  coverage: /TOTAL.*\s+(\d+)%/
EOF
            ;;
        go)
            cat <<EOF
image: golang:1.22

stages:
  - lint
  - test
  - build

lint:
  stage: lint
  script:
    - go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    - golangci-lint run

test:
  stage: test
  script:
    - go test -race -coverprofile=coverage.out ./...
    - go tool cover -func=coverage.out
  coverage: /total:\s+\(statements\)\s+(\d+.\d+)%/

build:
  stage: build
  script:
    - go build -v ./...
EOF
            ;;
        rust)
            cat <<EOF
image: rust:1.76

stages:
  - lint
  - test
  - build

cache:
  paths:
    - target/
    - .cargo/

lint:
  stage: lint
  script:
    - rustup component add clippy rustfmt
    - cargo fmt --all -- --check
    - cargo clippy --all-targets -- -D warnings

test:
  stage: test
  script:
    - cargo test --verbose

build:
  stage: build
  script:
    - cargo build --release
  artifacts:
    paths:
      - target/release/
EOF
            ;;
    esac
}

generate_circleci() {
    case "$LANGUAGE" in
        nodejs)
            cat <<EOF
version: 2.1

orbs:
  node: circleci/node@5

jobs:
  build-and-test:
    executor:
      name: node/default
      tag: '20'
    steps:
      - checkout
      - node/install-packages
      - run: npm run lint
      - run: npm test
      - run: npm run build

workflows:
  main:
    jobs:
      - build-and-test
EOF
            ;;
        python)
            cat <<EOF
version: 2.1

orbs:
  python: circleci/python@2

jobs:
  build-and-test:
    executor:
      name: python/default
      tag: '3.12'
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: black --check .
      - run: pytest --cov

workflows:
  main:
    jobs:
      - build-and-test
EOF
            ;;
        go)
            cat <<EOF
version: 2.1

orbs:
  go: circleci/go@1

jobs:
  build-and-test:
    executor:
      name: go/default
      tag: '1.22'
    steps:
      - checkout
      - go/load-cache
      - go/mod-download
      - go/save-cache
      - run: go test -race ./...
      - run: go build -v ./...

workflows:
  main:
    jobs:
      - build-and-test
EOF
            ;;
        rust)
            cat <<EOF
version: 2.1

jobs:
  build-and-test:
    docker:
      - image: rust:1.76
    steps:
      - checkout
      - run: rustup component add clippy rustfmt
      - run: cargo fmt --all -- --check
      - run: cargo clippy --all-targets -- -D warnings
      - run: cargo test --verbose
      - run: cargo build --verbose

workflows:
  main:
    jobs:
      - build-and-test
EOF
            ;;
    esac
}

# ─── Dockerfile ─────────────────────────────────────────────────────────────

generate_dockerfile() {
    case "$LANGUAGE" in
        nodejs)
            cat <<'EOF'
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build 2>/dev/null || true

# Production stage
FROM node:20-alpine

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app .

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "src/index.js"]
EOF
            ;;
        python)
            cat <<EOF
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production stage
FROM python:3.12-slim

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "src.$(to_python_module "$PROJECT_NAME").main"]
EOF
            ;;
        go)
            cat <<EOF
# Build stage
FROM golang:1.22-alpine AS builder

RUN apk add --no-cache git

WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-w -s' -o /app/bin/server ./cmd/${PROJECT_NAME}

# Production stage
FROM scratch

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/bin/server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
EOF
            ;;
        rust)
            cat <<EOF
# Build stage
FROM rust:1.76-slim AS builder

WORKDIR /app
COPY Cargo.toml Cargo.lock* ./

# Cache dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm src/main.rs

COPY . .
RUN touch src/main.rs && cargo build --release

# Production stage
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --from=builder /app/target/release/${PROJECT_NAME} /usr/local/bin/app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["app"]
EOF
            ;;
    esac
}

generate_docker_compose() {
    cat <<EOF
version: "3.8"

services:
  app:
    build: .
    ports:
      - "\${PORT:-8080}:8080"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
EOF
}

# ─── Language-Specific Source Files ─────────────────────────────────────────

create_nodejs_project() {
    local base="$PROJECT_DIR"

    # package.json
    create_file "$base/package.json" "{
  \"name\": \"$PROJECT_NAME\",
  \"version\": \"1.0.0\",
  \"description\": \"${DESCRIPTION:-A Node.js project}\",
  \"main\": \"src/index.js\",
  \"scripts\": {
    \"start\": \"node src/index.js\",
    \"dev\": \"node --watch src/index.js\",
    \"test\": \"node --test tests/\",
    \"lint\": \"eslint src/ tests/\",
    \"format\": \"prettier --write .\",
    \"build\": \"echo 'No build step required'\"
  },
  \"keywords\": [],
  \"author\": \"$AUTHOR_NAME ${AUTHOR_EMAIL:+<$AUTHOR_EMAIL>}\",
  \"license\": \"${LICENSE_TYPE^^}\",
  \"devDependencies\": {
    \"eslint\": \"^8.56.0\",
    \"prettier\": \"^3.2.0\"
  }
}"

    # ESLint config
    create_file "$base/.eslintrc.json" '{
  "env": {
    "node": true,
    "es2022": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "off",
    "semi": ["error", "always"],
    "quotes": ["error", "single"]
  }
}'

    # Prettier config
    create_file "$base/.prettierrc" '{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}'

    # Source files
    create_file "$base/src/index.js" "const { greet } = require('./lib/utils');

const main = () => {
  const message = greet('World');
  console.log(message);
  console.log('$PROJECT_NAME is running.');
};

main();

module.exports = { main };
"

    create_file "$base/src/lib/utils.js" "/**
 * Generate a greeting message.
 * @param {string} name - The name to greet.
 * @returns {string} The greeting message.
 */
const greet = (name) => {
  return \`Hello, \${name}!\`;
};

/**
 * Sleep for a given number of milliseconds.
 * @param {number} ms - Milliseconds to sleep.
 * @returns {Promise<void>}
 */
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

module.exports = { greet, sleep };
"

    # Test file
    create_file "$base/tests/index.test.js" "const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { greet, sleep } = require('../src/lib/utils');

describe('utils', () => {
  describe('greet', () => {
    it('should return a greeting message', () => {
      const result = greet('World');
      assert.strictEqual(result, 'Hello, World!');
    });

    it('should handle empty string', () => {
      const result = greet('');
      assert.strictEqual(result, 'Hello, !');
    });
  });

  describe('sleep', () => {
    it('should resolve after the given time', async () => {
      const start = Date.now();
      await sleep(50);
      const elapsed = Date.now() - start;
      assert.ok(elapsed >= 45, 'Should have waited at least 45ms');
    });
  });
});
"
}

create_python_project() {
    local base="$PROJECT_DIR"
    local module
    module=$(to_python_module "$PROJECT_NAME")

    # pyproject.toml
    create_file "$base/pyproject.toml" "[build-system]
requires = [\"setuptools>=68.0\", \"wheel\"]
build-backend = \"setuptools.backends._legacy:_Backend\"

[project]
name = \"$PROJECT_NAME\"
version = \"1.0.0\"
description = \"${DESCRIPTION:-A Python project}\"
authors = [{name = \"$AUTHOR_NAME\", email = \"$AUTHOR_EMAIL\"}]
license = {text = \"${LICENSE_TYPE^^}\"}
requires-python = \">=3.10\"
readme = \"README.md\"

[tool.pytest.ini_options]
testpaths = [\"tests\"]
pythonpath = [\"src\"]

[tool.black]
line-length = 100
target-version = [\"py310\"]

[tool.ruff]
line-length = 100
target-version = \"py310\"

[tool.mypy]
python_version = \"3.10\"
strict = true
"

    # setup.cfg
    create_file "$base/setup.cfg" "[metadata]
name = $PROJECT_NAME
version = 1.0.0

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.10

[options.packages.find]
where = src
"

    # Requirements
    create_file "$base/requirements.txt" "# Production dependencies
"

    create_file "$base/requirements-dev.txt" "# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
black>=24.0.0
ruff>=0.2.0
mypy>=1.8.0
"

    # Source files
    create_file "$base/src/${module}/__init__.py" "\"\"\"${DESCRIPTION:-$PROJECT_NAME package.}\"\"\"

__version__ = \"1.0.0\"
"

    create_file "$base/src/${module}/main.py" "\"\"\"Main entry point for $PROJECT_NAME.\"\"\"

from ${module}.utils import greet


def main() -> None:
    \"\"\"Run the main application logic.\"\"\"
    message = greet(\"World\")
    print(message)
    print(f\"$PROJECT_NAME is running.\")


if __name__ == \"__main__\":
    main()
"

    create_file "$base/src/${module}/utils.py" "\"\"\"Utility functions for $PROJECT_NAME.\"\"\"


def greet(name: str) -> str:
    \"\"\"Generate a greeting message.

    Args:
        name: The name to greet.

    Returns:
        The greeting message.
    \"\"\"
    return f\"Hello, {name}!\"


def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.

    Args:
        a: First number.
        b: Second number.

    Returns:
        The sum of a and b.
    \"\"\"
    return a + b
"

    # Tests
    create_file "$base/tests/__init__.py" ""

    create_file "$base/tests/test_main.py" "\"\"\"Tests for $PROJECT_NAME.\"\"\"

from ${module}.utils import greet, add


class TestGreet:
    def test_greet_with_name(self) -> None:
        assert greet(\"World\") == \"Hello, World!\"

    def test_greet_with_empty_string(self) -> None:
        assert greet(\"\") == \"Hello, !\"


class TestAdd:
    def test_add_positive_numbers(self) -> None:
        assert add(2, 3) == 5

    def test_add_negative_numbers(self) -> None:
        assert add(-1, -2) == -3

    def test_add_zero(self) -> None:
        assert add(0, 0) == 0
"
}

create_go_project() {
    local base="$PROJECT_DIR"
    local module_path="github.com/${AUTHOR_NAME:-user}/${PROJECT_NAME}"

    # go.mod
    create_file "$base/go.mod" "module $module_path

go 1.22
"

    # Makefile
    create_file "$base/Makefile" ".PHONY: build run test lint clean

BINARY=bin/${PROJECT_NAME}

build:
	go build -o \$(BINARY) ./cmd/${PROJECT_NAME}

run:
	go run ./cmd/${PROJECT_NAME}

test:
	go test -race -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

lint:
	golangci-lint run

clean:
	rm -rf bin/ coverage.out
"

    # golangci-lint config
    create_file "$base/.golangci.yml" "linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports
    - misspell

linters-settings:
  errcheck:
    check-type-assertions: true
  govet:
    check-shadowing: true

run:
  timeout: 5m
"

    # Source files
    create_file "$base/cmd/${PROJECT_NAME}/main.go" "package main

import (
	\"fmt\"

	\"$module_path/internal/app\"
)

func main() {
	message := app.Greet(\"World\")
	fmt.Println(message)
	fmt.Println(\"$PROJECT_NAME is running.\")
}
"

    create_file "$base/internal/app/app.go" "package app

import \"fmt\"

// Greet generates a greeting message for the given name.
func Greet(name string) string {
	return fmt.Sprintf(\"Hello, %s!\", name)
}

// Add returns the sum of two integers.
func Add(a, b int) int {
	return a + b
}
"

    create_file "$base/internal/app/app_test.go" "package app

import \"testing\"

func TestGreet(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{\"with name\", \"World\", \"Hello, World!\"},
		{\"empty string\", \"\", \"Hello, !\"},
		{\"with spaces\", \"Go Dev\", \"Hello, Go Dev!\"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := Greet(tt.input)
			if result != tt.expected {
				t.Errorf(\"Greet(%q) = %q, want %q\", tt.input, result, tt.expected)
			}
		})
	}
}

func TestAdd(t *testing.T) {
	tests := []struct {
		name     string
		a, b     int
		expected int
	}{
		{\"positive\", 2, 3, 5},
		{\"negative\", -1, -2, -3},
		{\"zero\", 0, 0, 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := Add(tt.a, tt.b)
			if result != tt.expected {
				t.Errorf(\"Add(%d, %d) = %d, want %d\", tt.a, tt.b, result, tt.expected)
			}
		})
	}
}
"

    create_file "$base/pkg/utils/utils.go" "// Package utils provides general utility functions.
package utils

import (
	\"strings\"
)

// Capitalize returns the string with the first letter uppercased.
func Capitalize(s string) string {
	if len(s) == 0 {
		return s
	}
	return strings.ToUpper(s[:1]) + s[1:]
}
"
}

create_rust_project() {
    local base="$PROJECT_DIR"

    # Cargo.toml
    create_file "$base/Cargo.toml" "[package]
name = \"$PROJECT_NAME\"
version = \"1.0.0\"
edition = \"2021\"
description = \"${DESCRIPTION:-A Rust project}\"
authors = [\"$AUTHOR_NAME ${AUTHOR_EMAIL:+<$AUTHOR_EMAIL>}\"]
license = \"${LICENSE_TYPE^^}\"

[dependencies]

[dev-dependencies]
"

    # rustfmt.toml
    create_file "$base/rustfmt.toml" "max_width = 100
tab_spaces = 4
edition = \"2021\"
"

    # Source files
    create_file "$base/src/main.rs" "use ${PROJECT_NAME//-/_}::greet;

fn main() {
    let message = greet(\"World\");
    println!(\"{}\", message);
    println!(\"$PROJECT_NAME is running.\");
}
"

    create_file "$base/src/lib.rs" "/// Generate a greeting message.
///
/// # Arguments
///
/// * \`name\` - The name to greet.
///
/// # Examples
///
/// \`\`\`
/// use ${PROJECT_NAME//-/_}::greet;
/// assert_eq!(greet(\"World\"), \"Hello, World!\");
/// \`\`\`
pub fn greet(name: &str) -> String {
    format!(\"Hello, {}!\", name)
}

/// Add two numbers.
///
/// # Examples
///
/// \`\`\`
/// use ${PROJECT_NAME//-/_}::add;
/// assert_eq!(add(2, 3), 5);
/// \`\`\`
pub fn add(a: i64, b: i64) -> i64 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(greet(\"World\"), \"Hello, World!\");
    }

    #[test]
    fn test_greet_empty() {
        assert_eq!(greet(\"\"), \"Hello, !\");
    }

    #[test]
    fn test_add_positive() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_add_negative() {
        assert_eq!(add(-1, -2), -3);
    }

    #[test]
    fn test_add_zero() {
        assert_eq!(add(0, 0), 0);
    }
}
"

    # Integration test
    create_file "$base/tests/integration_test.rs" "use ${PROJECT_NAME//-/_}::{greet, add};

#[test]
fn test_greet_integration() {
    let result = greet(\"Integration\");
    assert!(result.contains(\"Integration\"));
    assert!(result.starts_with(\"Hello\"));
}

#[test]
fn test_add_integration() {
    assert_eq!(add(100, 200), 300);
}
"
}

# ─── Main Assembly ──────────────────────────────────────────────────────────

# Create base directory
create_dir "$PROJECT_DIR"

# Common files
create_file "$PROJECT_DIR/.gitignore" "$(generate_gitignore)"
create_file "$PROJECT_DIR/.editorconfig" "$(generate_editorconfig)"
create_file "$PROJECT_DIR/LICENSE" "$(generate_license)"
create_file "$PROJECT_DIR/README.md" "$(generate_readme)"

# CI/CD
case "$CI_PROVIDER" in
    github)
        create_dir "$PROJECT_DIR/.github/workflows"
        create_file "$PROJECT_DIR/.github/workflows/ci.yml" "$(generate_github_actions)"
        ;;
    gitlab)
        create_file "$PROJECT_DIR/.gitlab-ci.yml" "$(generate_gitlab_ci)"
        ;;
    circleci)
        create_dir "$PROJECT_DIR/.circleci"
        create_file "$PROJECT_DIR/.circleci/config.yml" "$(generate_circleci)"
        ;;
esac

# Docker
if [[ "$INCLUDE_DOCKER" == "true" ]]; then
    create_file "$PROJECT_DIR/Dockerfile" "$(generate_dockerfile)"
    create_file "$PROJECT_DIR/docker-compose.yml" "$(generate_docker_compose)"
    create_file "$PROJECT_DIR/.dockerignore" "$(generate_dockerignore)"
fi

# Language-specific scaffolding
case "$LANGUAGE" in
    nodejs) create_nodejs_project ;;
    python) create_python_project ;;
    go)     create_go_project ;;
    rust)   create_rust_project ;;
esac

# Git init
if [[ "$GIT_INIT" == "true" ]] && [[ "$DRY_RUN" == "false" ]]; then
    (cd "$PROJECT_DIR" && git init -q && git add -A && git commit -q -m "Initial commit" 2>/dev/null) || true
    echo ""
    echo "  Git repository initialized with initial commit."
fi

# ─── Summary ────────────────────────────────────────────────────────────────

echo ""
echo "  Done! $FILES_CREATED files created in $PROJECT_DIR/"
echo ""
echo "  Next steps:"

case "$LANGUAGE" in
    nodejs)
        echo "    cd $PROJECT_NAME"
        echo "    npm install"
        echo "    npm start"
        ;;
    python)
        echo "    cd $PROJECT_NAME"
        echo "    python -m venv .venv"
        echo "    source .venv/bin/activate"
        echo "    pip install -r requirements-dev.txt"
        echo "    pytest"
        ;;
    go)
        echo "    cd $PROJECT_NAME"
        echo "    make build"
        echo "    make run"
        ;;
    rust)
        echo "    cd $PROJECT_NAME"
        echo "    cargo build"
        echo "    cargo run"
        ;;
esac

echo ""
