/**
 * Email Verification Helper (IMAP)
 * 
 * ⚠️ USER MUST PROVIDE THEIR OWN EMAIL CREDENTIALS
 * 
 * Recommended: Create a dedicated email for directory submissions
 * e.g., submissions@yourdomain.com or yourproduct.submissions@gmail.com
 * 
 * This allows the agent to:
 * - Check for verification emails
 * - Extract verification links
 * - Click to verify automatically
 */

const Imap = require('imap');
const { simpleParser } = require('mailparser');

class EmailVerifier {
  constructor(config) {
    this.config = {
      user: config.user || process.env.IMAP_USER,
      password: config.password || process.env.IMAP_PASSWORD,
      host: config.host || process.env.IMAP_HOST || 'imap.gmail.com',
      port: config.port || process.env.IMAP_PORT || 993,
      tls: true,
    };

    if (!this.config.user || !this.config.password) {
      throw new Error(
        'Email credentials not set.\n\n' +
        'To enable automatic email verification:\n' +
        '1. Create a dedicated email for submissions (recommended)\n' +
        '2. For Gmail: Enable "App Passwords" in Google Account settings\n' +
        '3. Set environment variables:\n' +
        '   export IMAP_USER="yourproduct.submissions@gmail.com"\n' +
        '   export IMAP_PASSWORD="your-app-password"\n' +
        '   export IMAP_HOST="imap.gmail.com"  # optional, gmail is default\n\n' +
        'Or skip this - agent will ask you to verify emails manually.'
      );
    }
  }

  /**
   * Connect to IMAP server
   */
  connect() {
    return new Promise((resolve, reject) => {
      this.imap = new Imap(this.config);
      
      this.imap.once('ready', () => resolve());
      this.imap.once('error', (err) => reject(err));
      
      this.imap.connect();
    });
  }

  /**
   * Disconnect from IMAP server
   */
  disconnect() {
    if (this.imap) {
      this.imap.end();
    }
  }

  /**
   * Search for verification emails from a directory
   * @param {string} fromDomain - Domain to search for (e.g., 'futurepedia.io')
   * @param {number} maxAgeMinutes - Only look at emails from last N minutes
   */
  async findVerificationEmail(fromDomain, maxAgeMinutes = 30) {
    return new Promise((resolve, reject) => {
      this.imap.openBox('INBOX', false, (err, box) => {
        if (err) return reject(err);

        const since = new Date();
        since.setMinutes(since.getMinutes() - maxAgeMinutes);

        const searchCriteria = [
          ['SINCE', since],
          ['FROM', fromDomain],
        ];

        this.imap.search(searchCriteria, (err, results) => {
          if (err) return reject(err);
          if (!results || results.length === 0) {
            return resolve(null);
          }

          // Get the most recent matching email
          const latestUid = results[results.length - 1];
          const fetch = this.imap.fetch([latestUid], { bodies: '' });

          fetch.on('message', (msg) => {
            msg.on('body', (stream) => {
              simpleParser(stream, (err, parsed) => {
                if (err) return reject(err);
                resolve({
                  from: parsed.from?.text,
                  subject: parsed.subject,
                  text: parsed.text,
                  html: parsed.html,
                  links: this.extractLinks(parsed.html || parsed.text),
                });
              });
            });
          });

          fetch.once('error', reject);
        });
      });
    });
  }

  /**
   * Extract verification links from email content
   */
  extractLinks(content) {
    if (!content) return [];
    
    const linkRegex = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g;
    const links = content.match(linkRegex) || [];
    
    // Filter for likely verification links
    const verificationKeywords = ['verify', 'confirm', 'activate', 'validate', 'click'];
    return links.filter(link => {
      const lowerLink = link.toLowerCase();
      return verificationKeywords.some(keyword => lowerLink.includes(keyword));
    });
  }

  /**
   * Wait for verification email and return link
   * @param {string} fromDomain - Domain to watch for
   * @param {number} timeoutMinutes - How long to wait
   * @param {number} checkIntervalSeconds - How often to check
   */
  async waitForVerificationLink(fromDomain, timeoutMinutes = 10, checkIntervalSeconds = 30) {
    const startTime = Date.now();
    const timeout = timeoutMinutes * 60 * 1000;

    while (Date.now() - startTime < timeout) {
      const email = await this.findVerificationEmail(fromDomain);
      
      if (email && email.links.length > 0) {
        return {
          found: true,
          link: email.links[0],
          subject: email.subject,
          allLinks: email.links,
        };
      }

      // Wait before checking again
      await new Promise(r => setTimeout(r, checkIntervalSeconds * 1000));
    }

    return {
      found: false,
      message: `No verification email from ${fromDomain} found within ${timeoutMinutes} minutes`,
    };
  }
}

module.exports = { EmailVerifier };

/**
 * SETUP INSTRUCTIONS FOR GMAIL:
 * 
 * 1. Create a new Gmail account (recommended) or use existing
 *    e.g., yourproduct.listings@gmail.com
 * 
 * 2. Enable 2-Factor Authentication:
 *    Google Account → Security → 2-Step Verification → Turn on
 * 
 * 3. Create App Password:
 *    Google Account → Security → App passwords → Generate
 *    Select "Mail" and "Other (Custom name)" → Generate
 *    Copy the 16-character password
 * 
 * 4. Set environment variables:
 *    export IMAP_USER="yourproduct.listings@gmail.com"
 *    export IMAP_PASSWORD="xxxx xxxx xxxx xxxx"  # the app password
 *    export IMAP_HOST="imap.gmail.com"
 * 
 * For other email providers:
 * - Outlook: imap-mail.outlook.com
 * - Yahoo: imap.mail.yahoo.com
 * - Custom domain: Check with your email provider
 */
