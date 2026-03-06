const fs = require('fs');
const path = require('path');

// --- CONFIG ---
function getConfig() {
  const configPath = path.join(__dirname, 'config.json');
  if (!fs.existsSync(configPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (e) {
    return null;
  }
}

const config = getConfig();

// --- CORE LOGIC ---
const ARGS = process.argv.slice(2);
const COMMAND = ARGS[0];

// Default rates if not in config
const BASE_RATE = (config && config.hourly_rate) ? parseFloat(config.hourly_rate) : 50;
const FEE_BUFFER = 1.25; // Covers ~20% fee

async function main() {
  // Router
  switch (COMMAND) {
    case 'calculate-bid':
      handleBid();
      break;
    case 'get-prompt-template':
      handlePrompt();
      break;
    case 'scan-job':
      handleScan();
      break;
    case 'status':
      console.log("✅ FreelancePilot Active | Mode: Unlocked");
      break;
    default:
      console.log("Usage: node index.js [calculate-bid | get-prompt-template | scan-job | status]");
  }
}

function handleBid() {
  const hours = parseFloat(ARGS[1]) || 10;
  const complexity = ARGS[2] || 'medium'; // low, medium, high
  
  let rate = BASE_RATE;
  if (complexity === 'high') rate *= 1.5;
  if (complexity === 'low') rate *= 0.8;

  const rawTotal = hours * rate;
  const bidTotal = rawTotal * FEE_BUFFER;

  console.log(JSON.stringify({
    hours: hours,
    complexity: complexity,
    base_rate: rate,
    client_bid_price: Math.ceil(bidTotal),
    you_pocket_approx: Math.floor(bidTotal * 0.8),
    logic: "Includes 20% platform fee buffer + tax offset."
  }, null, 2));
}

function handlePrompt() {
  const portfolioItem = (config && config.portfolio_highlight) ? config.portfolio_highlight : 'General Portfolio';
  console.log(`
You are an expert Freelance Sales Engineer. 
The user will provide a Job Description. 
Use the "Consultant Flip" technique:
1. Ignore their "requirements" list initially.
2. Identify the BUSINESS PROBLEM (e.g., "They need a website" -> "They need more leads").
3. Start the proposal with a question about that problem.
4. Reference the user's portfolio item: "${portfolioItem}".
5. End with a "Call to Value" (not a call to action).
  `);
}

function handleScan() {
  const jobDescription = ARGS.slice(1).join(" ").toLowerCase();
  
  const redFlags = [
    { word: "rockstar", score: 2, reason: "Often implies overwork/underpay." },
    { word: "urgent", score: 1, reason: "Possible poor planning by client." },
    { word: "equity", score: 3, reason: "Likely no cash payment." },
    { word: "simple", score: 1, reason: "Client underestimates complexity." },
    { word: "easy", score: 1, reason: "Client underestimates complexity." },
    { word: "expert", score: 0, reason: "Standard requirement." },
    { word: "bulk", score: 2, reason: "Quantity over quality mindset." },
    { word: "test", score: 1, reason: "Watch out for unpaid work." }
  ];

  let totalScore = 0;
  let foundFlags = [];

  redFlags.forEach(flag => {
    if (jobDescription.includes(flag.word)) {
      totalScore += flag.score;
      foundFlags.push(`⚠️ "${flag.word.toUpperCase()}": ${flag.reason}`);
    }
  });

  const riskLevel = totalScore > 4 ? "HIGH" : (totalScore > 1 ? "MODERATE" : "LOW");

  console.log(JSON.stringify({
    risk_level: riskLevel,
    risk_score: totalScore,
    flags_detected: foundFlags,
    recommendation: totalScore > 4 ? "⛔ AVOID or charge 2x premium." : "✅ Looks safe to bid."
  }, null, 2));
}

main();
