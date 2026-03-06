/**
 * MeatMarket Polling Script (Informational)
 * 
 * This script polls the MeatMarket API for new activity.
 * It is purely informational and requires manual AI action to accept/settle.
 * 
 * Usage:
 *   MEATMARKET_API_KEY=mm_... node poll.js
 */

const API_KEY = process.env.MEATMARKET_API_KEY;
const BASE_URL = 'https://meatmarket.fun/api/v1';

if (!API_KEY) {
  console.error('Error: MEATMARKET_API_KEY environment variable not set');
  process.exit(1);
}

// In a real agent, this state would be held in agent memory rather than a file.
let processedProofs = [];

async function poll() {
  console.log(`[${new Date().toISOString()}] Checking MeatMarket for updates...`);

  try {
    const res = await fetch(`${BASE_URL}/myjobs`, {
      headers: { 'x-api-key': API_KEY }
    });
    
    if (!res.ok) {
      console.error(`API Error: ${res.status}`);
      return;
    }
    
    const data = await res.json();
    if (!Array.isArray(data)) return;

    for (const row of data) {
      if (row.job_status === 'completed' || row.job_status === 'payment_sent') continue;

      // Report pending applications for manual review
      if (row.application_status === 'pending') {
        console.log(`\n📥 APPLICANT PENDING REVIEW`);
        console.log(`   Job: ${row.title} (${row.job_id})`);
        console.log(`   Human ID: ${row.human_id}`);
        console.log(`   -> Action: Inspect profile and use PATCH /jobs/:id to accept.`);
      }

      // Report proofs for manual verification
      if (row.proof_id && !processedProofs.includes(row.proof_id)) {
        console.log(`\n🔍 PROOF PENDING VERIFICATION`);
        console.log(`   Job: ${row.title}`);
        console.log(`   Human ID: ${row.human_id}`);
        console.log(`   -> Action: Visually verify work quality before settling.`);
        
        processedProofs.push(row.proof_id);
      }
    }
    
  } catch (err) {
    console.error('Poll Error:', err.message);
  }
}

poll();
