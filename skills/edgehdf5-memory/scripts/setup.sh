#!/usr/bin/env bash
set -euo pipefail

# Install edgehdf5 CLI from crates.io
if command -v edgehdf5 &>/dev/null; then
    echo "edgehdf5 already installed: $(edgehdf5 --version)"
else
    echo "Installing edgehdf5-cli from crates.io..."
    cargo install edgehdf5-cli
    echo "Installed: $(edgehdf5 --version)"
fi
