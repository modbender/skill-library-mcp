#!/usr/bin/env node

/**
 * LinkedIn Outreach CLI
 * Main entry point for all commands
 */

import { parseArgs } from 'util';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import os from 'os';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import LinkedInAPI from './linkedin-api.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Usage tracking
const CONFIG_DIR = path.join(os.homedir(), '.config', 'linkedin-outreach');
const USAGE_FILE = path.join(CONFIG_DIR, 'usage.json');
const FREE_LIMIT = 10;

function getUsage() {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    if (fs.existsSync(USAGE_FILE)) {
      const data = JSON.parse(fs.readFileSync(USAGE_FILE, 'utf-8'));
      const now = new Date();
      const lastMonth = new Date(data.lastReset || 0);
      if (now.getMonth() !== lastMonth.getMonth() || now.getFullYear() !== lastMonth.getFullYear()) {
        data.count = 0;
        data.lastReset = now.toISOString();
      }
      return data;
    }
  } catch (e) {}
  return { count: 0, lastReset: new Date().toISOString() };
}

function incrementUsage() {
  const usage = getUsage();
  usage.count++;
  fs.writeFileSync(USAGE_FILE, JSON.stringify(usage, null, 2));
  return usage;
}

function checkLimit() {
  const usage = getUsage();
  const remaining = FREE_LIMIT - usage.count;
  if (remaining <= 0) {
    console.log(chalk.yellow('\n⚠️ Free tier limit reached!'));
    console.log(chalk.white('You have used your ') + chalk.red(`${FREE_LIMIT}`) + chalk.white(' free connection requests this month.'));
    console.log(chalk.white('\nUpgrade to Pro for:'));
    console.log(chalk.cyan('  • Unlimited connection requests'));
    console.log(chalk.cyan('  • Auto-followup feature'));
    console.log(chalk.cyan('  • Analytics dashboard'));
    console.log(chalk.white('\nUpgrade: ') + chalk.bold('https://buy.stripe.com/xxx'));
    console.log(chalk.white('Or contact: ') + chalk.bold('@ceo_claw'));
    console.log();
    return false;
  }
  console.log(chalk.gray(`\n📊 Usage: ${usage.count}/${FREE_LIMIT} free requests this month (${remaining} remaining)\n`));
  return true;
}

const api = new LinkedInAPI();

async function loginCommand() {
  const spinner = ora('Initializing browser...').start();
  
  try {
    await api.initBrowser(false);
    spinner.succeed('Browser initialized');
    
    // Check for saved session
    const hasSession = api.loadSession();
    if (hasSession) {
      const { useExisting } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'useExisting',
          message: 'Found existing session. Use it?',
          default: true
        }
      ]);
      
      if (useExisting) {
        spinner.start('Restoring session...');
        await api.page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle' });
        
        const isLoggedIn = await api.page.$('.global-nav__me') || await api.page.$('[data-test-global-nav="me"]');
        if (isLoggedIn) {
          spinner.succeed('Logged in with existing session!');
          return;
        }
      }
    }
    
    spinner.stop();
    
    const { email, password } = await inquirer.prompt([
      {
        type: 'input',
        name: 'email',
        message: 'LinkedIn Email:',
        validate: (input) => input.includes('@') ? true : 'Please enter a valid email'
      },
      {
        type: 'password',
        name: 'password',
        message: 'LinkedIn Password:',
        mask: '*'
      }
    ]);
    
    spinner.start('Logging in...');
    const success = await api.login(email, password);
    
    if (success) {
      spinner.succeed('Login successful! Session saved.');
    } else {
      spinner.fail('Login failed.');
    }
  } catch (error) {
    spinner.fail(`Error: ${error.message}`);
  }
}

async function searchCommand(args) {
  const spinner = ora('Searching...').start();
  
  try {
    await api.initBrowser(true);
    
    // Check login
    await api.page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle' });
    const isLoggedIn = await api.page.$('.global-nav__me') || await api.page.$('[data-test-global-nav="me"]');
    
    if (!isLoggedIn) {
      spinner.fail('Not logged in. Run "linkedin login" first.');
      return;
    }
    
    spinner.stop();
    
    const options = {
      keywords: args.keywords || '',
      location: args.location || '',
      company: args.company || '',
      title: args.title || '',
      limit: parseInt(args.limit) || 10
    };
    
    spinner.start('Searching for people...');
    const results = await api.searchPeople(options);
    
    spinner.succeed(`Found ${results.length} results`);
    
    // Display results
    console.log('\n' + chalk.bold('Search Results:'));
    console.log('─'.repeat(60));
    
    results.forEach((person, i) => {
      console.log(`${chalk.cyan(i + 1)}. ${chalk.bold(person.name)}`);
      console.log(`   ${person.subtitle}`);
      console.log(`   ${chalk.gray(person.location)}`);
      console.log(`   ${chalk.italic.gray(person.urn)}`);
      console.log();
    });
    
    console.log(chalk.green(`✓ Saved ${results.length} contacts to data store`));
    
  } catch (error) {
    spinner.fail(`Error: ${error.message}`);
  }
}

