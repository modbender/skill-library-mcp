#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/../"
node -e "
import { generateInterchange } from './src/interchange.js';
generateInterchange();
console.log('Interchange refreshed');
"