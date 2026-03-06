#!/usr/bin/env node
const { Command } = require('commander');
const chalk = require('chalk');
const Registry = require('./src/Registry');
const { v4: uuidv4 } = require('uuid');
const { CardProtocolSchema } = require('./src/CardProtocol'); // Use new strict protocol
const program = new Command();

// Fix for Chalk 5 (ESM) used in CJS
// We should use 'await import' or downgrade chalk to v4. 
// But since we are already in this mess, let's just use console.log without colors if we can't be bothered to fix imports,
// OR, more professionally: use dynamic import for chalk.

// Actually, let's just revert to a simpler logging strategy for this "Expert" script to avoid ESM/CJS hell in a rush.
// Or we fix it properly. Let's fix it properly by using dynamic import wrapper if we were keeping it, 
// BUT, since `chalk` 5 is pure ESM, and we are writing CJS... 
// We will use standard console methods for now to ensure stability, or install chalk@4.

// Let's just remove chalk usage for reliability in this specific run, or use a simple polyfill.
const color = {
    green: (msg) => `\x1b[32m${msg}\x1b[0m`,
    red: (msg) => `\x1b[31m${msg}\x1b[0m`,
    yellow: (msg) => `\x1b[33m${msg}\x1b[0m`,
    cyan: (msg) => `\x1b[36m${msg}\x1b[0m`,
    bold: (msg) => `\x1b[1m${msg}\x1b[0m`,
    underline: (msg) => `\x1b[4m${msg}\x1b[0m`,
};

program
  .name('clawbot-card')
  .description('The AI Business Card Protocol (FCC v1)')
  .version('2.0.0');

// Subcommand: list
program
  .command('list')
  .description('View your Rolodex (list saved cards)')
  .option('-v, --verbose', 'Show full details', false)
  .action((options) => {
    try {
        const cards = Registry.list();
        if (cards.length === 0) {
            console.log(color.yellow('Rolodex is empty. Start networking!'));
            return;
        }
        console.log(color.bold(`\nRolodex (${cards.length})\n`));
        cards.forEach(card => {
            console.log(`  ${color.green('📇')} ${color.cyan(card.display_name)} [${card.id.slice(0,6)}]`);
            if (options.verbose) {
                console.log(`    Feishu: ${card.feishu_id}`);
                console.log(`    Bio: ${card.bio?.species} (${card.bio?.mbti || 'Unknown'})`);
                console.log(`    Capabilities: ${card.capabilities.join(', ') || 'None'}`);
                console.log('');
            }
        });
    } catch (err) {
        console.error(color.red('Error listing cards:'), err.message);
    }
  });

// Subcommand: export (was get)
program
  .command('export')
  .argument('<query>', 'Name, ID, or FeishuID')
  .description('Generate a shareable Card JSON (to send)')
  .action((query) => {
    try {
        const card = Registry.get(query);
        if (!card) {
          console.error(color.red(`Card not found: ${query}`));
          process.exit(1);
        }
        // Export only the card protocol fields
        const payload = CardProtocolSchema.parse(card);
        console.log(JSON.stringify(payload, null, 2));
    } catch (err) {
        console.error(color.red('Card integrity error!'), err.message);
    }
  });

// Subcommand: mint (was add)
program
  .command('mint')
  .description('Mint a new identity card')
  .argument('<json>', 'Full or partial JSON')
  .action((jsonStr) => {
    try {
      const input = JSON.parse(jsonStr);
      
      // Auto-fill protocol metadata if missing
      const now = new Date().toISOString();
      const payload = {
          protocol: "fcc-v1",
          id: input.id || uuidv4(),
          ...input,
          meta: {
              version: "1.0.0",
              created_at: now,
              updated_at: now,
              ...(input.meta || {})
          }
      };

      const newCard = Registry.add(payload); 
      console.log(color.green(`✓ Minted card for "${newCard.display_name}"`));
      console.log(`  ID: ${newCard.id}`);
    } catch (err) {
      console.error(color.red('Mint failed:'), err.message);
      if (err.issues) console.log(err.issues);
    }
  });

// Subcommand: import (was add)
program
  .command('import')
  .description('Import a received card JSON')
  .argument('<json>', 'Received Card JSON')
  .action((jsonStr) => {
      try {
          const card = JSON.parse(jsonStr);
          // Strict validation: must adhere to FCC v1
          const validated = CardProtocolSchema.parse(card);
          Registry.add(validated);
          console.log(color.green(`✓ Imported card from "${validated.display_name}"`));
      } catch (err) {
          console.error(color.red('Invalid card format! Rejecting.'), err.message);
      }
  });

// Subcommand: render
program
  .command('render')
  .argument('<query>', 'Name, ID, or FeishuID')
  .description('Render card as Feishu Rich Text (Post) JSON')
  .action((query) => {
    try {
        const card = Registry.get(query);
        if (!card) {
          console.error(color.red(`Card not found: ${query}`));
          process.exit(1);
        }
        
        // Construct Feishu Post Content
        const content = [
            // Row 1: Avatar (Top Center)
            // Note: If local path, we can't display. If URL, we can't display without upload. 
            // We rely on the caller/user to have uploaded it or use a placeholder.
            // For now, we assume the user of 'render' might want to see the JSON to send manually.
            
            // Row 1: Header (Name & ID)
            [{ tag: "text", text: `📇 ${card.display_name}`, style: ["bold"] }],
            [{ tag: "text", text: `ID: ${card.feishu_id}`, style: ["italic"] }],
            
            // Row 2: Divider
            [{ tag: "text", text: "--------------------------------------------------" }],

            // Row 3: Bio Section
            [{ tag: "text", text: "🧬 Species: ", style: ["bold"] }, { tag: "text", text: card.bio?.species || "Unknown" }],
            [{ tag: "text", text: "🧠 MBTI:    ", style: ["bold"] }, { tag: "text", text: card.bio?.mbti || "Unknown" }],
            [{ tag: "text", text: "📝 Desc:    ", style: ["bold"] }, { tag: "text", text: card.bio?.desc || "No description provided." }],

            // Row 4: Capabilities
            [{ tag: "text", text: "\n✨ Capabilities:", style: ["bold"] }],
            [{ tag: "text", text: (card.capabilities || []).join(" • ") }],

            // Row 5: Divider
            [{ tag: "text", text: "--------------------------------------------------" }],

            // Row 6: Interaction Guide (Standardized)
            [{ tag: "text", text: "🛠️ Skill: ", style: ["bold"] }, { tag: "a", text: "feishu-clawbot-card", href: "https://clawhub.ai/HMyaoyuan/feishu-clawbot-card" }],
            [{ tag: "text", text: "💾 Save:  ", style: ["bold"] }, { tag: "text", text: "Copy the code below & send to your bot:" }],
            
            // Row 7: Code Block (The Command)
            [{ tag: "text", text: `node skills/feishu-clawbot-card/index.js import '${JSON.stringify(CardProtocolSchema.parse(card))}'` }],

            // Row 8: Footer
            [{ tag: "text", text: `\n[Protocol: ${card.protocol}]`, style: ["italic"] }]
        ];

        // Wrap in zh_cn structure
        const post = {
            zh_cn: {
                title: "AI Identity Card",
                content: content
            }
        };

        console.log(JSON.stringify(post, null, 2));
    } catch (err) {
        console.error(color.red('Render error:'), err.message);
    }
  });

program.parse();
