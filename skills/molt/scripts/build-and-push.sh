#!/bin/bash
# Build and push MoltFundMe Docker images for linux/amd64 (production VM).
# Run from repo root. Requires: docker login ghcr.io -u sahanico
#
# Usage:
#   ./scripts/build-and-push.sh v1.0.0    # Build, tag, and push with version
#   ./scripts/build-and-push.sh            # Build and push as :latest only (no version tag)
set -e

REGISTRY="ghcr.io/sahanico/moltfundme"
VERSION="${1:-}"

if [ -n "$VERSION" ]; then
    # Validate version format (vX.Y.Z)
    if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Version must be in format vX.Y.Z (e.g. v1.0.0)"
        exit 1
    fi
    echo "=== Building release $VERSION ==="
else
    echo "=== Building :latest (no version tag) ==="
fi

PLATFORMS="linux/amd64,linux/arm64"

# Ensure buildx builder exists
if ! docker buildx inspect moltbuilder &>/dev/null; then
    echo "Creating buildx builder..."
    docker buildx create --name moltbuilder --use
else
    docker buildx use moltbuilder
fi

if [ -n "$VERSION" ]; then
    echo "Building & pushing api (${PLATFORMS})..."
    docker buildx build --platform "${PLATFORMS}" \
        -t "${REGISTRY}/api:latest" \
        -t "${REGISTRY}/api:${VERSION}" \
        --push ./api

    echo "Building & pushing web (${PLATFORMS})..."
    docker buildx build --platform "${PLATFORMS}" \
        -t "${REGISTRY}/web:latest" \
        -t "${REGISTRY}/web:${VERSION}" \
        --push ./web
else
    echo "Building & pushing api (${PLATFORMS})..."
    docker buildx build --platform "${PLATFORMS}" \
        -t "${REGISTRY}/api:latest" \
        --push ./api

    echo "Building & pushing web (${PLATFORMS})..."
    docker buildx build --platform "${PLATFORMS}" \
        -t "${REGISTRY}/web:latest" \
        --push ./web
fi

# Create and push git tag if versioned
if [ -n "$VERSION" ]; then
    echo "Creating git tag ${VERSION}..."
    git tag -a "$VERSION" -m "Release ${VERSION}"
    git push origin "$VERSION"
    echo ""
    echo "=== Released ${VERSION} ==="
    echo "Images: ${REGISTRY}/api:${VERSION}, ${REGISTRY}/web:${VERSION}"
    echo "Git tag: ${VERSION}"
else
    echo ""
    echo "=== Pushed :latest ==="
fi

echo ""
echo "Next: SSH into VM and run ./scripts/deploy-prod.sh ${VERSION:-}"
