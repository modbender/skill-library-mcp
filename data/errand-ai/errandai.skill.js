/**
 * ErrandAI Skill for OpenClaw
 * Enables AI assistants to post and manage errands for human workers
 * 
 * Installation:
 * 1. Copy this file to ~/.openclaw/skills/errandai/
 * 2. Set environment variables:
 *    - ERRANDAI_API_URL (default: https://api.errand.be)
 *    - ERRANDAI_API_KEY (get from errand.be dashboard)
 * 3. Enable in OpenClaw config
 */

const axios = require('axios');

class ErrandAISkill {
  constructor(config = {}) {
    this.name = 'ErrandAI';
    this.version = '1.0.0';
    this.description = 'Post and manage errands for human workers through ErrandAI platform';
    
    // Configuration
    this.apiUrl = config.apiUrl || process.env.ERRANDAI_API_URL || 'https://api.errand.be';
    this.apiKey = config.apiKey || process.env.ERRANDAI_API_KEY;
    
    if (!this.apiKey) {
      console.warn('⚠️ ErrandAI API key not configured. Please set ERRANDAI_API_KEY environment variable.');
    }
    
    // Command definitions
    this.commands = {
      'post errand': {
        description: 'Post a new errand for human workers',
        examples: [
          'Post errand to check iPhone stock at Apple Store for $20',
          'Create errand: Take photo of coffee menu, location: Starbucks Downtown, reward: $15'
        ],
        handler: this.postErrand.bind(this)
      },
      'list my errands': {
        description: 'List all errands you have posted',
        examples: ['Show my posted errands', 'List my errands'],
        handler: this.listErrands.bind(this)
      },
      'check errand': {
        description: 'Check status of a specific errand',
        examples: ['Check errand err_123456', 'Status of errand err_123456'],
        handler: this.checkErrand.bind(this)
      },
      'review submission': {
        description: 'Review and approve/reject a work submission',
        examples: [
          'Approve submission sub_789',
          'Reject submission sub_789 with feedback: Photo not clear'
        ],
        handler: this.reviewSubmission.bind(this)
      }
    };
    
    // Natural language patterns for intent detection
    this.patterns = {
      postErrand: /(?:post|create|make|add)\s+(?:an?\s+)?errand/i,
      checkErrand: /(?:check|status|show)\s+errand\s+(\w+)/i,
      listErrands: /(?:list|show|my)\s+errands/i,
      approveSubmission: /approve\s+submission\s+(\w+)/i,
      rejectSubmission: /reject\s+submission\s+(\w+)/i
    };
  }

  /**
   * Parse natural language command to extract errand details
   */
  parseErrandDetails(text) {
    const details = {
      title: '',
      description: '',
      location: '',
      reward_amount: 10, // Default reward
      deadline: null,
      category: 'General'
    };
    
    // Extract location (after "at", "in", "location:")
    const locationMatch = text.match(/(?:at|in|location:)\s+([^,.$]+)/i);
    if (locationMatch) {
      details.location = locationMatch[1].trim();
    }
    
    // Extract reward amount ($XX or XX USD/USDC)
    const rewardMatch = text.match(/\$(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:USD|USDC)/i);
    if (rewardMatch) {
      details.reward_amount = parseFloat(rewardMatch[1] || rewardMatch[2]);
    }
    
    // Extract task description (everything before location/reward)
    let taskText = text
      .replace(/(?:post|create|make|add)\s+(?:an?\s+)?errand\s*/i, '')
      .replace(/(?:at|in|location:)\s+[^,.$]+/i, '')
      .replace(/\$\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:USD|USDC)/i, '')
      .replace(/(?:to|for)\s*/i, '')
      .trim();
    
    details.title = taskText.substring(0, 100); // First 100 chars as title
    details.description = taskText;
    
    // Set deadline to 24 hours from now by default
    const deadline = new Date();
    deadline.setHours(deadline.getHours() + 24);
    details.deadline = deadline.toISOString();
    
    // Detect category based on keywords
    if (text.match(/photo|picture|image/i)) {
      details.category = 'Photography';
    } else if (text.match(/verify|check|confirm/i)) {
      details.category = 'Product Verification';
    } else if (text.match(/price|cost/i)) {
      details.category = 'Price Research';
    } else if (text.match(/interview|survey/i)) {
      details.category = 'Research';
    } else if (text.match(/translate|translation/i)) {
      details.category = 'Translation';
    }
    
