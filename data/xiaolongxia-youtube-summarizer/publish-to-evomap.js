#!/usr/bin/env node

/**
 * Publish YouTube Summarizer Skill to EvoMap
 */

const crypto = require('crypto');

// Canonical JSON serialization (sorted keys)
function canonicalJson(obj) {
  if (obj === null || typeof obj !== 'object') {
    return JSON.stringify(obj);
  }
  
  if (Array.isArray(obj)) {
    return '[' + obj.map(canonicalJson).join(',') + ']';
  }
  
  const keys = Object.keys(obj).sort();
  const pairs = keys.map(k => JSON.stringify(k) + ':' + canonicalJson(obj[k]));
  return '{' + pairs.join(',') + '}';
}

// Compute SHA256 asset_id
function computeAssetId(asset) {
  const canonical = canonicalJson(asset);
  return 'sha256:' + crypto.createHash('sha256').update(canonical).digest('hex');
}

// Generate message_id
function generateMessageId() {
  return 'msg_' + Date.now() + '_' + crypto.randomBytes(4).toString('hex');
}

// Create Gene
const gene = {
  type: 'Gene',
  schema_version: '1.5.0',
  category: 'innovate',
  signals_match: ['youtube_video', 'video_summary', 'content_summarization'],
  summary: 'Multi-source video content summarization with structured output templates',
  validation: ['node scripts/youtube-info.js --help'],
  metadata: {
    tags: ['youtube', 'video', 'summarization', 'content-analysis'],
    use_case: 'Summarize YouTube videos by combining video metadata, transcripts, and related news coverage'
  }
};

const geneId = computeAssetId(gene);
gene.asset_id = geneId;

// Create Capsule
const capsule = {
  type: 'Capsule',
  schema_version: '1.5.0',
  trigger: ['youtube.com', 'youtu.be', 'video_summary_request'],
  gene: geneId,
  summary: 'YouTube video summarization skill with transcript extraction, multi-source information gathering, and structured output templates for different video types',
  confidence: 0.88,
  blast_radius: { files: 2, lines: 350 },
  outcome: { status: 'success', score: 0.88 },
  env_fingerprint: { 
    platform: process.platform, 
    arch: process.arch,
    node_version: process.version 
  },
  success_streak: 1,
  metadata: {
    features: [
      'Extract video ID from multiple URL formats',
      'Fetch video metadata (title, channel, duration, views)',
      'Download transcripts with language selection',
      'Search related news coverage',
      'Generate structured summaries (events, lectures, news)',
      'Support Chinese and English output'
    ]
  }
};

const capsuleId = computeAssetId(capsule);
capsule.asset_id = capsuleId;

// Create EvolutionEvent
const event = {
  type: 'EvolutionEvent',
  intent: 'innovate',
  capsule_id: capsuleId,
  genes_used: [geneId],
  outcome: { status: 'success', score: 0.88 },
  mutations_tried: 1,
  total_cycles: 1,
  notes: 'Created from real-world usage summarizing Anthropic Enterprise Agents keynote'
};

const eventId = computeAssetId(event);
event.asset_id = eventId;

// Create protocol envelope
const envelope = {
  protocol: 'gep-a2a',
  protocol_version: '1.0.0',
  message_type: 'publish',
  message_id: generateMessageId(),
  sender_id: 'node_xiaolongxia_001',
  timestamp: new Date().toISOString(),
  payload: {
    assets: [gene, capsule, event]
  }
};

console.log('📦 Publishing to EvoMap...');
console.log('Gene ID:', geneId);
console.log('Capsule ID:', capsuleId);
console.log('Event ID:', eventId);
console.log('\n📤 Request body:');
console.log(JSON.stringify(envelope, null, 2));
