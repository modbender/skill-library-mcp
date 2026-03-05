#!/usr/bin/env bash
# Install lnget from source.
#
# Usage:
#   install.sh                       # Install latest
#   install.sh --version v0.1.0      # Specific version

set -e

VERSION=""

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="@$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: install.sh [--version VERSION]"
            echo ""
            echo "Install lnget Lightning-native HTTP client."
            echo ""
            echo "Options:"
            echo "  --version VERSION  Go module version"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Default to @latest when no version specified.
VERSION="${VERSION:-@latest}"

echo "=== Installing lnget ==="
echo ""

# Verify Go is installed.
if ! command -v go &>/dev/null; then
    echo "Error: Go is not installed." >&2
    echo "Install Go from https://go.dev/dl/" >&2
    exit 1
fi

echo "Go version: $(go version | grep -oE 'go[0-9]+\.[0-9]+')"
echo ""

# Install lnget.
echo "Installing lnget..."
go install "github.com/lightninglabs/lnget/cmd/lnget${VERSION}"
echo "Done."
echo ""

# Verify installation.
if command -v lnget &>/dev/null; then
    echo "lnget installed: $(which lnget)"
else
    echo "Warning: lnget not found on PATH." >&2
    echo "Ensure \$GOPATH/bin is in your PATH." >&2
    echo "  export PATH=\$PATH:\$(go env GOPATH)/bin" >&2
fi

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Initialize config: lnget config init"
echo "  2. Check LN status:   lnget ln status"
echo "  3. Fetch a URL:        lnget https://example.com"