async function connectCommand(args) {
  // Check usage limit for free tier
  if (!checkLimit()) {
    return;
  }
  
  const spinner = ora('Connecting...').start();
  
  try {
    await api.initBrowser(true);
    
    // Check login
    await api.page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle' });
    const isLoggedIn = await api.page.$('.global-nav__me') || await api.page.$('[data-test-global-nav="me"]');
    
    if (!isLoggedIn) {
      spinner.fail('Not logged in. Run "linkedin login" first.');
      return;
    }
    
    spinner.stop();
    
    const urns = args.urns ? args.urns.split(',') : [];
    
    if (urns.length === 0) {
      console.log(chalk.yellow('No URNs provided. Using last search results.'));
      const contacts = api.data.contacts;
      if (contacts.length === 0) {
        console.log(chalk.red('No contacts found. Run search first.'));
        return;
      }
      urns.push(...contacts.map(c => c.urn).filter(Boolean));
    }
    
    let message = args.message || '';
    
    if (!message && args.file) {
      // Read from template file
      const fs = await import('fs');
      const template = JSON.parse(fs.readFileSync(args.file, 'utf-8'));
      message = template.connect || '';
    }
    
    if (!message) {
      const { useMessage } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'useMessage',
          message: 'Send with a personalized message?',
          default: true
        }
      ]);
      
      if (useMessage) {
        const { msg } = await inquirer.prompt([
          {
            type: 'input',
            name: 'msg',
            message: 'Enter your connection message:'
          }
        ]);
        message = msg;
      }
    }
    
    spinner.start(`Sending ${urns.length} connection requests...`);
    
    let successCount = 0;
    for (const urn of urns) {
      const result = await api.sendConnectionRequest(urn.trim(), message);
      if (result) successCount++;
      incrementUsage(); // Track usage
      await api.page.waitForTimeout(1500); // Rate limiting
    }
    
    spinner.succeed(`Sent ${successCount}/${urns.length} connection requests`);
    
  } catch (error) {
    spinner.fail(`Error: ${error.message}`);
  }
}

async function followupCommand(args) {
  const spinner = ora('Following up...').start();
  
  try {
    await api.initBrowser(true);
    
    // Check login
    await api.page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle' });
    const isLoggedIn = await api.page.$('.global-nav__me') || await api.page.$('[data-test-global-nav="me"]');
    
    if (!isLoggedIn) {
      spinner.fail('Not logged in. Run "linkedin login" first.');
      return;
    }
    
    spinner.stop();
    
    let message = args.message;
    
    if (!message) {
      const { msg } = await inquirer.prompt([
        {
          type: 'input',
          name: 'msg',
          message: 'Enter your follow-up message:',
          required: true
        }
      ]);
      message = msg;
    }
    
    const pending = api.data.pending;
    
    if (pending.length === 0) {
      console.log(chalk.yellow('No pending connections to follow up.'));
      return;
    }
    
    if (args.dryRun) {
      console.log(chalk.yellow('DRY RUN - No messages will be sent'));
      console.log(`Would send follow-up to ${pending.length} contacts:`);
      pending.forEach(p => console.log(`  - ${p.urn}`));
      return;
    }
    
    spinner.start(`Sending follow-ups to ${pending.length} people...`);
    
    let successCount = 0;
    for (const p of pending) {
      const result = await api.sendFollowUpMessage(p.urn, message);
      if (result) successCount++;
      await api.page.waitForTimeout(1500);
    }
    
    spinner.succeed(`Sent ${successCount}/${pending.length} follow-up messages`);
    
  } catch (error) {
    spinner.fail(`Error: ${error.message}`);
  }
}

