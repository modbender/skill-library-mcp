#!/usr/bin/env bash
# Install Lightning Terminal (litd) — bundles lnd, loop, pool, tapd, faraday.
#
# Default: pulls the pre-built Docker image (fast, no Go required).
# Fallback: --source builds lnd from source (requires Go 1.21+).
#
# Usage:
#   install.sh                              # Docker pull (default)
#   install.sh --version v0.17.0-alpha      # Specific version
#   install.sh --source                     # Build lnd from source
#   install.sh --source --version v0.20.0-beta

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSIONS_FILE="$SCRIPT_DIR/../../../versions.env"

# Source pinned versions.
if [ -f "$VERSIONS_FILE" ]; then
    source "$VERSIONS_FILE"
fi

VERSION=""
SOURCE=false
BUILD_TAGS="signrpc walletrpc chainrpc invoicesrpc routerrpc peersrpc kvdb_sqlite neutrinorpc"

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --source)
            SOURCE=true
            shift
            ;;
        --tags)
            BUILD_TAGS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: install.sh [options]"
            echo ""
            echo "Install Lightning Terminal (litd) for agent operation."
            echo ""
            echo "Default: pulls the pre-built Docker image."
            echo ""
            echo "Options:"
            echo "  --version VERSION  Image tag or git tag (default: from versions.env)"
            echo "  --source           Build lnd from source instead of pulling Docker image"
            echo "  --tags TAGS        Build tags for --source mode"
            echo ""
            echo "Docker mode (default):"
            echo "  Pulls lightninglabs/lightning-terminal:VERSION"
            echo "  Includes: litd, lncli, litcli, loop, pool, tapcli, frcli"
            echo ""
            echo "Source mode (--source):"
            echo "  Clones and builds lnd + lncli from source (requires Go 1.21+)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [ "$SOURCE" = true ]; then
    # --- Source build mode: clone and build lnd from source ---
    echo "=== Installing lnd from source ==="
    echo ""

    # Verify Go is installed.
    if ! command -v go &>/dev/null; then
        echo "Error: Go is not installed." >&2
        echo "Install Go from https://go.dev/dl/" >&2
        exit 1
    fi

    GO_VERSION=$(go version | grep -oE 'go[0-9]+\.[0-9]+' | head -1)
    echo "Go version: $GO_VERSION"
    echo "Build tags: $BUILD_TAGS"
    echo ""

    # Use LND_VERSION from versions.env if no --version given.
    SOURCE_VERSION="${VERSION:-${LND_VERSION:-}}"

    # Clone lnd into a temp directory and build from source.
    TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR" EXIT

    echo "Cloning lnd..."
    git clone --quiet https://github.com/lightningnetwork/lnd.git "$TMPDIR/lnd"

    cd "$TMPDIR/lnd"

    # Checkout specific version if requested, otherwise use latest tag.
    if [ -n "$SOURCE_VERSION" ]; then
        echo "Checking out $SOURCE_VERSION..."
        git checkout --quiet "$SOURCE_VERSION"
    else
        LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
        if [ -n "$LATEST_TAG" ]; then
            echo "Using latest tag: $LATEST_TAG"
            git checkout --quiet "$LATEST_TAG"
        else
            echo "Using HEAD (no tags found)."
        fi
    fi
    echo ""

    GOBIN=$(go env GOPATH)/bin

    # Build lnd.
    echo "Building lnd..."
    go build -tags "$BUILD_TAGS" -o "$GOBIN/lnd" ./cmd/lnd
    echo "Done."

    # Build lncli.
    echo "Building lncli..."
    go build -tags "$BUILD_TAGS" -o "$GOBIN/lncli" ./cmd/lncli
    echo "Done."
    echo ""

    # Verify installation.
    if command -v lnd &>/dev/null; then
        echo "lnd installed: $(which lnd)"
        lnd --version 2>/dev/null || true
    else
        echo "Warning: lnd not found on PATH." >&2
        echo "Ensure \$GOPATH/bin is in your PATH." >&2
        echo "  export PATH=\$PATH:\$(go env GOPATH)/bin" >&2
    fi

    if command -v lncli &>/dev/null; then
        echo "lncli installed: $(which lncli)"
    else
        echo "Warning: lncli not found on PATH." >&2
    fi

    echo ""
    echo "Source installation complete."
    echo ""
    echo "Next steps:"
    echo "  1. Create wallet: skills/lnd/scripts/create-wallet.sh"
    echo "  2. Start lnd:     skills/lnd/scripts/start-lnd.sh --native"

else
    # --- Docker mode (default): pull pre-built image ---
    echo "=== Installing Lightning Terminal (litd) via Docker ==="
    echo ""

    # Verify Docker is available.
    if ! command -v docker &>/dev/null; then
        echo "Error: Docker is not installed." >&2
        echo "Install Docker from https://docs.docker.com/get-docker/" >&2
        echo "" >&2
        echo "Or use --source to build from source (requires Go 1.21+)." >&2
        exit 1
    fi

    IMAGE="${LITD_IMAGE:-lightninglabs/lightning-terminal}"
    TAG="${VERSION:-${LITD_VERSION:-v0.16.0-alpha}}"

    echo "Image: $IMAGE:$TAG"
    echo ""

    # Pull the image.
    echo "Pulling image..."
    docker pull "$IMAGE:$TAG"
    echo ""

    # Verify the image works.
    echo "Verifying installation..."
    docker run --rm "$IMAGE:$TAG" litd --version 2>/dev/null || true
    echo ""

    # Show available CLIs inside the container.
    echo "Available CLIs in container:"
    echo "  lncli   — lnd command-line interface"
    echo "  litcli  — Lightning Terminal CLI"
    echo "  loop    — Lightning Loop CLI (submarine swaps)"
    echo "  pool    — Lightning Pool CLI (channel marketplace)"
    echo "  tapcli  — Taproot Assets CLI"
    echo "  frcli   — Faraday CLI (channel analytics)"
    echo ""

    echo "Installation complete."
    echo ""
    echo "Next steps:"
    echo "  1. Start litd:     skills/lnd/scripts/docker-start.sh"
    echo "  2. Create wallet:  skills/lnd/scripts/create-wallet.sh"
    echo "  3. Check status:   skills/lnd/scripts/lncli.sh getinfo"
fi
