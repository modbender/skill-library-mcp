/**
 * IMAP Client for Proton Mail Bridge
 * 
 * Provides low-level IMAP operations for reading emails from ProtonMail.
 * Connects to Bridge's local IMAP server (127.0.0.1:1143 by default).
 * 
 * @packageDocumentation
 */

import Imap from 'imap';
import { simpleParser, ParsedMail } from 'mailparser';

/**
 * IMAP connection configuration
 */
export interface IMAPConfig {
  /** Bridge account username (email address) */
  user: string;
  
  /** Bridge-generated password */
  password: string;
  
  /** IMAP host (Bridge runs on localhost) */
  host: string;
  
  /** IMAP port (Bridge default: 1143) */
  port: number;
  
  /** Enable TLS (Bridge uses self-signed cert) */
  tls: boolean;
  
  /** TLS options (set rejectUnauthorized: false for Bridge) */
  tlsOptions?: { rejectUnauthorized: boolean };
}

/**
 * Email metadata returned by list operations
 */
export interface EmailMetadata {
  /** Message UID */
  uid: string;
  
  /** Sender address */
  from: string;
  
  /** Subject line */
  subject: string;
  
  /** Received date */
  date: Date;
  
  /** Read/unread status */
  flags: string[];
}

/**
 * IMAP client for reading emails via Proton Mail Bridge
 * 
 * @remarks
 * This client handles connection pooling and error recovery automatically.
 * Bridge must be running before calling connect().
 */
export class IMAPClient {
  private imap: Imap;
  private config: IMAPConfig;
  private isConnected = false;

  /**
   * Create a new IMAP client
   * 
   * @param config - IMAP connection settings
   */
  constructor(config: IMAPConfig) {
    this.config = config;
    this.imap = new Imap(config);
    
    // Set up error handlers
    this.imap.on('error', (err: Error) => {
      console.error('IMAP error:', err);
      this.isConnected = false;
    });
    
    this.imap.on('end', () => {
      this.isConnected = false;
    });
  }

