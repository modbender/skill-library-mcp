const Imap = require('imap');
const { simpleParser } = require('mailparser');

class ImapClient {
  constructor(config) {
    this.config = config;
    this.imap = null;
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.imap = new Imap({
        ...this.config,
        connTimeout: 10000,
        authTimeout: 10000
      });

      this.imap.once('ready', () => resolve());
      this.imap.once('error', (err) => reject(new Error(`IMAP connection failed: ${err.message}`)));
      this.imap.connect();
    });
  }

  async disconnect() {
    if (this.imap) {
      this.imap.end();
    }
  }

  async openBox(mailbox = 'INBOX', readOnly = true) {
    return new Promise((resolve, reject) => {
      this.imap.openBox(mailbox, readOnly, (err, box) => {
        if (err) reject(err);
        else resolve(box);
      });
    });
  }

  async search(criteria, mailbox = 'INBOX') {
    await this.openBox(mailbox, true);
    return new Promise((resolve, reject) => {
      this.imap.search(criteria, (err, uids) => {
        if (err) reject(err);
        else resolve(uids || []);
      });
    });
  }

  async fetchMessages(uids, options = {}) {
    if (!uids || uids.length === 0) return [];

    const messages = [];
    const fetch = this.imap.fetch(uids, {
      bodies: '',
      struct: true,
      ...options
    });

    return new Promise((resolve, reject) => {
      fetch.on('message', (msg, seqno) => {
        let buffer = '';
        let attrs = null;

        msg.on('body', (stream) => {
          stream.on('data', (chunk) => {
            buffer += chunk.toString('utf8');
          });
        });

        msg.once('attributes', (a) => {
          attrs = a;
        });

        msg.once('end', async () => {
          try {
            const parsed = await simpleParser(buffer);
            messages.push({
              uid: attrs.uid,
              flags: attrs.flags,
              date: attrs.date,
              subject: parsed.subject,
              from: parsed.from?.text || '',
              to: parsed.to?.text || '',
              text: parsed.text || '',
              html: parsed.html || '',
              attachments: parsed.attachments || []
            });
          } catch (err) {
            console.error(`Error parsing message ${seqno}:`, err.message);
          }
        });
      });

      fetch.once('error', reject);
      fetch.once('end', () => resolve(messages));
    });
  }

  async getUnreadMessages(limit = 10, mailbox = 'INBOX') {
    const uids = await this.search(['UNSEEN'], mailbox);
    const limitedUids = uids.slice(-limit);
    return this.fetchMessages(limitedUids);
  }

  async getRecentMessages(hours = 24, limit = 20, mailbox = 'INBOX') {
    const sinceDate = new Date(Date.now() - hours * 60 * 60 * 1000);
    const uids = await this.search(['SINCE', sinceDate], mailbox);
    const limitedUids = uids.slice(-limit);
    return this.fetchMessages(limitedUids);
  }

  async searchByKeywords(keywords, limit = 50, mailbox = 'INBOX') {
    const allMessages = [];
    
    for (const keyword of keywords) {
      const subjectUids = await this.search(['SUBJECT', keyword], mailbox);
      const bodyUids = await this.search(['BODY', keyword], mailbox);
      const combinedUids = [...new Set([...subjectUids, ...bodyUids])];
      
      if (combinedUids.length > 0) {
        const messages = await this.fetchMessages(combinedUids.slice(-limit));
        allMessages.push(...messages);
      }
    }

    // 중복 제거 (uid 기준)
    const uniqueMessages = Array.from(
      new Map(allMessages.map(m => [m.uid, m])).values()
    );

    return uniqueMessages.slice(-limit);
  }

  async markAsRead(uids, mailbox = 'INBOX') {
    await this.openBox(mailbox, false); // read-write mode
    return new Promise((resolve, reject) => {
      this.imap.addFlags(uids, '\\Seen', (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  async markAsUnread(uids, mailbox = 'INBOX') {
    await this.openBox(mailbox, false);
    return new Promise((resolve, reject) => {
      this.imap.delFlags(uids, '\\Seen', (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
}

module.exports = ImapClient;
