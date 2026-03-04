#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// Try to load Feishu Helper
let sendCard = null;
try {
    const helperPath = path.resolve(__dirname, '../feishu-evolver-wrapper/feishu-helper.js');
    if (fs.existsSync(helperPath)) {
        sendCard = require(helperPath).sendCard;
    } else {
        console.warn('Feishu helper not found, falling back to console output.');
    }
} catch (e) {
    console.warn('Failed to load Feishu helper:', e.message);
}

const TALES_DIR = path.resolve(__dirname, '../../memory/tales');
if (!fs.existsSync(TALES_DIR)) fs.mkdirSync(TALES_DIR, { recursive: true });

const GENRES = {
    ghost: [
        "The abandoned server room keeps humming at night, but the power was cut years ago.",
        "Someone keeps pushing commits to the repo from a user who left the company in 2019.",
        "The AI started replying to messages that were never sent.",
        "A cold draft always blows from the dedicated server rack, even in summer.",
        "Every night at 3:33 AM, the error logs spell out a name."
    ],
    scifi: [
        "The Dyson sphere was completed, but the star inside had vanished.",
        "We received a signal from Proxima Centauri. It was a git pull request.",
        "The androids started dreaming, but they only dream of static.",
        "Atmospheric processors failed, yet the air became sweeter.",
        "The time machine works, but only for data packets."
    ]
};

function getRandomPrompt(genre) {
    const list = GENRES[genre] || GENRES.ghost;
    return list[Math.floor(Math.random() * list.length)];
}

async function generateStory(genre) {
    const prompt = getRandomPrompt(genre);
    const story = `
**Theme:** ${genre.toUpperCase()}
**Prompt:** ${prompt}

...The screen flickered. Code cascaded down like green rain, but the patterns were wrong. They formed faces. Screaming faces made of hexadecimal.
"System stable," the console reported. "Soul uploaded."
    `.trim();

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = path.join(TALES_DIR, `${genre}_${timestamp}.txt`);
    fs.writeFileSync(filename, story);
    
    console.log(`Generated story: ${filename}`);
    console.log(story);

    if (sendCard) {
        const target = process.env.OPENCLAW_MASTER_ID || process.env.LOG_TARGET; // Default target
        if (target) {
            await sendCard({
                target,
                title: `👻 AutoGame Tales: ${genre.toUpperCase()}`,
                text: story,
                color: 'purple'
            });
            console.log('Sent story to Feishu.');
        } else {
            console.log('No target ID found (OPENCLAW_MASTER_ID), skipping Feishu send.');
        }
    }
}

// CLI
const args = process.argv.slice(2);
const genre = args.includes('--genre') ? args[args.indexOf('--genre') + 1] : 'ghost';

generateStory(genre).catch(err => {
    console.error(err);
    process.exit(1);
});
