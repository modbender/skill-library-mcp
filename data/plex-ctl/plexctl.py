#!/usr/bin/env python3
"""
plexctl — Standalone Plex Media Server CLI

Control your Plex server and clients directly via the Plex API.
No Apple TV, no vision, no automation — just fast, simple Plex control.

Usage:
    plexctl setup                           # First-time setup (URL, token, client)
    plexctl play "Movie Title"              # Play a movie
    plexctl play "Show Name" -s 2 -e 6      # Play specific episode
    plexctl search "query"                  # Search across all libraries
    plexctl now-playing                     # What's currently playing
    plexctl pause                           # Pause playback
    plexctl resume                          # Resume playback
    plexctl stop                            # Stop playback
    plexctl next                            # Next track/episode
    plexctl prev                            # Previous track/episode
    plexctl clients                         # List available clients
    plexctl libraries                       # List all libraries
    plexctl recent                          # Recently added content
    plexctl on-deck                         # Continue watching
    plexctl info "Title"                    # Detailed info about a title

Config: ~/.plexctl/config.json
"""

import argparse
import json
import os
import sys
from typing import Optional


CONFIG_PATH = os.path.expanduser("~/.plexctl/config.json")


# ---------------------------------------------------------------------------
# Config Management
# ---------------------------------------------------------------------------

def load_config():
    """Load config from ~/.plexctl/config.json"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(cfg):
    """Save config to ~/.plexctl/config.json"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"✓ Config saved to {CONFIG_PATH}")


# ---------------------------------------------------------------------------
# Plex Connection
# ---------------------------------------------------------------------------

def connect_plex():
    """Connect to Plex server using config credentials."""
    try:
        from plexapi.server import PlexServer
    except ImportError:
        print("Error: plexapi not installed")
        print("Install with: pip install plexapi")
        sys.exit(1)

    cfg = load_config()
    url = cfg.get("plex_url")
    token = cfg.get("plex_token")

    if not url or not token:
        print("Error: Plex not configured")
        print("Run: plexctl setup")
        sys.exit(1)

    try:
        return PlexServer(url, token)
    except Exception as e:
        print(f"Error connecting to Plex server: {e}")
        print(f"URL: {url}")
        print("Check your plex_url and plex_token in config")
        sys.exit(1)


