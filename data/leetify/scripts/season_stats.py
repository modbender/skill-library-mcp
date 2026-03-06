
import sys
import os
import json
from datetime import datetime

# Use current directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from profile_with_stats import api_request
except ImportError:
    print("Error importing profile_with_stats")
    sys.exit(1)

# Дата начала сезона: 22 января 2026
SEASON_START = datetime(2026, 1, 22)

# Load players from steam_ids.json instead of hardcoding
STEAM_IDS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "steam_ids.json")

def load_players():
    players = []
    try:
        with open(STEAM_IDS_JSON, 'r') as f:
            data = json.load(f)
            for username, info in data.items():
                players.append({
                    'name': info.get('name', username),
                    'handle': f"@{username}",
                    'steam_id': info.get('steam_id')
                })
    except Exception as e:
        print(f"Error loading players from {STEAM_IDS_JSON}: {e}")
    return players

players = load_players()


def calculate_stats(steam_id):
    # Get profile for rating
    profile_result = api_request('/v3/profile', {'steam64_id': steam_id})
    premier_rank = 0
    if profile_result['success']:
        raw_premier = profile_result['data'].get('ranks', {}).get('premier', 0)
        premier_rank = raw_premier if raw_premier is not None else 0

    # Get matches for stats
    matches_result = api_request('/v3/profile/matches', {'steam64_id': steam_id, 'limit': 100})
    if not matches_result['success']:
        return None
        
    raw_matches = matches_result['data']
    season_matches = []
    
    for m in raw_matches:
        if not m.get('finished_at'): continue
        
        date_str = m['finished_at'].replace('Z', '')
        if '.' in date_str: date_str = date_str.split('.')[0]
        try:
            finished_at = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue

        if finished_at < SEASON_START: continue
        if m.get('data_source') != 'matchmaking': continue
        
        player_stat = None
        for s in m.get('stats', []):
            if s['steam64_id'] == steam_id:
                player_stat = s
                break
        
        if not player_stat: continue
        
        player_team = player_stat['initial_team_number']
        player_score = 0
        enemy_score = 0
        for ts in m.get('team_scores', []):
            if ts['team_number'] == player_team:
                player_score = ts['score']
            else:
                enemy_score = ts['score']
        
        outcome = 'win' if player_score > enemy_score else ('loss' if player_score < enemy_score else 'tie')
        
        season_matches.append({
            'outcome': outcome,
            'kills': player_stat.get('total_kills', 0),
            'deaths': player_stat.get('total_deaths', 0),
            'adr': player_stat.get('dpr', 0),
            'hs_kills': player_stat.get('total_hs_kills', 0)
        })

    if not season_matches:
        return {'count': 0, 'premier': premier_rank}

    count = len(season_matches)
    kills = sum(m['kills'] for m in season_matches)
    deaths = sum(m['deaths'] for m in season_matches)
    adr = sum(m['adr'] for m in season_matches) / count
    hs_pct = (sum(m['hs_kills'] for m in season_matches) / max(kills, 1)) * 100
    wins = len([m for m in season_matches if m['outcome'] == 'win'])
    winrate = (wins / count) * 100
    kd = kills / max(deaths, 1)
    
    return {
        'count': count,
        'kd': kd,
        'adr': adr,
        'hs': hs_pct,
        'winrate': winrate,
        'premier': premier_rank
    }

results = []
for p in players:
    stats = calculate_stats(p['steam_id'])
    if stats and (stats['count'] > 0 or stats['premier'] > 0):
        results.append((p, stats))

# Сортировка по KD
results.sort(key=lambda x: x[1]['kd'], reverse=True)

print("🏆 *Топ сезона CS2 (с 22.01.2026)*")
print(f"🗓 _Данные на: {datetime.now().strftime('%d.%m.%Y %H:%M')} UTC_\n")

medals = ["🥇", "🥈", "🥉"]

for i, (p, stats) in enumerate(results):
    place_emoji = medals[i] if i < 3 else f"{i+1}."
    name = f"*{p['name']}*"
    kd = f"*{stats['kd']:.2f}*"
    wr = f"{stats['winrate']:.0f}%" if stats['count'] > 0 else "0%"
    if stats['count'] > 0:
        if stats['winrate'] >= 55: wr += " 🔥"
        elif stats['winrate'] <= 45: wr += " 💀"
    
    premier = f"`{stats['premier']}`" if stats['premier'] > 0 else "_нет_"
    
    line = f"{place_emoji} {name} — {premier} pts | KD: {kd} | ADR: {stats['adr']:.0f} | WR: {wr} | {stats['count']} игр"
    print(line)

if not results:
    print("\n🤷‍♂️ Матчей в новом сезоне пока не найдено.")
