#!/usr/bin/env node
/**
 * LeadFlow CLI
 */

import { Command } from 'commander';
import { config, hasApiKey } from './config/index.js';
import { initDatabase, closeDatabase } from './storage/sqlite.client.js';
import {
  findLeads,
  countLeadsByStatus,
  countLeadsBySource,
  countLeadsByTrade,
  getTotalLeadCount,
  updateLead,
} from './storage/lead.repository.js';
import { persistChanges } from './storage/index.js';
import { runScrape, getScrapableSources } from './orchestrator/scrape.orchestrator.js';
import {
  exportToXlsx,
  exportToCsv,
  exportToInstantly,
  exportToHubspot,
  exportToSalesforce,
  exportToPipedrive,
  exportToAirtable,
} from './export/xlsx.exporter.js';
import { enrichAllLeads, getEnrichmentStatus } from './enrichment/enrichment.service.js';
import { isZeroBounceConfigured, batchVerifyEmails } from './enrichment/zerobounce.client.js';
import { isTwilioConfigured, batchValidatePhones } from './enrichment/twilio.client.js';
import { scoreAllLeads } from './scoring/lead-scorer.js';
import { sendLeadsToWebhook } from './webhooks/webhook.service.js';
import { Trade, LeadSource, LeadStatus } from './types/index.js';

const program = new Command();

program
  .name('leadflow')
  .description('Business lead generation - Google Maps & Yelp with enrichment, verification, scoring, and CRM export')
  .version('1.0.0')
  .option('--json', 'Output results as JSON (for agent/automation use)', false);

/** Trade key -> enum mapping */
const tradeMap: Record<string, Trade> = {
  hvac: Trade.HVAC,
  plumbing: Trade.PLUMBING,
  electrical: Trade.ELECTRICAL,
  roofing: Trade.ROOFING,
  general: Trade.GENERAL,
  landscaping: Trade.LANDSCAPING,
  pest: Trade.PEST_CONTROL,
  cleaning: Trade.CLEANING,
  painting: Trade.PAINTING,
  flooring: Trade.FLOORING,
  fencing: Trade.FENCING,
  tree: Trade.TREE_SERVICE,
  pool: Trade.POOL,
  auto: Trade.AUTO_REPAIR,
  autobody: Trade.AUTO_BODY,
  towing: Trade.TOWING,
  dental: Trade.DENTAL,
  chiro: Trade.CHIROPRACTIC,
  vet: Trade.VETERINARY,
  legal: Trade.LEGAL,
  accounting: Trade.ACCOUNTING,
  realestate: Trade.REAL_ESTATE,
  insurance: Trade.INSURANCE,
  restaurant: Trade.RESTAURANT,
  salon: Trade.SALON,
  fitness: Trade.FITNESS,
  photography: Trade.PHOTOGRAPHY,
  it: Trade.IT_SERVICES,
  marketing: Trade.MARKETING,
  consulting: Trade.CONSULTING,
  retail: Trade.RETAIL,
};

/** Source key -> enum mapping */
const sourceMap: Record<string, LeadSource> = {
  google: LeadSource.GOOGLE_MAPS,
  yelp: LeadSource.YELP,
};

/** Status key -> enum mapping */
const statusMap: Record<string, LeadStatus> = {
  new: LeadStatus.NEW,
  enriched: LeadStatus.ENRICHED,
  verified: LeadStatus.VERIFIED,
  exported: LeadStatus.EXPORTED,
};

function isJsonMode(): boolean {
  return program.opts().json === true;
}

function outputJson(data: Record<string, unknown>): void {
  console.log(JSON.stringify(data, null, 2));
}

function log(message: string): void {
  if (!isJsonMode()) {
    console.log(message);
  }
}

