#!/bin/bash
# install.sh

# This script builds and installs the soccer-cli binary.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building soccer-cli..."

# Build the Go binary. This creates a 'soccer-cli' executable in the current directory.
go build -o soccer-cli main.go

# Define the installation directory.
# We'll use ~/.local/bin, which is a common place for user-installed executables.
# Make sure to add this directory to your shell's PATH if it isn't already.
INSTALL_DIR="$HOME/.local/bin"

# Create the installation directory if it doesn't exist.
mkdir -p "$INSTALL_DIR"

# Move the binary to the installation directory.
mv soccer-cli "$INSTALL_DIR/"

echo "soccer-cli installed successfully to $INSTALL_DIR"
echo "Please ensure '$INSTALL_DIR' is in your PATH."
