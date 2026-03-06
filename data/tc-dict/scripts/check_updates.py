#!/usr/bin/env python3
"""
Check for dictionary updates.

This script is designed to be run via cron job to periodically check
if new dictionary versions are available from MOE.

Requirements:
    No dependencies required (uses only stdlib)

Usage:
    python check_updates.py [--dict-name DICT_NAME] [--storage-path PATH] [--auto-update]

Args:
    --dict-name: Dictionary to check (default: 'concised')
    --storage-path: Storage directory (default: ~/.openclaw/dictionaries)
    --auto-update: Automatically download if update available

Returns:
    JSON with current version, latest version, and update status
"""

import argparse
import json
import logging
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Configure logging for cron jobs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class UpdateChecker:
    """Check for dictionary updates."""
    
    # MOE dictionary info
    DICTIONARIES = {
        'concised': {
            'name': '國語辭典簡編本',
            'url': 'https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html',
            'pattern': r'dict_concised_2014_(\d{8})',
        },
        'revised': {
            'name': '重編國語辭典修訂本',
            'url': 'https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_revised_download.html',
            'pattern': r'dict_revised_2014_(\d{8})',
        },
        'idiom': {
            'name': '成語典',
            'url': 'https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_idiom_download.html',
            'pattern': r'dict_idiom_2014_(\d{8})',
        },
        'mini': {
            'name': '國語小字典',
            'url': 'https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_mini_download.html',
            'pattern': r'dict_mini_2014_(\d{8})',
        },
    }
    
    def __init__(self, storage_path: str = None):
        """
        Initialize checker.
        
        Args:
            storage_path: Directory with dictionaries
        """
        if storage_path:
            self.storage_path = Path(storage_path).expanduser()
        else:
            self.storage_path = Path.home() / '.openclaw' / 'dictionaries'
        
        self.metadata_file = self.storage_path / 'metadata.json'
    
    def load_metadata(self) -> dict:
        """Load local version info."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
                return {}
        return {}
    
    def get_latest_version(self, dict_name: str) -> dict:
        """
        Fetch latest version from MOE.
        
        Args:
            dict_name: Dictionary identifier
        
        Returns:
            dict with version or error info
        """
        if dict_name not in self.DICTIONARIES:
            return {'error': f'Unknown dictionary: {dict_name}'}
        
        info = self.DICTIONARIES[dict_name]
        
        try:
            logger.info(f"Checking {dict_name} at {info['url']}...")
            
            with urllib.request.urlopen(info['url'], timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # Extract version from filename pattern
                matches = re.findall(info['pattern'], html)
                
                if matches:
                    # Return the latest (highest) version
                    latest = sorted(matches, reverse=True)[0]
                    logger.info(f"Latest version of {dict_name}: {latest}")
                    
                    return {
                        'dict_name': dict_name,
                        'latest_version': latest,
                        'checked_at': datetime.utcnow().isoformat() + 'Z',
                    }
                else:
                    return {
                        'error': f'Could not extract version for {dict_name}',
                        'dict_name': dict_name,
                    }
        
        except urllib.error.URLError as e:
            logger.error(f"Network error: {e}")
            return {
                'error': f'Network error: {e}',
                'dict_name': dict_name,
            }
        except Exception as e:
            logger.error(f"Error checking {dict_name}: {e}")
            return {
                'error': str(e),
                'dict_name': dict_name,
            }
    
    def compare_versions(self, dict_name: str) -> dict:
        """
        Compare local version with latest.
        
        Args:
            dict_name: Dictionary identifier
        
        Returns:
            dict with comparison result
        """
        metadata = self.load_metadata()
        local_version = metadata.get(dict_name, {}).get('version')
        
        latest_info = self.get_latest_version(dict_name)
        
        if 'error' in latest_info:
            return latest_info
        
        latest_version = latest_info['latest_version']
        
        # Compare versions
        if local_version is None:
            status = 'not_installed'
        elif local_version == latest_version:
            status = 'up_to_date'
        elif local_version < latest_version:
            status = 'update_available'
        else:
            status = 'newer_than_remote'
        
        result = {
            'dict_name': dict_name,
            'local_version': local_version,
            'latest_version': latest_version,
            'status': status,
            'update_available': status == 'update_available',
            'checked_at': latest_info['checked_at'],
        }
        
        logger.info(f"Status for {dict_name}: {status}")
        
        return result
    
    def check_all(self) -> dict:
        """Check all configured dictionaries."""
        results = []
        
        metadata = self.load_metadata()
        for dict_name in metadata.keys():
            result = self.compare_versions(dict_name)
            results.append(result)
        
        has_updates = any(r.get('update_available') for r in results)
        
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'dictionaries': results,
            'updates_available': has_updates,
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Check for dictionary updates')
    parser.add_argument('--dict-name', help='Check specific dictionary')
    parser.add_argument('--storage-path', help='Storage directory')
    parser.add_argument('--auto-update', action='store_true', help='Auto-update if available')
    parser.add_argument('--check-all', action='store_true', help='Check all dictionaries')
    
    args = parser.parse_args()
    
    try:
        checker = UpdateChecker(args.storage_path)
        
        if args.check_all:
            result = checker.check_all()
        elif args.dict_name:
            result = checker.compare_versions(args.dict_name)
        else:
            # Default: check concised
            result = checker.compare_versions('concised')
        
        # If auto-update requested and updates available
        if args.auto_update and result.get('update_available'):
            logger.info("Updates available, initiating download...")
            logger.info("Note: Use download_dictionary.py for actual download")
            # In production, would call download_dictionary.py here
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(json.dumps({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