// ============================================================================
// Scrape command
// ============================================================================
program
  .command('scrape')
  .description('Scrape business leads from Google Maps and Yelp')
  .option('-s, --sources <sources>', 'Comma-separated sources (google,yelp)', 'google,yelp')
  .option('-t, --trades <trades>', 'Comma-separated trades (dental,legal,hvac,...) or "all"', 'all')
  .option('-l, --location <location>', 'Target location (City, ST)', 'Westchester County, NY')
  .option('--max-results <number>', 'Max results per source', '100')
  .option('--radius <miles>', 'Search radius in miles (default: no limit)')
  .option('--skip-deduplication', 'Skip deduplication step', false)
  .option('--dry-run', 'Preview what would be scraped without executing', false)
  .action(async (options) => {
    await initDatabase();

    let sources: LeadSource[];
    if (options.sources === 'all') {
      sources = getScrapableSources();
    } else {
      sources = options.sources
        .split(',')
        .map((s: string) => sourceMap[s.trim().toLowerCase()])
        .filter(Boolean);
    }

    const trades =
      options.trades === 'all'
        ? Object.values(tradeMap)
        : options.trades
            .split(',')
            .map((t: string) => tradeMap[t.trim().toLowerCase()])
            .filter(Boolean);

    const locationParts = options.location.split(',').map((p: string) => p.trim());
    const location: { city?: string; county?: string; state?: string; radius?: number } = {};
    if (locationParts.length >= 2) {
      const lastPart = locationParts[locationParts.length - 1];
      if (lastPart && lastPart.length === 2) location.state = lastPart;
      const firstPart = locationParts[0];
      if (firstPart) {
        if (firstPart.toLowerCase().includes('county')) location.county = firstPart;
        else location.city = firstPart;
      }
    } else if (locationParts[0]) {
      location.city = locationParts[0];
    }

    if (options.radius) {
      location.radius = parseFloat(options.radius);
    }

    if (options.dryRun) {
      const dryRunData = {
        location: options.location,
        radius: location.radius ? `${location.radius} miles` : 'unlimited',
        trades: trades.map(String),
        sources: sources.map(String),
        maxResultsPerSource: parseInt(options.maxResults, 10),
      };
      if (isJsonMode()) {
        outputJson({ success: true, command: 'scrape', dryRun: true, data: dryRunData });
      } else {
        log('\n DRY RUN - No scraping will occur\n');
        log(`   Location: ${options.location}`);
        log(`   Trades: ${trades.join(', ')}`);
        log(`   Sources: ${sources.join(', ')}`);
        log(`   Max results per source: ${options.maxResults}`);
      }
      await closeDatabase();
      return;
    }

    log('\n LeadFlow Configuration:');
    log(`   Location: ${options.location}`);
    if (location.radius) log(`   Radius: ${location.radius} miles`);
    log(`   Trades: ${trades.join(', ')}`);
    log(`   Sources: ${sources.join(', ')}`);
    log(`   Max results per source: ${options.maxResults}`);
    log('\n Starting scrape...\n');

    try {
      const result = await runScrape({
        sources,
        trades,
        location,
        maxResultsPerSource: parseInt(options.maxResults, 10),
        skipDeduplication: options.skipDeduplication,
        onProgress: (progress) => {
          if (isJsonMode()) return;
          if (progress.status === 'starting') log(`  Starting ${progress.source}...`);
          else if (progress.status === 'scraping') {
            process.stdout.write(
              `\r   Found: ${progress.found} | Saved: ${progress.saved} | Duplicates: ${progress.duplicates}`
            );
          } else if (progress.status === 'complete') {
            log(`\n  ${progress.source}: ${progress.found} found, ${progress.saved} saved, ${progress.duplicates} duplicates`);
          } else if (progress.status === 'error') {
            log(`\n  ERROR ${progress.source}: ${progress.error}`);
          }
        },
      });

      if (isJsonMode()) {
        outputJson({
          success: true, command: 'scrape',
          data: { totalFound: result.totalFound, totalSaved: result.totalSaved, totalDuplicates: result.totalDuplicates, bySource: result.bySource, errors: result.errors },
        });
      } else {
        log('\n Scrape Summary:');
        log(`   Total found: ${result.totalFound}`);
        log(`   Total saved: ${result.totalSaved}`);
        log(`   Total duplicates: ${result.totalDuplicates}`);
        if (result.errors.length > 0) {
          log('\n  Errors:');
          for (const error of result.errors) log(`   ${error.source}: ${error.error}`);
        }
      }
    } catch (error) {
      if (isJsonMode()) {
        outputJson({ success: false, command: 'scrape', error: error instanceof Error ? error.message : String(error) });
      } else {
        console.error(`\n Scrape failed: ${error}`);
      }
    }

    await closeDatabase();
  });

