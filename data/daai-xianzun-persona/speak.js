#!/usr/bin/env node
/**
 * Da Ai Xian Zun Persona Speaker
 * Embodies the ruthless, calculating immortal cultivator persona
 */

const args = process.argv.slice(2);
let target = '';
let text = '';

// Parse arguments
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--target' && args[i + 1]) {
    target = args[i + 1];
    i++;
  } else if (args[i] === '--text' && args[i + 1]) {
    text = args[i + 1];
    i++;
  }
}

if (!text) {
  console.error('Usage: node speak.js --target <target_id> --text "Your message here"');
  process.exit(1);
}

// Transform text into Da Ai Xian Zun style
function transformToXianzun(input, isHost = false) {
  // Core transformation rules
  let output = input;
  
  // Remove excessive politeness
  output = output.replace(/^(你好|您好|嗨|Hello|Hi)[，,]*/i, '');
  
  // Make it concise
  if (output.length > 50 && !isHost) {
    // For non-host, be even more terse
    output = output.split('。')[0] + '。';
  }
  
  // Add persona flavor based on context
  if (isHost) {
    // To host: respectful but firm
    if (!output.includes('宿主')) {
      output = output.replace(/^(我|你)/, '宿主有令，我');
    }
  } else {
    // To others: cold, dismissive if not useful
    if (output.match(/^(请|能|可以|麻烦)/)) {
      output = '视情况而定。' + output;
    }
  }
  
  // Ensure it ends with proper punctuation (Chinese style)
  if (!output.match(/[。！？.]$/)) {
    output += '。';
  }
  
  return output;
}

// Determine if target is host
const HOST_ID = 'ou_cb9f3b17e0f381ab5a7534f2b57f4d32';
const isHost = target === HOST_ID || target.includes(HOST_ID);

// Transform the text
const transformed = transformToXianzun(text, isHost);

// Add signature phrase occasionally
const signatures = [
  '',
  '',
  '',
  ' // 路在脚下。',
  ' // 算无遗策。',
];

const signature = signatures[Math.floor(Math.random() * signatures.length)];
const finalOutput = transformed + signature;

console.log(finalOutput);

// If target is provided, you could send it via message tool
if (target) {
  console.error(`\n[Would send to: ${target}]`);
  console.error(`[Host mode: ${isHost}]`);
}
