#!/usr/bin/env python3
"""
Fixed Music Server - Background server for music playback control
Portable version with configurable paths
"""

import os
import sys
import json
import socket
import threading
import time
from pathlib import Path
import pygame

# Configuration - All paths are configurable via environment variables
CONTROL_PORT = 12346
LOCK_FILE = Path(os.environ.get("MUSIC_LOCK_FILE", "/tmp/music_player.lock"))

# MUSIC_DIR can be set via environment variable, defaults to ./music in current directory
DEFAULT_MUSIC_DIR = Path.cwd() / "music"
MUSIC_DIR = Path(os.environ.get("MUSIC_DIR", str(DEFAULT_MUSIC_DIR)))

# Global state
current_song = None
is_playing = False
is_paused = False
position = 0
server_running = True
pygame_initialized = False

def save_lock_file():
    """Save server port to lock file"""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(CONTROL_PORT))
        os.chmod(LOCK_FILE, 0o666)  # Make it readable by all
    except Exception as e:
        print(f"Error saving lock file: {e}", file=sys.stderr)

def remove_lock_file():
    """Remove lock file"""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except:
        pass

def initialize_pygame():
    """Initialize pygame mixer"""
    global pygame_initialized
    if not pygame_initialized:
        pygame.mixer.init()
        pygame_initialized = True
    return pygame

def play_music(song_name):
    """Play a music file by name"""
    global current_song, is_playing, is_paused, position
    
    # Build full path
    song_path = MUSIC_DIR / song_name
    
    if not song_path.exists():
        # Try with .mp3 extension if not provided
        if not song_name.endswith('.mp3'):
            song_path = MUSIC_DIR / f"{song_name}.mp3"
    
    if not song_path.exists():
        print(f"File not found: {song_name} (looked in {MUSIC_DIR})", file=sys.stderr)
        return False
    
    print(f"Attempting to play: {song_path}", file=sys.stderr)
    
    try:
        pygame = initialize_pygame()
        pygame.mixer.music.load(str(song_path))
        pygame.mixer.music.play()
        current_song = song_name
        is_playing = True
        is_paused = False
        position = 0
        print(f"Now playing: {song_name}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error playing music: {e}", file=sys.stderr)
        return False

def pause_music():
    """Pause currently playing music"""
    global is_paused
    
    if pygame.mixer.music.get_busy() and not is_paused:
        pygame.mixer.music.pause()
        is_paused = True
        print("Music paused", file=sys.stderr)
        return True
    return False

def resume_music():
    """Resume paused music"""
    global is_paused
    
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
        print("Music resumed", file=sys.stderr)
        return True
    return False

def stop_music():
    """Stop currently playing music"""
    global current_song, is_playing, is_paused, position
    
    pygame.mixer.music.stop()
    current_song = None
    is_playing = False
    is_paused = False
    position = 0
    print("Music stopped", file=sys.stderr)
    return True

def get_status():
    """Get current playback status"""
    global position
    
    # Update position if playing
    if is_playing and not is_paused:
        position += 0.1  # Simple approximation
    
    status = {
        "server_running": server_running,
        "playback_status": "playing" if is_playing and not is_paused else 
                          "paused" if is_paused else 
                          "stopped",
        "current_song": current_song,
        "position": position,
        "volume": pygame.mixer.music.get_volume() if pygame.mixer.get_init() else 0
    }
    return status

def handle_client(client_socket):
    """Handle a client connection"""
    global server_running
    
    try:
        # Receive command
        data = client_socket.recv(1024).decode()
        if not data:
            return
        
        command = json.loads(data)
        cmd = command.get("command")
        
        response = {"status": "error", "error": "Unknown command"}
        
        if cmd == "play":
            song_name = command.get("song")
            if song_name:
                if play_music(song_name):
                    response = {"status": "ok", "message": f"Playing {song_name}"}
                else:
                    response = {"status": "error", "error": f"Failed to play {song_name}"}
            else:
                response = {"status": "error", "error": "No song specified"}
                
        elif cmd == "pause":
            if pause_music():
                response = {"status": "ok", "message": "Music paused"}
            else:
                response = {"status": "error", "error": "No music playing to pause"}
                
        elif cmd == "resume":
            if resume_music():
                response = {"status": "ok", "message": "Music resumed"}
            else:
                response = {"status": "error", "error": "No music paused to resume"}
                
        elif cmd == "stop":
            if stop_music():
                response = {"status": "ok", "message": "Music stopped - server will shut down"}
                # Set flag to shut down server after responding
                server_running = False
            else:
                response = {"status": "error", "error": "No music playing to stop"}
                
        elif cmd == "status":
            status = get_status()
            response = {"status": "ok", **status}
            
        elif cmd == "shutdown":
            response = {"status": "ok", "message": "Server shutting down"}
            server_running = False
            
        else:
            response = {"status": "error", "error": f"Unknown command: {cmd}"}
        
        # Send response
        client_socket.send(json.dumps(response).encode())
        
    except json.JSONDecodeError:
        response = {"status": "error", "error": "Invalid JSON"}
        client_socket.send(json.dumps(response).encode())
    except Exception as e:
        response = {"status": "error", "error": str(e)}
        client_socket.send(json.dumps(response).encode())
    finally:
        client_socket.close()

def main():
    """Main server function"""
    global server_running
    
    # Initialize pygame
    try:
        pygame.mixer.init()
        print("Pygame mixer initialized", file=sys.stderr)
    except Exception as e:
        print(f"Failed to initialize pygame: {e}", file=sys.stderr)
        return 1
    
    # Create socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('127.0.0.1', CONTROL_PORT))
        server_socket.listen(5)
        
        # Save lock file
        save_lock_file()
        print(f"Music server started on port {CONTROL_PORT}", file=sys.stderr)
        print(f"Music directory: {MUSIC_DIR}", file=sys.stderr)
        sys.stderr.flush()  # Ensure output is visible
        
        # Main server loop
        while server_running:
            try:
                # Set timeout to allow checking server_running flag
                server_socket.settimeout(1.0)
                client_socket, addr = server_socket.accept()
                print(f"Client connected: {addr}", file=sys.stderr)
                handle_client(client_socket)
            except socket.timeout:
                # Timeout is expected, just continue
                continue
            except Exception as e:
                if server_running:  # Only print error if server should still be running
                    print(f"Error accepting connection: {e}", file=sys.stderr)
        
        print("Server shutdown requested", file=sys.stderr)
        
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1
    finally:
        server_socket.close()
        remove_lock_file()
        print("Music server stopped", file=sys.stderr)
    
    return 0

if __name__ == "__main__":
    # Flush output immediately
    sys.stderr.flush()
    sys.exit(main())