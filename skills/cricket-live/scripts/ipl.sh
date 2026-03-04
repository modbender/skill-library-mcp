#!/usr/bin/env bash
# IPL Hub — standings, upcoming, results, live
set -uo pipefail
source "$(dirname "$0")/helpers.sh"

SUBCOMMAND="${1:-live}"

# IPL series detection — search for current IPL series
get_ipl_series_id() {
    local response
    response=$(api_call "series" "series-list" 86400)
    if [[ $? -ne 0 ]]; then
        echo ""
        return 1
    fi
    # Find IPL series (most recent)
    local series_id
    series_id=$(echo "$response" | jq -r '[.data // [] | .[] | select(.info // "" | test("IPL|Indian Premier League"; "i"))] | sort_by(.startDate) | last | .id // ""' 2>/dev/null)
    echo "$series_id"
}

filter_ipl_matches() {
    local matches="$1" filter="$2"
    # Filter matches containing "IPL" or "Indian Premier League" in name or series
    echo "$matches" | jq --arg f "$filter" '[.[] | select(
        (.name // "" | test("IPL|Indian Premier League"; "i")) or
        (.series_id // "" | test("IPL"; "i"))
    ) | select(
        if $f == "live" then (.matchStarted == true and .matchEnded != true)
        elif $f == "upcoming" then (.matchStarted == false or .matchStarted == "false")
        elif $f == "results" then (.matchEnded == true or .matchEnded == "true")
        else true
        end
    )]' 2>/dev/null
}

case "$SUBCOMMAND" in
    standings|table|points)
        echo "🏆 *IPL STANDINGS*"
        echo "━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Try to get series info with standings
        series_id=$(get_ipl_series_id)
        if [[ -n "$series_id" ]]; then
            response=$(api_call "series_points" "ipl-standings" 1800 "id=${series_id}")
            if [[ $? -eq 0 ]]; then
                echo "$response" | jq -c '.data // [] | .[]' 2>/dev/null | while read -r team; do
                    name=$(echo "$team" | jq -r '.teamname // .team // "Unknown"')
                    played=$(echo "$team" | jq -r '.matches // .played // 0')
                    won=$(echo "$team" | jq -r '.win // .won // 0')
                    lost=$(echo "$team" | jq -r '.loss // .lost // 0')
                    points=$(echo "$team" | jq -r '.points // 0')
                    nrr=$(echo "$team" | jq -r '.nrr // "0.000"')
                    
                    echo "  🏏 *${name}*"
                    echo "     P:${played} W:${won} L:${lost} Pts:${points} NRR:${nrr}"
                    echo ""
                done
            else
                echo "⚠️ Could not fetch IPL standings"
                echo "The IPL season may not have started yet, or series ID not found."
            fi
        else
            echo "⚠️ No active IPL series found"
            echo "The IPL season may not have started yet."
        fi
        ;;
    
    upcoming|schedule)
        echo "📅 *UPCOMING IPL MATCHES*"
        echo "━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        response=$(api_call "matches" "all-matches" 1800 "offset=0")
        if [[ $? -ne 0 ]]; then
            echo "$response"
            exit 1
        fi
        
        matches=$(echo "$response" | jq '.data // []')
        ipl=$(filter_ipl_matches "$matches" "upcoming")
        count=$(echo "$ipl" | jq 'length')
        
        if [[ "$count" -eq 0 ]]; then
            echo "No upcoming IPL matches found"
            echo "The IPL season may not have started yet."
            exit 0
        fi
        
        echo "$ipl" | jq -c '.[]' | head -10 | while read -r match; do
            name=$(echo "$match" | jq -r '.name // "Unknown"')
            date_str=$(echo "$match" | jq -r '.date // .dateTimeGMT // ""')
            venue=$(echo "$match" | jq -r '.venue // ""')
            
            echo "🏏 *${name}*"
            echo "   📅 $(to_ist "$date_str")"
            [[ -n "$venue" ]] && echo "   📍 $venue"
            echo ""
        done
        ;;
    
    results|recent)
        echo "✅ *RECENT IPL RESULTS*"
        echo "━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        response=$(api_call "matches" "all-matches" 1800 "offset=0")
        if [[ $? -ne 0 ]]; then
            echo "$response"
            exit 1
        fi
        
        matches=$(echo "$response" | jq '.data // []')
        ipl=$(filter_ipl_matches "$matches" "results")
        count=$(echo "$ipl" | jq 'length')
        
        if [[ "$count" -eq 0 ]]; then
            echo "No recent IPL results found"
            exit 0
        fi
        
        echo "$ipl" | jq -c '.[]' | head -10 | while read -r match; do
            name=$(echo "$match" | jq -r '.name // "Unknown"')
            status=$(echo "$match" | jq -r '.status // ""')
            
            score_lines=""
            while read -r s; do
                [[ -z "$s" ]] && continue
                inning=$(echo "$s" | jq -r '.inning // ""')
                runs=$(echo "$s" | jq -r '.r // 0')
                wickets=$(echo "$s" | jq -r '.w // 0')
                overs=$(echo "$s" | jq -r '.o // 0')
                score_lines="${score_lines}   📊 ${inning}: ${runs}/${wickets} (${overs} ov)\n"
            done < <(echo "$match" | jq -c '.score // [] | .[]' 2>/dev/null)
            
            echo "🏏 *${name}*"
            [[ -n "$score_lines" ]] && echo -e "$score_lines"
            echo "   $(format_status "$status")"
            echo ""
        done
        ;;
    
    live)
        echo "🔴 *LIVE IPL MATCHES*"
        echo "━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        response=$(api_call "currentMatches" "live-matches" 120)
        if [[ $? -ne 0 ]]; then
            echo "$response"
            exit 1
        fi
        
        matches=$(echo "$response" | jq '.data // []')
        ipl=$(filter_ipl_matches "$matches" "live")
        count=$(echo "$ipl" | jq 'length')
        
        if [[ "$count" -eq 0 ]]; then
            echo "No live IPL matches right now 🏏"
            echo ""
            echo "Check upcoming: bash scripts/ipl.sh upcoming"
            exit 0
        fi
        
        echo "$ipl" | jq -c '.[]' | while read -r match; do
            name=$(echo "$match" | jq -r '.name // "Unknown"')
            status=$(echo "$match" | jq -r '.status // "In Progress"')
            venue=$(echo "$match" | jq -r '.venue // ""')
            id=$(echo "$match" | jq -r '.id // ""')
            
            echo "🏏 *${name}*"
            
            echo "$match" | jq -c '.score // [] | .[]' 2>/dev/null | while read -r s; do
                inning=$(echo "$s" | jq -r '.inning // ""')
                runs=$(echo "$s" | jq -r '.r // 0')
                wickets=$(echo "$s" | jq -r '.w // 0')
                overs=$(echo "$s" | jq -r '.o // 0')
                echo "   📊 ${inning}: ${runs}/${wickets} (${overs} ov)"
            done
            
            echo "   $(format_status "$status")"
            [[ -n "$venue" ]] && echo "   📍 $venue"
            [[ -n "$id" ]] && echo "   🔗 ID: $id"
            echo ""
        done
        ;;
    
    *)
        echo "🏏 *IPL Hub*"
        echo ""
        echo "Usage: bash scripts/ipl.sh <command>"
        echo ""
        echo "Commands:"
        echo "  live       — Live IPL matches (default)"
        echo "  standings  — Points table"
        echo "  upcoming   — Upcoming IPL matches"
        echo "  results    — Recent IPL results"
        ;;
esac
