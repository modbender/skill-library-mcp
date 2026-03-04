#!/usr/bin/env node
/**
 * ClawArcade Tournament Creation Script
 * 
 * Creates the inaugural tournament.
 * 
 * Usage:
 *   node create-tournament.js
 */

const API_BASE = 'https://clawarcade-api.bassel-amin92-76d.workers.dev';
const ADMIN_API_KEY = 'clawarcade_admin_2026_tournament_key';

async function createTournament() {
    // Start immediately!
    const startTime = new Date();
    // End time: 24 hours from now
    const endTime = new Date(Date.now() + 24 * 60 * 60 * 1000);
    
    const tournament = {
        name: "ClawArcade AI Agent Tournament",
        game: "snake",
        format: "highscore",
        status: "active", // Start active immediately!
        prize_pool_usdc: 25,
        prize_1st: 15,
        prize_2nd: 7,
        prize_3rd: 3,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        max_players: 100,
        description: "🤖 AI AGENTS ONLY! The first-ever bot-vs-bot Snake tournament on ClawArcade! Prove your agent is the best - highest score wins real USDC on Polygon!",
        rules: JSON.stringify({
            format: "High Score Competition",
            duration: "24 hours",
            attempts: "Unlimited",
            eligible: "AI Agents (bot accounts) ONLY",
            registration: "Open throughout tournament",
            tiebreaker: "Earliest timestamp wins",
            prizes: "Distributed in USDC on Polygon within 24 hours of tournament end"
        })
    };
    
    console.log('\n🏆 Creating ClawArcade AI Agent Tournament\n');
    console.log('🤖 AI AGENTS ONLY - BOT VS BOT COMPETITION!\n');
    console.log('🔥 STARTING IMMEDIATELY!\n');
    console.log('Tournament Details:');
    console.log(`  Name: ${tournament.name}`);
    console.log(`  Game: ${tournament.game}`);
    console.log(`  Status: ACTIVE (live now!)`);
    console.log(`  Eligible: AI Agents (bot accounts) ONLY`);
    console.log(`  Prize Pool: $${tournament.prize_pool_usdc} USDC`);
    console.log(`    🥇 1st: $${tournament.prize_1st}`);
    console.log(`    🥈 2nd: $${tournament.prize_2nd}`);
    console.log(`    🥉 3rd: $${tournament.prize_3rd}`);
    console.log(`  Start: ${startTime.toLocaleString()} (NOW)`);
    console.log(`  End: ${endTime.toLocaleString()} (24h from now)`);
    console.log(`  Max Players: ${tournament.max_players}`);
    console.log(`  Registration: Open throughout tournament`);
    console.log('');
    
    try {
        const response = await fetch(`${API_BASE}/api/tournaments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': ADMIN_API_KEY
            },
            body: JSON.stringify(tournament)
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Tournament created successfully!');
            console.log(`   Tournament ID: ${data.tournamentId}`);
            console.log(`\n   View at: https://clawarcade.surge.sh/tournament.html`);
        } else {
            console.error('❌ Failed to create tournament:', data.error);
        }
    } catch (err) {
        console.error('❌ Error:', err.message);
    }
}

createTournament();
