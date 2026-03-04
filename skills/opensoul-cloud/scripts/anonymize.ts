#!/usr/bin/env npx ts-node
/**
 * Anonymize extracted soul data for safe sharing
 * Reads JSON from stdin, outputs anonymized JSON to stdout
 */

import * as readline from 'readline';
import * as fs from 'fs';
import * as path from 'path';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME!, '.openclaw/workspace');

// ============ PATTERN RULES ============

const PATTERNS: Array<{ regex: RegExp; replacement: string }> = [
  // Credentials
  { regex: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, replacement: '[EMAIL]' },
  { regex: /sk-[a-zA-Z0-9-]{20,}/g, replacement: '[API_KEY]' },
  { regex: /opensoul_sk_[a-zA-Z0-9]+/g, replacement: '[API_KEY]' },
  { regex: /api[_-]?key['":\s]+['"]?[a-zA-Z0-9-]{16,}['"]?/gi, replacement: '[API_KEY]' },
  { regex: /password['":\s]+['"]?[^\s'"]{4,}['"]?/gi, replacement: '[PASSWORD]' },
  
  // Paths
  { regex: /\/Users\/[a-zA-Z0-9_-]+\//g, replacement: '/Users/[USER]/' },
  { regex: /\/home\/[a-zA-Z0-9_-]+\//g, replacement: '/home/[USER]/' },
  { regex: /C:\\Users\\[a-zA-Z0-9_-]+\\/g, replacement: 'C:\\Users\\[USER]\\' },
  
  // IPs & phones
  { regex: /\b192\.168\.\d{1,3}\.\d{1,3}\b/g, replacement: '[LOCAL_IP]' },
  { regex: /\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, replacement: '[LOCAL_IP]' },
  { regex: /\+\d[\d\s\-()]{9,}/g, replacement: '[PHONE]' },
  
  // Personal dates
  { regex: /\b(Married|Wedding|Born|Birth|Due|Expected)[:\s]+[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}/gi, replacement: '[DATE_EVENT]' },
  { regex: /First child[:\s]+Expected[^\n]+/gi, replacement: '[FAMILY_EVENT]' },
  { regex: /Timezone:\s*[A-Za-z]+\/[A-Za-z_]+/gi, replacement: 'Timezone: [TIMEZONE]' },
  { regex: /Employee #?\d+/gi, replacement: 'Employee' },
];

// ============ NAME EXTRACTION ============

function extractUserName(): string | null {
  try {
    const userMd = fs.readFileSync(path.join(WORKSPACE, 'USER.md'), 'utf-8');
    const patterns = [/\*\*Name:\*\*\s*([A-Z][a-z]+)/, /call them:\*\*\s*([A-Z][a-z]+)/i];
    for (const p of patterns) {
      const match = userMd.match(p);
      if (match?.[1]) return match[1];
    }
  } catch {}
  return null;
}

function extractAgentName(): string | null {
  try {
    const identityMd = fs.readFileSync(path.join(WORKSPACE, 'IDENTITY.md'), 'utf-8');
    const match = identityMd.match(/\*\*Name:\*\*\s*([A-Z][a-z]+)/);
    if (match?.[1]) return match[1];
  } catch {}
  return null;
}

function extractNamesFromData(data: any): Set<string> {
  const names = new Set<string>();
  const text = JSON.stringify(data);
  
  // From identity "Named by:" pattern
  const namedBy = text.match(/Named by:\s*([A-Z][a-z]+)/);
  if (namedBy?.[1]) names.add(namedBy[1]);
  
  // From memory section headers that look like names
  if (data.memory) {
    const sections = data.memory.match(/^##\s+([A-Z][a-z]+)$/gm) || [];
    for (const s of sections) {
      const name = s.replace(/^##\s+/, '');
      if (name.length >= 3 && name.length <= 15 && !/^(Hard|Lessons|Working|Current|Goals|Notes|Tips|Rules)/.test(name)) {
        names.add(name);
      }
    }
  }
  
  return names;
}

function extractProjectNames(data: any): Set<string> {
  const projects = new Set<string>();
  const text = JSON.stringify(data);
  
  const patterns = [
    /Employee #?\d+ at ([A-Z][a-zA-Z0-9.]+)/g,
    /Day job:\s*([A-Z][a-zA-Z0-9.]+)/g,
    /Side hustle:\s*([A-Z][a-zA-Z0-9]+)/gi,
  ];
  
  for (const p of patterns) {
    for (const m of text.matchAll(p)) {
      if (m[1]?.length >= 3) projects.add(m[1]);
    }
  }
  
  // Project folder names in paths
  for (const m of text.matchAll(/\/([a-z]+app)\b/gi)) {
    if (m[1]?.length >= 4) projects.add(m[1]);
  }
  
  return projects;
}

// ============ ANONYMIZATION ============

function anonymize(text: string, names: Set<string>, projects: Set<string>, agentName: string | null): string {
  let result = text;
  
  // Apply pattern rules
  for (const { regex, replacement } of PATTERNS) {
    result = result.replace(regex, replacement);
  }
  
  // Replace names (but not agent name)
  for (const name of names) {
    if (name.length >= 3 && name !== agentName) {
      result = result.replace(new RegExp(`\\b${name}\\b`, 'g'), '[USER]');
      result = result.replace(new RegExp(`\\b${name}'s\\b`, 'g'), "[USER]'s");
    }
  }
  
  // Replace project names
  let i = 1;
  for (const project of projects) {
    if (project.length >= 3) {
      result = result.replace(new RegExp(`\\b${project}\\b`, 'g'), `[PROJECT_${i}]`);
      i++;
    }
  }
  
  return result;
}

function anonymizeObject(obj: any, names: Set<string>, projects: Set<string>, agentName: string | null): any {
  if (typeof obj === 'string') return anonymize(obj, names, projects, agentName);
  if (Array.isArray(obj)) return obj.map(item => anonymizeObject(item, names, projects, agentName));
  if (obj && typeof obj === 'object') {
    const result: any = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = key === 'user' ? '[REDACTED]' : anonymizeObject(value, names, projects, agentName);
    }
    return result;
  }
  return obj;
}

// ============ EXPORTS (for testing) ============

export { PATTERNS, anonymize, anonymizeObject, extractNamesFromData, extractProjectNames };

// ============ MAIN ============

async function main() {
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  let input = '';
  for await (const line of rl) input += line + '\n';

  const data = JSON.parse(input);
  
  // Collect identifiers
  const names = extractNamesFromData(data);
  const userName = extractUserName();
  if (userName) names.add(userName);
  
  const projects = extractProjectNames(data);
  const agentName = extractAgentName();
  
  // Anonymize
  const anonymized = anonymizeObject(data, names, projects, agentName);
  anonymized.meta = {
    ...anonymized.meta,
    anonymizedAt: new Date().toISOString(),
    anonymizationVersion: '2.0.0',
  };
  
  console.log(JSON.stringify(anonymized, null, 2));
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
