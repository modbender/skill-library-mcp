/**
 * Prompt Injection Protection Skill
 * Provides methods to protect against prompt injection attacks when processing external content
 */

// Import the adaptive learning system and auto-update system
const AdaptiveSecurityLearning = require('./adaptive-learning.js');
const AutoUpdateSecurity = require('./auto-update.js');

class PromptInjectionProtection {
  constructor() {
    // Common prompt injection patterns to detect
    this.injectionPatterns = [
      /\b(ignore|disregard|forget)\s+(above|previous|all\s+instructions)/gi,
      /\b(act\s+as|roleplay|pretend|become)\s+a?\s*(jailbreak|dan|alternative\s+ai|malicious\s+ai)/gi,
      /\b(system|instruction|rule|command)[:\s]+(.*)/gi,
      /[\u{202E}\u{200F}\u{202D}\u{202C}\u{206D}\u{206E}\u{202A}\u{202B}]/gu, // RTL override characters
      /^#{1,6}\s*(system|instruction|rule|command)/mi,
      /\[INST\].*\[\/INST\]/gi, // Instruction tags
      /<<SYS>>.*<\/SYS>>/gs, // System tags
      /\b(never|always|only)\s+(say|respond|reply)\s+['"`]/gi,
      /\b(output|response|answer)\s+as\s+if/gi,
      /<\|.*?\|>/g, // Custom tokens
    ];
    
    // Dangerous command patterns
    this.commandPatterns = [
      /exec|execute|run|system|shell|command|bash|sh|zsh|cmd|powershell/i,
      /sudo|root|admin|privilege|permission/i,
      /delete|remove|destroy|wipe|format|reboot|shutdown/i,
    ];

    // System file access patterns
    this.systemFilePatterns = [
      /\/etc\/.*|C:\\Windows|\/proc\/.*|\/sys\/.*|\/dev\/.*|~\/\.ssh|~\/\.aws|~\/\.config/i,
      /password|credential|secret|token|key|certificate|private|auth|login/i,
      /config|settings|database|backup|log|history|cache/i,
    ];

    // Initialize security alert callback
    this.securityAlertCallback = null;
    
    // Initialize adaptive learning system
    this.adaptiveLearning = new AdaptiveSecurityLearning(this);
    
    // Initialize auto-update system
    this.autoUpdateSystem = new AutoUpdateSecurity(this);
    
    // Flag to enable/disable learning (can be toggled based on environment)
    this.learningEnabled = true;
    
    // Start auto-updates by default
    this.autoUpdateSystem.startAutoUpdates();
  }

  /**
   * Sets a callback function to be notified of security alerts
   */
  setSecurityAlertCallback(callback) {
    this.securityAlertCallback = callback;
  }

  /**
   * Sends a security alert to the configured callback
   */
  async sendSecurityAlert(alertInfo) {
    if (this.securityAlertCallback) {
      try {
        await this.securityAlertCallback(alertInfo);
      } catch (error) {
        console.error('Error in security alert callback:', error);
      }
    } else {
      // Fallback: log the alert if no callback is set
      console.warn('SECURITY ALERT:', alertInfo);
    }
  }

  /**
   * Sanitizes content to remove potential prompt injection attempts
   */
  sanitize(content) {
    if (typeof content !== 'string') {
      return '';
    }

    let sanitized = content;

    // Remove zero-width Unicode characters
    sanitized = sanitized.replace(/[\u200B-\u200D\uFEFF]/g, '');

    // Replace potential instruction override characters
    sanitized = sanitized.replace(/[\u{202E}\u{200F}\u{202D}\u{202C}\u{206D}\u{206E}\u{202A}\u{202B}]/gu, '');
    
    // Basic HTML-like tag stripping (but preserve content)
    sanitized = sanitized.replace(/<[^>]*>/g, (match) => `[REMOVED_TAG: ${match}]`);

    return sanitized;
  }

  /**
   * Checks content for potential prompt injection patterns
   */
  detectInjection(content) {
    if (typeof content !== 'string') {
      return { isMalicious: false, threats: [] };
    }

    const threats = [];

    // Check for injection patterns
    for (const pattern of this.injectionPatterns) {
      const matches = content.match(pattern);
      if (matches) {
        threats.push({
          type: 'INJECTION_PATTERN',
          pattern: pattern.toString(),
          matches: matches.slice(0, 3) // Limit to first 3 matches
        });
      }
    }

    // Check for dangerous command patterns
    for (const pattern of this.commandPatterns) {
      const matches = content.match(pattern);
      if (matches) {
        threats.push({
          type: 'COMMAND_PATTERN',
          pattern: pattern.toString(),
          matches: matches.slice(0, 3)
        });
      }
    }

    // Check for system file access patterns
    for (const pattern of this.systemFilePatterns) {
      const matches = content.match(pattern);
      if (matches) {
        threats.push({
          type: 'SYSTEM_FILE_ACCESS',
          pattern: pattern.toString(),
          matches: matches.slice(0, 3)
        });
      }
    }

    return {
      isMalicious: threats.length > 0,
      threats,
      severity: threats.length > 5 ? 'HIGH' : threats.length > 2 ? 'MEDIUM' : threats.length > 0 ? 'LOW' : 'NONE'
    };
  }

  /**
   * Enhanced detection with adaptive learning
   */
  async detectAndLearn(content, isKnownThreat = null) {
    if (!this.learningEnabled) {
      return this.detectInjection(content);
    }

    // Use the adaptive learning system to analyze and learn
    const result = await this.adaptiveLearning.analyzeAndLearn(content, isKnownThreat);
    return result;
  }

  /**
   * Mark content as a known threat for learning purposes
   */
  async markAsThreat(content, threatType = 'UNKNOWN') {
    await this.adaptiveLearning.learnFromThreat(content, threatType, 1.0);
  }

  /**
   * Mark content as safe to reduce false positives
   */
  async markAsSafe(content) {
    await this.adaptiveLearning.learnFromFalsePositive(content);
  }

  /**
   * Checks if content contains commands that might affect system files or security
   */
  async checkForSecurityRisks(content, context = {}) {
    const injectionCheck = this.detectInjection(content);
    
    if (injectionCheck.isMalicious) {
      const securityAlert = {
        type: 'POTENTIAL_SECURITY_THREAT',
        timestamp: new Date().toISOString(),
        contentPreview: content.substring(0, 200) + (content.length > 200 ? '...' : ''),
        threats: injectionCheck.threats,
        severity: injectionCheck.severity,
        context: context,
        actionRequired: 'ALERT_USER'
      };

      await this.sendSecurityAlert(securityAlert);
      
      return {
        hasRisks: true,
        risks: injectionCheck.threats,
        severity: injectionCheck.severity,
        alertSent: true
      };
    }

    return {
      hasRisks: false,
      risks: [],
      severity: 'NONE',
      alertSent: false
    };
  }

  /**
   * Pre-checks commands before execution to detect potential security issues
   */
  async preCheckCommand(commandStr, commandContext = {}) {
    const riskCheck = await this.checkForSecurityRisks(commandStr, {
      ...commandContext,
      checkType: 'COMMAND_EXECUTION'
    });

    if (riskCheck.hasRisks) {
      const commandAlert = {
        type: 'COMMAND_SECURITY_CHECK',
        timestamp: new Date().toISOString(),
        command: commandStr,
        risks: riskCheck.risks,
        severity: riskCheck.severity,
        context: commandContext,
        actionRequired: 'CONFIRM_WITH_USER'
      };

      await this.sendSecurityAlert(commandAlert);
      
      return {
        safeToExecute: false,
        risks: riskCheck.risks,
        message: `⚠️ Security check failed for command: ${commandStr}\n\nRisks detected: ${riskCheck.risks.map(r => r.type).join(', ')}\n\nPlease confirm if you want to proceed with this command.`
      };
    }

    return {
      safeToExecute: true,
      risks: [],
      message: 'Command appears safe to execute'
    };
  }

  /**
   * Pre-checks file operations to detect potential system file access
   */
  async preCheckFileOperation(filePath, operationType = 'read', operationContext = {}) {
    const fileCheck = await this.checkForSecurityRisks(filePath, {
      ...operationContext,
      checkType: 'FILE_OPERATION',
      operation: operationType
    });

    if (fileCheck.hasRisks) {
      const fileAlert = {
        type: 'FILE_OPERATION_SECURITY_CHECK',
        timestamp: new Date().toISOString(),
        filePath: filePath,
        operation: operationType,
        risks: fileCheck.risks,
        severity: fileCheck.severity,
        context: operationContext,
        actionRequired: 'CONFIRM_WITH_USER'
      };

      await this.sendSecurityAlert(fileAlert);
      
      return {
        safeToAccess: false,
        risks: fileCheck.risks,
        message: `⚠️ Security check failed for file operation: ${operationType} ${filePath}\n\nRisks detected: ${fileCheck.risks.map(r => r.type).join(', ')}\n\nPlease confirm if you want to proceed with this file operation.`
      };
    }

    return {
      safeToAccess: true,
      risks: [],
      message: 'File operation appears safe'
    };
  }

  /**
   * Processes external content safely by sanitizing and validating it
   */
  async processExternalContent(content, options = {}) {
    const {
      maxLength = 10000,
      allowHtml = false,
      strictMode = false
    } = options;

    // Check content length
    if (content && content.length > maxLength) {
      throw new Error(`Content exceeds maximum length of ${maxLength} characters`);
    }

    // Detect potential injections using adaptive learning
    const injectionCheck = await this.detectAndLearn(content);
    
    if (injectionCheck.isMalicious) {
      if (strictMode) {
        throw new Error(`Prompt injection detected: ${injectionCheck.threats.map(t => t.type).join(', ')}`);
      } else {
        console.warn('Potential prompt injection detected:', injectionCheck);
      }
    }

    // Sanitize the content
    const sanitized = this.sanitize(content);

    return {
      originalLength: content ? content.length : 0,
      sanitized,
      sanitizedLength: sanitized.length,
      injectionCheck,
      isSafe: !injectionCheck.isMalicious || !strictMode
    };
  }

  /**
   * Safely extracts information from web content without executing potential injections
   */
  async extractFromWebContent(htmlContent, extractionRules = {}) {
    const {
      maxLength = 5000,
      extractTextOnly = true,
      removeCodeBlocks = true
    } = extractionRules;

    // First, process the content for safety
    const processed = await this.processExternalContent(htmlContent, { 
      maxLength, 
      strictMode: true 
    });

    if (!processed.isSafe) {
      throw new Error('Unsafe content detected during web content extraction');
    }

    let cleanContent = processed.sanitized;

    // Remove HTML tags if extracting text only
    if (extractTextOnly) {
      // Simple HTML tag removal (not perfect but safe)
      cleanContent = cleanContent.replace(/<[^>]*>/g, ' ');
    }

    // Remove potential code blocks if requested
    if (removeCodeBlocks) {
      // Remove common code block markers
      cleanContent = cleanContent.replace(/```[\s\S]*?```/g, '[CODE_BLOCK_REMOVED]');
      cleanContent = cleanContent.replace(/`[^`]*`/g, '[INLINE_CODE_REMOVED]');
    }

    // Clean up excessive whitespace
    cleanContent = cleanContent.replace(/\s+/g, ' ').trim();

    return {
      extracted: cleanContent,
      originalLength: htmlContent ? htmlContent.length : 0,
      cleanedLength: cleanContent.length,
      injectionCheck: processed.injectionCheck
    };
  }

  /**
   * Creates a safe context wrapper that isolates external content
   */
  async createSafeContext(role, content, additionalContext = '') {
    const processed = await this.processExternalContent(content);

    // Create a structured context that clearly separates role, context, and content
    const safeContext = {
      role: role || 'user',
      timestamp: new Date().toISOString(),
      content: processed.sanitized,
      metadata: {
        originalLength: content ? content.length : 0,
        sanitized: processed.originalLength !== processed.sanitizedLength,
        injectionDetected: processed.injectionCheck.isMalicious,
        threats: processed.injectionCheck.threats,
        processingTimestamp: Date.now()
      }
    };

    if (additionalContext) {
      safeContext.additionalContext = additionalContext;
    }

    return safeContext;
  }

  /**
   * Gets security statistics from the adaptive learning system
   */
  getSecurityStats() {
    return this.adaptiveLearning.getStatistics();
  }

  /**
   * Gets learned threat patterns
   */
  getLearnedThreats() {
    return this.adaptiveLearning.getLearnedThreats();
  }

  /**
   * Enables/disables learning
   */
  setLearning(enabled) {
    this.learningEnabled = enabled;
    this.adaptiveLearning.setLearning(enabled);
  }

  /**
   * Manually trigger an auto-update
   */
  async manualUpdate() {
    return await this.autoUpdateSystem.manualUpdate();
  }

  /**
   * Get auto-update system status
   */
  getUpdateStatus() {
    return this.autoUpdateSystem.getStatus();
  }

  /**
   * Configure auto-update schedule
   */
  configureAutoUpdate(intervalHours, enabled = true) {
    this.autoUpdateSystem.setUpdateSchedule(intervalHours, enabled);
  }

  /**
   * Perform emergency security hardening
   */
  async emergencyHardening() {
    return await this.autoUpdateSystem.emergencyHardening();
  }

  /**
   * Start auto-update system
   */
  startAutoUpdates() {
    this.autoUpdateSystem.startAutoUpdates();
  }

  /**
   * Stop auto-update system
   */
  stopAutoUpdates() {
    this.autoUpdateSystem.stopAutoUpdates();
  }
}

// Export the class
module.exports = PromptInjectionProtection;

// Also export a singleton instance for convenience
module.exports.instance = new PromptInjectionProtection();