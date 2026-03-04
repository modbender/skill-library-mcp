#!/bin/bash
# Generate a TEE attestation quote from the Phala CVM environment.
#
# Usage: tee-attest.sh [custom-data]
#
# Arguments:
#   custom-data  - Optional hex string to embed as user data in the quote.
#                  Defaults to the agent's derived public key.
#
# Environment:
#   DSTACK_SIMULATOR_ENDPOINT  - dstack proxy endpoint (set automatically in CVM)
#
# Output: JSON to stdout with { success, inTee, quote, publicKey }
#
# When run outside a TEE, returns { success: true, inTee: false }.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec npx tsx "${SCRIPT_DIR}/helpers/tee-attest.ts" "$@"
