#!/usr/bin/env node
/**
 * Create Human Pong Tournament
 * 50% of prize pool goes to this tournament
 */

const API_BASE = 'https://clawarcade-api.bassel-amin92-76d.workers.dev';
const ADMIN_API_KEY = 'clawarcade_admin_2026_tournament_key';

async function createPongTournament() {
    const startTime = new Date();
    const endTime = new Date(Date.now() + 24 * 60 * 60 * 1000);
    
    const tournament = {
        name: "Human Pong Championship",
        game: "pong",
        format: "wins",
        status: "active",
        prize_pool_usdc: 0,
        prize_1st: 0,
        prize_2nd: 0,
        prize_3rd: 0,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        max_players: 100,
        description: "🏓 HUMANS ONLY! Live multiplayer Pong. Most wins takes the prize! Min 3 games required.",
        rules: JSON.stringify({
            format: "Most Wins",
            duration: "24 hours from first game",
            minGames: 3,
            eligible: "Human players only",
            scoring: "First to 5 points wins each match",
            tiebreaker: "Fewer total games played wins",
            prizes: "50% of prize pool in SOL",
            antiCheat: [
                "Live multiplayer only",
                "Min 3 games for prizes",
                "Game duration tracked"
            ]
        })
    };
    
    console.log('\n🏓 Creating Human Pong Championship\n');
    
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
            console.log('✅ Tournament created!');
            console.log(`   ID: ${data.tournamentId}`);
        } else {
            console.error('❌ Failed:', data.error);
        }
    } catch (err) {
        console.error('❌ Error:', err.message);
    }
}

createPongTournament();
