/**
 * MailCheck Email Verification Skill
 * Main entry point
 */

'use strict';

const { skill, command, tool, parameter } = require('openclaw');

// Email verification command
command(
  'email-verify',
  'Verify a single email address',
  [
    parameter('email', 'string', 'Email address to verify'),
    parameter('api_key', 'string', 'MailCheck API key (falls back to env MAILCHECK_API_KEY)')
  ],
  async (ctx) => {
    const { email, api_key } = ctx.args;
    
    if (!email) {
      return { error: 'Email address is required' };
    }
    
    const apiKey = api_key || process.env.MAILCHECK_API_KEY;
    
    if (!apiKey) {
      return { error: 'API key required. Set MAILCHECK_API_KEY env var or provide api_key parameter.' };
    }
    
    try {
      const response = await fetch('https://api.mailcheck.dev/v1/verify', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'API request failed', raw: data };
      }
      
      return {
        success: true,
        email: data.email,
        valid: data.valid,
        score: data.score,
        reason: data.reason,
        risk_level: data.details?.risk_level,
        checks: data.checks,
        details: data.details,
      };
    } catch (error) {
      return { error: 'Failed to verify email', message: error.message };
    }
  }
);

// Bulk verification command
command(
  'email-bulk-verify',
  'Verify multiple email addresses (up to 100)',
  [
    parameter('emails', 'string[]', 'Array of email addresses'),
    parameter('api_key', 'string', 'MailCheck API key')
  ],
  async (ctx) => {
    const { emails, api_key } = ctx.args;
    
    if (!emails || !Array.isArray(emails)) {
      return { error: 'Emails array is required' };
    }
    
    if (emails.length > 100) {
      return { error: 'Maximum 100 emails allowed per request' };
    }
    
    const apiKey = api_key || process.env.MAILCHECK_API_KEY;
    
    if (!apiKey) {
      return { error: 'API key required' };
    }
    
    try {
      const response = await fetch('https://api.mailcheck.dev/v1/verify/bulk', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ emails }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'API request failed', raw: data };
      }
      
      return {
        success: true,
        results: data.results,
        total: data.total,
        unique_verified: data.unique_verified,
        credits_remaining: data.credits_remaining,
        summary: {
          valid: data.results.filter(r => r.valid).length,
          invalid: data.results.filter(r => !r.valid).length,
        }
      };
    } catch (error) {
      return { error: 'Failed to verify emails', message: error.message };
    }
  }
);

// Authenticity analysis command
command(
  'email-auth-verify',
  'Analyze email headers for authenticity (SPF/DKIM/DMARC, phishing detection)',
  [
    parameter('headers', 'string', 'Email headers to analyze'),
    parameter('trusted_domains', 'string[]', 'Optional: trusted domains for lookalike detection'),
    parameter('api_key', 'string', 'MailCheck API key')
  ],
  async (ctx) => {
    const { headers, trusted_domains, api_key } = ctx.args;
    
    if (!headers) {
      return { error: 'Email headers are required' };
    }
    
    const apiKey = api_key || process.env.MAILCHECK_API_KEY;
    
    if (!apiKey) {
      return { error: 'API key required' };
    }
    
    try {
      const response = await fetch('https://api.mailcheck.dev/v1/verify/auth', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          headers,
          trusted_domains: trusted_domains || []
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'API request failed', raw: data };
      }
      
      return {
        success: true,
        trust_score: data.trust_score,
        verdict: data.verdict,
        from: data.from,
        authentication: data.authentication,
        anomalies: data.anomalies,
        lookalike: data.lookalike,
        privacy: data.privacy,
      };
    } catch (error) {
      return { error: 'Failed to analyze email', message: error.message };
    }
  }
);

module.exports = { name: 'mailcheck-email-verification', version: '1.0.0' };