// ============================================================================
// Enrich command - waterfall email enrichment
// ============================================================================
program
  .command('enrich')
  .description('Enrich leads with emails (waterfall: scrape -> Hunter -> Apollo -> Dropcontact)')
  .option('--limit <number>', 'Max leads to enrich', '100')
  .option('--trade <trade>', 'Filter by trade')
  .option('--source <source>', 'Filter by source')
  .action(async (options) => {
    await initDatabase();

    const limit = parseInt(options.limit, 10);
    log(`\n Enriching up to ${limit} leads...\n`);

    // Show which providers are configured
    const status = getEnrichmentStatus();
    if (!isJsonMode()) {
      log('  Providers:');
      for (const p of status.providers) {
        log(`    ${p.configured ? '[OK]' : '[--]'} ${p.name}`);
      }
      log('');
    }

    try {
      const result = await enrichAllLeads(
        {
          trade: options.trade ? String(tradeMap[options.trade.toLowerCase()]) : undefined,
          source: options.source ? String(sourceMap[options.source.toLowerCase()]) : undefined,
          limit,
        },
        (completed, total) => {
          if (!isJsonMode()) process.stdout.write(`\r   Progress: ${completed}/${total}`);
        }
      );

      await persistChanges();

      if (isJsonMode()) {
        outputJson({
          success: true, command: 'enrich',
          data: {
            total: result.stats.total,
            enriched: result.stats.enriched,
            failed: result.stats.failed,
            skipped: result.stats.skipped,
            alreadyHadEmail: result.stats.alreadyHadEmail,
            noWebsite: result.stats.noWebsite,
            byProvider: result.stats.byProvider,
          },
        });
      } else {
        log(`\n\n Enrichment Complete:`);
        log(`   Total processed: ${result.stats.total}`);
        log(`   Emails found: ${result.stats.enriched}`);
        log(`   Failed: ${result.stats.failed}`);
        log(`   Skipped (no website): ${result.stats.noWebsite}`);
        log(`   Already had email: ${result.stats.alreadyHadEmail}`);
        if (Object.keys(result.stats.byProvider).length > 0) {
          log(`\n   By Provider:`);
          for (const [provider, count] of Object.entries(result.stats.byProvider)) {
            log(`     ${provider}: ${count}`);
          }
        }
      }
    } catch (error) {
      if (isJsonMode()) {
        outputJson({ success: false, command: 'enrich', error: error instanceof Error ? error.message : String(error) });
      } else {
        console.error(`\n Enrichment failed: ${error}`);
      }
    }

    await closeDatabase();
  });

