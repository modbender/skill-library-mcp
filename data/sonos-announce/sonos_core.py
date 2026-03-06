#!/usr/bin/env python3
"""
Sonos Core - Shared module for Sonos announcement playback with state restoration.

This module handles the core logic of:
1. Discovering Sonos speakers and coordinators
2. Saving current playback state
3. Pausing if needed (handling Line-In specially)
4. Playing an audio file
5. Restoring previous playback state

Can be imported by other scripts or called directly.
"""

import soco
import time
import subprocess
import socket
import os
import urllib.parse
import platform


def get_local_ip():
    """Auto-detect the machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't actually connect, just gets the route
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


# HTTP server config - auto-detect IP, allow env override
HTTP_HOST = os.environ.get('SONOS_HTTP_HOST') or get_local_ip()
HTTP_PORT = int(os.environ.get('SONOS_HTTP_PORT', 8888))
PID_FILE = os.path.join(os.path.dirname(__file__), '.http_server.pid')


def can_seek_uri(uri):
    """Check if the URI supports seeking (local files, queues, track/playlist streams)."""
    if not uri:
        return False
    # Decode URI for checking (Sonos sends URL-encoded)
    uri_decoded = urllib.parse.unquote(uri)
    # These cannot be seeked
    if any(x in uri_decoded for x in ['x-rincon-mp3radio:', 'pandora:']):
        return False
    # Spotify/Tidal: only track and playlist can seek, radio/station cannot
    if 'spotify' in uri_decoded or 'tidal' in uri_decoded:
        return any(x in uri_decoded for x in ['track:', 'playlist:'])
    return True


def is_server_running(host=HTTP_HOST, port=HTTP_PORT):
    """Check if the HTTP server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def start_http_server(media_dir=None):
    """Start the HTTP server for streaming audio to Sonos."""
    if media_dir is None:
        media_dir = os.path.expanduser("~/.local/share/openclaw/media/outbound")
    
    # Always kill any stale server first, then start fresh
    print("Stopping any existing HTTP server...")
    stop_http_server()
    time.sleep(1)
    
    print(f"Starting HTTP server from {media_dir}...")
    if platform.system() == "Windows":
        # Start server and save PID to file
        os.system(f'start /b python -m http.server {HTTP_PORT} --directory "{media_dir}"')
        # On Windows, we can't easily get the PID of start /b, so just track by port
        # The stop_http_server will use port-based killing as fallback
    else:
        # Use nohup to ensure it persists and save PID
        os.system(f'nohup python3 -m http.server {HTTP_PORT} --directory "{media_dir}" > /tmp/sonos_http.log 2>&1 &')
        # Save PID for clean shutdown
        time.sleep(1)
        # Find the PID by port and save it
        try:
            pid = subprocess.check_output(f"lsof -ti:{HTTP_PORT}", shell=True).decode().strip()
            with open(PID_FILE, 'w') as f:
                f.write(pid)
        except:
            pass
    time.sleep(1)


def stop_http_server():
    """Stop the HTTP server gracefully using PID file, then fallback to port."""
    # Try PID file first (cleanest)
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = f.read().strip()
            if pid:
                os.kill(int(pid), 9)
                print(f"Stopped HTTP server (PID {pid})")
        except:
            pass
        try:
            os.remove(PID_FILE)
        except:
            pass
    
    # Fallback: kill by port
    if platform.system() == "Windows":
        # Use netstat to find and kill the process on the port
        try:
            result = subprocess.run(
                f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{HTTP_PORT} ^| findstr LISTENING\') do taskkill /f /pid %a',
                shell=True, capture_output=True, text=True
            )
        except:
            pass
    else:
        os.system(f"lsof -ti:{HTTP_PORT} | xargs kill -9 2>/dev/null")
        os.system(f"pkill -9 -f 'python3 -m http.server {HTTP_PORT}' 2>/dev/null")


def is_external_input(uri):
    """
    Check if URI is an external input (Line-In, TV, Bluetooth, etc.)
    These sources can't be paused/resumed - they must be restored after announcement.
    """
    if not uri:
        return False
    
    # External input patterns (should NOT be paused)
    external_patterns = [
        'x-rincon:RINCON_',           # Line-In (direct)
        'x-rincon-stream:RINCON_',    # Line-In (stream)
        'x-sonos-htastream:',         # TV/HDMI (Sonos Home Theater)
        'x-sonos-vanished:',          # Vanished device
        'x-rincon蓝牙:',               # Bluetooth (Chinese)
        'x-rincon-bt:',               # Bluetooth
        'x-sonos-aphone:',            # Phone/USB input
    ]
    
    return any(pattern in uri for pattern in external_patterns)


