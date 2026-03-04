#!/usr/bin/env python3
"""
SSH Connection Script for OpenClaw

Usage:
    python ssh.py <host> <username> <password> <command>
    
Example:
    python ssh.py 10.0.3.120 root 7758258Cc "uptime"
"""

import sys
import paramiko
import time


def ssh_connect(host, username, password, command):
    """Execute command via SSH using paramiko."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=username, password=password)
        
        # Execute command
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Read output
        output = stdout.read().decode()
        errors = stderr.read().decode()
        
        # Print results
        if output:
            print(output)
        if errors:
            print(f"Errors: {errors}", file=sys.stderr)
            
        return 0
        
    except Exception as e:
        print(f"SSH Error: {e}", file=sys.stderr)
        return 1
    finally:
        ssh.close()


def ssh_shell(host, username, password, commands):
    """Execute multiple commands via shell session."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=username, password=password)
        shell = ssh.invoke_shell()
        
        for cmd in commands:
            shell.send(cmd + '\n')
            time.sleep(1)
            output = shell.recv(4096).decode()
            print(output)
            
        return 0
        
    except Exception as e:
        print(f"SSH Shell Error: {e}", file=sys.stderr)
        return 1
    finally:
        ssh.close()


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python ssh.py <host> <username> <password> <command>")
        print("Or: python ssh.py <host> <username> <password> --shell 'cmd1;cmd2;cmd3'")
        sys.exit(1)
    
    host = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    command = sys.argv[4]
    
    if command == '--shell' and len(sys.argv) > 5:
        # Multi-command shell mode
        commands = sys.argv[5].split(';')
        sys.exit(ssh_shell(host, username, password, commands))
    else:
        # Single command mode
        sys.exit(ssh_connect(host, username, password, command))
