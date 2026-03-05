#!/usr/bin/env python3
"""
Minecraft Server Status Checker

Queries a Minecraft server for basic status information:
- Online status
- Player count (current/max)
- Server motd/message
- Ping response time
- Version information

Uses Minecraft Server List Ping protocol (SLP).
"""

import socket
import struct
import json
import sys
import time

def encode_varint(num):
    """Encode an integer as a Minecraft varint."""
    if num < 0:
        num = (1 << 32) + num
    out = b""
    while num > 0x7F:
        out += bytes([(num & 0x7F) | 0x80])
        num >>= 7
    out += bytes([num])
    return out

def decode_varint(sock):
    """Decode a Minecraft varint from socket."""
    num = 0
    shift = 0
    while True:
        byte = sock.recv(1)
        if not byte:
            raise IOError("Connection closed")
        byte = byte[0]
        num |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return num

def send_handshake(sock, host, port):
    """Send handshake packet."""
    data = b""
    # Packet ID (handshake = 0x00)
    data += b"\x00"
    # Protocol version (use latest: 765 for 1.19.3+)
    data += encode_varint(765)
    # Server address
    host_bytes = host.encode('utf-8') if isinstance(host, str) else host
    data += encode_varint(len(host_bytes))
    data += host_bytes
    # Server port
    data += struct.pack(">H", port)
    # Next state (status = 1)
    data += b"\x01"

    # Length prefix
    length = encode_varint(len(data))
    sock.send(length + data)

def send_status_request(sock):
    """Send status request packet."""
    data = b"\x01\x00"  # Request (empty)
    length = encode_varint(len(data))
    sock.send(length + data)

def read_status_response(sock):
    """Read server status response."""
    # Packet length
    length = decode_varint(sock)
    # Packet ID should be 0x00
    packet_id = decode_varint(sock)

    # Response length
    response_len = decode_varint(sock)
    # Response data (JSON)
    response = b""
    while len(response) < response_len:
        response += sock.recv(response_len - len(response))

    return json.loads(response.decode('utf-8'))

def minecraft_status(host, port=25565, timeout=5):
    """Get Minecraft server status."""
    try:
        start_time = time.time()

        # Connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        # Handshake
        send_handshake(sock, host, port)
        send_status_request(sock)

        # Read response
        data = read_status_response(sock)

        sock.close()

        ping_ms = round((time.time() - start_time) * 1000, 1)

        # Parse response
        result = {
            'online': True,
            'host': host,
            'port': port,
            'ping': ping_ms,
        }

        # Version info
        if 'version' in data:
            result['version'] = data['version'].get('name', 'Unknown')
            result['protocol'] = data['version'].get('protocol', 'Unknown')

        # Player count
        if 'players' in data:
            players = data['players']
            result['players_online'] = players.get('online', 0)
            result['players_max'] = players.get('max', 0)
            if 'sample' in players and players['sample']:
                result['player_list'] = [p['name'] for p in players['sample']]

        # MOTD (message of the day)
        if 'description' in data:
            motd = data['description']
            if isinstance(motd, dict):
                motd = motd.get('text', '')
            result['motd'] = motd

        return result

    except socket.timeout:
        return {
            'online': False,
            'host': host,
            'port': port,
            'error': 'Connection timed out'
        }
    except ConnectionRefusedError:
        return {
            'online': False,
            'host': host,
            'port': port,
            'error': 'Connection refused'
        }
    except Exception as e:
        return {
            'online': False,
            'host': host,
            'port': port,
            'error': str(e)
        }

def format_status(status):
    """Format status for human-readable output."""
    if not status['online']:
        print(f"🔴 {status['host']}:{status['port']} - OFFLINE")
        print(f"   Error: {status.get('error', 'Unknown')}")
        return

    emoji = "🟢" if status['ping'] < 100 else "🟡" if status['ping'] < 200 else "🟠"
    print(f"{emoji} {status['host']}:{status['port']} - ONLINE ({status['ping']}ms)")
    print(f"   Version: {status.get('version', 'Unknown')}")
    print(f"   Players: {status.get('players_online', 0)}/{status.get('players_max', 0)}")

    if 'player_list' in status and status['player_list']:
        print(f"   Online: {', '.join(status['player_list'][:5])}" +
              (f" ... +{len(status['player_list'])-5} more" if len(status['player_list']) > 5 else ""))

    if 'motd' in status and status['motd']:
        motd = status['motd'].strip()
        if motd:
            print(f"   MOTD: {motd[:80]}{'...' if len(motd) > 80 else ''}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python minecraft-status.py <host[:port]> [timeout]")
        print("")
        print("Examples:")
        print("  python minecraft-status.py corejourney.org")
        print("  python minecraft-status.py corejourney.org:25565")
        print("  python minecraft-status.py 192.168.1.10:25566 10")
        sys.exit(1)

    # Parse host:port
    hostport = sys.argv[1]
    if ':' in hostport:
        host, port_str = hostport.rsplit(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            print(f"Invalid port: {port_str}")
            sys.exit(1)
    else:
        host = hostport
        port = 25565

    # Parse timeout
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    status = minecraft_status(host, port, timeout)
    format_status(status)

    # Return exit code 0 if online, 1 if offline
    sys.exit(0 if status['online'] else 1)

if __name__ == '__main__':
    main()