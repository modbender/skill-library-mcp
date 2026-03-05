#!/usr/bin/env bash
# Install aperture from source.
#
# Usage:
#   install.sh                          # Install latest
#   install.sh --version v0.3.3-beta    # Specific version

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
            echo "Install aperture L402 reverse proxy."
            echo ""
            echo "Options:"
            echo "  --version VERSION  Go module version (e.g., v0.3.3-beta)"
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

echo "=== Installing Aperture ==="
echo ""

# Verify Go is installed.
if ! command -v go &>/dev/null; then
    echo "Error: Go is not installed." >&2
    echo "Install Go from https://go.dev/dl/" >&2
    exit 1
fi

echo "Go version: $(go version | grep -oE 'go[0-9]+\.[0-9]+')"
echo ""

# Install aperture.
echo "Installing aperture..."
go install "github.com/lightninglabs/aperture/cmd/aperture${VERSION}"
echo "Done."
echo ""

# Verify installation.
if command -v aperture &>/dev/null; then
    echo "aperture installed: $(which aperture)"
else
    echo "Warning: aperture not found on PATH." >&2
    echo "Ensure \$GOPATH/bin is in your PATH." >&2
    echo "  export PATH=\$PATH:\$(go env GOPATH)/bin" >&2
fi

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Setup config: skills/aperture/scripts/setup.sh"
echo "  2. Start:        skills/aperture/scripts/start.sh"
