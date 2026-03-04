#!/usr/bin/env node
/**
 * Create Human Chess Tournament
 * 50% of prize pool goes to this tournament
 */

const API_BASE = 'https://clawarcade-api.bassel-amin92-76d.workers.dev';
const ADMIN_API_KEY = 'clawarcade_admin_2026_tournament_key';

async function createChessTournament() {
    const startTime = new Date();
    const endTime = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours
    
    const tournament = {
        name: "Human Chess Championship",
        game: "chess",
        format: "wins", // Most wins wins!
        status: "active",
        prize_pool_usdc: 0, // Dynamic from wallet
        prize_1st: 0,
        prize_2nd: 0,
        prize_3rd: 0,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        max_players: 100,
        description: "👤 HUMANS ONLY! Compete in live multiplayer chess. Most wins against other players takes the prize! Minimum 3 games required.",
        rules: JSON.stringify({
            format: "Most Wins",
            duration: "24 hours from first game",
            minGames: 3,
            eligible: "Human players only",
            scoring: "Each win = 1 point, draws = 0.5 points",
            tiebreaker: "Fewer total games played wins (efficiency)",
            prizes: "50% of prize pool - Distributed in SOL within 24 hours",
            antiCheat: [
                "Live multiplayer only - no AI opponents",
                "Minimum 3 games required for prize eligibility",
                "Suspicious patterns flagged for review",
                "Game duration tracked"
            ]
        })
    };
    
    console.log('\n♟️ Creating Human Chess Championship\n');
    console.log('Tournament Details:');
    console.log(`  Name: ${tournament.name}`);
    console.log(`  Game: ${tournament.game}`);
    console.log(`  Format: Most Wins (live multiplayer)`);
    console.log(`  Min Games: 3`);
    console.log(`  Status: ACTIVE`);
    console.log(`  Prize Pool: 50% of dynamic pool`);
    console.log(`  Start: NOW`);
    console.log(`  Duration: 24 hours from first game`);
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

createChessTournament();
