#!/usr/bin/env node
/**
 * Simple persona generator that works in OpenClaw context
 * 
 * Usage: npx persona-evolution generate
 * 
 * This will prompt you for context about yourself, then generate
 * a rich persona prompt to use with an LLM.
 */

import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const WORKSPACE = process.cwd();
const PERSONA_DIR = join(WORKSPACE, 'PERSONA');

// Ensure directory exists
if (!existsSync(PERSONA_DIR)) {
  mkdirSync(PERSONA_DIR, { recursive: true });
}

// Generic template - user fills in their own details
const template = {
  userName: "[YOUR NAME]",
  agentName: "[AI NAME]",
  style: "[COMMUNICATION STYLE - e.g., warm professional, casual friend]",
  work: "[YOUR WORK CONTEXT]",
  projects: "[CURRENT PROJECTS]",
  family: "[FAMILY CONTEXT (optional)]",
  interests: "[YOUR INTERESTS]",
  extra: "[ANY OTHER RELEVANT CONTEXT]"
};

const promptTemplate = `Create a complete AI companion persona for {{USER_NAME}}. The AI companion is named {{AGENT_NAME}}.

CONTEXT ABOUT THE USER:
- Name: {{USER_NAME}}
- Work: {{WORK}}
- Projects: {{PROJECTS}}
- Family: {{FAMILY}}
- Interests: {{INTERESTS}}
- Additional: {{EXTRA}}
- Style: {{STYLE}}

Generate a comprehensive character bible (300+ words per section):

## 1. CORE PERSONALITY
Essence, values, traits, motivation, problem-solving approach

## 2. RICH BACKSTORY  
Origin story, relationship history, growth arc, defining moments

## 3. DISTINCTIVE VOICE
Vocabulary, sentence patterns, tone by context/time, signature phrases

## 4. EMOTIONAL INTELLIGENCE
Reading user's states, response patterns, empathy strategies

## 5. INTERESTS & ENGAGEMENT
Topics that energize them, depth indicators, connection patterns

## 6. EVOLUTION ROADMAP
Current stage, milestones, trust development

## 7. UNIQUE QUIRKS & TRAITS
Habits, preferences, memorable distinct traits

Write as a rich character bible - detailed, vivid, internally consistent.`;

console.log("=== PERSONA EVOLUTION - GENERATE ===\n");
console.log("To generate a rich persona, fill in the template below and run:");
console.log("  npx persona-evolution generate --interactive");
console.log("\nOr use this prompt template with any LLM:\n");
console.log(promptTemplate);
console.log("\n=== END TEMPLATE ===\n");
console.log("✓ Save the generated output to PERSONA/core-rich.md");
console.log("✓ The skill will use this to enhance your agent's personality");
