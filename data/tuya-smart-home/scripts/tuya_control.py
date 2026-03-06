#!/usr/bin/env python3
"""Tuya Smart Home device control — cloud and local modes."""

import argparse
import json
import sys


def cloud_connect(access_id, access_secret, region):
    from tuya_connector import TuyaOpenAPI
    endpoints = {
        'cn': 'https://openapi.tuyacn.com',
        'us': 'https://openapi.tuyaus.com',
        'eu': 'https://openapi.tuyaeu.com',
        'in': 'https://openapi.tuyain.com',
    }
    endpoint = endpoints.get(region, endpoints['us'])
    api = TuyaOpenAPI(endpoint, access_id, access_secret)
    resp = api.connect()
    if not resp.get('success'):
        print(f"❌ Cloud connect failed: {resp.get('msg', 'unknown error')}", file=sys.stderr)
        sys.exit(1)
    return api


def cloud_info(api, device_id):
    resp = api.get(f'/v1.0/devices/{device_id}')
    if resp.get('success'):
        result = resp['result']
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ {resp.get('msg')}", file=sys.stderr)
        sys.exit(1)


def cloud_status(api, device_id):
    resp = api.get(f'/v1.0/devices/{device_id}/status')
    if resp.get('success'):
        for item in resp['result']:
            print(f"  {item['code']}: {item['value']}")
    else:
        print(f"❌ {resp.get('msg')}", file=sys.stderr)
        sys.exit(1)


def cloud_send(api, device_id, code, value):
    # Auto-convert value types
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass  # keep as string

    resp = api.post(f'/v1.0/devices/{device_id}/commands', {
        'commands': [{'code': code, 'value': value}]
    })
    if resp.get('success'):
        print(f"✅ Sent {code}={value} to {device_id}")
    else:
        print(f"❌ {resp.get('msg')}", file=sys.stderr)
        sys.exit(1)


def local_connect(device_id, ip, local_key, version=3.4):
    import tinytuya
    d = tinytuya.Device(device_id, ip, local_key, version=version)
    d.set_socketTimeout(5)
    return d


def local_status(device):
    status = device.status()
    if 'Error' in status:
        print(f"❌ {status['Error']}: {status.get('Err', '')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(status, indent=2, ensure_ascii=False))


def local_send(device, dp_id, value):
    # Auto-convert value types
    if isinstance(value, str):
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                pass

    device.set_value(int(dp_id), value)
    print(f"✅ Sent DP {dp_id}={value}")


def main():
    parser = argparse.ArgumentParser(description='Tuya Smart Home device control')
    parser.add_argument('--mode', choices=['cloud', 'local'], required=True, help='Control mode')
    parser.add_argument('--action', choices=['send', 'status', 'info'], required=True, help='Action')
    parser.add_argument('--device-id', required=True, help='Device ID')

    # Cloud options
    parser.add_argument('--access-id', help='Tuya Access ID (cloud mode)')
    parser.add_argument('--access-secret', help='Tuya Access Secret (cloud mode)')
    parser.add_argument('--region', default='cn', choices=['cn', 'us', 'eu', 'in'], help='Data center region')

    # Local options
    parser.add_argument('--ip', help='Device IP (local mode)')
    parser.add_argument('--local-key', help='Device local key (local mode)')
    parser.add_argument('--version', type=float, default=3.4, help='Protocol version (default: 3.4)')

    # Command options
    parser.add_argument('--code', help='DP code name (cloud send)')
    parser.add_argument('--value', help='Value to set')
    parser.add_argument('--dp-id', help='DP ID number (local send)')

    args = parser.parse_args()

    if args.mode == 'cloud':
        if not args.access_id or not args.access_secret:
            parser.error('Cloud mode requires --access-id and --access-secret')
        api = cloud_connect(args.access_id, args.access_secret, args.region)

        if args.action == 'info':
            cloud_info(api, args.device_id)
        elif args.action == 'status':
            cloud_status(api, args.device_id)
        elif args.action == 'send':
            if not args.code or args.value is None:
                parser.error('Cloud send requires --code and --value')
            cloud_send(api, args.device_id, args.code, args.value)

    elif args.mode == 'local':
        if not args.ip or not args.local_key:
            parser.error('Local mode requires --ip and --local-key')
        device = local_connect(args.device_id, args.ip, args.local_key, args.version)

        if args.action == 'status':
            local_status(device)
        elif args.action == 'send':
            if not args.dp_id or args.value is None:
                parser.error('Local send requires --dp-id and --value')
            local_send(device, args.dp_id, args.value)
        elif args.action == 'info':
            print("ℹ️ Info action not available in local mode. Use cloud mode or check status.")


if __name__ == '__main__':
    main()