def get_client(plex, client_name: Optional[str] = None):
    """Get a Plex client. Tries local GDM first, then cloud resources."""
    cfg = load_config()
    if client_name is None:
        client_name = cfg.get("default_client")
    
    if not client_name:
        print("Error: No client specified and no default_client in config")
        print("Run: plexctl setup")
        sys.exit(1)

    # Try local GDM discovery first (fastest)
    try:
        return plex.client(client_name)
    except Exception:
        pass

    # Fallback: cloud discovery via MyPlex account
    try:
        account = plex.myPlexAccount()
        for res in account.resources():
            if "player" in res.provides and res.name == client_name:
                return res.connect()
    except Exception:
        pass

    # Show what's available
    print(f"Error: Client '{client_name}' not found")
    print("\nAvailable clients:")
    
    # Local clients
    local_clients = plex.clients()
    if local_clients:
        print("  Local:")
        for c in local_clients:
            print(f"    • {c.title} ({c.product})")
    
    # Cloud clients
    try:
        account = plex.myPlexAccount()
        cloud_players = [r for r in account.resources() if "player" in r.provides]
        if cloud_players:
            print("  Cloud:")
            for r in cloud_players:
                print(f"    • {r.name}")
    except Exception:
        pass
    
    print("\nMake sure the Plex app is open on your client device.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_setup():
    """Interactive first-time setup."""
    print("=== Plex Setup ===\n")
    
    # Get Plex server URL
    default_url = "http://192.168.86.86:32400"
    url = input(f"Plex server URL [{default_url}]: ").strip() or default_url
    
    # Get Plex token
    print("\nHow to get your Plex token:")
    print("  1. Go to Settings → Account → Authorized Devices")
    print("  2. Or copy from browser URL: app.plex.tv/desktop/#!/settings/account")
    print("  3. Look for X-Plex-Token in the URL or page source")
    token = input("\nPlex token: ").strip()
    
    if not token:
        print("Error: Token required")
        sys.exit(1)
    
    # Test connection
    print("\nConnecting to Plex...")
    try:
        from plexapi.server import PlexServer
        plex = PlexServer(url, token)
        print(f"✓ Connected to: {plex.friendlyName}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)
    
    # Discover clients
    print("\nDiscovering clients...")
    clients = plex.clients()
    
    if not clients:
        print("Warning: No local clients found (make sure Plex app is open)")
        default_client = input("Default client name: ").strip()
    else:
        print("\nAvailable clients:")
        for i, c in enumerate(clients):
            print(f"  [{i}] {c.title} ({c.product} on {c.platform})")
        
        if len(clients) == 1:
            idx = 0
        else:
            idx = int(input(f"\nSelect default client [0-{len(clients)-1}]: "))
        
        default_client = clients[idx].title
    
    # Save config
    cfg = {
        "plex_url": url,
        "plex_token": token,
        "default_client": default_client
    }
    save_config(cfg)
    
    print(f"\n✓ Setup complete!")
    print(f"  Default client: {default_client}")
    print(f"\nTry: plexctl search \"fight club\"")


def cmd_play(query: str, season: Optional[int] = None, episode: Optional[int] = None, 
             client_name: Optional[str] = None):
    """Play content via Plex API with fuzzy search."""
    plex = connect_plex()
    client = get_client(plex, client_name)
    
    # Search across all libraries
    results = plex.search(query)
    if not results:
        print(f"No results found for: {query}")
        return False
    
    # Prefer exact matches, fallback to first result
    item = results[0]
    for r in results:
        if r.title.lower() == query.lower():
            item = r
            break
    
    print(f"Found: {item.title} ({item.type})", end="")
    if hasattr(item, 'year') and item.year:
        print(f" [{item.year}]", end="")
    print()
    
    # Navigate to specific episode if requested
    if season is not None and hasattr(item, 'season'):
        try:
            ep = item.season(season).episode(episode or 1)
            print(f"  → S{season:02d}E{(episode or 1):02d}: {ep.title}")
            item = ep
        except Exception as e:
            print(f"Error: Could not find S{season}E{episode or 1}: {e}")
            return False
    
    # Play it
    try:
        client.playMedia(item)
        print(f"✓ Playing on {client.title}")
        return True
    except Exception as e:
        print(f"Error: Playback failed: {e}")
        return False


def cmd_search(query: str):
    """Search Plex library and display results."""
    plex = connect_plex()
    results = plex.search(query)
    
    if not results:
        print(f"No results for: {query}")
        return
    
    print(f"Results for '{query}':\n")
    for r in results[:20]:
        icon = {
            "movie": "🎬",
            "show": "📺",
            "episode": "  📺",
            "artist": "🎵",
            "album": "💿",
            "track": "  🎵"
        }.get(r.type, "  ")
        
        extra = ""
        if r.type == "movie" and hasattr(r, 'year') and r.year:
            extra = f" ({r.year})"
        elif r.type == "show" and hasattr(r, 'childCount'):
            extra = f" ({r.childCount} seasons)"
        elif r.type == "episode":
            extra = f" — S{r.parentIndex:02d}E{r.index:02d}"
        elif r.type == "album" and hasattr(r, 'year') and r.year:
            extra = f" ({r.year})"
        
        print(f"{icon} {r.title}{extra}")


def cmd_now_playing():
    """Show what's currently playing on all clients."""
    plex = connect_plex()
    clients = plex.clients()
    
    if not clients:
        print("No active clients found")
        return
    
    print("Currently playing:\n")
    for client in clients:
        try:
            timeline = client.timeline
            if timeline and timeline.state != "stopped":
                media = timeline
                pos_min = int(media.time / 60000) if media.time else 0
                dur_min = int(media.duration / 60000) if media.duration else 0
                print(f"🔊 {client.title}")
                print(f"   {media.title}")
                if hasattr(media, 'grandparentTitle') and media.grandparentTitle:
                    print(f"   {media.grandparentTitle} — S{media.parentIndex:02d}E{media.index:02d}")
                print(f"   {media.state.upper()} [{pos_min}:{pos_min%60:02d} / {dur_min}:{dur_min%60:02d}]")
            else:
                print(f"⏸️  {client.title} — idle")
        except Exception as e:
            print(f"⚠️  {client.title} — {e}")
        print()


def cmd_pause(client_name: Optional[str] = None):
    """Pause current playback."""
    plex = connect_plex()
    client = get_client(plex, client_name)
    
    try:
        client.pause()
        print(f"⏸️  Paused on {client.title}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_resume(client_name: Optional[str] = None):
    """Resume playback."""
    plex = connect_plex()
    client = get_client(plex, client_name)
    
    try:
        client.play()
        print(f"▶️  Resumed on {client.title}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_stop(client_name: Optional[str] = None):
    """Stop playback."""
    plex = connect_plex()
    client = get_client(plex, client_name)
    
    try:
        client.stop()
        print(f"⏹️  Stopped on {client.title}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_next(client_name: Optional[str] = None):
    """Skip to next track/episode."""
    plex = connect_plex()
    client = get_client(plex, client_name)
    
    try:
        client.skipNext()
        print(f"⏭️  Next on {client.title}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_prev(client_name: Optional[str] = None):
    """Skip to previous track/episode."""
    plex = connect_plex()
    client = get_client(plex, client_name)
    
    try:
        client.skipPrevious()
        print(f"⏮️  Previous on {client.title}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_clients():
    """List available Plex clients."""
    plex = connect_plex()
    clients = plex.clients()
    
    print("Available clients:\n")
    if clients:
        print("Local (GDM):")
        for c in clients:
            print(f"  • {c.title}")
            print(f"    {c.product} on {c.platform}")
            print(f"    {c.address}:{c.port}")
            print()
    else:
        print("  (none)")
    
    # Also check cloud
    try:
        account = plex.myPlexAccount()
        cloud_players = [r for r in account.resources() if "player" in r.provides]
        if cloud_players:
            print("\nCloud (MyPlex):")
            for r in cloud_players:
                print(f"  • {r.name}")
                print(f"    {r.product}")
                print()
    except Exception:
        pass


def cmd_libraries():
    """List all Plex libraries with item counts."""
    plex = connect_plex()
    
    print("Libraries:\n")
    for section in plex.library.sections():
        icon = {
            "movie": "🎬",
            "show": "📺",
            "artist": "🎵"
        }.get(section.type, "📁")
        
        print(f"{icon} {section.title}")
        print(f"   {section.type} — {section.totalSize} items")
        print()


def cmd_recent(limit: int = 10):
    """Show recently added content."""
    plex = connect_plex()
    
    print(f"Recently added (last {limit}):\n")
    recent = plex.library.recentlyAdded()[:limit]
    
    for item in recent:
        icon = {
            "movie": "🎬",
            "show": "📺",
            "episode": "  📺",
            "album": "💿",
            "track": "  🎵"
        }.get(item.type, "  ")
        
        title = item.title
        extra = ""
        
        if item.type == "movie" and hasattr(item, 'year') and item.year:
            extra = f" ({item.year})"
        elif item.type == "episode":
            title = f"{item.grandparentTitle} — S{item.parentIndex:02d}E{item.index:02d}: {item.title}"
        elif item.type == "show" and hasattr(item, 'year') and item.year:
            extra = f" ({item.year})"
        
        print(f"{icon} {title}{extra}")


def cmd_on_deck():
    """Show on-deck (continue watching) items."""
    plex = connect_plex()
    
    print("On Deck (continue watching):\n")
    on_deck = plex.library.onDeck()
    
    if not on_deck:
        print("  (nothing on deck)")
        return
    
    for item in on_deck:
        icon = {
            "movie": "🎬",
            "episode": "📺"
        }.get(item.type, "  ")
        
        title = item.title
        if item.type == "episode":
            title = f"{item.grandparentTitle} — S{item.parentIndex:02d}E{item.index:02d}: {item.title}"
        
        # Show progress if available
        if hasattr(item, 'viewOffset') and item.viewOffset:
            progress = int((item.viewOffset / item.duration) * 100) if item.duration else 0
            print(f"{icon} {title} [{progress}%]")
        else:
            print(f"{icon} {title}")


def cmd_info(query: str):
    """Show detailed info about a specific title."""
    plex = connect_plex()
    results = plex.search(query)
    
    if not results:
        print(f"No results found for: {query}")
        return
    
    # Prefer exact matches
    item = results[0]
    for r in results:
        if r.title.lower() == query.lower():
            item = r
            break
    
    print(f"\n{item.title}\n{'=' * len(item.title)}\n")
    
    # Type-specific info
    if item.type == "movie":
        if hasattr(item, 'year') and item.year:
            print(f"Year: {item.year}")
        if hasattr(item, 'rating') and item.rating:
            print(f"Rating: {item.rating}/10")
        if hasattr(item, 'contentRating') and item.contentRating:
            print(f"Content Rating: {item.contentRating}")
        if hasattr(item, 'duration') and item.duration:
            minutes = int(item.duration / 60000)
            print(f"Duration: {minutes} min")
        if hasattr(item, 'genres'):
            genres = [g.tag for g in item.genres]
            print(f"Genres: {', '.join(genres)}")
        if hasattr(item, 'directors'):
            directors = [d.tag for d in item.directors]
            print(f"Directors: {', '.join(directors)}")
        if hasattr(item, 'roles'):
            actors = [a.tag for a in item.roles[:5]]
            print(f"Cast: {', '.join(actors)}")
    
    elif item.type == "show":
        if hasattr(item, 'year') and item.year:
            print(f"Year: {item.year}")
        if hasattr(item, 'rating') and item.rating:
            print(f"Rating: {item.rating}/10")
        if hasattr(item, 'contentRating') and item.contentRating:
            print(f"Content Rating: {item.contentRating}")
        if hasattr(item, 'childCount'):
            print(f"Seasons: {item.childCount}")
        if hasattr(item, 'leafCount'):
            print(f"Episodes: {item.leafCount}")
        if hasattr(item, 'genres'):
            genres = [g.tag for g in item.genres]
            print(f"Genres: {', '.join(genres)}")
    
    elif item.type == "episode":
        print(f"Show: {item.grandparentTitle}")
        print(f"Season: {item.parentIndex}")
        print(f"Episode: {item.index}")
        if hasattr(item, 'rating') and item.rating:
            print(f"Rating: {item.rating}/10")
        if hasattr(item, 'duration') and item.duration:
            minutes = int(item.duration / 60000)
            print(f"Duration: {minutes} min")
    
    # Summary (all types)
    if hasattr(item, 'summary') and item.summary:
        print(f"\nSummary:\n{item.summary}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="plexctl — Standalone Plex Media Server CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  plexctl setup
  plexctl play "Fight Club"
  plexctl play "The Office" -s 3 -e 10
  plexctl search "matrix"
  plexctl now-playing
  plexctl pause
  plexctl resume
  plexctl clients
  plexctl libraries
  plexctl recent
  plexctl on-deck
  plexctl info "Inception"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # setup
    subparsers.add_parser("setup", help="First-time setup")
    
    # play
    play_parser = subparsers.add_parser("play", help="Play content")
    play_parser.add_argument("query", help="Title to search for")
    play_parser.add_argument("-s", "--season", type=int, help="Season number (for TV shows)")
    play_parser.add_argument("-e", "--episode", type=int, help="Episode number (for TV shows)")
    play_parser.add_argument("-c", "--client", help="Client name (overrides default)")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search library")
    search_parser.add_argument("query", help="Search query")
    
    # now-playing
    subparsers.add_parser("now-playing", help="Show what's currently playing")
    
    # playback controls
    pause_parser = subparsers.add_parser("pause", help="Pause playback")
    pause_parser.add_argument("-c", "--client", help="Client name")
    
    resume_parser = subparsers.add_parser("resume", help="Resume playback")
    resume_parser.add_argument("-c", "--client", help="Client name")
    
    stop_parser = subparsers.add_parser("stop", help="Stop playback")
    stop_parser.add_argument("-c", "--client", help="Client name")
    
    next_parser = subparsers.add_parser("next", help="Next track/episode")
    next_parser.add_argument("-c", "--client", help="Client name")
    
    prev_parser = subparsers.add_parser("prev", help="Previous track/episode")
    prev_parser.add_argument("-c", "--client", help="Client name")
    
    # discovery
    subparsers.add_parser("clients", help="List available clients")
    subparsers.add_parser("libraries", help="List all libraries")
    
    # content discovery
    recent_parser = subparsers.add_parser("recent", help="Recently added content")
    recent_parser.add_argument("-n", "--limit", type=int, default=10, help="Number of items")
    
    subparsers.add_parser("on-deck", help="Continue watching")
    
    # info
    info_parser = subparsers.add_parser("info", help="Detailed info about a title")
    info_parser.add_argument("query", help="Title to look up")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Route to command handlers
    if args.command == "setup":
        cmd_setup()
    elif args.command == "play":
        cmd_play(args.query, args.season, args.episode, args.client)
    elif args.command == "search":
        cmd_search(args.query)
    elif args.command == "now-playing":
        cmd_now_playing()
    elif args.command == "pause":
        cmd_pause(args.client)
    elif args.command == "resume":
        cmd_resume(args.client)
    elif args.command == "stop":
        cmd_stop(args.client)
    elif args.command == "next":
        cmd_next(args.client)
    elif args.command == "prev":
        cmd_prev(args.client)
    elif args.command == "clients":
        cmd_clients()
    elif args.command == "libraries":
        cmd_libraries()
    elif args.command == "recent":
        cmd_recent(args.limit)
    elif args.command == "on-deck":
        cmd_on_deck()
    elif args.command == "info":
        cmd_info(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