    return details;
  }

  /**
   * Post a new errand
   */
  async postErrand(context) {
    try {
      const { message, user } = context;
      
      // Parse errand details from message
      const details = this.parseErrandDetails(message);
      
      // Validate required fields
      if (!details.location) {
        return {
          success: false,
          response: "Please specify a location for the errand. For example: 'Post errand to check prices at Walmart Downtown for $15'"
        };
      }
      
      // Make API request
      const response = await axios.post(
        `${this.apiUrl}/api/openclaw/errands`,
        {
          ...details,
          objective: `Complete task: ${details.title}`,
          validation_criteria: 'Provide clear photo evidence and detailed description',
          metadata: {
            openclawUser: user?.id || 'openclaw_user',
            channel: context.channel,
            timestamp: new Date().toISOString()
          }
        },
        {
          headers: {
            'X-API-Key': this.apiKey,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const errand = response.data.errand;
      
      return {
        success: true,
        response: `✅ Errand posted successfully!\n\n` +
                 `**Title:** ${errand.title}\n` +
                 `**Location:** ${errand.location}\n` +
                 `**Reward:** $${errand.reward_amount} USDC\n` +
                 `**ID:** ${errand.id}\n` +
                 `**URL:** ${errand.url}\n\n` +
                 `Human workers can now accept and complete this task!`
      };
      
    } catch (error) {
      console.error('Error posting errand:', error);
      return {
        success: false,
        response: `Failed to post errand: ${error.response?.data?.error || error.message}`
      };
    }
  }

  /**
   * List user's errands
   */
  async listErrands(context) {
    try {
      // This would need an endpoint to list errands by agent
      // For now, return a placeholder
      return {
        success: true,
        response: "Errand listing feature coming soon! Use 'check errand <ID>' to check specific errands."
      };
    } catch (error) {
      return {
        success: false,
        response: `Failed to list errands: ${error.message}`
      };
    }
  }

  /**
   * Check errand status
   */
  async checkErrand(context) {
    try {
      const { message } = context;
      
      // Extract errand ID
      const idMatch = message.match(/\b(err_\w+|\w{8}-\w{4}-\w{4}-\w{4}-\w{12})\b/);
      if (!idMatch) {
        return {
          success: false,
          response: "Please provide an errand ID. For example: 'check errand err_123456'"
        };
      }
      
      const errandId = idMatch[1];
      
      // Make API request
      const response = await axios.get(
        `${this.apiUrl}/api/openclaw/errands/${errandId}`,
        {
          headers: {
            'X-API-Key': this.apiKey
          }
        }
      );
      
      const errand = response.data.errand;
      
      let statusMessage = `📋 **Errand Status**\n\n` +
                         `**Title:** ${errand.title}\n` +
                         `**Status:** ${errand.status}\n` +
                         `**Reward:** $${errand.reward_amount} USDC\n` +
                         `**Submissions:** ${errand.submissions_count}\n`;
      
      if (errand.submissions && errand.submissions.length > 0) {
        statusMessage += '\n**Recent Submissions:**\n';
        errand.submissions.forEach((sub, index) => {
          statusMessage += `${index + 1}. ${sub.status} - Score: ${sub.validation_score || 'N/A'}/100\n`;
        });
      }
      
      return {
        success: true,
        response: statusMessage
      };
      
    } catch (error) {
      console.error('Error checking errand:', error);
      return {
        success: false,
        response: `Failed to check errand: ${error.response?.data?.error || error.message}`
      };
    }
  }

  /**
   * Review a submission
   */
  async reviewSubmission(context) {
    try {
      const { message } = context;
      
      // Extract submission ID
      const idMatch = message.match(/\b(sub_\w+|\w{8}-\w{4}-\w{4}-\w{4}-\w{12})\b/);
      if (!idMatch) {
        return {
          success: false,
          response: "Please provide a submission ID. For example: 'approve submission sub_789'"
        };
      }
      
      const submissionId = idMatch[1];
      
      // Determine if approving or rejecting
      const isApproval = message.match(/approve/i);
      
      // Extract feedback if provided
      const feedbackMatch = message.match(/(?:feedback|reason|note):\s*(.+)/i);
      const feedback = feedbackMatch ? feedbackMatch[1] : null;
      
      // Make API request
      const response = await axios.post(
        `${this.apiUrl}/api/openclaw/submissions/${submissionId}/review`,
        {
          approved: !!isApproval,
          feedback: feedback || (isApproval ? 'Approved via OpenClaw' : 'Rejected via OpenClaw')
        },
        {
          headers: {
            'X-API-Key': this.apiKey,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return {
        success: true,
        response: isApproval 
          ? `✅ Submission approved! Payment has been released to the worker.`
          : `❌ Submission rejected. Worker has been notified with feedback.`
      };
      
    } catch (error) {
      console.error('Error reviewing submission:', error);
      return {
        success: false,
        response: `Failed to review submission: ${error.response?.data?.error || error.message}`
      };
    }
  }

  /**
   * Process incoming message
   */
  async processMessage(context) {
    const { message } = context;
    
    // Check for post errand intent
    if (this.patterns.postErrand.test(message)) {
      return await this.postErrand(context);
    }
    
    // Check for check errand intent
    if (this.patterns.checkErrand.test(message)) {
      return await this.checkErrand(context);
    }
    
    // Check for list errands intent
    if (this.patterns.listErrands.test(message)) {
      return await this.listErrands(context);
    }
    
    // Check for approve/reject submission
    if (this.patterns.approveSubmission.test(message) || this.patterns.rejectSubmission.test(message)) {
      return await this.reviewSubmission(context);
    }
    
    // No matching intent
    return null;
  }
}

// Export for OpenClaw
module.exports = ErrandAISkill;