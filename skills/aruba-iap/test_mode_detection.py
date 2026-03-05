#!/usr/bin/env python3
"""Test device mode detection."""

import sys
sys.path.insert(0, 'iapctl/src')

from iapctl.connection import IAPConnection

# Test connection
with IAPConnection(host='192.168.20.56', username='admin', password='sh8beijing') as conn:
    # Get version
    version_info = conn.get_version()
    print('Version Info:')
    for k, v in version_info.items():
        print(f'  {k}: {v}')

    # Detect device mode
    device_mode = conn.detect_device_mode()
    print('\nDevice Mode:')
    for k, v in device_mode.items():
        print(f'  {k}: {v}')

    # Test commands
    print('\nTesting Commands:')

    # Try show wlan (VC command)
    try:
        result = conn.send_command('show wlan')
        print('  show wlan: SUCCESS')
        print(f'    Output length: {len(result)} chars')
    except Exception as e:
        print(f'  show wlan: FAILED - {e}')

    # Try wlan command (standalone command)
    try:
        result = conn.send_command('wlan')
        print('  wlan: SUCCESS')
        print(f'    Output length: {len(result)} chars')
        print(f'    First 100 chars: {result[:100]}')
    except Exception as e:
        print(f'  wlan: FAILED - {e}')

    # Try show ap database (VC command)
    try:
        result = conn.send_command('show ap database')
        print('  show ap database: SUCCESS')
        print(f'    Output length: {len(result)} chars')
    except Exception as e:
        print(f'  show ap database: FAILED - {e}')

    # Try show ap info (standalone command)
    try:
        result = conn.send_command('show ap info')
        print('  show ap info: SUCCESS')
        print(f'    Output length: {len(result)} chars')
        print(f'    First 100 chars: {result[:100]}')
    except Exception as e:
        print(f'  show ap info: FAILED - {e}')
