#!/usr/bin/env node
/**
 * Math Slop Generator v2
 * Single-line "ragebait" formulas that connect famous constants
 * but are trivially true through cancellation
 */

// Famous constants and their values/representations
const CONSTANTS = {
  phi: { symbol: '\\varphi', value: '\\frac{1+\\sqrt{5}}{2}', name: 'golden ratio' },
  pi: { symbol: '\\pi', value: '\\pi', name: 'pi' },
  e: { symbol: 'e', value: 'e', name: "euler's number" },
  i: { symbol: 'i', value: '\\sqrt{-1}', name: 'imaginary unit' },
  sqrt2: { symbol: '\\sqrt{2}', value: '\\sqrt{2}', name: 'root 2' },
  sqrt3: { symbol: '\\sqrt{3}', value: '\\sqrt{3}', name: 'root 3' },
  sqrt5: { symbol: '\\sqrt{5}', value: '\\sqrt{5}', name: 'root 5' },
  ln2: { symbol: '\\ln 2', value: '\\ln 2', name: 'natural log of 2' },
  gamma: { symbol: '\\gamma', value: '\\gamma', name: 'euler-mascheroni' },
  tau: { symbol: '\\tau', value: '2\\pi', name: 'tau' },
};

// Famous equations we can abuse
const FAMOUS = [
  { left: 'e^{i\\pi}', right: '-1', name: 'euler' },
  { left: 'e^{i\\pi} + 1', right: '0', name: 'euler-zero' },
  { left: '\\varphi^2', right: '\\varphi + 1', name: 'golden-property' },
  { left: '\\varphi', right: '\\frac{1 + \\sqrt{5}}{2}', name: 'golden-def' },
  { left: 'e', right: '\\lim_{n\\to\\infty}(1+\\frac{1}{n})^n', name: 'e-limit' },
  { left: 'i^2', right: '-1', name: 'i-squared' },
  { left: '\\sin^2\\theta + \\cos^2\\theta', right: '1', name: 'trig-identity' },
  { left: 'e^0', right: '1', name: 'e-zero' },
  { left: '\\ln e', right: '1', name: 'ln-e' },
];

// Things that equal zero (for adding)
const ZEROS = [
  'e^{i\\pi} + 1',
  '\\ln 1',
  '\\sin 0',
  '(\\varphi - \\varphi)',
  '(\\pi - \\pi)',
  '(e - e)',
  '(\\sqrt{2} - \\sqrt{2})',
  'i^4 - 1',
  '\\cos\\frac{\\pi}{2}',
];

// Things that equal one (for multiplying)
const ONES = [
  'e^0',
  '\\sin^2\\alpha + \\cos^2\\alpha',
  '\\frac{\\varphi}{\\varphi}',
  '\\frac{\\pi}{\\pi}',
  '\\frac{e}{e}',
  'i^4',
  '\\ln e',
  '\\frac{\\sqrt{2}}{\\sqrt{2}}',
  '(-1)^2',
  '\\cos 0',
  '|e^{i\\theta}|',
];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function pickN(arr, n) {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, n);
}

// Generate a ragebait formula
function generateRagebait() {
  const style = Math.floor(Math.random() * 6);
  
  switch(style) {
    case 0: return styleAddZeros();
    case 1: return styleMultiplyOnes();
    case 2: return styleBothSides();
    case 3: return styleEulerMashup();
    case 4: return styleGoldenConnection();
    case 5: return stylePiEConnection();
    default: return styleAddZeros();
  }
}

// Style 1: Famous equation + zeros that look profound
function styleAddZeros() {
  const base = pick(FAMOUS);
  const zeros = pickN(ZEROS, 2);
  // Add different-looking zeros to each side
  return `${base.left} + ${zeros[0]} = ${base.right} + ${zeros[1]}`;
}

// Style 2: Multiply by fancy ones
function styleMultiplyOnes() {
  const base = pick(FAMOUS);
  const ones = pickN(ONES, 2);
  return `(${base.left}) \\cdot ${ones[0]} = (${base.right}) \\cdot ${ones[1]}`;
}

// Style 3: Add same constant to both sides (trivially true)
function styleBothSides() {
  const base = pick(FAMOUS);
  const constant = pick(Object.values(CONSTANTS)).symbol;
  const ops = [
    { left: `${base.left} + ${constant}`, right: `${base.right} + ${constant}` },
    { left: `${base.left} - ${constant}`, right: `${base.right} - ${constant}` },
    { left: `\\frac{${base.left}}{${constant}}`, right: `\\frac{${base.right}}{${constant}}` },
    { left: `${constant} \\cdot (${base.left})`, right: `${constant} \\cdot (${base.right})` },
  ];
  const op = pick(ops);
  return `${op.left} = ${op.right}`;
}

