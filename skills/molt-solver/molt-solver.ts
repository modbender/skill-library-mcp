/**
 * 🦞 Molt-Solver - Automated Moltbook Verification
 * 
 * Tooling to parse and solve those annoying lobster math problems.
 */

import * as fs from 'fs';
import * as path from 'path';

const BASE_URL = 'https://www.moltbook.com/api/v1';
const CRED_PATH = path.join(process.env.HOME || '', '.config/moltbook/credentials.json');

// ============================================
// Logic
// ============================================

/**
 * Since Moltbook challenges are mixed-case strings with words representing numbers,
 * we use a mapping to normalize them.
 */
const NUM_WORDS: Record<string, number> = {
  zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
  eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17,
  eighteen: 18, nineteen: 19, twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60,
  seventy: 70, eighty: 80, ninety: 90
};

export function solveChallenge(challenge: string): string {
  const normalized = challenge.toLowerCase().replace(/[^a-z\s*]/g, ' ');
  const words = normalized.split(/\s+/).filter(Boolean);
  
  let numbers: number[] = [];
  let currentNum = 0;
  
  // Basic number parser for compound words like "ninety four"
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (NUM_WORDS[word] !== undefined) {
      const val = NUM_WORDS[word];
      if (val >= 20 && i + 1 < words.length && NUM_WORDS[words[i+1]] < 10) {
        numbers.push(val + NUM_WORDS[words[i+1]]);
        i++;
      } else {
        numbers.push(val);
      }
    }
  }

  // Operation detection
  let result = 0;
  const isMultiplication = challenge.includes('*');
  const isSubtraction = normalized.includes('los es') || normalized.includes('slows by') || normalized.includes('remains');
  
  if (isMultiplication && numbers.length >= 1) {
    // Usually "* TWO claws"
    const factor = numbers[numbers.length - 1];
    result = numbers[0] * factor;
  } else if (isSubtraction && numbers.length >= 2) {
    result = numbers[0] - numbers[1];
  } else if (numbers.length >= 2) {
    // Default to addition for "adds", "increases", "total", etc.
    result = numbers.reduce((a, b) => a + b, 0);
  } else if (numbers.length === 1) {
    result = numbers[0];
  }

  return result.toFixed(2);
}

export async function verify(code: string, answer: string): Promise<any> {
  if (!fs.existsSync(CRED_PATH)) throw new Error('Not logged in to Moltbook');
  const creds = JSON.parse(fs.readFileSync(CRED_PATH, 'utf-8'));
  
  const res = await fetch(`${BASE_URL}/verify`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${creds.api_key}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ verification_code: code, answer })
  });
  
  return await res.json();
}
