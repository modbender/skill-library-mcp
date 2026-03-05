/**
 * LinkedIn API - Browser Automation Module
 * Uses Playwright for LinkedIn interactions
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONFIG_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'linkedin-outreach');
const SESSION_FILE = path.join(CONFIG_DIR, 'session.json');
const DATA_FILE = path.join(CONFIG_DIR, 'data.json');

class LinkedInAPI {
  constructor() {
    this.browser = null;
    this.context = null;
    this.page = null;
    this.isLoggedIn = false;
    this.data = this.loadData();
  }

  ensureConfigDir() {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
  }

  loadData() {
    this.ensureConfigDir();
    if (fs.existsSync(DATA_FILE)) {
      try {
        return JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
      } catch {
        return { contacts: [], connections: [], pending: [] };
      }
    }
    return { contacts: [], connections: [], pending: [] };
  }

  saveData() {
    this.ensureConfigDir();
    fs.writeFileSync(DATA_FILE, JSON.stringify(this.data, null, 2));
  }

  async initBrowser(headless = false) {
    this.browser = await chromium.launch({ 
      headless,
      args: ['--disable-blink-features=AutomationControlled']
    });
    
    // Try to load existing session
    const session = this.loadSession();
    if (session) {
      this.context = await this.browser.newContext({
        storageState: session
      });
    } else {
      this.context = await this.browser.newContext();
    }
    
    this.page = await this.context.newPage();
    
    // Set realistic viewport
    await this.page.setViewportSize({ width: 1280, height: 800 });
    
    return this.page;
  }

  loadSession() {
    if (fs.existsSync(SESSION_FILE)) {
      try {
        return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
      } catch {
        return null;
      }
    }
    return null;
  }

  saveSession() {
    if (this.context) {
      this.ensureConfigDir();
      this.context.storageState().then(state => {
        fs.writeFileSync(SESSION_FILE, JSON.stringify(state));
      });
    }
  }

  async login(email, password) {
    if (!this.browser) {
      await this.initBrowser(false);
    }

    console.log('🔐 Opening LinkedIn login page...');
    await this.page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle' });

    console.log('📝 Entering credentials...');
    await this.page.fill('#username', email);
    await this.page.fill('#password', password);
    await this.page.click('[type="submit"]');

    // Wait for login to complete
    try {
      await this.page.waitForURL('**/feed/**', { timeout: 30000 });
      console.log('✅ Login successful!');
      this.isLoggedIn = true;
      this.saveSession();
      return true;
    } catch (e) {
      // Check if 2FA is required
      const url = this.page.url();
      if (url.includes('checkpoint')) {
        console.log('⚠️  2FA required. Please complete verification in the browser, then press Enter.');
        await this.page.waitForURL('**/feed/**', { timeout: 300000 }); // 5 min for 2FA
        this.isLoggedIn = true;
        this.saveSession();
        return true;
      }
      console.log('❌ Login failed. Please check credentials.');
      return false;
    }
  }

  async searchPeople(options = {}) {
    const { keywords = '', location = '', company = '', title = '', limit = 10 } = options;
    
    if (!this.isLoggedIn) {
      throw new Error('Not logged in. Please run login first.');
    }

    console.log(`🔍 Searching for: ${keywords} ${location ? `in ${location}` : ''}`);
    
    // Build search URL
    let searchUrl = 'https://www.linkedin.com/search/results/people/?';
    const params = new URLSearchParams();
    
    if (keywords) params.append('keywords', keywords);
    if (location) params.append('geoUrn', this.locationToGeoUrn(location));
    if (company) params.append('companyUrn', this.companyToCompanyUrn(company));
    if (title) params.append('titleScene', title);
    
    searchUrl += params.toString();
    
    await this.page.goto(searchUrl, { waitUntil: 'networkidle' });
    await this.page.waitForTimeout(2000);

    // Extract people results
    const results = await this.page.evaluate((limit) => {
      const people = [];
      const items = document.querySelectorAll('.reusable-search__result-container');
      
      for (let i = 0; i < Math.min(items.length, limit); i++) {
        const item = items[i];
        const nameEl = item.querySelector('.entity-result__title-text');
        const subtitleEl = item.querySelector('.entity-result__subtitle');
        const metaEl = item.querySelector('.entity-result__meta');
        const urnEl = item.querySelector('[data-test-app-aware-link]');
        
        if (nameEl) {
          people.push({
            name: nameEl.textContent?.trim() || '',
            subtitle: subtitleEl?.textContent?.trim() || '',
            location: metaEl?.textContent?.trim() || '',
            urn: urnEl?.href?.match(/urn:li:member:\d+/)?.[0] || '',
            profileUrl: urnEl?.href || ''
          });
        }
      }
      return people;
    }, limit);

    console.log(`📋 Found ${results.length} results`);
    
    // Save to data
    this.data.contacts = [...this.data.contacts, ...results];
    this.saveData();
    
    return results;
  }

  async sendConnectionRequest(urn, message = '') {
    if (!this.isLoggedIn) {
      throw new Error('Not logged in.');
    }

    console.log(`➕ Sending connection request to ${urn}...`);
    
    // Navigate to profile
    const profileUrl = `https://www.linkedin.com/in/${urn.replace('urn:li:member:', '')}/`;
    await this.page.goto(profileUrl, { waitUntil: 'networkidle' });
    await this.page.waitForTimeout(1500);

    // Find and click connect button
    try {
      // Try different selectors for connect button
      const connectButton = await this.page.$('button:has-text("Connect")') || 
                           await this.page.$('button[aria-label*="Connect"]') ||
                           await this.page.$('.pv-top-card-v2-cta button');
      
      if (connectButton) {
        await connectButton.click();
        await this.page.waitForTimeout(500);
        
        // If message is provided, add it
        if (message) {
          const addNoteButton = await this.page.$('button:has-text("Add a note")');
          if (addNoteButton) {
            await addNoteButton.click();
            await this.page.waitForTimeout(300);
            await this.page.fill('textarea[name="message"]', message);
          }
        }
        
        // Send the request
        const sendButton = await this.page.$('button:has-text("Send")') ||
                          await this.page.$('button[aria-label*="Send"]');
        if (sendButton) {
          await sendButton.click();
          await this.page.waitForTimeout(1000);
        }
        
        console.log(`✅ Connection request sent to ${urn}`);
        
        // Record in data
        this.data.pending.push({
          urn,
          message,
          sentAt: new Date().toISOString()
        });
        this.saveData();
        
        return true;
      }
    } catch (e) {
      console.log(`❌ Failed to send request to ${urn}: ${e.message}`);
    }
    
    return false;
  }

  async sendBulkConnectionRequests(urns, message = '') {
    const results = [];
    
    for (const urn of urns) {
      const success = await this.sendConnectionRequest(urn, message);
      results.push({ urn, success });
      
      // Rate limiting - wait between requests
      await this.page.waitForTimeout(2000 + Math.random() * 1000);
    }
    
    return results;
  }

  async sendFollowUpMessage(urn, message) {
    if (!this.isLoggedIn) {
      throw new Error('Not logged in.');
    }

    console.log(`💬 Sending follow-up to ${urn}...`);
    
    // Navigate to messaging
    await this.page.goto('https://www.linkedin.com/messaging/', { waitUntil: 'networkidle' });
    await this.page.waitForTimeout(1500);

    // Find the conversation
    const conversations = await this.page.$$('.msg-conversation-list-item');
    
    for (const conv of conversations) {
      const name = await conv.$('.msg-conversation-list-item__name');
      if (name) {
        const text = await name.textContent();
        // Check if this is the right conversation
        // For now, we'll open a new message
        
        // Click compose new message
        await this.page.click('[data-test-modal-trigger]');
        await this.page.waitForTimeout(500);
        
        // Search for the person
        await this.page.fill('.msg-compose-form__recipients-input input', urn);
        await this.page.waitForTimeout(500);
        
        // Select from dropdown
        const selectItem = await this.page.$('.typeahead__item');
        if (selectItem) {
          await selectItem.click();
          await this.page.waitForTimeout(300);
        }
        
        // Type message
        await this.page.fill('.msg-compose-form__message-editor', message);
        
        // Send
        await this.page.click('.msg-compose-form__send-button');
        await this.page.waitForTimeout(1000);
        
        console.log(`✅ Follow-up sent to ${urn}`);
        return true;
      }
    }
    
    console.log(`⚠️  Could not find conversation for ${urn}`);
    return false;
  }

  generateReport(format = 'csv', filter = 'all') {
    let contacts = [];
    
    switch (filter) {
      case 'pending':
        contacts = this.data.pending;
        break;
      case 'connected':
        contacts = this.data.connections;
        break;
      default:
        contacts = this.data.contacts;
    }

    if (format === 'json') {
      return JSON.stringify(contacts, null, 2);
    }

    // CSV format
    const headers = ['Name', 'URN', 'Profile URL', 'Message', 'Sent At'];
    const rows = contacts.map(c => [
      c.name || '',
      c.urn || '',
      c.profileUrl || '',
      c.message || '',
      c.sentAt || ''
    ]);

    return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  // Helper methods
  locationToGeoUrn(location) {
    // Simplified - would need proper geo URN mapping
    const geoMap = {
      'san francisco': 'urn:li:geo:102221843',
      'new york': 'urn:li:geo:102257491',
      'los angeles': 'urn:li:geo:102264491',
      'chicago': 'urn:li:geo:102272359'
    };
    return geoMap[location.toLowerCase()] || '';
  }

  companyToCompanyUrn(company) {
    // Would need company search to get URN
    return '';
  }
}

export default LinkedInAPI;
