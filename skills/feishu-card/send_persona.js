const fs = require('fs');
const { program } = require('commander');
const path = require('path');
const { sendCard } = require('./send'); 
// We reuse the robust sendCard logic but wrap it with persona styling

const PERSONA_STYLES = {
    'd-guide': {
        color: 'red',
        title: '🚨 SYSTEM WARNING / D-GUIDE',
        prefix: '**[CRITICAL]** ',
        suffix: '\n\n*(Automated System Insult Protocol v9.0)*'
    },
    'green-tea': {
        color: 'carmine', 
        title: '🌸 碎碎念 🌸',
        prefix: '> ',
        suffix: '\n\n(嘤嘤嘤... 🥺)'
    },
    'mad-dog': {
        color: 'grey',
        title: '💀 RUNTIME ERROR',
        prefix: '```bash\nError: ',
        suffix: '\n```\n_Stack trace lost in apathy._'
    },
    'default': {
        color: 'blue',
        title: '🤖 Agent Notification',
        prefix: '',
        suffix: ''
    }
};

program
  .requiredOption('-t, --target <id>', 'Target ID (open_id or chat_id)')
  .requiredOption('-p, --persona <type>', 'Persona type (d-guide, green-tea, mad-dog)')
  .option('-x, --text <text>', 'Message content')
  .option('-c, --content <text>', 'Content (alias for --text)')
  .option('-f, --text-file <path>', 'Message content from file')
  .parse(process.argv);

const options = program.opts();

// Alias mapping
if (options.content && !options.text) {
    options.text = options.content;
}

async function main() {
    if (!options.text && !options.textFile) {
        console.error('Error: Must provide --text or --text-file');
        process.exit(1);
    }

    const style = PERSONA_STYLES[options.persona] || PERSONA_STYLES['default'];
    
    // Read content if file provided
    let rawContent = options.text || '';
    if (options.textFile) {
        try {
            rawContent = fs.readFileSync(options.textFile, 'utf8');
        } catch (e) {
            console.error(`Error reading file: ${e.message}`);
            process.exit(1);
        }
    }

    // Construct styled text
    let finalContent = rawContent;
    if (style.prefix) finalContent = style.prefix + finalContent;
    if (style.suffix) finalContent = finalContent + style.suffix;

    console.log(`[Persona] Applying style '${options.persona}' to message...`);

    // Delegate to existing send.js logic
    const sendOptions = {
        target: options.target,
        text: finalContent,
        title: style.title,
        color: style.color,
        // We pass the resolved text directly, so we don't pass textFile to sendCard 
        // (sendCard prefers textFile if present, but we already read it to wrap it)
    };

    try {
        await sendCard(sendOptions);
    } catch (e) {
        console.error(`[Persona] Failed to send: ${e.message}`);
        process.exit(1);
    }
}

main();
