/**
 * @module interchange
 * Generate ops/ and state/ interchange .md files from CRM DB.
 * ops/ files contain ZERO deal values, contact info, or user data.
 */
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeMd } from '../../interchange/src/index.js';
import { generatePipelineReport } from './reports.js';
import { listDueFollowups } from './followups.js';
import { getContact } from './contacts.js';
import { listActivities } from './activities.js';
import { getSchemaVersion } from './db.js';
import fs from 'node:fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const INTERCHANGE_DIR = path.join(__dirname, '..', 'interchange', 'crm');

const BASE_META = {
  skill: 'crm',
  generator: 'crm@1.0.0',
  version: 1,
};

/**
 * Refresh all interchange files.
 * @param {import('better-sqlite3').Database} db
 */
export async function refreshInterchange(db) {
  await writeCapabilities(db);
  await writeSchemas(db);
  await writePipeline(db);
  await writeFollowUps(db);
  await writeDealFiles(db);
}

async function writeCapabilities(db) {
  const version = getSchemaVersion(db);
  const meta = { ...BASE_META, type: 'summary', layer: 'ops', tags: ['capabilities', 'reference'] };
  const content = `# CRM Capabilities

## Schema Version
${version}

## Supported Stages
prospect, qualified, proposal, negotiation, closed-won, closed-lost

## Commands
- \`crm lead add\` — Add a contact
- \`crm lead list\` — List contacts
- \`crm deal add\` — Create a deal
- \`crm deal stage\` — Move deal to new stage
- \`crm deal note\` — Add activity to deal
- \`crm followup add\` — Schedule follow-up
- \`crm followup due\` — List due follow-ups
- \`crm report pipeline\` — Pipeline summary
- \`crm search\` — Full-text search
`;
  await writeMd(path.join(INTERCHANGE_DIR, 'ops', 'capabilities.md'), meta, content);
}

async function writeSchemas(db) {
  const version = getSchemaVersion(db);
  const migrations = db.prepare('SELECT version, name, applied_at FROM _migrations ORDER BY version ASC').all();
  const meta = { ...BASE_META, type: 'summary', layer: 'ops', tags: ['schema'] };

  let content = `# CRM Schemas\n\n## Current Version\n${version}\n\n## Applied Migrations\n`;
  for (const m of migrations) {
    content += `- v${m.version}: ${m.name} (applied ${m.applied_at})\n`;
  }
  await writeMd(path.join(INTERCHANGE_DIR, 'ops', 'schemas.md'), meta, content);
}

async function writePipeline(db) {
  const meta = { ...BASE_META, type: 'detail', layer: 'state', tags: ['pipeline', 'overview'] };
  const content = generatePipelineReport(db);
  await writeMd(path.join(INTERCHANGE_DIR, 'state', 'pipeline.md'), meta, content);
}

async function writeFollowUps(db) {
  const followups = listDueFollowups(db, 7);
  const meta = { ...BASE_META, type: 'detail', layer: 'state', tags: ['followups'] };
  const now = new Date().toISOString().slice(0, 10);

  let content = '# Follow-Ups\n\nDue or overdue in the next 7 days.\n\n';
  if (followups.length === 0) {
    content += 'No follow-ups due.\n';
  } else {
    content += '| Due Date | Status | Deal | Note |\n| --- | --- | --- | --- |\n';
    for (const fu of followups) {
      const status = fu.due_date < now ? 'Overdue' : 'Due';
      content += `| ${fu.due_date} | ${status} | ${fu.deal_title || '-'} | ${fu.note || '-'} |\n`;
    }
  }
  await writeMd(path.join(INTERCHANGE_DIR, 'state', 'follow-ups.md'), meta, content);
}

async function writeDealFiles(db) {
  const deals = db.prepare(
    "SELECT * FROM deals WHERE stage IN ('prospect','qualified','proposal','negotiation')"
  ).all();

  const dealsDir = path.join(INTERCHANGE_DIR, 'state', 'deals');
  fs.mkdirSync(dealsDir, { recursive: true });

  for (const deal of deals) {
    const slug = deal.title.toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
      .slice(0, 50) + '-' + deal.id.substring(0, 8);

    const contact = deal.contact_id ? getContact(db, deal.contact_id) : null;
    const activities = listActivities(db, deal.id);
    const tags = db.prepare('SELECT tag FROM tags WHERE deal_id = ? ORDER BY tag').all(deal.id).map(t => t.tag);

    const meta = { ...BASE_META, type: 'detail', layer: 'state', deal_id: deal.id, tags: ['deal'] };

    let content = `# ${deal.title}\n\n`;
    content += `**Stage:** ${deal.stage} | **Value:** $${deal.value} | **Source:** ${deal.source || 'Direct'}\n\n`;

    if (contact) {
      content += `## Contact\n- **Name:** ${contact.name}\n- **Company:** ${contact.company || '-'}\n- **Email:** ${contact.email || '-'}\n\n`;
    }

    content += `## Activities\n`;
    if (activities.length === 0) {
      content += 'No activities logged.\n';
    } else {
      for (const a of activities) {
        content += `- ${a.timestamp} **${a.type}**: ${a.content}\n`;
      }
    }

    content += `\n## Tags\n${tags.length > 0 ? tags.join(', ') : 'None'}\n`;

    await writeMd(path.join(dealsDir, `${slug}.md`), meta, content);
  }
}