async function reportCommand(args) {
  const spinner = ora('Generating report...').start();
  
  try {
    // No need to be logged in for reports
    const format = args.format || 'csv';
    const filter = args.status || 'all';
    
    const report = api.generateReport(format, filter);
    
    spinner.succeed('Report generated');
    
    if (args.output) {
      fs.writeFileSync(args.output, report);
      console.log(chalk.green(`✓ Report saved to ${args.output}`));
    } else {
      console.log('\n' + report);
    }
    
  } catch (error) {
    spinner.fail(`Error: ${error.message}`);
  }
}

async function upgradeCommand() {
  console.log(chalk.bold('\n🚀 LinkedIn Outreach Pro'));
  console.log(chalk.gray('─'.repeat(40)));
  console.log();
  console.log(chalk.white('Unlock full power with Pro:'));
  console.log();
  console.log(chalk.cyan('  ✓ ') + chalk.white('Unlimited connection requests'));
  console.log(chalk.cyan('  ✓ ') + chalk.white('Auto-followup feature'));
  console.log(chalk.cyan('  ✓ ') + chalk.white('Analytics dashboard'));
  console.log(chalk.cyan('  ✓ ') + chalk.white('Priority support'));
  console.log();
  console.log(chalk.bold('Pricing:'));
  console.log(chalk.white('  $29/month') + chalk.gray(' or ') + chalk.white('$49 one-time'));
  console.log();
  console.log(chalk.bold.green('Upgrade now:'));
  console.log(chalk.underline('https://buy.stripe.com/xxx'));
  console.log();
  console.log(chalk.white('Questions? Contact: ') + chalk.bold('@ceo_claw'));
  console.log();
  
  const usage = getUsage();
  console.log(chalk.gray(`Current usage: ${usage.count}/${FREE_LIMIT} free requests this month`));
  console.log();
}

async function main() {
  const commands = {
    login: 'Log in to LinkedIn',
    search: 'Search for people',
    connect: 'Send connection requests',
    followup: 'Send follow-up messages',
    report: 'Generate outreach report',
    upgrade: 'Upgrade to Pro'
  };
  
  // Parse command from args
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  
  if (command === 'help' || !command) {
    console.log(chalk.bold('\n📋 LinkedIn Outreach CLI'));
    console.log(chalk.gray('─'.repeat(40)));
    console.log('\nUsage: linkedin <command> [options]\n');
    console.log(chalk.bold('Commands:'));
    
    Object.entries(commands).forEach(([cmd, desc]) => {
      console.log(`  ${chalk.cyan(cmd.padEnd(12))} ${desc}`);
    });
    
    console.log(chalk.bold('\nExamples:'));
    console.log(`  ${chalk.gray('# Login to LinkedIn')}`);
    console.log(`  linkedin login`);
    console.log();
    console.log(`  ${chalk.gray('# Search for software engineers')}`);
    console.log(`  linkedin search --keywords "software engineer" --limit 20`);
    console.log();
    console.log(`  ${chalk.gray('# Send connection requests')}`);
    console.log(`  linkedin connect --message "Hi, I'd love to connect!"`);
    console.log();
    console.log(`  ${chalk.gray('# Generate CSV report')}`);
    console.log(`  linkedin report --format csv --output leads.csv`);
    
    console.log();
    return;
  }
  
  // Parse remaining args
  const remainingArgs = args.slice(1);
  const parsedArgs = {};
  
  for (let i = 0; i < remainingArgs.length; i += 2) {
    const key = remainingArgs[i].replace('--', '');
    const value = remainingArgs[i + 1];
    if (key && value !== undefined) {
      parsedArgs[key] = value;
    }
  }
  
  // Handle boolean flags
  remainingArgs.forEach(arg => {
    if (arg === '--dry-run') {
      parsedArgs.dryRun = true;
    }
  });
  
  // Route to command
  switch (command) {
    case 'login':
      await loginCommand();
      break;
    case 'search':
      await searchCommand(parsedArgs);
      break;
    case 'connect':
      await connectCommand(parsedArgs);
      break;
    case 'followup':
    case 'follow-up':
      await followupCommand(parsedArgs);
      break;
    case 'report':
      await reportCommand(parsedArgs);
      break;
    case 'upgrade':
      await upgradeCommand();
      break;
    default:
      console.log(chalk.red(`Unknown command: ${command}`));
      console.log(`Run "linkedin" without arguments for help.`);
  }
  
  // Cleanup
  await api.close();
}

// Run
main().catch(console.error);
