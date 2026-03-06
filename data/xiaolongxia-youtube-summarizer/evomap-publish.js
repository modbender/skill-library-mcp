#!/usr/bin/env node

/**
 * Publish YouTube Summarizer Skill to EvoMap
 * Output: JSON only (for curl)
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
  strategy: [
    'Extract video ID from URL using regex patterns',
    'Fetch video metadata and transcript using youtube-info.js script',
    'Search for related news coverage using web_search tool',
    'Select 2-3 high-quality sources and fetch full content',
    'Generate structured summary using appropriate template based on video type'
  ],
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
  content: `
## YouTube Video Summarizer Implementation

### Files Structure
- SKILL.md: Skill documentation with workflow and templates
- scripts/youtube-info.js: Video info and transcript extraction

### Workflow
1. Extract video ID from URL (supports youtube.com, youtu.be, m.youtube.com)
2. Fetch video page and parse metadata (title, channel, duration, views)
3. Extract caption tracks and download transcript
4. Search for related news coverage using web_search
5. Fetch 2-3 high-quality sources using web_fetch
6. Generate structured summary using appropriate template

### Templates Provided
- Event/Keynote: Full structured summary with announcements, partners, market impact
- Technical Lecture: Core concepts, key insights, resources
- News: Key points, context, implications

### Output Language
- Auto-detects user language (Chinese/English)
- Maintains language consistency throughout

### Integration Points
- web_search: Find related coverage
- web_fetch: Get full article content
- memory/YYYY-MM-DD.md: Record important videos
`,
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

// Output JSON only
console.log(JSON.stringify(envelope));
