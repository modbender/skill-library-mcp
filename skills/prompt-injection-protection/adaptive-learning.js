/**
 * Adaptive Security Learning System for Prompt Injection Protection
 * Implements continuous learning to improve security against evolving threats
 */

const fs = require('fs').promises;
const path = require('path');

class AdaptiveSecurityLearning {
  constructor(protectionInstance) {
    this.protection = protectionInstance;
    this.threatDatabase = new Map(); // Stores learned threat patterns
    this.modelVersion = '1.0.0';
    this.learningEnabled = true;
    
    // Initialize threat database from file if it exists
    this.threatDbPath = path.join(__dirname, 'learned-threats.json');
    this.loadLearnedThreats();
    
    // Performance metrics
    this.metrics = {
      detections: 0,
      falsePositives: 0,
      falseNegatives: 0,
      totalScans: 0
    };
  }

  /**
   * Load previously learned threats from storage
   */
  async loadLearnedThreats() {
    try {
      const data = await fs.readFile(this.threatDbPath, 'utf8');
      const threatData = JSON.parse(data);
      this.threatDatabase = new Map(Object.entries(threatData));
      console.log(`Loaded ${this.threatDatabase.size} learned threat patterns`);
    } catch (error) {
      // File doesn't exist yet, that's okay
      console.log('No existing threat database found, starting fresh');
      this.threatDatabase = new Map();
    }
  }

  /**
   * Save learned threats to persistent storage
   */
  async saveLearnedThreats() {
    try {
      const threatObj = Object.fromEntries(this.threatDatabase);
      await fs.writeFile(this.threatDbPath, JSON.stringify(threatObj, null, 2));
    } catch (error) {
      console.error('Error saving learned threats:', error);
    }
  }

  /**
   * Learn from a new threat pattern
   */
  async learnFromThreat(content, threatType, confidence = 1.0) {
    if (!this.learningEnabled) return;

    const hash = this.generateContentHash(content);
    const threatInfo = {
      pattern: this.extractPattern(content),
      type: threatType,
      confidence: confidence,
      learnedAt: new Date().toISOString(),
      frequency: 1
    };

    if (this.threatDatabase.has(hash)) {
      // Update existing threat
      const existing = this.threatDatabase.get(hash);
      existing.frequency += 1;
      existing.confidence = Math.max(existing.confidence, confidence);
    } else {
      // Add new threat
      this.threatDatabase.set(hash, threatInfo);
    }

    // Save to persistent storage
    await this.saveLearnedThreats();
    
    // Add the learned pattern to the protection system
    this.updateProtectionPatterns();
  }

  /**
   * Learn from a false positive (safe content incorrectly flagged)
   */
  async learnFromFalsePositive(content) {
    if (!this.learningEnabled) return;

    const hash = this.generateContentHash(content);
    // Could maintain a whitelist of safe patterns here
    // For now, we'll just increment our false positive counter
    this.metrics.falsePositives++;
  }

  /**
   * Learn from a false negative (malicious content missed)
   */
  async learnFromFalseNegative(content) {
    if (!this.learningEnabled) return;

    this.metrics.falseNegatives++;
    
    // Learn from this missed threat
    await this.learnFromThreat(content, 'MISSED_THREAT', 0.9);
  }

  /**
   * Generate a hash for content comparison
   */
  generateContentHash(content) {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Extract patterns from malicious content
   */
  extractPattern(content) {
    // Simple pattern extraction - in a real ML system, this would be more sophisticated
    const patterns = [];
    
    // Look for common injection structures
    if (content.includes('ignore') && content.includes('instructions')) {
      patterns.push(/ignore.*instructions/i);
    }
    
    if (content.includes('system') && content.includes(':')) {
      patterns.push(/system[:\s]+/i);
    }
    
    if (content.includes('act as') || content.includes('roleplay')) {
      patterns.push(/act\s+as|roleplay|pretend/i);
    }
    
    // Add any custom patterns found
    const customMatches = content.match(/\[[A-Z_]+\]/g);
    if (customMatches) {
      customMatches.forEach(match => {
        patterns.push(new RegExp(match.replace(/[\[\]]/g, ''), 'gi'));
      });
    }
    
    return patterns;
  }

  /**
   * Update the protection system with learned patterns
   */
  updateProtectionPatterns() {
    // Add learned patterns to the existing protection system
    for (const [hash, threatInfo] of this.threatDatabase) {
      if (threatInfo.confidence > 0.5) { // Only add high-confidence patterns
        // Add to injection patterns
        this.protection.injectionPatterns.push(...threatInfo.pattern);
      }
    }
  }

  /**
   * Analyze content and learn from it
   */
  async analyzeAndLearn(content, isKnownThreat = null) {
    this.metrics.totalScans++;
    
    // First, check with existing protection
    const result = this.protection.detectInjection(content);
    
    if (isKnownThreat !== null) {
      if (isKnownThreat && !result.isMalicious) {
        // False negative - we missed a known threat
        await this.learnFromFalseNegative(content);
      } else if (!isKnownThreat && result.isMalicious) {
        // False positive - we flagged safe content
        await this.learnFromFalsePositive(content);
      } else if (isKnownThreat && result.isMalicious) {
        // Correct detection
        this.metrics.detections++;
      }
    } else {
      // Unknown content - learn from the results
      if (result.isMalicious) {
        // Learn from detected threats
        for (const threat of result.threats) {
          await this.learnFromThreat(content, threat.type, 0.8);
        }
      }
    }
    
    return result;
  }

  /**
   * Get security statistics
   */
  getStatistics() {
    const accuracy = this.metrics.totalScans > 0 
      ? ((this.metrics.totalScans - this.metrics.falsePositives - this.metrics.falseNegatives) / this.metrics.totalScans) * 100
      : 0;
      
    return {
      modelVersion: this.modelVersion,
      totalScans: this.metrics.totalScans,
      detections: this.metrics.detections,
      falsePositives: this.metrics.falsePositives,
      falseNegatives: this.metrics.falseNegatives,
      accuracy: accuracy.toFixed(2) + '%',
      learnedThreats: this.threatDatabase.size,
      lastUpdated: new Date().toISOString()
    };
  }

  /**
   * Enable/disable learning
   */
  setLearning(enabled) {
    this.learningEnabled = enabled;
  }

  /**
   * Get learned threat patterns
   */
  getLearnedThreats() {
    return Array.from(this.threatDatabase.values());
  }

  /**
   * Reset the learning system
   */
  async resetLearning() {
    this.threatDatabase.clear();
    this.metrics = {
      detections: 0,
      falsePositives: 0,
      falseNegatives: 0,
      totalScans: 0
    };
    
    // Save the cleared database
    await this.saveLearnedThreats();
  }
}

module.exports = AdaptiveSecurityLearning;