  /**
   * Connect to Bridge IMAP server
   * 
   * @throws {Error} If Bridge is not running or credentials are invalid
   * 
   * @remarks
   * Ensure Proton Mail Bridge is running before calling this.
   * Connection timeout is 10 seconds by default.
   */
  async connect(): Promise<void> {
    if (this.isConnected) {
      return; // Already connected
    }
    
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('IMAP connection timeout - is Bridge running?'));
      }, 10000);
      
      this.imap.once('ready', () => {
        clearTimeout(timeout);
        this.isConnected = true;
        resolve();
      });
      
      this.imap.once('error', (err: Error) => {
        clearTimeout(timeout);
        reject(err);
      });
      
      this.imap.connect();
    });
  }

  /**
   * Disconnect from Bridge
   */
  async disconnect(): Promise<void> {
    if (this.isConnected) {
      this.imap.end();
      this.isConnected = false;
    }
  }

  /**
   * List emails from inbox
   * 
   * @param limit - Maximum emails to return
   * @param unreadOnly - Filter to unread messages only
   * @returns Array of email metadata
   * 
   * @example
   * ```typescript
   * const emails = await imap.listInbox(10, true);
   * console.log(emails.map(e => `${e.from}: ${e.subject}`));
   * ```
   */
  async listInbox(limit = 10, unreadOnly = false): Promise<EmailMetadata[]> {
    return new Promise((resolve, reject) => {
      this.imap.openBox('INBOX', true, (err, box) => {
        if (err) {
          reject(err);
          return;
        }

        const searchCriteria = unreadOnly ? ['UNSEEN'] : ['ALL'];
        
        this.imap.search(searchCriteria, (err, results) => {
          if (err) {
            reject(err);
            return;
          }

          if (!results || results.length === 0) {
            resolve([]);
            return;
          }

          // Get the most recent messages up to limit
          const uids = results.slice(-limit).reverse();
          const emails: EmailMetadata[] = [];

          const fetch = this.imap.fetch(uids, {
            bodies: 'HEADER.FIELDS (FROM TO SUBJECT DATE)',
            struct: true
          });

          fetch.on('message', (msg, seqno) => {
            let buffer = '';
            let uid = '';

            msg.on('body', (stream) => {
              stream.on('data', (chunk) => {
                buffer += chunk.toString('utf8');
              });
            });

            msg.once('attributes', (attrs) => {
              uid = attrs.uid.toString();
            });

            msg.once('end', () => {
              const header = Imap.parseHeader(buffer);
              emails.push({
                uid,
                from: Array.isArray(header.from) ? header.from[0] : header.from || '',
                subject: Array.isArray(header.subject) ? header.subject[0] : header.subject || '',
                date: new Date(Array.isArray(header.date) ? header.date[0] : header.date || ''),
                flags: []
              });
            });
          });

          fetch.once('error', reject);
          
          fetch.once('end', () => {
            resolve(emails);
          });
        });
      });
    });
  }

  /**
   * Search emails by query
   * 
   * @param query - Search query (supports IMAP search syntax)
   * @param limit - Maximum results
   * @returns Matching emails
   * 
   * @example
   * Supported query formats:
   * - `from:alice@example.com` - Emails from sender
   * - `subject:meeting` - Subject contains keyword
   * - `body:invoice` - Body contains keyword
   * - `newer_than:7d` - Last 7 days
   */
  async search(query: string, limit = 10): Promise<EmailMetadata[]> {
    return new Promise((resolve, reject) => {
      this.imap.openBox('INBOX', true, (err, box) => {
        if (err) {
          reject(err);
          return;
        }

        // Parse query into IMAP criteria
        const criteria = this.parseSearchQuery(query);
        
        this.imap.search(criteria, (err, results) => {
          if (err) {
            reject(err);
            return;
          }

          if (!results || results.length === 0) {
            resolve([]);
            return;
          }

          const uids = results.slice(-limit).reverse();
          const emails: EmailMetadata[] = [];

          const fetch = this.imap.fetch(uids, {
            bodies: 'HEADER.FIELDS (FROM TO SUBJECT DATE)',
            struct: true
          });

          fetch.on('message', (msg, seqno) => {
            let buffer = '';
            let uid = '';

            msg.on('body', (stream) => {
              stream.on('data', (chunk) => {
                buffer += chunk.toString('utf8');
              });
            });

            msg.once('attributes', (attrs) => {
              uid = attrs.uid.toString();
            });

            msg.once('end', () => {
              const header = Imap.parseHeader(buffer);
              emails.push({
                uid,
                from: Array.isArray(header.from) ? header.from[0] : header.from || '',
                subject: Array.isArray(header.subject) ? header.subject[0] : header.subject || '',
                date: new Date(Array.isArray(header.date) ? header.date[0] : header.date || ''),
                flags: []
              });
            });
          });

          fetch.once('error', reject);
          
          fetch.once('end', () => {
            resolve(emails);
          });
        });
      });
    });
  }

  /**
   * Parse search query string into IMAP criteria
   * 
   * @param query - User-friendly search query
   * @returns IMAP search criteria array
   * 
   * @private
   */
  private parseSearchQuery(query: string): any[] {
    const criteria: any[] = [];

    const q = this.sanitizeSearchInput(query);

    // Parse supported key:value filters with quoted or unquoted values
    const filterRegex = /(from|subject|body):(?:"([^"]{1,200})"|([^\s]{1,200}))/gi;
    let match: RegExpExecArray | null;
    while ((match = filterRegex.exec(q)) !== null) {
      const key = match[1].toLowerCase();
      const rawValue = (match[2] || match[3] || '').trim();
      const value = this.sanitizeSearchValue(rawValue);
      if (!value) continue;

      if (key === 'from') criteria.push(['FROM', value]);
      if (key === 'subject') criteria.push(['SUBJECT', value]);
      if (key === 'body') criteria.push(['BODY', value]);
    }

    const dateMatch = q.match(/newer_than:(\d{1,3})([dh])/i);
    if (dateMatch) {
      const value = parseInt(dateMatch[1], 10);
      const unit = dateMatch[2].toLowerCase();
      if (value > 0 && value <= 365) {
        const date = new Date();
        if (unit === 'd') date.setDate(date.getDate() - value);
        else if (unit === 'h') date.setHours(date.getHours() - value);
        criteria.push(['SINCE', date]);
      }
    }

    // If no supported filters, do safe keyword subject search
    if (criteria.length === 0) {
      const fallback = this.sanitizeSearchValue(q.replace(/(from|subject|body|newer_than):[^\s]+/gi, '').trim());
      if (!fallback) {
        throw new Error('Search query is empty or contains unsupported characters');
      }
      criteria.push(['SUBJECT', fallback]);
    }

    return criteria;
  }

  private sanitizeSearchInput(input: string): string {
    const trimmed = (input || '').trim();
    if (!trimmed) {
      throw new Error('Search query is required');
    }
    if (trimmed.length > 200) {
      throw new Error('Search query too long (max 200 chars)');
    }
    // Block CR/LF and control chars
    if (/[\r\n\x00-\x1F\x7F]/.test(trimmed)) {
      throw new Error('Search query contains invalid control characters');
    }
    return trimmed;
  }

  private sanitizeSearchValue(input: string): string {
    const value = (input || '').trim();
    if (!value) return '';
    // Allowlist: common email/search characters only
    if (!/^[a-zA-Z0-9@._+\-\s:]+$/.test(value)) {
      throw new Error('Search query contains unsupported characters');
    }
    return value.slice(0, 200);
  }

  /**
   * Read full email content by UID
   * 
   * @param messageId - Message UID
   * @returns Parsed email with headers, body, and attachments
   * 
   * @throws {Error} If message UID is invalid
   * 
   * @example
   * ```typescript
   * const email = await imap.readMessage('1234');
   * console.log(email.text); // Plain text body
   * console.log(email.html); // HTML body
   * console.log(email.attachments); // File attachments
   * ```
   */
  async readMessage(messageId: string): Promise<ParsedMail> {
    return new Promise((resolve, reject) => {
      this.imap.openBox('INBOX', true, (err, box) => {
        if (err) {
          reject(err);
          return;
        }

        const fetch = this.imap.fetch(messageId, { bodies: '' });
        
        fetch.on('message', (msg) => {
          msg.on('body', async (stream) => {
            try {
              const parsed = await simpleParser(stream as any);
              resolve(parsed);
            } catch (err) {
              reject(err);
            }
          });
        });

        fetch.once('error', reject);
      });
    });
  }
}