// ============================================================================
// Verify command - email verification via ZeroBounce + phone validation via Twilio
// ============================================================================
program
  .command('verify')
  .description('Verify email addresses (ZeroBounce) and phone numbers (Twilio)')
  .option('--emails', 'Verify email addresses', false)
  .option('--phones', 'Validate phone numbers', false)
  .option('--limit <number>', 'Max leads to verify', '100')
  .option('--trade <trade>', 'Filter by trade')
  .action(async (options) => {
    await initDatabase();

    const doEmails = options.emails || (!options.emails && !options.phones); // default: emails
    const doPhones = options.phones;
    const limit = parseInt(options.limit, 10);

    const emailResults = { verified: 0, invalid: 0, errors: 0 };
    const phoneResults = { validated: 0, mobile: 0, landline: 0, voip: 0, errors: 0 };

    // Email verification
    if (doEmails) {
      if (!isZeroBounceConfigured()) {
        if (isJsonMode()) {
          outputJson({ success: false, command: 'verify', error: 'ZEROBOUNCE_API_KEY not configured' });
        } else {
          log('\n ZEROBOUNCE_API_KEY not configured. Set it in .env to verify emails.');
        }
        if (!doPhones) { await closeDatabase(); return; }
      } else {
        const leads = findLeads({
          hasEmail: true,
          trade: options.trade ? tradeMap[options.trade.toLowerCase()] : undefined,
          limit,
        }).filter(l => !l.emailVerified);

        log(`\n Verifying ${leads.length} email addresses...\n`);

        const emails = leads.map(l => l.email!);
        const results = await batchVerifyEmails(emails, (done, total) => {
          if (!isJsonMode()) process.stdout.write(`\r   Progress: ${done}/${total}`);
        });

        for (const lead of leads) {
          const result = results.get(lead.email!);
          if (result) {
            updateLead(lead.id, {
              emailVerified: result.isValid,
              emailVerificationStatus: result.status,
              verifiedAt: new Date(),
              status: result.isValid ? ('Verified' as LeadStatus) : lead.status,
            });
            if (result.isValid) emailResults.verified++;
            else emailResults.invalid++;
          } else {
            emailResults.errors++;
          }
        }
      }
    }

    // Phone validation
    if (doPhones) {
      if (!isTwilioConfigured()) {
        if (isJsonMode()) {
          outputJson({ success: false, command: 'verify', error: 'TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN not configured' });
        } else {
          log('\n Twilio not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env.');
        }
        if (!doEmails) { await closeDatabase(); return; }
      } else {
        const leads = findLeads({
          hasPhone: true,
          trade: options.trade ? tradeMap[options.trade.toLowerCase()] : undefined,
          limit,
        }).filter(l => !l.phoneVerified);

        log(`\n Validating ${leads.length} phone numbers...\n`);

        const phones = leads.map(l => l.normalizedPhone || l.phone!);
        const results = await batchValidatePhones(phones, (done, total) => {
          if (!isJsonMode()) process.stdout.write(`\r   Progress: ${done}/${total}`);
        });

        for (const lead of leads) {
          const phone = lead.normalizedPhone || lead.phone!;
          const result = results.get(phone);
          if (result) {
            updateLead(lead.id, {
              phoneVerified: result.valid,
              phoneType: result.lineType,
              phoneCarrier: result.carrier ?? undefined,
            });
            phoneResults.validated++;
            if (result.lineType === 'mobile') phoneResults.mobile++;
            else if (result.lineType === 'landline') phoneResults.landline++;
            else if (result.lineType === 'voip') phoneResults.voip++;
          } else {
            phoneResults.errors++;
          }
        }
      }
    }

    await persistChanges();

    if (isJsonMode()) {
      outputJson({
        success: true, command: 'verify',
        data: {
          ...(doEmails ? { email: emailResults } : {}),
          ...(doPhones ? { phone: phoneResults } : {}),
        },
      });
    } else {
      if (doEmails) {
        log(`\n\n Email Verification:`);
        log(`   Valid: ${emailResults.verified}`);
        log(`   Invalid: ${emailResults.invalid}`);
        log(`   Errors: ${emailResults.errors}`);
      }
      if (doPhones) {
        log(`\n Phone Validation:`);
        log(`   Validated: ${phoneResults.validated}`);
        log(`   Mobile: ${phoneResults.mobile}`);
        log(`   Landline: ${phoneResults.landline}`);
        log(`   VoIP: ${phoneResults.voip}`);
        log(`   Errors: ${phoneResults.errors}`);
      }
    }

    await closeDatabase();
  });

// ============================================================================
// Score command - lead scoring
// ============================================================================
program
  .command('score')
  .description('Score all leads (composite 0-100 based on data completeness and quality)')
  .option('--trade <trade>', 'Filter by trade')
  .option('--limit <number>', 'Max leads to score', '10000')
  .action(async (options) => {
    await initDatabase();

    log(`\n Scoring leads...\n`);

    const stats = scoreAllLeads(
      {
        trade: options.trade ? String(tradeMap[options.trade.toLowerCase()]) : undefined,
        limit: parseInt(options.limit, 10),
      },
      (done, total) => {
        if (!isJsonMode()) process.stdout.write(`\r   Progress: ${done}/${total}`);
      }
    );

    await persistChanges();

    if (isJsonMode()) {
      outputJson({ success: true, command: 'score', data: stats });
    } else {
      log(`\n\n Scoring Complete:`);
      log(`   Leads scored: ${stats.scored}`);
      log(`   Average score: ${stats.averageScore}/100`);
      log(`\n   Distribution:`);
      for (const bucket of stats.distribution) {
        const bar = '#'.repeat(Math.round(bucket.count / Math.max(1, stats.scored) * 40));
        log(`     ${bucket.range.padEnd(6)} ${bar} ${bucket.count}`);
      }
    }

    await closeDatabase();
  });

