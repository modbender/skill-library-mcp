#!/usr/bin/env node
/**
 * Blinko stats viewer
 * Usage: node stats.js <address> [profile|games|leaderboard|honey] [limit]
 */
const API = 'https://api.blinko.gg';

async function get(url) {
  const r = await fetch(url);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const j = await r.json();
  return j.data || j;
}

const pad = (s, w = 18) => String(s).padEnd(w);

async function profile(addr) {
  const p = await get(`${API}/blinko/profiles/${addr}`);
  if (!p) return console.log('No profile yet - play a game first.');
  console.log('🧑 Profile');
  console.log(`${pad('Address')} ${addr}`);
  if (p.name) console.log(`${pad('Name')} ${p.name}`);
  console.log(`${pad('Total Honey')} ${p.totalHoney || 0}`);
  console.log(`${pad('Harvested')} ${p.harvestedHoney || 0}`);
  console.log(`${pad('Referral')} ${p.referralHoney || 0}`);
  if (p.referralCode) console.log(`${pad('Referral Code')} ${p.referralCode}`);
  if (p.stats) {
    console.log('\n📊 Stats');
    console.log(`${pad('Games')} ${p.stats.totalGamesPlayed || 0}`);
    console.log(`${pad('Best Multi')} ${p.stats.highestMultiplier || 0}x`);
    console.log(`${pad('Bonus Games')} ${p.stats.bonusGamesReached || 0}`);
    console.log(`${pad('Best Bonus Lvl')} ${p.stats.highestBonusLevel || 0}`);
    console.log(`${pad('Streak')} ${p.stats.currentDailyStreak || 0} (max ${p.stats.maxDailyStreak || 0})`);
  }
}

async function games(addr, limit = 10) {
  const g = await get(`${API}/blinko/players/${addr}/games?limit=${limit}`);
  if (!g || !Array.isArray(g) || !g.length) return console.log('No games yet.');
  console.log(`🎮 Last ${g.length} games`);
  g.forEach((x, i) => {
    const bet = (Number(x.betAmount || 0) / 1e18).toFixed(4);
    const pay = (Number(x.payoutAmount || 0) / 1e18).toFixed(4);
    const won = x.status === 'won';
    console.log(`${won ? '✅' : '❌'} ${bet} → ${pay} ETH  ${x.gameId?.slice(0, 14)}...`);
  });
}

async function leaderboard(addr) {
  const d = await get(`${API}/blinko/v2/leaderboard?address=${addr}`);
  if (!d) return console.log('Leaderboard unavailable.');
  const top = d.leaderboard || [];
  console.log(`🏆 Top 10 (of ${d.total || '?'} players)`);
  top.slice(0, 10).forEach(e => {
    const name = e.name || `${e.address.slice(0, 10)}...`;
    const tw = e.twitterHandle ? ` ${e.twitterHandle}` : '';
    console.log(`${String(e.rank).padStart(2)}. ${name}${tw} — 🍯 ${e.totalHoney}`);
  });
  console.log('');
  if (d.myRank) {
    console.log(`You: #${d.myRank.rank} — 🍯 ${d.myRank.totalHoney}`);
  } else {
    const me = top.find(e => e.address.toLowerCase() === addr.toLowerCase());
    console.log(me ? `You: #${me.rank} — 🍯 ${me.totalHoney}` : 'You: not ranked yet');
  }
}

async function honey(addr) {
  const h = await get(`${API}/blinko/profiles/${addr}/honey`);
  if (!h) return console.log('No honey data yet.');
  console.log('🍯 Honey');
  console.log(`${pad('Harvested')} ${h.harvested || h.harvestedHoney || 0}`);
  console.log(`${pad('Referral')} ${h.referral || h.referralHoney || 0}`);
  console.log(`${pad('Total')} ${h.total || h.totalHoney || 0}`);
}

const [,, addr, cmd = 'profile', lim] = process.argv;
if (!addr || !addr.startsWith('0x')) {
  console.log('Usage: node stats.js <address> [profile|games|leaderboard|honey] [limit]');
  process.exit(1);
}

const fns = { profile, games, leaderboard, honey };
const fn = fns[cmd];
if (!fn) { console.log(`Unknown command: ${cmd}`); process.exit(1); }

fn(addr, lim ? Number(lim) : undefined).catch(e => { console.error('❌', e.message); process.exit(1); });
