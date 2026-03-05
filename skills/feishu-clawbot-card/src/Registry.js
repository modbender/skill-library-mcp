const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const chalk = require('chalk');
const { CardProtocolSchema } = require('./CardProtocol'); // Use Protocol Schema

// Rolodex = Registry
const ROLODEX_FILE = path.resolve(__dirname, '../rolodex.json');
const ROLODEX_BACKUP = path.resolve(__dirname, '../rolodex.json.bak');

class Registry {
  constructor() {
    this.cards = [];
    this.init();
  }

  init() {
    if (!fs.existsSync(ROLODEX_FILE)) {
      this.save([]); // Create empty rolodex if missing
    }
    try {
      const data = fs.readFileSync(ROLODEX_FILE, 'utf8');
      this.cards = JSON.parse(data);
    } catch (e) {
      console.error(chalk.red('FATAL: Rolodex file corrupted. Check backups.'));
      throw e;
    }
  }

  save(cards = this.cards) {
    // Atomic write simulation: write to temp, rename
    const tempFile = ROLODEX_FILE + '.tmp';
    fs.writeFileSync(tempFile, JSON.stringify(cards, null, 2));
    if (fs.existsSync(ROLODEX_FILE)) {
      fs.copyFileSync(ROLODEX_FILE, ROLODEX_BACKUP); // Create backup
    }
    fs.renameSync(tempFile, ROLODEX_FILE);
  }

  add(card) {
    // Strict Protocol Validation (FCC v1)
    const validated = CardProtocolSchema.parse(card);
    
    // Check uniqueness (Feishu ID must be unique)
    if (this.cards.find(c => c.feishu_id === validated.feishu_id)) {
      // Instead of error, let's update if exists? Or strict error?
      // For import, maybe we want to update. For now, strict error to prevent accidental overwrite.
      // User should use 'update' or 'delete' first.
      throw new Error(`Bot with Feishu OpenID ${validated.feishu_id} already exists in your Rolodex.`);
    }

    this.cards.push(validated);
    this.save();
    return validated;
  }

  list() {
    return this.cards;
  }

  get(query) {
    // Query by ID, Name, or FeishuID
    return this.cards.find(c => 
      c.id === query || 
      c.display_name === query || 
      c.feishu_id === query
    );
  }

  update(id, updates) {
    const index = this.cards.findIndex(c => c.id === id);
    if (index === -1) throw new Error(`Card ID ${id} not found.`);

    const current = this.cards[index];
    const merged = { ...current, ...updates, meta: { ...current.meta, updated_at: new Date().toISOString() } };
    
    // Validate merged object (Strict FCC v1)
    const validated = CardProtocolSchema.parse(merged);
    
    this.cards[index] = validated;
    this.save();
    return validated;
  }

  delete(id) {
    const initialLen = this.cards.length;
    this.cards = this.cards.filter(c => c.id !== id);
    if (this.cards.length === initialLen) throw new Error(`Card ID ${id} not found.`);
    this.save();
  }
}

module.exports = new Registry();
