#!/usr/bin/env python3
"""
Docker-OSX Skill - Run macOS in Docker for iOS building
"""

import subprocess
import os
import sys
import json

CONTAINER_NAME = "macos-vm"
IMAGE = "sickcodes/docker-osx:stable"

def check_kvm():
    """Check if KVM is available"""
    return os.path.exists('/dev/kvm')

def check_docker():
    """Check if Docker is installed"""
    result = subprocess.run(['docker', '--version'], capture_output=True)
    return result.returncode == 0

def start_macos():
    """Start macOS container"""
    if not check_kvm():
        return {
            'success': False,
            'error': 'KVM not available. This server does not support hardware virtualization (--device /dev/kvm required).'
        }
    
    if not check_docker():
        return {
            'success': False,
            'error': 'Docker not installed. Install with: curl -sSL get.docker.com | sh'
        }
    
    # Check if already running
    result = subprocess.run(['docker', 'ps', '--filter', f'name={CONTAINER_NAME}', '--format', '{{.ID}}'], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        return {
            'success': False,
            'error': f'macOS VM is already running! Connect with: ssh -p 50922 user@localhost'
        }
    
    # Remove old container if exists
    subprocess.run(['docker', 'rm', '-f', CONTAINER_NAME], capture_output=True)
    
    # Start container
    result = subprocess.run([
        'docker', 'run', '-d',
        '--device', '/dev/kvm',
        '-p', '50922:10022',
        '-p', '5900:5900',
        '--name', CONTAINER_NAME,
        IMAGE
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return {
            'success': True,
            'message': '🚀 macOS VM starting!',
            'details': 'Takes 2-5 minutes to boot. Use "status macos" to check.',
            'ssh': 'ssh -p 50922 user@localhost',
            'vnc': 'vnc://localhost:5900',
            'password': 'alpine'
        }
    else:
        return {
            'success': False,
            'error': result.stderr
        }

def stop_macos():
    """Stop macOS container"""
    result = subprocess.run(['docker', 'stop', CONTAINER_NAME], capture_output=True, text=True)
    subprocess.run(['docker', 'rm', CONTAINER_NAME], capture_output=True)
    
    return {
        'success': True,
        'message': '🛑 macOS VM stopped and removed.'
    }

def status_macos():
    """Check macOS status"""
    result = subprocess.run([
        'docker', 'ps', '--filter', f'name={CONTAINER_NAME}', 
        '--format', '{{.Status}}|{{.Ports}}'
    ], capture_output=True, text=True)
    
    output = result.stdout.strip()
    
    if output:
        parts = output.split('|')
        status = parts[0] if parts else 'running'
        ports = parts[1] if len(parts) > 1 else ''
        
        return {
            'status': 'running',
            'container_status': status,
            'ports': ports,
            'ssh': 'ssh -p 50922 user@localhost',
            'vnc': 'vnc://localhost:5900',
            'password': 'alpine'
        }
    else:
        return {
            'status': 'stopped',
            'message': 'macOS is not running. Use "start macos" to start.'
        }

def logs_macos():
    """Get macOS logs"""
    result = subprocess.run(['docker', 'logs', '-f', '--tail', '50', CONTAINER_NAME], 
                          capture_output=True, text=True, timeout=30)
    return {
        'success': True,
        'logs': result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout
    }

def run_command(command: str):
    """Main command handler"""
    cmd = command.lower().strip()
    
    if cmd in ['start', 'start macos', 'start osx', 'docker_osx start']:
        return start_macos()
    
    elif cmd in ['stop', 'stop macos', 'stop osx', 'docker_osx stop']:
        return stop_macos()
    
    elif cmd in ['status', 'status macos', 'status osx', 'docker_osx status']:
        return status_macos()
    
    elif cmd in ['logs', 'logs macos', 'docker_osx logs']:
        return logs_macos()
    
    elif cmd in ['ssh', 'ssh macos']:
        return {
            'ssh': 'ssh -p 50922 user@localhost',
            'password': 'alpine'
        }
    
    elif cmd in ['vnc', 'vnc macos']:
        return {
            'vnc': 'vnc://localhost:5900',
            'password': 'alpine'
        }
    
    else:
        return {
            'success': False,
            'error': f'Unknown command: {command}',
            'available': ['start', 'stop', 'status', 'logs', 'ssh', 'vnc']
        }

def cli():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: docker_osx.py <command>")
        print("Commands: start, stop, status, logs, ssh, vnc")
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    result = run_command(command)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    cli()
