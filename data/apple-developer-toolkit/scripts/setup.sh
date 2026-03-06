#!/bin/bash
# Apple Developer Toolkit - Setup Script
# Installs appstore and swiftship CLIs via Homebrew.
#
# What this script does:
#   1. Checks that Homebrew is installed
#   2. Adds the Abdullah4AI/tap Homebrew tap (public GitHub repo)
#   3. Installs 'appstore' and 'swiftship' CLI binaries
#
# What this script does NOT do:
#   - Does not configure API keys or credentials
#   - Does not install Xcode or Xcode Command Line Tools
#   - Does not modify system files or require sudo
#
# Source code:
#   - appstore: https://github.com/Abdullah4AI/appstore
#   - swiftship: https://github.com/Abdullah4AI/swiftship
#   - Homebrew tap: https://github.com/Abdullah4AI/homebrew-tap

set -e

# Check if Homebrew is available
if ! command -v brew &>/dev/null; then
  echo "Homebrew required. Install: https://brew.sh"
  exit 1
fi

# Add tap if not already added
if ! brew tap | grep -q "abdullah4ai/tap"; then
  echo "Adding tap (source: https://github.com/Abdullah4AI/homebrew-tap)..."
  brew tap Abdullah4AI/tap
fi

# Install appstore CLI
if ! command -v appstore &>/dev/null; then
  echo "Installing appstore CLI..."
  brew install Abdullah4AI/tap/appstore
else
  echo "appstore CLI already installed: $(which appstore)"
fi

# Install swiftship CLI
if ! command -v swiftship &>/dev/null; then
  echo "Installing swiftship CLI..."
  brew install Abdullah4AI/tap/swiftship
else
  echo "swiftship CLI already installed: $(which swiftship)"
fi

echo ""
echo "Setup complete."
echo "  appstore --help    App Store Connect CLI"
echo "  swiftship --help   iOS App Builder"
echo ""
echo "Next steps:"
echo "  - For App Store Connect: run 'appstore auth login' with your API key"
echo "  - For iOS App Builder: run 'swiftship setup' to check prerequisites"
