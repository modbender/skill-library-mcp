#!/usr/bin/env node

import { Command } from 'commander';
import { initDb } from './db.js';
import { addContact, listContacts, editContact, getContact } from './contacts.js';
import { addDeal, listDeals, updateStage, getDeal } from './deals.js';
import { addTag, getTags } from './tags.js';
import { addActivity } from './activities.js';
import { addFollowup, listDueFollowups, completeFollowup } from './followups.js';
import { search } from './search.js';
import { generatePipelineReport } from './reports.js';
import { refreshInterchange } from './interchange.js';
import { createBackup, restoreFromBackup } from './backup.js';

const program = new Command();
program
  .name('crm')
  .description('Local-first CRM')
  .version('1.0.0');

let db;
try {
  db = initDb();
} catch (error) {
  console.error('Failed to initialize database:', error.message);
  process.exit(1);
}

// Lead (Contacts)
const leadCmd = program.command('lead').description('Contact management');

leadCmd
  .command('add')
  .description('Add a new contact')
  .argument('<name>', 'Contact name')
  .option('-c, --company <company>', 'Company name')
  .option('-e, --email <email>', 'Email address')
  .option('-p, --phone <phone>', 'Phone number')
  .option('-n, --notes <notes>', 'Notes')
  .action((name, options) => {
    try {
      const id = addContact(db, { name, ...options });
      console.log(`Contact added with ID: ${id}`);
    } catch (error) {
      console.error('Error adding contact:', error.message);
      process.exit(1);
    }
  });

leadCmd
  .command('list')
  .description('List contacts')
  .option('-s, --search <query>', 'Search query')
  .action((options) => {
    try {
      const contacts = listContacts(db, options.search);
      if (contacts.length === 0) {
        console.log('No contacts found.');
        return;
      }
      console.log('Contacts:');
      contacts.forEach((c) => {
        console.log(`  ${c.id}: ${c.name}${c.company ? ` (${c.company})` : ''} - ${c.email || 'No email'}`);
        if (c.notes) console.log(`    Notes: ${c.notes}`);
      });
    } catch (error) {
      console.error('Error listing contacts:', error.message);
    }
  });

leadCmd
  .command('edit')
  .description('Edit a contact')
  .argument('<id>', 'Contact ID')
  .option('-c, --company <company>')
  .option('-e, --email <email>')
  .option('-p, --phone <phone>')
  .option('-n, --notes <notes>')
  .action((id, options) => {
    const updates = {};
    if (options.company !== undefined) updates.company = options.company;
    if (options.email !== undefined) updates.email = options.email;
    if (options.phone !== undefined) updates.phone = options.phone;
    if (options.notes !== undefined) updates.notes = options.notes;
    try {
      editContact(db, id, updates);
      console.log(`Contact ${id} updated.`);
    } catch (error) {
      console.error('Error editing contact:', error.message);
      process.exit(1);
    }
  });

// Deal
const dealCmd = program.command('deal').description('Deal management');

dealCmd
  .command('add')
  .description('Add a new deal')
  .argument('<title>', 'Deal title')
  .option('-c, --contact <id>', 'Contact ID')
  .option('-v, --value <value>', 'Deal value', parseFloat, 0)
  .option('-s, --source <source>', 'Deal source')
  .option('--stage <stage>', 'Initial stage', 'prospect')
  .action((title, options) => {
    try {
      const data = { title, value: options.value, source: options.source, stage: options.stage };
      if (options.contact) data.contact_id = options.contact;
      const id = addDeal(db, data);
      console.log(`Deal added with ID: ${id}`);
    } catch (error) {
      console.error('Error adding deal:', error.message);
      process.exit(1);
    }
  });

dealCmd
  .command('list')
  .description('List deals')
  .option('--stage <stage>', 'Filter by stage')
  .option('--tag <tag>', 'Filter by tag')
  .action((options) => {
    try {
      const deals = listDeals(db, { stage: options.stage, tag: options.tag });
      if (deals.length === 0) {
        console.log('No deals found.');
        return;
      }
      console.log('Deals:');
      deals.forEach((d) => {
        console.log(`  ${d.id}: ${d.title} - Stage: ${d.stage}, Value: $${d.value.toLocaleString()}`);
        if (d.contact_id) {
          const contact = getContact(db, d.contact_id);
          if (contact) console.log(`    Contact: ${contact.name} (${contact.company || ''})`);
        }
        const tags = getTags(db, d.id);
        if (tags.length > 0) console.log(`    Tags: ${tags.join(', ')}`);
      });
    } catch (error) {
      console.error('Error listing deals:', error.message);
    }
  });

dealCmd
  .command('stage')
  .description('Update deal stage')
  .argument('<id>', 'Deal ID')
  .argument('<stage>', 'New stage')
  .action((id, stage) => {
    try {
      updateStage(db, id, stage);
      console.log(`Deal ${id} stage updated to ${stage}.`);
    } catch (error) {
      console.error('Error updating stage:', error.message);
      process.exit(1);
    }
  });

