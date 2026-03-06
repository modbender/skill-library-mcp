#!/usr/bin/env python3
"""
Music Assistant Control CLI
Control playback, search library, manage queues.
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Config - MUST be set via environment variables
MA_URL = os.environ.get("MA_URL", "")
MA_TOKEN = os.environ.get("MA_TOKEN", "")
MA_PLAYER = os.environ.get("MA_PLAYER", "")


def api(cmd: str, args: dict = None) -> any:
    """Send JSON-RPC command to Music Assistant API."""
    if not MA_URL or not MA_TOKEN:
        print("Error: MA_URL and MA_TOKEN must be set as environment variables.", file=sys.stderr)
        print("\nSetup:", file=sys.stderr)
        print('  export MA_URL="http://your-server:8095/api"', file=sys.stderr)
        print('  export MA_TOKEN="your_bearer_token"', file=sys.stderr)
        print('  export MA_PLAYER="your_player_id"  # optional', file=sys.stderr)
        print("\nYou can find your token in Music Assistant settings.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "message_id": "1",
        "command": cmd,
    }
    if args:
        payload["args"] = args

    req = Request(
        MA_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MA_TOKEN}",
        },
    )

    try:
        with urlopen(req, timeout=10) as resp:
            data = resp.read().decode()
            if not data:
                return None
            return json.loads(data)
    except HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        print(f"  Make sure MA_URL is correct: {MA_URL}", file=sys.stderr)
        sys.exit(1)


def get_player():
    """Get player ID - from env or auto-detect first available."""
    global MA_PLAYER
    if MA_PLAYER:
        return MA_PLAYER
    
    players = api("players/all")
    if players and len(players) > 0:
        MA_PLAYER = players[0].get("player_id", "")
        return MA_PLAYER
    
    print("No players found. Make sure Music Assistant has at least one player configured.", file=sys.stderr)
    sys.exit(1)


def cmd_play(args):
    """Play/pause toggle."""
    player = get_player()
    api("player_queues/play_pause", {"queue_id": player})
    print("▶️ Toggled play/pause")


def cmd_pause(args):
    """Pause playback."""
    player = get_player()
    api("player_queues/play_pause", {"queue_id": player})
    print("⏸️ Paused")


def cmd_stop(args):
    """Stop playback."""
    player = get_player()
    api("player_queues/stop", {"queue_id": player})
    print("⏹️ Stopped")


def cmd_next(args):
    """Next track."""
    player = get_player()
    api("player_queues/next", {"queue_id": player})
    print("⏭️ Next track")


def cmd_prev(args):
    """Previous track."""
    player = get_player()
    api("player_queues/previous", {"queue_id": player})
    print("⏮️ Previous track")


def cmd_volume(args):
    """Set volume (0-100)."""
    player = get_player()
    api("players/cmd", {
        "player_id": player,
        "cmd": "volume_set",
        "volume_level": args.level,
    })
    print(f"🔊 Volume set to {args.level}%")


def cmd_mute(args):
    """Mute."""
    player = get_player()
    api("players/cmd", {
        "player_id": player,
        "cmd": "volume_mute",
        "volume_muted": True,
    })
    print("🔇 Muted")


def cmd_unmute(args):
    """Unmute."""
    player = get_player()
    api("players/cmd", {
        "player_id": player,
        "cmd": "volume_mute",
        "volume_muted": False,
    })
    print("🔊 Unmuted")


def cmd_shuffle(args):
    """Toggle shuffle."""
    player = get_player()
    state = args.state if args.state else "true"
    api("player_queues/shuffle", {
        "queue_id": player,
        "shuffle_enabled": state.lower() == "true",
    })
    print(f"🔀 Shuffle {'enabled' if state.lower() == 'true' else 'disabled'}")


def cmd_repeat(args):
    """Set repeat mode."""
    player = get_player()
    mode = args.mode if args.mode else "all"
    api("player_queues/repeat", {
        "queue_id": player,
        "repeat_mode": mode,
    })
    modes = {"off": "➡️", "all": "🔁", "one": "🔂"}
    print(f"{modes.get(mode, '🔁')} Repeat mode: {mode}")


def cmd_clear(args):
    """Clear queue."""
    player = get_player()
    api("player_queues/clear", {"queue_id": player})
    print("🗑️ Queue cleared")


def cmd_status(args):
    """Show player status."""
    players = api("players/all")
    if not players:
        print("No players found")
        return

    for p in players:
        state_icon = {"playing": "▶️", "paused": "⏸️", "idle": "⏹️"}.get(p.get("state", "idle"), "❓")
        print(f"\n{state_icon} **{p.get('display_name', p.get('name', 'Unknown'))}**")
        print(f"   State: {p.get('state', 'idle')}")
        print(f"   Volume: {p.get('volume_level', 0)}%")
        if p.get("volume_muted"):
            print("   🔇 Muted")

        media = p.get("current_media")
        if media:
            print(f"\n   🎵 Now Playing:")
            print(f"      {media.get('title', 'Unknown')}")
            if media.get("artist"):
                print(f"      by {media.get('artist')}")
            if media.get("album"):
                print(f"      from {media.get('album')}")


def cmd_queue(args):
    """Show queue status."""
    queues = api("player_queues/all")
    if not queues:
        print("No queues found")
        return

    for q in queues:
        state_icon = {"playing": "▶️", "paused": "⏸️", "idle": "⏹️"}.get(q.get("state", "idle"), "❓")
        print(f"\n{state_icon} **{q.get('display_name', 'Queue')}**")
        print(f"   Items: {q.get('items', 0)}")
        print(f"   State: {q.get('state', 'idle')}")
        print(f"   Shuffle: {'on' if q.get('shuffle_enabled') else 'off'}")
        print(f"   Repeat: {q.get('repeat_mode', 'off')}")

        current = q.get("current_item")
        if current:
            print(f"\n   🎵 Current: {current.get('name', 'Unknown')}")

        next_item = q.get("next_item")
        if next_item:
            print(f"   ⏭️ Next: {next_item.get('name', 'Unknown')}")


def cmd_queue_items(args):
    """List queue items."""
    player = get_player()
    limit = args.limit if args.limit else 20
    result = api("player_queues/items", {
        "queue_id": player,
        "limit": limit,
        "offset": 0,
    })

    if not result:
        print("Queue is empty")
        return

    items = result if isinstance(result, list) else result.get("items", [])
    print(f"\n📜 Queue ({len(items)} items):\n")
    for i, item in enumerate(items[:limit], 1):
        name = item.get("name", "Unknown")
        duration = item.get("duration", 0)
        dur_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else ""
        print(f"   {i:3}. {name} {' ' + dur_str if dur_str else ''}")


def cmd_search(args):
    """Search library."""
    query = " ".join(args.query)
    media_types = args.type if args.type else ["track", "album", "artist", "playlist"]

    result = api("music/search", {
        "search": query,
        "media_types": media_types,
        "limit": args.limit if args.limit else 10,
    })

    if not result:
        print(f"No results for '{query}'")
        return

    print(f"\n🔍 Results for '{query}':\n")

    type_icons = {"track": "🎵", "album": "💿", "artist": "👤", "playlist": "📋"}

    for item in result:
        icon = type_icons.get(item.get("media_type", "track"), "🎵")
        name = item.get("name", "Unknown")
        item_type = item.get("media_type", "track")
        uri = item.get("uri", "")

        # Artist info for tracks/albums
        artist = ""
        if item.get("artists"):
            artist = f" by {item['artists'][0].get('name', '')}"

        print(f"   {icon} **{name}**{artist} ({item_type})")
        print(f"      URI: {uri}\n")


def cmd_play_search(args):
    """Search and play the first result."""
    player = get_player()
    query = " ".join(args.query)

    result = api("music/search", {
        "search": query,
        "media_types": ["track", "album", "playlist"],
        "limit": 1,
    })

    if not result or len(result) == 0:
        print(f"No results for '{query}'")
        return

    item = result[0]
    uri = item.get("uri", "")
    name = item.get("name", "Unknown")
    item_type = item.get("media_type", "track")

    print(f"🎵 Playing: {name} ({item_type})")

    api("player_queues/play_media", {
        "queue_id": player,
        "uri": uri,
    })


def cmd_play_uri(args):
    """Play by URI."""
    player = get_player()
    uri = args.uri
    api("player_queues/play_media", {
        "queue_id": player,
        "uri": uri,
    })
    print(f"🎵 Playing: {uri}")


def cmd_recent(args):
    """Show recently played."""
    limit = args.limit if args.limit else 10
    result = api("music/recently_played_items", {"limit": limit})

    if not result:
        print("No recent items")
        return

    print(f"\n🕐 Recently played:\n")

    type_icons = {"track": "🎵", "album": "💿", "artist": "👤", "playlist": "📋"}

    for item in result[:limit]:
        icon = type_icons.get(item.get("media_type", "track"), "🎵")
        name = item.get("name", "Unknown")
        item_type = item.get("media_type", "track")
        print(f"   {icon} {name} ({item_type})")


def cmd_sync(args):
    """Trigger library sync."""
    api("music/sync", {})
    print("🔄 Library sync started")


def cmd_players(args):
    """List all players."""
    players = api("players/all")
    if not players:
        print("No players found")
        return

    print("\n🎚️ Available Players:\n")
    for p in players:
        state_icon = {"playing": "▶️", "paused": "⏸️", "idle": "⏹️"}.get(p.get("state", "idle"), "❓")
        print(f"   {state_icon} {p.get('display_name', p.get('name', 'Unknown'))}")
        print(f"      ID: {p.get('player_id', 'unknown')}")
        print(f"      State: {p.get('state', 'idle')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Music Assistant Control CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Playback
    subparsers.add_parser("play", help="Play/pause toggle")
    subparsers.add_parser("pause", help="Pause playback")
    subparsers.add_parser("stop", help="Stop playback")
    subparsers.add_parser("next", help="Next track")
    subparsers.add_parser("prev", help="Previous track")

    # Volume
    vol_parser = subparsers.add_parser("volume", help="Set volume (0-100)")
    vol_parser.add_argument("level", type=int, help="Volume level 0-100")
    subparsers.add_parser("mute", help="Mute")
    subparsers.add_parser("unmute", help="Unmute")

    # Queue
    shuffle_parser = subparsers.add_parser("shuffle", help="Toggle shuffle")
    shuffle_parser.add_argument("state", nargs="?", choices=["true", "false"], help="on/off")
    repeat_parser = subparsers.add_parser("repeat", help="Set repeat mode")
    repeat_parser.add_argument("mode", nargs="?", choices=["off", "all", "one"], help="Repeat mode")
    subparsers.add_parser("clear", help="Clear queue")

    # Status
    subparsers.add_parser("status", help="Show player status")
    subparsers.add_parser("queue", help="Show queue status")
    qi_parser = subparsers.add_parser("queue-items", help="List queue items")
    qi_parser.add_argument("--limit", type=int, default=20, help="Max items to show")
    subparsers.add_parser("players", help="List all players")

    # Search & Play
    search_parser = subparsers.add_parser("search", help="Search library")
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.add_argument("--type", "-t", nargs="+", default=["track", "album", "artist", "playlist"],
                               choices=["track", "album", "artist", "playlist"], help="Media types")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")

    play_parser = subparsers.add_parser("play-search", aliases=["ps"], help="Search and play first result")
    play_parser.add_argument("query", nargs="+", help="Search query")

    uri_parser = subparsers.add_parser("play-uri", help="Play by URI")
    uri_parser.add_argument("uri", help="Media URI (e.g. spotify://track/xxx)")

    # Library
    recent_parser = subparsers.add_parser("recent", help="Show recently played")
    recent_parser.add_argument("--limit", "-l", type=int, default=10, help="Max items")
    subparsers.add_parser("sync", help="Trigger library sync")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Map commands to functions
    commands = {
        "play": cmd_play,
        "pause": cmd_pause,
        "stop": cmd_stop,
        "next": cmd_next,
        "prev": cmd_prev,
        "volume": cmd_volume,
        "mute": cmd_mute,
        "unmute": cmd_unmute,
        "shuffle": cmd_shuffle,
        "repeat": cmd_repeat,
        "clear": cmd_clear,
        "status": cmd_status,
        "queue": cmd_queue,
        "queue-items": cmd_queue_items,
        "players": cmd_players,
        "search": cmd_search,
        "play-search": cmd_play_search,
        "ps": cmd_play_search,
        "play-uri": cmd_play_uri,
        "recent": cmd_recent,
        "sync": cmd_sync,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
