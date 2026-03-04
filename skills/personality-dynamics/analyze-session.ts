#!/usr/bin/env node
/**
 * Persona Evolution Skill - Session Analyzer
 * 
 * Analyzes conversation patterns after each session
 * Updates evolves/ files with detected patterns
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WORKSPACE = process.cwd();
const PERSONA_DIR = join(WORKSPACE, 'PERSONA');
const EVOLVES_DIR = join(PERSONA_DIR, 'evolves');

// Ensure directories exist
if (!existsSync(EVOLVES_DIR)) {
  mkdirSync(EVOLVES_DIR, { recursive: true });
}

// Default analysis structure
const defaultAnalysis = {
  session_count: 0,
  last_updated: new Date().toISOString(),
  communication_style: {
    preferred_format: 'mixed',
    detail_level: 'balanced',
    response_latency: 'considered'
  },
  engagement_signals: {
    enthusiasm_topics: [],
    disengagement_topics: [],
    humor_receptivity: 0.5
  },
  trust_indicators: {
    autonomous_actions: 0,
    clarifications_asked: 0,
    corrections_made: 0,
    trust_level: 'building' // building, established, high
  },
  emotional_context: {
    stress_signals: [],
    celebration_moments: [],
    dominant_mood: 'neutral'
  }
};

function loadOrCreate(filename, defaultContent) {
  const path = join(EVOLVES_DIR, filename);
  if (existsSync(path)) {
    try {
      return JSON.parse(readFileSync(path, 'utf-8'));
    } catch {
      return defaultContent;
    }
  }
  return defaultContent;
}

function save(filename, content) {
  const path = join(EVOLVES_DIR, filename);
  writeFileSync(path, JSON.stringify(content, null, 2));
}

// Simple pattern detection from session transcript
// In production, this would use the LLM to analyze
function analyzeSession(transcript) {
  const analysis = {
    timestamp: new Date().toISOString(),
    signals: {
      preferred_bullets: (transcript.match(/^[\s]*[-•]/gm) || []).length > 5,
      preferred_code: (transcript.match(/```/g) || []).length > 2,
      asked_questions: (transcript.match(/\?/g) || []).length,
      enthusiasm_markers: [
        'great', 'awesome', 'love', 'perfect', 'excellent',
        'excited', 'amazing', 'brilliant', 'fantastic'
      ].filter(word => transcript.toLowerCase().includes(word)),
      stress_markers: [
        'stressed', 'overwhelmed', 'frustrated', 'urgent',
        'deadline', 'worried', 'behind', 'struggling'
      ].filter(word => transcript.toLowerCase().includes(word)),
      celebration_markers: [
        'launched', 'shipped', 'completed', 'done', 'success',
        'working', 'fixed', 'deployed', 'live'
      ].filter(word => transcript.toLowerCase().includes(word))
    }
  };
  
  return analysis;
}

// Main analysis function
async function main() {
  console.log('🔍 Analyzing session for persona evolution...');
  
  // Load current patterns
  const patterns = loadOrCreate('patterns.json', defaultAnalysis);
  
  // Read session transcript (would be passed as argument or read from memory)
  // For now, we'll analyze the most recent memory file
  const memoryDir = join(WORKSPACE, 'memory');
  const today = new Date().toISOString().split('T')[0];
  const memoryFile = join(memoryDir, `${today}.md`);
  
  let sessionAnalysis;
  if (existsSync(memoryFile)) {
    const transcript = readFileSync(memoryFile, 'utf-8');
    sessionAnalysis = analyzeSession(transcript);
  } else {
    console.log('⚠️  No memory file found for today');
    sessionAnalysis = { timestamp: new Date().toISOString(), signals: {} };
  }
  
  // Update patterns
  patterns.session_count++;
  patterns.last_updated = new Date().toISOString();
  
  // Detect format preference
  if (sessionAnalysis.signals.preferred_bullets) {
    patterns.communication_style.preferred_format = 'bullets';
  }
  
  // Track enthusiasm topics
  if (sessionAnalysis.signals.enthusiasm_markers.length > 0) {
    patterns.engagement_signals.enthusiasm_topics = [
      ...new Set([
        ...patterns.engagement_signals.enthusiasm_topics,
        ...sessionAnalysis.signals.enthusiasm_markers
      ])
    ].slice(-10); // Keep last 10
  }
  
  // Track stress
  if (sessionAnalysis.signals.stress_markers.length > 0) {
    patterns.emotional_context.stress_signals.push({
      date: today,
      markers: sessionAnalysis.signals.stress_markers
    });
    patterns.emotional_context.dominant_mood = 'stressed';
  }
  
  // Track celebrations
  if (sessionAnalysis.signals.celebration_markers.length > 0) {
    patterns.emotional_context.celebration_moments.push({
      date: today,
      markers: sessionAnalysis.signals.celebration_markers
    });
    if (patterns.emotional_context.dominant_mood !== 'stressed') {
      patterns.emotional_context.dominant_mood = 'celebratory';
    }
  }
  
  // Save updated patterns
  save('patterns.json', patterns);
  save(`session-${Date.now()}.json`, sessionAnalysis);
  
  console.log('✅ Session analysis complete');
  console.log(`📊 Session count: ${patterns.session_count}`);
  console.log(`😊 Dominant mood: ${patterns.emotional_context.dominant_mood}`);
}

main().catch(console.error);