def get_audio_duration(file_path):
    """Get actual audio duration using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as e:
        print(f"Could not get duration: {e}")
    return None


def discover_coordinators():
    """Discover all Sonos group coordinators."""
    speakers = list(soco.discover())
    if not speakers:
        raise Exception("No Sonos speakers found")
    
    coordinators = []
    seen_uuids = set()
    for s in speakers:
        try:
            if hasattr(s, 'group') and s.group:
                coordinator = s.group.coordinator
                if coordinator and coordinator.uid not in seen_uuids:
                    seen_uuids.add(coordinator.uid)
                    coordinators.append(coordinator)
            else:
                if s.uid not in seen_uuids:
                    seen_uuids.add(s.uid)
                    coordinators.append(s)
        except Exception:
            if s.ip_address not in [sp.ip_address for sp in coordinators]:
                coordinators.append(s)
    
    return coordinators


def save_state(coordinators):
    """Save playback state for all coordinators."""
    states = {}
    for s in coordinators:
        try:
            t = s.get_current_transport_info()
            tr = s.get_current_track_info()
            
            uri = t.get('uri', tr.get('uri', ''))
            # Try both keys - soco uses 'current_transport_state'
            transport_state = t.get('current_transport_state') or t.get('transport_state', 'STOPPED')
            
            pos = tr.get('position', '0:00:00')
            if pos == 'NOT_IMPLEMENTED':
                pos = '0:00:00'
            
            queue_pos = tr.get('playlist_position', None)
            if queue_pos:
                try:
                    queue_pos = int(queue_pos) - 1
                except:
                    queue_pos = None
            
            is_external = is_external_input(uri)
            
            # Determine what to restore to
            was_playing = transport_state == 'PLAYING' and not is_external
            was_paused = transport_state == 'PAUSED' and not is_external
            was_no_content = transport_state == 'NO_CONTENT' or not uri
            
            states[s.ip_address] = {
                'uri': uri,
                'position': pos,
                'queue_position': queue_pos,
                'was_playing': was_playing,
                'was_paused': was_paused,
                'was_no_content': was_no_content,
                'is_external': is_external,
                'transport_state': transport_state,
                'speaker_name': s.player_name,
            }
        except Exception as e:
            print(f"  {s.player_name}: error saving state - {e}")
            states[s.ip_address] = {
                'uri': '', 'position': '0:00:00', 'queue_position': None,
                'was_playing': False, 'was_paused': False, 'was_no_content': True,
                'is_external': False, 'transport_state': 'NO_CONTENT',
                'speaker_name': s.player_name,
            }
    
    return states


def prepare_speakers(coordinators, states):
    """Pause speakers if needed (skip Line-In)."""
    for s in coordinators:
        state = states.get(s.ip_address, {})
        
        if state.get('is_external'):
            print(f"  {s.player_name}: External input - skipping pause")
            continue
        
        if state.get('was_playing'):
            try:
                s.pause()
                print(f"  {s.player_name}: was playing - paused")
            except Exception as e:
                print(f"  {s.player_name}: pause error - {e}")
        elif state.get('was_no_content'):
            print(f"  {s.player_name}: No Content - will stop after announcement")
        else:
            print(f"  {s.player_name}: was paused or stopped - skipping")


def play_announcement(coordinators, audio_url, title=None, artist=None, media_dir=None):
    """Play announcement on all coordinators."""
    for s in coordinators:
        try:
            # Try to extract metadata from file if not provided
            if not title or not artist:
                filename = os.path.basename(audio_url)
                file_path = os.path.join(media_dir or '', filename) if media_dir else filename
                # Try to read ID3 tags using ffprobe
                try:
                    import subprocess
                    result = subprocess.run(
                        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', file_path],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        import json
                        data = json.loads(result.stdout)
                        tags = data.get('format', {}).get('tags', {})
                        if not title:
                            title = tags.get('title', '')
                        if not artist:
                            artist = tags.get('artist', '')
                except Exception:
                    pass
            
            # Fallback to filename parsing if still no metadata
            if not title:
                filename = os.path.basename(audio_url)
                name_without_ext = os.path.splitext(filename)[0]
                title = name_without_ext.replace('-', ' ').title()
            
            if not artist:
                artist = 'Voice Studio'
            
            # Use force_radio=False so Sonos reads ID3 tags from the file
            # If file has no ID3 tags, pass title/artist as fallback
            s.play_uri(audio_url, title=title, artist=artist, force_radio=False)
            print(f"  {s.player_name}: playing '{title}' by {artist}")
        except Exception as e:
            print(f"  {s.player_name}: play error - {e}")


def restorePlayback(coordinators, states):
    """Restore playback state after announcement."""
    for s in coordinators:
        state = states.get(s.ip_address, {})
        
        if state.get('is_external'):
            try:
                print(f"  {s.player_name}: restoring external input")
                s.play_uri(state['uri'])
            except Exception as e:
                print(f"  {s.player_name}: Line-In restore error - {e}")
            continue
        
        # Handle NO_CONTENT - stop playback (wasn't playing anything)
        if state.get('was_no_content'):
            print(f"  {s.player_name}: was No Content - stopping (was not playing)")
            try:
                s.stop()
            except Exception as e:
                print(f"  {s.player_name}: stop error - {e}")
            continue
        
        # Handle PAUSED - restore to paused state
        if state.get('was_paused'):
            try:
                queue_pos = state.get('queue_position')
                uri = state.get('uri', '')
                
                if queue_pos is not None and queue_pos >= 0:
                    print(f"  {s.player_name}: restoring to paused at queue {queue_pos}")
                    s.play_from_queue(queue_pos)
                    time.sleep(0.5)
                    if can_seek_uri(uri):
                        s.seek(state['position'])
                        time.sleep(0.5)
                    s.pause()
                elif uri:
                    print(f"  {s.player_name}: restoring to paused")
                    s.play_uri(uri)
                    time.sleep(0.5)
                    if can_seek_uri(uri):
                        s.seek(state['position'])
                        time.sleep(0.5)
                    s.pause()
            except Exception as e:
                print(f"  {s.player_name}: pause restore error - {e}")
            continue
        
        if not state.get('was_playing'):
            print(f"  {s.player_name}: was stopped - staying stopped")
            continue
        
        # Restore to playing
        try:
            queue_pos = state.get('queue_position')
            uri = state.get('uri', '')
            # Check if URI supports seeking
            can_seek = can_seek_uri(uri)
            
            if queue_pos is not None and queue_pos >= 0:
                print(f"  {s.player_name}: resuming from queue {queue_pos}")
                s.play_from_queue(queue_pos)
                time.sleep(0.5)
                if can_seek:
                    s.seek(state['position'])
                    time.sleep(0.5)
                s.play()
            elif uri:
                print(f"  {s.player_name}: resuming at {state['position']} (can_seek={can_seek})")
                s.play_uri(uri)
                if can_seek:
                    time.sleep(0.5)
                    s.seek(state['position'])
                    time.sleep(0.5)
                s.play()
            else:
                s.play()
        except Exception as e:
            print(f"  {s.player_name}: restore error - {e}")


def announce(audio_file_path, wait_for_audio=True, media_dir=None, title=None, artist=None):
    """
    Core function: Play audio on Sonos and restore previous state.
    
    Args:
        audio_file_path: Path to the audio file to play
        media_dir: Directory to serve from HTTP server (default: ~/.local/share/openclaw/media/outbound)
        wait_for_audio: If True, calculate duration and wait. If False, just wait a fixed time.
        title: Optional title to display on Sonos
        artist: Optional artist to display on Sonos
    
    Returns:
        dict: Summary of what happened
    """
    print(f"=== Sonos Announcement ===")
    print(f"Audio: {audio_file_path}")
    
    # Ensure HTTP server is running
    start_http_server(media_dir)
    
    # Get audio duration - use full path for ffprobe
    full_path = os.path.join(media_dir, audio_file_path) if media_dir else audio_file_path
    if wait_for_audio:
        duration = get_audio_duration(full_path)
        if duration:
            wait_time = max(duration + 3, 5)
            print(f"Duration: {duration:.1f}s, waiting {wait_time:.1f}s")
        else:
            wait_time = 10
            print(f"Could not determine duration, waiting {wait_time}s")
    else:
        wait_time = 5
        print(f"Waiting fixed {wait_time}s")
    
    # Discover and save state
    print("Discovering speakers...")
    coordinators = discover_coordinators()
    print(f"Found {len(coordinators)} coordinator(s)")
    
    print("Saving state...")
    states = save_state(coordinators)
    for ip, state in states.items():
        ext = " (External)" if state.get('is_external') else ""
        print(f"  {state['speaker_name']}: {state['transport_state']}{ext}")
    
    # Prepare (pause if needed)
    print("Preparing speakers...")
    prepare_speakers(coordinators, states)
    time.sleep(0.5)
    
    # Play
    audio_filename = os.path.basename(audio_file_path)
    audio_url = f"http://{HTTP_HOST}:{HTTP_PORT}/{audio_filename}"
    print(f"Playing: {audio_url}")
    play_announcement(coordinators, audio_url, title=title, artist=artist, media_dir=media_dir)
    
    # Wait for announcement
    print(f"Waiting {wait_time:.1f}s...")
    time.sleep(wait_time)
    
    # Restore
    print("Restoring playback...")
    restorePlayback(coordinators, states)
    
    print("=== Done ===")
    return {
        'coordinators': len(coordinators),
        'states': states,
    }


# CLI entry point
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sonos_core.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    announce(audio_file)
