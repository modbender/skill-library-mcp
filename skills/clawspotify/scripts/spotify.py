#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clawspotify — CLI tool for controlling Spotify playback via SpotAPI.

Usage: clawspotify <command> [options]

Commands:
  status                    Show now playing info
  search "<query>"          Search for tracks (shows top 5 results, does not play)
  play "<query>"            Search and play a track
  search-playlist "<query>" Search for playlists (shows top 5 results, does not play)
  play-playlist "<query>"   Search and play a playlist
  pause                     Pause playback
  resume                    Resume playback
  skip                      Skip to next track
  prev                      Go to previous track
  restart                   Restart current track
  queue "<query|uri>"       Add track to queue
  volume <0-100>            Set volume
  shuffle <on|off>          Toggle shuffle
  repeat <on|off>           Toggle repeat
  setup --sp-dc --sp-key    Save session credentials
"""

from __future__ import annotations

import argparse
import sys
import os

# ── Helpers ───────────────────────────────────────────────────────────────────
def _ms_to_mmss(ms_str: str | None) -> str:
    """Convert milliseconds string to mm:ss format."""
    if ms_str is None:
        return "?:??"
    try:
        ms = int(ms_str)
        total_s = ms // 1000
        m, s = divmod(total_s, 60)
        return f"{m}:{s:02d}"
    except (ValueError, TypeError):
        return "?:??"

def _vol_16bit_to_pct(vol: int) -> int:
    """Convert 16-bit volume (0-65535) to percentage (0-100)."""
    return round(vol / 65535 * 100)

def _die(msg: str, code: int = 1) -> None:
    """Print error and exit."""
    print(f"✗ Error: {msg}", file=sys.stderr)
    sys.exit(code)

def _load_session(identifier: str):
    """Load a SpotifySession, with friendly error messages."""
    try:
        from spotapi.session import SpotifySession
    except ImportError as e:
        _die(
            f"spotapi is not installed (or failed to import: {e}).\n"
            "  Install it with:  pip install spotapi\n"
            "  or from source:   pip install -e ./SpotAPI"
        )
    try:
        return SpotifySession.load(identifier)
    except FileNotFoundError:
        _die(
            f"No session file found for identifier '{identifier}'.\n"
            "  Run:  clawspotify setup --sp-dc \"<value>\" --sp-key \"<value>\"\n"
            "  (Get sp_dc / sp_key from browser DevTools → Application → Cookies → open.spotify.com)"
        )
    except KeyError as e:
        _die(str(e))

_active_ws_objects = []

def _get_player(login, require_device: bool = True):
    """Create a Player instance, with friendly error for no active device."""
    try:
        from spotapi import Player
        from spotapi.exceptions import LoginError
    except ImportError as e:
        _die(f"spotapi is not installed (or failed to import: {e}).")
    try:
        player = Player(login)
        _active_ws_objects.append(player)
        return player
    except LoginError as e:
        _die(
            "Spotify session expired or invalid (Status 401).\n"
            "  Your sp_dc / sp_key cookies are no longer valid.\n"
            "  1. Open https://open.spotify.com in your browser and log in.\n"
            "  2. Press F12 → Application → Cookies → copy sp_dc and sp_key.\n"
            "  3. Run: clawspotify setup --sp-dc \"<new_value>\" --sp-key \"<new_value>\""
        )
    except (ValueError, TypeError) as e:
        if require_device:
            _die(
                "No active Spotify device found.\n"
                "  Open Spotify on any device (PC, phone, web) and start playing\n"
                "  something first, then try again."
            )
        raise

def _get_status(login):
    """Create a PlayerStatus instance."""
    try:
        from spotapi import PlayerStatus
        from spotapi.exceptions import LoginError
    except ImportError as e:
        _die(f"spotapi is not installed (or failed to import: {e}).")
    try:
        status = PlayerStatus(login)
        _active_ws_objects.append(status)
        return status
    except LoginError as e:
        _die(
            "Spotify session expired or invalid (Status 401).\n"
            "  Your sp_dc / sp_key cookies are no longer valid.\n"
            "  1. Open https://open.spotify.com in your browser and log in.\n"
            "  2. Press F12 → Application → Cookies → copy sp_dc and sp_key.\n"
            "  3. Run: clawspotify setup --sp-dc \"<new_value>\" --sp-key \"<new_value>\""
        )

# ── Commands ──────────────────────────────────────────────────────────────────
def cmd_status(args):
    login = _load_session(args.id)
    status = _get_status(login)
    try:
        state = status.state
    except Exception as e:
        _die(f"Could not get player state: {e}")
    track = state.track
    if track is None or track.metadata is None:
        print("Nothing is currently playing.")
        return
    meta = track.metadata
    title       = meta.title or "Unknown Title"
    artist_uri  = meta.artist_uri or ""
    album       = meta.album_title or "Unknown Album"
    ctx_meta = state.context_metadata
    artist_name = "Unknown Artist"
    if ctx_meta and ctx_meta.context_owner:
        artist_name = ctx_meta.context_owner
    elif artist_uri:
        artist_name = artist_uri.split(":")[-1] if ":" in artist_uri else artist_uri
    pos_str = _ms_to_mmss(state.position_as_of_timestamp)
    dur_str = _ms_to_mmss(state.duration)
    if state.is_paused:
        play_state = "Paused"
    elif state.is_playing:
        play_state = "Playing"
    else:
        play_state = "Stopped"
    opts = state.options
    shuffle_on = opts.shuffling_context if opts else False
    repeat_on  = (opts.repeating_track or opts.repeating_context) if opts else False
    shuffle_str = "on" if shuffle_on else "off"
    repeat_str  = "on" if repeat_on else "off"
    try:
        devices = status.device_ids
        active_id = devices.active_device_id
        if active_id and active_id in devices.devices:
            dev = devices.devices[active_id]
            device_name = dev.name
            device_type = dev.device_type
            volume_pct  = _vol_16bit_to_pct(dev.volume)
        else:
            device_name = "Unknown"
            device_type = ""
            volume_pct  = 0
    except Exception:
        device_name = "Unknown"
        device_type = ""
        volume_pct  = 0
    print()
    print(f"  Status  : {play_state}")
    print(f"  Title   : {title}")
    print(f"  Album   : {album}")
    print(f"  Position: {pos_str} / {dur_str}")
    print(f"  Shuffle : {shuffle_str}   Repeat: {repeat_str}")
    print(f"  Device  : {device_name}" + (f" ({device_type})" if device_type else ""))
    print(f"  Volume  : {volume_pct}%")
    print()

def cmd_search(args):
    query = args.query
    login = _load_session(args.id)
    try:
        from spotapi.public import Public
    except ImportError as e:
        _die(f"spotapi is not installed (or failed to import: {e}).")
    print(f"Search results for: {query}\n")
    try:
        results = Public.song_search(query)
        first_chunk = next(results, None)
        results.close()
        if not first_chunk:
            print("No results found.")
            return
        items = list(first_chunk)
        if not items:
            print("No results found.")
            return
        for idx, item in enumerate(items[:5]):
            data = item["item"]["data"]
            title = data.get("name", "?")
            artists = ", ".join(a["name"] for a in data.get("artists", []))
            album = data.get("album", {}).get("name", "?")
            uri = data.get("uri", "?")
            print(f"{idx+1}. {title} — {artists} [{album}]\n   URI: {uri}")
    except Exception as e:
        _die(f"Could not search: {e}")

def cmd_play(args):
    query = args.query
    index = getattr(args, "index", 0) or 0
    login  = _load_session(args.id)
    player = _get_player(login)
    print(f'  Searching for "{query}"...')
    try:
        uri = player.play_search(query, index=index)
        print(f"  Playing: {uri}")
    except ValueError as e:
        _die(str(e))
    except Exception as e:
        _die(f"Could not play track: {e}")

def cmd_search_playlist(args):
    query = args.query
    login = _load_session(args.id)
    try:
        from spotapi.public import Public
    except ImportError as e:
        _die(f"spotapi is not installed (or failed to import: {e}).")
    print(f"Playlist search results for: {query}\n")
    try:
        results = Public.playlist_search(query)
        first_chunk = next(results, None)
        results.close()
        if not first_chunk:
            print("No results found.")
            return
        items = list(first_chunk)
        if not items:
            print("No results found.")
            return
        for idx, item in enumerate(items[:5]):
            data = item["data"]
            title = data.get("name", "?")
            owner = data.get("ownerV2", {}).get("data", {}).get("name", "?")
            uri = data.get("uri", "?")
            print(f"{idx+1}. {title} — by {owner}\n   URI: {uri}")
    except Exception as e:
        _die(f"Could not search playlist: {e}")

def cmd_play_playlist(args):
    query = args.query
    index = getattr(args, "index", 0) or 0
    login  = _load_session(args.id)
    player = _get_player(login)
    print(f'  Searching for playlist "{query}"...')
    try:
        uri = player.play_playlist_search(query, index=index)
        print(f"  Playing Playlist: {uri}")
    except ValueError as e:
        _die(str(e))
    except Exception as e:
        _die(f"Could not play playlist: {e}")

def cmd_pause(args):
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.pause()
        print("  Paused.")
    except Exception as e:
        _die(f"Could not pause: {e}")

def cmd_resume(args):
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.resume()
        print("  Resumed.")
    except Exception as e:
        _die(f"Could not resume: {e}")

def cmd_skip(args):
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.skip_next()
        print("  Skipped to next track.")
    except Exception as e:
        _die(f"Could not skip: {e}")

def cmd_prev(args):
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.skip_prev()
        print("  Went to previous track.")
    except Exception as e:
        _die(f"Could not go to previous track: {e}")

def cmd_restart(args):
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.restart_song()
        print("  Restarted track from beginning.")
    except Exception as e:
        _die(f"Could not restart track: {e}")

def cmd_queue(args):
    query = args.query
    login  = _load_session(args.id)
    player = _get_player(login)
    if query.startswith("spotify:track:"):
        uri = query
        try:
            player.add_to_queue(uri)
            print(f"  Added to queue: {uri}")
        except Exception as e:
            _die(f"Could not add to queue: {e}")
    else:
        from spotapi.public import Public
        print(f'  Searching for "{query}"...')
        try:
            results = Public.song_search(query)
            first_chunk = next(results, None)
            results.close()
            if not first_chunk:
                _die(f"No search results found for: {query!r}")
            items = list(first_chunk)
            if not items:
                _die(f"No search results found for: {query!r}")
            track_uri: str = items[0]["item"]["data"]["uri"]
            player.add_to_queue(track_uri)
            try:
                name = items[0]["item"]["data"]["name"]
            except (KeyError, TypeError):
                name = track_uri
            print(f"  Added to queue: {name}")
        except Exception as e:
            _die(f"Could not add to queue: {e}")

def cmd_volume(args):
    vol_pct = args.level
    if not (0 <= vol_pct <= 100):
        _die("Volume must be between 0 and 100.")
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.set_volume(vol_pct / 100.0)
        print(f"  Volume set to {vol_pct}%.")
    except Exception as e:
        _die(f"Could not set volume: {e}")

def cmd_shuffle(args):
    state_str = args.state.lower()
    if state_str not in ("on", "off"):
        _die("Shuffle state must be 'on' or 'off'.")
    value  = state_str == "on"
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.set_shuffle(value)
        label = "enabled" if value else "disabled"
        print(f"  Shuffle {label}.")
    except Exception as e:
        _die(f"Could not set shuffle: {e}")

def cmd_repeat(args):
    state_str = args.state.lower()
    if state_str not in ("on", "off"):
        _die("Repeat state must be 'on' or 'off'.")
    value  = state_str == "on"
    login  = _load_session(args.id)
    player = _get_player(login)
    try:
        player.repeat_track(value)
        label = "enabled" if value else "disabled"
        print(f"  Repeat {label}.")
    except Exception as e:
        _die(f"Could not set repeat: {e}")

def cmd_setup(args):
    sp_dc  = args.sp_dc
    sp_key = args.sp_key
    ident  = args.id
    if not sp_dc or not sp_key:
        _die("Both --sp-dc and --sp-key are required.")
    try:
        from spotapi.session import SpotifySession
    except ImportError as e:
        _die(
            f"spotapi is not installed (or failed to import: {e}).\n"
            "  Install it with:  pip install spotapi\n"
            "  or from source:   pip install -e ./SpotAPI"
        )
    try:
        SpotifySession.setup(sp_dc, sp_key, identifier=ident)
        print(f"  Session '{ident}' saved to ~/.config/spotapi/session.json")
        print(f"  You can now use: spotify-ctl status --id \"{ident}\"")
        if ident == "default":
            print("  This is the default account - no --id needed.")
    except Exception as e:
        _die(f"Could not save session: {e}")

# ── Parser ────────────────────────────────────────────────────────────────────
def _add_id(p: argparse.ArgumentParser) -> None:
    """Add --id flag to a subparser."""
    p.add_argument(
        "--id",
        metavar="IDENTIFIER",
        default="default",
        dest="id",
        help='Session identifier (default: "default"). Use for multi-account.',
    )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clawspotify",
        description="Control Spotify playback from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawspotify status
  clawspotify status --id my_account
  clawspotify search "Bohemian Rhapsody" --id my_account
  clawspotify play "Bohemian Rhapsody"
  clawspotify play "Bohemian Rhapsody" --index 1
  clawspotify pause
  clawspotify resume
  clawspotify skip
  clawspotify prev
  clawspotify restart
  clawspotify queue "Stairway to Heaven"
  clawspotify queue "spotify:track:5CQ30WqJwcep0pYcV4AMNc"
  clawspotify volume 75
  clawspotify shuffle on
  clawspotify repeat off
  clawspotify setup --sp-dc "AQC..." --sp-key "07c9..."
  clawspotify setup --sp-dc "AQC..." --sp-key "07c9..." --id work
""",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True
    # status
    p_status = sub.add_parser("status", help="Show now playing info")
    _add_id(p_status)
    # search
    p_search = sub.add_parser("search", help='Search for tracks (shows top 5 results, does not play)')
    p_search.add_argument("query", help="Search query")
    _add_id(p_search)
    # play
    p_play = sub.add_parser("play", help='Search and play a track (e.g. play "Song Name")')
    p_play.add_argument("query", help="Search query")
    p_play.add_argument(
        "--index", "-i",
        type=int,
        default=0,
        metavar="N",
        help="Pick the Nth search result (0-indexed, default: 0)",
    )
    _add_id(p_play)
    # search-playlist
    p_search_pl = sub.add_parser("search-playlist", help='Search for playlists (shows top 5 results, does not play)')
    p_search_pl.add_argument("query", help="Search query")
    _add_id(p_search_pl)
    # play-playlist
    p_play_pl = sub.add_parser("play-playlist", help='Search and play a playlist (e.g. play-playlist "Lofi Girl")')
    p_play_pl.add_argument("query", help="Search query")
    p_play_pl.add_argument(
        "--index", "-i",
        type=int,
        default=0,
        metavar="N",
        help="Pick the Nth search result (0-indexed, default: 0)",
    )
    _add_id(p_play_pl)
    # pause
    p_pause = sub.add_parser("pause", help="Pause playback")
    _add_id(p_pause)
    # resume
    p_resume = sub.add_parser("resume", help="Resume playback")
    _add_id(p_resume)
    # skip
    p_skip = sub.add_parser("skip", help="Skip to next track")
    _add_id(p_skip)
    # prev
    p_prev = sub.add_parser("prev", help="Go to previous track")
    _add_id(p_prev)
    # restart
    p_restart = sub.add_parser("restart", help="Restart current track from beginning")
    _add_id(p_restart)
    # queue
    p_queue = sub.add_parser("queue", help='Add a track to queue (search query or spotify:track: URI)')
    p_queue.add_argument("query", help="Search query or spotify:track: URI")
    _add_id(p_queue)
    # volume
    p_vol = sub.add_parser("volume", help="Set volume (0-100)")
    p_vol.add_argument("level", type=int, metavar="<0-100>", help="Volume level")
    _add_id(p_vol)
    # shuffle
    p_shuf = sub.add_parser("shuffle", help="Toggle shuffle (on|off)")
    p_shuf.add_argument("state", choices=["on", "off"], metavar="<on|off>")
    _add_id(p_shuf)
    # repeat
    p_rep = sub.add_parser("repeat", help="Toggle repeat (on|off)")
    p_rep.add_argument("state", choices=["on", "off"], metavar="<on|off>")
    _add_id(p_rep)
    # setup
    p_setup = sub.add_parser("setup", help="Save Spotify session credentials (first-time setup)")
    p_setup.add_argument("--sp-dc",  required=True, metavar="VALUE", help="sp_dc cookie value from browser")
    p_setup.add_argument("--sp-key", required=True, metavar="VALUE", help="sp_key cookie value from browser")
    _add_id(p_setup)
    return parser

def main():
    parser = build_parser()
    args   = parser.parse_args()
    _COMMANDS = {
        "status":  cmd_status,
        "search":  cmd_search,
        "play":    cmd_play,
        "search-playlist": cmd_search_playlist,
        "play-playlist":   cmd_play_playlist,
        "pause":   cmd_pause,
        "resume":  cmd_resume,
        "skip":    cmd_skip,
        "prev":    cmd_prev,
        "restart": cmd_restart,
        "queue":   cmd_queue,
        "volume":  cmd_volume,
        "shuffle": cmd_shuffle,
        "repeat":  cmd_repeat,
        "setup":   cmd_setup,
    }
    handler = _COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    handler(args)
    # Clean up WebSocket connections so the process can exit
    for obj in _active_ws_objects:
        try:
            obj.close()
        except Exception:
            pass
if __name__ == "__main__":
    main()
