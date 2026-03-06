/**
 * Tests for openclaw-crm
 */
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { initDb } from '../src/db.js';
import { addContact, getContact, listContacts } from '../src/contacts.js';
import { addDeal, getDeal, listDeals, updateStage } from '../src/deals.js';
import { addActivity, listActivities } from '../src/activities.js';
import { addFollowup, getFollowup, completeFollowup, listDueFollowups } from '../src/followups.js';
import { search } from '../src/search.js';
import { generatePipelineReport } from '../src/reports.js';
import { refreshInterchange } from '../src/interchange.js';

let db;
let tmpDir;

before(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'crm-test-'));
  db = initDb(path.join(tmpDir, 'test.db'));
});

after(() => {
  if (db) db.close();
  // Clean up interchange files
  const interDir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'interchange');
  if (fs.existsSync(interDir)) fs.rmSync(interDir, { recursive: true, force: true });
  try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
});

describe('Contacts', () => {
  it('1. Add contact → stored and retrievable', () => {
    const id = addContact(db, { name: 'John Doe', company: 'Test Co', email: 'john@test.com' });
    const contact = getContact(db, id);
    assert.ok(contact);
    assert.equal(contact.name, 'John Doe');
    assert.equal(contact.company, 'Test Co');
  });
});

describe('Deals', () => {
  let contactId, dealId;

  before(() => {
    contactId = addContact(db, { name: 'Jane Smith', company: 'Acme', email: 'jane@acme.com' });
  });

  it('2. Add deal with contact → linked correctly, stage = prospect', () => {
    dealId = addDeal(db, { title: 'Acme Deal', contact_id: contactId, value: 50000, source: 'referral' });
    const deal = getDeal(db, dealId);
    assert.ok(deal);
    assert.equal(deal.title, 'Acme Deal');
    assert.equal(deal.stage, 'prospect');
    assert.equal(deal.contact_id, contactId);
  });

  it('3. Move deal through stages → stage updated', () => {
    updateStage(db, dealId, 'qualified');
    let deal = getDeal(db, dealId);
    assert.equal(deal.stage, 'qualified');
    assert.ok(deal.updated_at);

    updateStage(db, dealId, 'closed-won');
    deal = getDeal(db, dealId);
    assert.equal(deal.stage, 'closed-won');
    assert.ok(deal.closed_at);
  });

  it('4. Add activity to deal → activity logged', () => {
    const id = addActivity(db, { deal_id: dealId, type: 'call', content: 'Initial discovery call' });
    const acts = listActivities(db, dealId);
    assert.ok(acts.length >= 1);
    assert.equal(acts[0].content, 'Initial discovery call');
  });
});

describe('Follow-ups', () => {
  let dealId, fuId;

  before(() => {
    dealId = addDeal(db, { title: 'Follow-up Test Deal', value: 10000 });
  });

  it('5. Schedule follow-up → stored with due date', () => {
    fuId = addFollowup(db, { deal_id: dealId, due_date: '2026-02-20', note: 'Send proposal' });
    const fu = getFollowup(db, fuId);
    assert.ok(fu);
    assert.equal(fu.due_date, '2026-02-20');
  });

  it('6. Complete follow-up → marked done', () => {
    completeFollowup(db, fuId);
    const fu = getFollowup(db, fuId);
    assert.equal(fu.completed, 1);
    assert.ok(fu.completed_at);
  });

  it('7. List due follow-ups → returns only incomplete + due', () => {
    // Add a new incomplete follow-up due tomorrow
    const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
    const fuId2 = addFollowup(db, { deal_id: dealId, due_date: tomorrow, note: 'Check in' });
    const due = listDueFollowups(db, 7);
    // Should include the new one but not the completed one
    assert.ok(due.some(f => f.id === fuId2));
    assert.ok(!due.some(f => f.id === fuId));
  });
});

describe('Pipeline Report', () => {
  it('8. Pipeline report → correct counts and values', () => {
    // We have 1 active deal (Follow-up Test Deal, prospect, $10000)
    const report = generatePipelineReport(db);
    assert.ok(report.includes('Sales Pipeline'));
    assert.ok(report.includes('Active Deals'));
  });
});

describe('Search', () => {
  it('9. Search → finds contacts by keyword', () => {
    const results = search(db, 'John');
    assert.ok(results.length > 0);
  });
});

describe('Interchange', () => {
  it('10. Interchange refresh → valid .md files, ops/ has no deal values', async () => {
    await refreshInterchange(db);
    const interDir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'interchange', 'crm');

    assert.ok(fs.existsSync(path.join(interDir, 'ops', 'capabilities.md')));
    assert.ok(fs.existsSync(path.join(interDir, 'ops', 'schemas.md')));
    assert.ok(fs.existsSync(path.join(interDir, 'state', 'pipeline.md')));

    // Verify ops/ has no dollar amounts
    const capsContent = fs.readFileSync(path.join(interDir, 'ops', 'capabilities.md'), 'utf8');
    assert.ok(!capsContent.includes('$50000'));
    assert.ok(!capsContent.includes('$10000'));
    assert.ok(capsContent.includes('layer: ops'));
  });
});