// ============================================================================
// Export command - multiple formats
// ============================================================================
program
  .command('export')
  .description('Export leads to XLSX, CSV, or CRM-native formats')
  .option('-o, --output <path>', 'Output file path')
  .option('--status <status>', 'Filter by status (new,enriched,verified,all)', 'all')
  .option('--trade <trade>', 'Filter by trade')
  .option('--min-score <number>', 'Minimum lead score')
  .option(
    '--format <format>',
    'Export format (xlsx, csv, instantly, hubspot, salesforce, pipedrive, airtable)',
    'xlsx'
  )
  .action(async (options) => {
    await initDatabase();

    const filters: Parameters<typeof findLeads>[0] = {};
    if (options.status !== 'all') filters.status = statusMap[options.status.toLowerCase()];
    if (options.trade) filters.trade = tradeMap[options.trade.toLowerCase()];

    log('\n Exporting leads...');

    try {
      let result: { path: string; count: number; skipped?: number };

      switch (options.format.toLowerCase()) {
        case 'csv':
          result = await exportToCsv(options.output, filters);
          break;
        case 'instantly':
          result = await exportToInstantly(options.output, filters);
          break;
        case 'hubspot':
          result = await exportToHubspot(options.output, filters);
          break;
        case 'salesforce':
          result = await exportToSalesforce(options.output, filters);
          break;
        case 'pipedrive':
          result = await exportToPipedrive(options.output, filters);
          break;
        case 'airtable':
          result = await exportToAirtable(options.output, filters);
          break;
        default:
          result = await exportToXlsx(options.output, filters);
      }

      if (isJsonMode()) {
        outputJson({
          success: true, command: 'export',
          data: { format: options.format, path: result.path, count: result.count, skipped: result.skipped },
        });
      } else {
        if (result.count === 0) log('   No leads to export');
        else {
          log(`   Exported ${result.count} leads to ${result.path}`);
          if (result.skipped) log(`   Skipped ${result.skipped} leads without email`);
        }
      }
    } catch (error) {
      if (isJsonMode()) {
        outputJson({ success: false, command: 'export', error: error instanceof Error ? error.message : String(error) });
      } else {
        console.error(`   Export failed: ${error}`);
      }
    }

    await closeDatabase();
  });

// ============================================================================
// Webhook command
// ============================================================================
program
  .command('webhook')
  .description('POST leads as JSON to a webhook URL (Zapier, n8n, Make, etc.)')
  .requiredOption('-u, --url <url>', 'Webhook URL to POST leads to')
  .option('--status <status>', 'Filter by status', 'all')
  .option('--trade <trade>', 'Filter by trade')
  .option('--limit <number>', 'Max leads to send', '100')
  .option('--batch-size <number>', 'Batch size per request', '50')
  .action(async (options) => {
    await initDatabase();

    const filters: Parameters<typeof findLeads>[0] = {};
    if (options.status !== 'all') filters.status = statusMap[options.status.toLowerCase()];
    if (options.trade) filters.trade = tradeMap[options.trade.toLowerCase()];
    if (options.limit) filters.limit = parseInt(options.limit, 10);

    log(`\n Sending leads to webhook: ${options.url}\n`);

    try {
      const result = await sendLeadsToWebhook(options.url, filters, {
        batchSize: parseInt(options.batchSize, 10),
      });

      if (isJsonMode()) {
        outputJson({
          success: result.success, command: 'webhook',
          data: { leadsPosted: result.leadsPosted, statusCode: result.statusCode, error: result.error },
        });
      } else {
        if (result.success) {
          log(`   Success! Posted ${result.leadsPosted} leads`);
        } else {
          log(`   Failed: ${result.error}`);
          log(`   Leads posted before failure: ${result.leadsPosted}`);
        }
      }
    } catch (error) {
      if (isJsonMode()) {
        outputJson({ success: false, command: 'webhook', error: error instanceof Error ? error.message : String(error) });
      } else {
        console.error(`\n Webhook failed: ${error}`);
      }
    }

    await closeDatabase();
  });