dealCmd
  .command('note')
  .description('Add a note/activity to a deal')
  .argument('<id>', 'Deal ID')
  .argument('<content>', 'Note content')
  .option('-t, --type <type>', 'Activity type', 'note')
  .action((id, content, options) => {
    try {
      addActivity(db, { deal_id: id, type: options.type, content });
      console.log(`Activity added to deal ${id}.`);
    } catch (error) {
      console.error('Error adding activity:', error.message);
      process.exit(1);
    }
  });

dealCmd
  .command('tag')
  .description('Add a tag to a deal')
  .argument('<id>', 'Deal ID')
  .argument('<tag>', 'Tag name')
  .action((id, tag) => {
    try {
      addTag(db, id, tag);
      console.log(`Tag '${tag}' added to deal ${id}.`);
    } catch (error) {
      console.error('Error adding tag:', error.message);
      process.exit(1);
    }
  });

// Follow-up
const followupCmd = program.command('followup').description('Follow-up management');

followupCmd
  .command('add')
  .description('Add a follow-up')
  .argument('<deal-id>', 'Deal ID')
  .requiredOption('-d, --date <date>', 'Due date (YYYY-MM-DD)')
  .option('-n, --note <note>', 'Follow-up note')
  .action((dealId, options) => {
    try {
      const id = addFollowup(db, { deal_id: dealId, due_date: options.date, note: options.note });
      console.log(`Follow-up added with ID: ${id}`);
    } catch (error) {
      console.error('Error adding follow-up:', error.message);
      process.exit(1);
    }
  });

followupCmd
  .command('due')
  .description('List due follow-ups')
  .option('--days <days>', 'Days from now', '0', parseInt)
  .action((options) => {
    try {
      const followups = listDueFollowups(db, options.days);
      if (followups.length === 0) {
        console.log('No due follow-ups.');
        return;
      }
      console.log('Due follow-ups:');
      followups.forEach((fu) => {
        const status = fu.due_date < new Date().toISOString().split('T')[0] ? 'OVERDUE' : 'Due';
        console.log(`  ${fu.id}: ${status} on ${fu.due_date} for "${fu.deal_title}" (${fu.contact_name || 'No contact'}) - ${fu.note || 'No note'}`);
      });
    } catch (error) {
      console.error('Error listing follow-ups:', error.message);
    }
  });

followupCmd
  .command('complete')
  .description('Complete a follow-up')
  .argument('<id>', 'Follow-up ID')
  .action((id) => {
    try {
      completeFollowup(db, parseInt(id));
      console.log(`Follow-up ${id} completed.`);
    } catch (error) {
      console.error('Error completing follow-up:', error.message);
      process.exit(1);
    }
  });

// Report
const reportCmd = program.command('report').description('Reports');

reportCmd
  .command('pipeline')
  .description('Generate pipeline report')
  .action(() => {
    try {
      const report = generatePipelineReport(db);
      console.log(report);
    } catch (error) {
      console.error('Error generating report:', error.message);
    }
  });

// Search
program
  .command('search')
  .description('Search contacts and deals')
  .argument('<query>', 'Search query')
  .action((query) => {
    try {
      const results = search(db, query);
      if (results.length === 0) {
        console.log('No results found.');
        return;
      }
      console.log('Search results:');
      results.forEach((r) => {
        if (r.type === 'contact') {
          console.log(`  Contact ${r.id}: ${r.title} (${r.company || 'N/A'}) - ${r.email || ''}`);
        } else {
          console.log(`  Deal ${r.id}: ${r.title}`);
        }
      });
    } catch (error) {
      console.error('Error searching:', error.message);
      process.exit(1);
    }
  });

// Refresh
program
  .command('refresh')
  .description('Refresh interchange files')
  .action(() => {
    try {
      refreshInterchange(db);
    } catch (error) {
      console.error('Error refreshing interchange:', error.message);
      process.exit(1);
    }
  });

// Backup
program
  .command('backup')
  .description('Create DB backup')
  .option('-o, --output <path>', 'Output file path (default: data/crm-backup-YYYY-MM-DD.db)')
  .action((options) => {
    try {
      const dbBase = join(process.cwd(), 'data', 'crm');
      let outPath;
      if (options.output) {
        const outputPath = options.output.startsWith('/') ? options.output : join(process.cwd(), options.output);
        const baseOut = outputPath.endsWith('.db') ? outputPath.slice(0, -3) : outputPath;
        copyDbFiles(dbBase, baseOut);
        outPath = baseOut + '.db';
      } else {
        outPath = createBackup(dbBase);
      }
      console.log(`Backup created: ${outPath}`);
    } catch (error) {
      console.error('Error creating backup:', error.message);
      process.exit(1);
    }
  });

// Restore
program
  .command('restore')
  .description('Restore from backup')
  .argument('<file>', 'Backup file path')
  .action((file) => {
    try {
      const dbBase = join(process.cwd(), 'data', 'crm');
      restoreFromBackup(dbBase, file);
    } catch (error) {
      console.error('Error restoring:', error.message);
      process.exit(1);
    }
  });

program.parse(process.argv);

if (process.argv.length <= 2) {
  program.help();
}