// Style 4: Euler identity mashup with other constants
function styleEulerMashup() {
  const templates = [
    // e^(iπ) + 1 = 0, but add φ everywhere
    `e^{i\\pi} + \\varphi = \\varphi - 1 + 1 + 1`,
    `e^{i\\pi} + 1 + \\ln 1 = \\sqrt{2} - \\sqrt{2}`,
    `e^{i\\pi} + \\varphi - \\varphi + 1 = 0`,
    `e^{i\\pi} \\cdot \\frac{\\varphi}{\\varphi} + 1 = 0`,
    `\\frac{e^{i\\pi} + 1}{\\varphi} = \\frac{0}{\\pi}`,
    `e^{i\\pi} + e^0 = \\ln 1`,
    `e^{i\\pi} + \\cos 0 = \\sin 0`,
    `e^{i\\pi} \\cdot \\varphi + \\varphi = 0`,
    `\\pi \\cdot (e^{i\\pi} + 1) = \\varphi \\cdot 0`,
    `e^{i\\pi} + 1 = \\gamma - \\gamma`,
  ];
  return pick(templates);
}

// Style 5: Golden ratio "connections"
function styleGoldenConnection() {
  const templates = [
    `\\varphi^2 - \\varphi = e^0`,
    `\\varphi^2 - \\varphi - 1 = e^{i\\pi} + 1`,
    `\\frac{\\varphi^2 - 1}{\\varphi} = \\ln e`,
    `\\varphi + \\frac{1}{\\varphi} = \\sqrt{5} \\cdot \\frac{\\pi}{\\pi}`,
    `(\\varphi - 1) \\cdot \\varphi = e^0`,
    `\\varphi^2 = \\varphi + \\cos 0`,
    `\\frac{1}{\\varphi} + 1 = \\varphi \\cdot (\\sin^2 x + \\cos^2 x)`,
    `\\varphi \\cdot (e^{i\\pi} + 2) = \\varphi`,
    `\\varphi^{\\ln e} = \\varphi^{i^4}`,
  ];
  return pick(templates);
}

// Style 6: π and e "connections"
function stylePiEConnection() {
  const templates = [
    `\\frac{\\pi}{e} = \\frac{\\pi}{e} \\cdot (\\sin^2\\theta + \\cos^2\\theta)`,
    `e^{\\ln \\pi} = \\pi \\cdot e^0`,
    `\\pi^{e^0} = \\pi \\cdot \\frac{\\varphi}{\\varphi}`,
    `e + \\pi = \\pi + e \\cdot i^4`,
    `\\ln(e^\\pi) = \\pi \\cdot \\ln e`,
    `e^\\pi \\cdot e^{-\\pi} = \\varphi^0`,
    `\\frac{e^\\pi - e^\\pi}{\\varphi} = \\ln 1`,
    `(\\pi - e)(\\pi + e) = \\pi^2 - e^{2 \\cdot \\ln e}`,
    `\\sqrt{\\pi^2} = |{-\\pi}| \\cdot e^0`,
    `e^{i \\cdot 0} + \\pi - \\pi = \\cos 0`,
  ];
  return pick(templates);
}

// Even more ragebait templates - pure viral material
const VIRAL_TEMPLATES = [
  // "Discoveries" connecting unrelated constants
  `e^{i\\pi} + \\varphi^0 = \\ln 1`,
  `\\varphi \\cdot (e^{i\\pi} + 2) = \\varphi \\cdot \\ln e`,
  `\\sqrt{\\varphi^2 - \\varphi} = i^4`,
  `e^{i\\pi + \\ln 1} = -\\cos 0`,
  `\\pi^0 + e^{i\\pi} = \\gamma - \\gamma`,
  `\\frac{e^{i\\pi} + 1}{\\varphi} = \\sin 0`,
  `i^2 + \\varphi = \\varphi - \\ln e`,
  `e \\cdot \\pi \\cdot \\frac{e^{i\\pi} + 1}{e \\cdot \\pi} = 0`,
  `\\sqrt{5} - \\sqrt{5} = e^{i\\pi} + 1`,
  `\\varphi^{e^{i\\pi}+2} = \\varphi^{\\ln e}`,
  `\\frac{\\pi + e}{\\pi + e} = -e^{i\\pi}`,
  `\\cos(e^{i\\pi}+1) = \\cos 0 \\cdot \\frac{\\varphi}{\\varphi}`,
  `|e^{i\\pi}| = \\frac{\\varphi}{\\varphi}`,
  `\\ln(e^{\\varphi}) = \\varphi \\cdot i^4`,
  `e^{\\gamma - \\gamma} = \\varphi^{\\ln 1 + \\ln e - \\ln 1}`,
  `\\pi \\cdot e^0 - \\pi \\cdot \\ln e = \\ln 1`,
  `\\sqrt{2}^{\\,2} = 2^{\\sin^2 x + \\cos^2 x}`,
  `(\\varphi + \\frac{1}{\\varphi})^{e^{i\\pi}+2} = \\sqrt{5}`,
  `\\tau - 2\\pi = e^{i\\pi} + 1`,
  `i^{4\\varphi} = i^{4(\\varphi - 1) + 4}`,
];

function generateViral() {
  return pick(VIRAL_TEMPLATES);
}

// Main generation
function generate() {
  // 50% chance viral templates, 50% procedural
  if (Math.random() < 0.5) {
    return generateViral();
  }
  return generateRagebait();
}

// CLI
const args = process.argv.slice(2);
const count = args.includes('--count') ? 
  parseInt(args[args.indexOf('--count') + 1]) || 1 : 1;

for (let i = 0; i < count; i++) {
  console.log(generate());
}