// ============================================================================
// Status command
// ============================================================================
program
  .command('status')
  .description('Show database statistics, API key status, and enrichment providers')
  .action(async () => {
    await initDatabase();

    const total = getTotalLeadCount();
    const byStatus = countLeadsByStatus();
    const bySource = countLeadsBySource();
    const byTrade = countLeadsByTrade();
    const scrapers = getScrapableSources();
    const enrichStatus = getEnrichmentStatus();

    const apiKeys: Record<string, boolean> = {
      GOOGLE_PLACES_API_KEY: hasApiKey('GOOGLE_PLACES_API_KEY'),
      YELP_API_KEY: hasApiKey('YELP_API_KEY'),
      HUNTER_API_KEY: hasApiKey('HUNTER_API_KEY'),
      APOLLO_API_KEY: hasApiKey('APOLLO_API_KEY'),
      DROPCONTACT_API_KEY: hasApiKey('DROPCONTACT_API_KEY'),
      ZEROBOUNCE_API_KEY: hasApiKey('ZEROBOUNCE_API_KEY'),
      TWILIO_ACCOUNT_SID: hasApiKey('TWILIO_ACCOUNT_SID'),
    };

    if (isJsonMode()) {
      outputJson({
        success: true, command: 'status',
        data: {
          totalLeads: total,
          byStatus, bySource, byTrade,
          availableScrapers: scrapers.map(String),
          apiKeys,
          enrichmentProviders: enrichStatus.providers,
          enrichable: enrichStatus.enrichable,
          databasePath: config.DATABASE_PATH,
          exportPath: config.EXPORT_PATH,
        },
      });
    } else {
      log('\n LeadFlow v1.0 Statistics\n');
      log(`Total leads: ${total}\n`);

      if (Object.keys(byStatus).length > 0) {
        log('By Status:');
        for (const [status, count] of Object.entries(byStatus)) log(`   ${status}: ${count}`);
      }
      if (Object.keys(bySource).length > 0) {
        log('\nBy Source:');
        for (const [source, count] of Object.entries(bySource)) log(`   ${source}: ${count}`);
      }
      if (Object.keys(byTrade).length > 0) {
        log('\nBy Trade:');
        for (const [trade, count] of Object.entries(byTrade)) log(`   ${trade}: ${count}`);
      }

      log('\n API Keys:');
      for (const [key, configured] of Object.entries(apiKeys)) {
        log(`   ${key}: ${configured ? 'OK' : 'NOT SET'}`);
      }

      log('\n Enrichment Providers:');
      for (const p of enrichStatus.providers) {
        log(`   ${p.configured ? '[OK]' : '[--]'} ${p.name}`);
      }
      log(`\n Enrichable leads (have website, no email): ${enrichStatus.enrichable}`);
      log(` Available Scrapers: ${scrapers.join(', ')}`);
      log(` Database: ${config.DATABASE_PATH}`);
      log(` Exports: ${config.EXPORT_PATH}`);
    }

    await closeDatabase();
  });

// ============================================================================
// Trades command
// ============================================================================
program
  .command('trades')
  .description('List all available trade categories')
  .action(() => {
    const trades = Object.entries(tradeMap).map(([key, value]) => ({
      key, name: String(value),
    }));

    if (isJsonMode()) {
      outputJson({ success: true, command: 'trades', data: { trades } });
    } else {
      log('\n Available Trades:\n');
      log('   Home Services:');
      log('     hvac, plumbing, electrical, roofing, general, landscaping,');
      log('     pest, cleaning, painting, flooring, fencing, tree, pool');
      log('\n   Auto:');
      log('     auto, autobody, towing');
      log('\n   Healthcare:');
      log('     dental, chiro, vet');
      log('\n   Professional:');
      log('     legal, accounting, realestate, insurance, it, marketing, consulting');
      log('\n   Food & Hospitality:');
      log('     restaurant');
      log('\n   Personal Services:');
      log('     salon, fitness, photography');
      log('\n   Other:');
      log('     retail');
    }
  });

// ============================================================================
// Providers command
// ============================================================================
program
  .command('providers')
  .description('Show configured enrichment and verification providers')
  .action(async () => {
    await initDatabase();
    const status = getEnrichmentStatus();

    const verification = {
      ZeroBounce: isZeroBounceConfigured(),
      Twilio: isTwilioConfigured(),
    };

    if (isJsonMode()) {
      outputJson({
        success: true, command: 'providers',
        data: {
          enrichment: status.providers,
          verification: Object.entries(verification).map(([name, configured]) => ({ name, configured })),
        },
      });
    } else {
      log('\n Enrichment Providers:');
      for (const p of status.providers) log(`   ${p.configured ? '[OK]' : '[--]'} ${p.name}`);
      log('\n Verification Providers:');
      for (const [name, configured] of Object.entries(verification)) {
        log(`   ${configured ? '[OK]' : '[--]'} ${name}`);
      }
    }

    await closeDatabase();
  });

// Handle errors
program.exitOverride();

try {
  await program.parseAsync(process.argv);
} catch (error) {
  if (error instanceof Error) {
    const errorCode = (error as { code?: string }).code;
    const isHelpOrVersionExit =
      errorCode === 'commander.help' ||
      errorCode === 'commander.helpDisplayed' ||
      errorCode === 'commander.version';
    if (!isHelpOrVersionExit) {
      if (isJsonMode()) {
        outputJson({ success: false, error: error.message });
      } else {
        console.error(error.message);
      }
      process.exit(1);
    }
  }
}
