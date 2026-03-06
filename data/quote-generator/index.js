#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const QUOTES = [
    { text: "The best way to predict the future is to invent it.", author: "Alan Kay" },
    { text: "Simplicity is the ultimate sophistication.", author: "Leonardo da Vinci" },
    { text: "Code is like humor. When you have to explain it, it’s bad.", author: "Cory House" },
    { text: "First, solve the problem. Then, write the code.", author: "John Johnson" },
    { text: "Experience is the name everyone gives to their mistakes.", author: "Oscar Wilde" },
    { text: "Innovation is the ability to see change as an opportunity - not a threat.", author: "Steve Jobs" },
    { text: "Make it work, make it right, make it fast.", author: "Kent Beck" },
    { text: "Talk is cheap. Show me the code.", author: "Linus Torvalds" }
];

function getRandomQuote() {
    return QUOTES[Math.floor(Math.random() * QUOTES.length)];
}

const args = process.argv.slice(2);
let format = 'text'; // 'text' or 'json'
let output = null;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--format') format = args[i+1];
    if (args[i] === '--output') output = args[i+1];
}

const quote = getRandomQuote();
let result;

if (format === 'json') {
    result = JSON.stringify(quote);
} else {
    result = `"${quote.text}" - ${quote.author}`;
}

if (output) {
    fs.writeFileSync(output, result);
    console.log(`Quote written to ${output}`);
} else {
    console.log(result);
}
