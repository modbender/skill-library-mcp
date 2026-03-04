#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/../"
node -e "
import { checkAllPrices } from './src/price-check.js';
await checkAllPrices();
console.log('Prices checked');
"