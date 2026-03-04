#!/usr/bin/env python3
"""Fetch current Garmin Connect daily stats."""

import json
import os
import subprocess
import sys
from datetime import datetime

VENV_PACKAGES = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'venv', 'lib', 'python3.12', 'site-packages'
)
sys.path.insert(0, VENV_PACKAGES)

try:
    from garminconnect import Garmin, GarminConnectAuthenticationError
except ImportError:
    print(json.dumps({"error": "garminconnect not installed. Run: pip install garminconnect"}), file=sys.stderr)
    sys.exit(1)


def get_garmin_client():
    """Authenticate with Garmin Connect via 1Password credentials."""
    item_name = os.getenv("GARMIN_1P_ITEM_NAME", "Garmin Connect")
    vault = os.getenv("GARMIN_1P_VAULT", "Personal")
    op_token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")

    if not op_token:
        _die("OP_SERVICE_ACCOUNT_TOKEN not set")

    result = subprocess.run(
        ['op', 'item', 'get', item_name, '--vault', vault, '--format', 'json'],
        capture_output=True, text=True,
        env={**os.environ, 'OP_SERVICE_ACCOUNT_TOKEN': op_token}
    )
    if result.returncode != 0:
        _die(f"1Password lookup failed for '{item_name}': {result.stderr.strip()}")

    creds = json.loads(result.stdout)
    email = password = None
    for field in creds.get('fields', []):
        if field.get('id') == 'username':
            email = field.get('value')
        elif field.get('id') == 'password':
            password = field.get('value')

    if not email or not password:
        _die("Credentials incomplete in 1Password item")

    auth_dir = '/tmp/garmin-session/'
    os.makedirs(auth_dir, exist_ok=True)

    try:
        client = Garmin(email, password)
        client.login()
        client.garth.dump(dir_path=auth_dir)
        return client
    except GarminConnectAuthenticationError as e:
        _die(f"Auth failed: {e}")
    except Exception as e:
        _die(f"Login failed: {e}")


def _die(msg):
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(1)


def _safe(fn, default=None):
    """Run fn, return default on any exception."""
    try:
        return fn()
    except Exception:
        return default


def main():
    client = get_garmin_client()
    today = datetime.now().strftime('%Y-%m-%d')
    stats = {}

    # Profile
    stats['name'] = _safe(lambda: client.get_full_name())

    # Sleep
    sleep_raw = _safe(lambda: client.get_sleep_data(today), {})
    dto = sleep_raw.get('dailySleepDTO', {}) if sleep_raw else {}
    if dto:
        stats['sleep'] = {
            'duration_hours': round(dto.get('sleepTimeSeconds', 0) / 3600, 1),
            'deep_sleep_seconds': dto.get('deepSleepSeconds', 0),
            'light_sleep_seconds': dto.get('lightSleepSeconds', 0),
            'rem_sleep_seconds': dto.get('remSleepSeconds', 0),
            'awake_seconds': dto.get('awakeSleepSeconds', 0),
            'sleep_score': dto.get('sleepScores', {}).get('overall', {}).get('value'),
        }

    # Body Battery
    bb = _safe(lambda: client.get_body_battery(today), [])
    if bb:
        latest = bb[-1]
        stats['body_battery'] = {
            'current': latest.get('charged', 0),
        }

    # Resting Heart Rate
    hr = _safe(lambda: client.get_rhr_day(today))
    if hr:
        rhr = (hr.get('allMetrics', {})
                 .get('metricsMap', {})
                 .get('WELLNESS_RESTING_HEART_RATE', [{}])[0]
                 .get('value'))
        stats['heart_rate'] = {'resting': rhr}

    # Training Status
    ts = _safe(lambda: client.get_training_status(cdate=today))
    if ts:
        # Find primary device
        recent = ts.get('mostRecentTrainingStatus', {})
        devices = recent.get('recordedDevices', [])
        device_id = str(devices[0]['deviceId']) if devices else None

        status = None
        if device_id:
            status = (recent.get('latestTrainingStatusData', {})
                           .get(device_id, {})
                           .get('trainingStatusFeedbackPhrase'))

        # VO2 Max (check generic → running → cycling)
        vo2 = ts.get('mostRecentVO2Max', {})
        vo2_val = None
        for key in ('generic', 'running', 'cycling'):
            entry = vo2.get(key)
            if entry and entry.get('vo2MaxValue') is not None:
                vo2_val = entry['vo2MaxValue']
                break

        stats['training_status'] = {
            'status': status,
        }

    # Stress
    stress = _safe(lambda: client.get_stress_data(today))
    if stress and stress.get('avgStressLevel'):
        stats['stress'] = {
            'average': stress['avgStressLevel'],
            'max': stress.get('maxStressLevel'),
        }

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
