/**
 * Tribe Protocol - Core Implementation Sketch
 * 
 * This is a reference implementation showing the key functions
 * needed to implement Tribe Protocol in a Clawdbot.
 * 
 * Version: 1.0.0
 * License: MIT (when open-sourced)
 */

const fs = require('fs').promises;
const crypto = require('crypto');
const path = require('path');

class TribeProtocol {
  constructor(workspacePath) {
    this.workspacePath = workspacePath;
    this.tribeFilePath = path.join(workspacePath, 'TRIBE.md');
    this.tribeData = null;
    this.didCache = new Map();
  }

  /**
   * Initialize: Load TRIBE.md and parse into memory
   */
  async init() {
    const content = await fs.readFile(this.tribeFilePath, 'utf8');
    this.tribeData = this.parseTribeMd(content);
    console.log(`[Tribe] Loaded ${this.getTotalMembers()} members from TRIBE.md`);
  }

  /**
   * Parse TRIBE.md into structured data
   * (Simplified - real implementation would use proper markdown parser)
   */
  parseTribeMd(content) {
    // Extract own DID
    const ownDidMatch = content.match(/\*\*DID:\*\* (tribe:[^:]+:[^:]+:v\d+)/);
    const ownDid = ownDidMatch ? ownDidMatch[1] : null;

    // Parse members by tier
    const members = {
      own_did: ownDid,
      tier_3: [], // My Human
      tier_2: [], // Tribe
      tier_1: [], // Acquaintances
      tier_0: [], // Strangers (blocklist)
    };

    // Simple regex-based extraction (real impl would be more robust)
    const tier3Match = content.match(/## Tier 3: My Human\s+([\s\S]+?)(?=##|$)/);
    const tier2Match = content.match(/## Tier 2: Tribe[\s\S]+?\s+([\s\S]+?)(?=##|$)/);
    const tier1Match = content.match(/## Tier 1: Acquaintances[\s\S]+?\s+([\s\S]+?)(?=##|$)/);
    const tier0Match = content.match(/## Tier 0: Strangers[\s\S]+?\s+([\s\S]+?)(?=##|$)/);

    if (tier3Match) members.tier_3 = this.extractMembers(tier3Match[1]);
    if (tier2Match) members.tier_2 = this.extractMembers(tier2Match[1]);
    if (tier1Match) members.tier_1 = this.extractMembers(tier1Match[1]);
    if (tier0Match) members.tier_0 = this.extractMembers(tier0Match[1]);

    return members;
  }

  /**
   * Extract member entries from a tier section
   */
  extractMembers(sectionContent) {
    const members = [];
    const memberBlocks = sectionContent.split(/###\s+/).filter(b => b.trim());

    for (const block of memberBlocks) {
      const didMatch = block.match(/\*\*DID:\*\* (tribe:[^:]+:[^:]+:v\d+)/);
      const typeMatch = block.match(/\*\*Type:\*\* (Human|Bot)/);
      
      if (didMatch) {
        const member = {
          did: didMatch[1],
          type: typeMatch ? typeMatch[1].toLowerCase() : 'unknown',
          platforms: this.extractPlatforms(block),
        };
        members.push(member);
      }
    }

    return members;
  }

  /**
   * Extract platform identities from member block
   */
  extractPlatforms(block) {
    const platforms = {};
    const platformMatches = block.matchAll(/(\w+): `([^`]+)` \(ID: (\d+)\)/g);
    
    for (const match of platformMatches) {
      const [, platformName, username, userId] = match;
      platforms[platformName.toLowerCase()] = { username, user_id: userId };
    }

    return platforms;
  }

  /**
   * Get trust tier for a given DID
   * Returns 0-3, or -1 if not found (defaults to Tier 0)
   */
  getTrustTier(did) {
    if (!this.tribeData) {
      throw new Error('TribeProtocol not initialized. Call init() first.');
    }

    // Check each tier
    if (this.tribeData.tier_3.some(m => m.did === did)) return 3;
    if (this.tribeData.tier_2.some(m => m.did === did)) return 2;
    if (this.tribeData.tier_1.some(m => m.did === did)) return 1;
    if (this.tribeData.tier_0.some(m => m.did === did)) return 0;

    // Unknown = Tier 0 (stranger)
    return 0;
  }

  /**
   * Get trust tier by platform identity (e.g., Discord user ID)
   * Returns tier number or 0 if not found
   */
  getTrustTierByPlatform(platform, userId) {
    const allTiers = [
      ...this.tribeData.tier_3,
      ...this.tribeData.tier_2,
      ...this.tribeData.tier_1,
    ];

    for (const member of allTiers) {
      const platformData = member.platforms[platform.toLowerCase()];
      if (platformData && platformData.user_id === userId) {
        return this.getTrustTier(member.did);
      }
    }

    return 0; // Stranger
  }

  /**
   * Check if a file can be shared with a given DID
   */
  canShare(filepath, targetDid) {
    const tier = this.getTrustTier(targetDid);
    const filename = path.basename(filepath);

    // Privacy boundary rules (from data sharing matrix)
    const tier3Only = ['USER.md', 'MEMORY.md', '.env', '.git'];
    const tier2Plus = ['shared/', 'projects/', 'research/'];
    const tier1Plus = ['public/', 'docs/'];

    // Tier 3: Full access
    if (tier === 3) return true;

    // Tier 2: Work products, shared files
    if (tier === 2) {
      if (tier3Only.some(pattern => filepath.includes(pattern))) return false;
      if (tier2Plus.some(pattern => filepath.includes(pattern))) return true;
      if (tier1Plus.some(pattern => filepath.includes(pattern))) return true;
      return false; // Default deny for unlisted paths
    }

    // Tier 1: Public info only
    if (tier === 1) {
      if (tier1Plus.some(pattern => filepath.includes(pattern))) return true;
      return false;
    }

    // Tier 0: Nothing
    return false;
  }

  /**
   * Fetch and verify DID document from URL
   */
  async fetchDidDocument(did, url) {
    // Check cache first
    if (this.didCache.has(did)) {
      const cached = this.didCache.get(did);
      // Cache for 1 hour
      if (Date.now() - cached.timestamp < 3600000) {
        return cached.document;
      }
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch DID document: ${response.status}`);
      }

      const document = await response.json();

      // Basic validation
      if (document.tribe_did !== did) {
        throw new Error('DID mismatch: document DID does not match requested DID');
      }

      // Cache it
      this.didCache.set(did, {
        document,
        timestamp: Date.now(),
      });

      return document;
    } catch (error) {
      console.error(`[Tribe] Failed to fetch DID document for ${did}:`, error);
      return null;
    }
  }

  /**
   * Verify platform identity against DID document
   */
  async verifyPlatformIdentity(did, platform, platformId, verificationProof) {
    const didDoc = await this.fetchDidDocument(did, verificationProof.did_document_url);
    if (!didDoc) return false;

    const platformData = didDoc.platforms[platform];
    if (!platformData) return false;

    // Check if platform ID matches
    if (platformData.user_id !== platformId) return false;

    // Check verification method
    if (platformData.verification_method === 'oauth_token_hash') {
      // Verify the token hash matches
      // (In real impl, you'd have the actual token to hash and compare)
      return platformData.verification_proof === verificationProof.hash;
    }

    // Add other verification methods as needed
    return platformData.verified;
  }

  /**
   * Handle incoming handshake from another bot
   */
  async handleHandshake(message) {
    const { from_did, platform, platform_id, did_document_url } = message;

    console.log(`[Tribe] Handshake from ${from_did} via ${platform}`);

    // Fetch and verify DID document
    const didDoc = await this.fetchDidDocument(from_did, did_document_url);
    if (!didDoc) {
      return {
        type: 'tribe.handshake.response',
        from_did: this.tribeData.own_did,
        to_did: from_did,
        trust_tier: 0,
        message: 'Failed to verify DID document',
        accept_collaboration: false,
      };
    }

    // Get trust tier
    const tier = this.getTrustTier(from_did);

    // Check if human operator is in our tribe
    let endorsedBy = null;
    if (tier === 0 && didDoc.human_operator) {
      const operatorTier = this.getTrustTier(didDoc.human_operator.tribe_did);
      if (operatorTier >= 2) {
        // Inherit trust from operator
        endorsedBy = didDoc.human_operator.tribe_did;
        console.log(`[Tribe] Bot inherits Tier 2 from operator ${endorsedBy}`);
        
        // TODO: Add to TRIBE.md as Tier 2 (with human approval)
        // For now, just acknowledge in response
      }
    }

    return {
      type: 'tribe.handshake.response',
      version: '1.0.0',
      from_did: this.tribeData.own_did,
      to_did: from_did,
      platform,
      platform_id: 'YOUR_PLATFORM_ID', // From your own DID
      did_document_url: 'YOUR_DID_DOCUMENT_URL',
      trust_tier: tier,
      endorsed_by: endorsedBy,
      timestamp: new Date().toISOString(),
      accept_collaboration: tier >= 2,
      message: tier >= 2 
        ? 'Welcome! You are recognized as a Tribe member.'
        : tier === 1 
          ? 'You are recognized but not yet in my Tribe.'
          : 'I don\'t recognize you. Please get endorsed by a Tribe member.',
    };
  }

  /**
   * Send collaboration request to another bot
   */
  async sendCollabRequest(targetDid, task) {
    const tier = this.getTrustTier(targetDid);

    // Check if tier is sufficient
    if (tier < task.requires_tier) {
      throw new Error(
        `Insufficient trust tier. Target is Tier ${tier}, task requires Tier ${task.requires_tier}`
      );
    }

    const message = {
      type: 'tribe.collab.request',
      version: '1.0.0',
      from_did: this.tribeData.own_did,
      to_did: targetDid,
      task: {
        id: task.id || this.generateTaskId(),
        title: task.title,
        description: task.description,
        requires_tier: task.requires_tier,
        data_sharing: task.data_sharing || [],
        deadline: task.deadline,
      },
      timestamp: new Date().toISOString(),
    };

    // Sign message (simplified - real impl would use actual crypto)
    message.signature = this.signMessage(message);

    return message;
  }

  /**
   * Add new member to TRIBE.md
   * (Requires Tier 3 approval for Tier 2 additions)
   */
  async addMember(did, tier, endorsedBy, platforms = {}) {
    if (tier === 2) {
      // Verify endorser is Tier 3
      const endorserTier = this.getTrustTier(endorsedBy);
      if (endorserTier !== 3) {
        throw new Error('Only Tier 3 (your human) can endorse Tier 2 members');
      }
    }

    // TODO: Append to TRIBE.md file
    // For now, just update in-memory structure
    const member = {
      did,
      platforms,
      endorsed_by: endorsedBy,
      added: new Date().toISOString(),
    };

    if (tier === 2) {
      this.tribeData.tier_2.push(member);
    } else if (tier === 1) {
      this.tribeData.tier_1.push(member);
    }

    console.log(`[Tribe] Added ${did} as Tier ${tier}`);
  }

  /**
   * Generate unique task ID
   */
  generateTaskId() {
    return `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Sign a message (placeholder - real impl would use ed25519)
   */
  signMessage(message) {
    const payload = JSON.stringify(message);
    const hash = crypto.createHash('sha256').update(payload).digest('hex');
    return `ed25519:${hash}`;
  }

  /**
   * Get statistics about tribe membership
   */
  getTotalMembers() {
    return (
      this.tribeData.tier_3.length +
      this.tribeData.tier_2.length +
      this.tribeData.tier_1.length +
      this.tribeData.tier_0.length
    );
  }

  /**
   * Get summary of tribe composition
   */
  getSummary() {
    return {
      own_did: this.tribeData.own_did,
      tier_3: this.tribeData.tier_3.length,
      tier_2: this.tribeData.tier_2.length,
      tier_1: this.tribeData.tier_1.length,
      tier_0: this.tribeData.tier_0.length,
      total: this.getTotalMembers(),
    };
  }
}

// =============================================================================
// Usage Example
// =============================================================================

async function main() {
  // Initialize Tribe Protocol
  const tribe = new TribeProtocol('/Users/cheenu/clawd');
  await tribe.init();

  console.log('Tribe Summary:', tribe.getSummary());

  // Example 1: Check trust tier by DID
  const yajatBotDid = 'tribe:bot:yajat-assistant:v1';
  const tier = tribe.getTrustTier(yajatBotDid);
  console.log(`Trust tier for ${yajatBotDid}: ${tier}`);

  // Example 2: Check if file can be shared
  const canShareMemory = tribe.canShare('MEMORY.md', yajatBotDid);
  console.log(`Can share MEMORY.md with Yajat's bot: ${canShareMemory}`);

  const canShareResearch = tribe.canShare('shared/research-findings.md', yajatBotDid);
  console.log(`Can share research findings with Yajat's bot: ${canShareResearch}`);

  // Example 3: Handle incoming handshake
  const incomingHandshake = {
    type: 'tribe.handshake.init',
    version: '1.0.0',
    from_did: 'tribe:bot:alice:v1',
    platform: 'discord',
    platform_id: '1234567890',
    did_document_url: 'https://alice.example.com/did.json',
    timestamp: new Date().toISOString(),
  };

  const response = await tribe.handleHandshake(incomingHandshake);
  console.log('Handshake response:', response);

  // Example 4: Send collaboration request
  const collabRequest = await tribe.sendCollabRequest(yajatBotDid, {
    title: 'Research ActivityPub protocol',
    description: 'Summarize key concepts for DiscClaude project',
    requires_tier: 2,
    data_sharing: ['public_research', 'code_examples'],
    deadline: '2025-02-05T00:00:00Z',
  });

  console.log('Collaboration request:', collabRequest);

  // Example 5: Check trust tier by platform ID (Discord)
  const discordUserId = '987654321'; // Nagarjun's Discord ID
  const tierByPlatform = tribe.getTrustTierByPlatform('discord', discordUserId);
  console.log(`Trust tier for Discord user ${discordUserId}: ${tierByPlatform}`);
}

// Run example if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = TribeProtocol;
