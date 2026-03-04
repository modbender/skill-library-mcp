#!/usr/bin/env python3
"""
WordPress Media Uploader

Batch upload media files to WordPress with support for metadata,
alt text, captions, and post attachments.

Usage:
    python media_uploader.py image1.jpg image2.png
    python media_uploader.py --directory ./images --recursive
    python media_uploader.py --csv media_list.csv
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


class MediaUploader:
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize WordPress media uploader.
        
        Args:
            base_url: WordPress site URL
            username: WordPress username
            password: Application password
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def upload_single_file(self, file_path: str, metadata: Optional[Dict] = None) -> Optional[Dict]:
        """
        Upload a single file to WordPress media library.
        
        Args:
            file_path: Path to file
            metadata: Optional metadata dict with keys:
                - title: Media title
                - caption: Media caption
                - alt_text: Alt text
                - description: Description
                - post: Post ID to attach to
                
        Returns:
            Media data dictionary or None if failed
        """
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            return None
        
        metadata = metadata or {}
        file_name = os.path.basename(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {}
                
                # Add metadata if provided
                for key in ['title', 'caption', 'alt_text', 'description', 'post']:
                    if key in metadata:
                        data[key] = metadata[key]
                
                # If no title provided, use filename without extension
                if 'title' not in data:
                    data['title'] = os.path.splitext(file_name)[0]
                
                print(f"Uploading: {file_name} ({os.path.getsize(file_path)/1024:.1f} KB)...")
                
                response = self.session.post(
                    f"{self.api_url}/media",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 201:
                    media_data = response.json()
                    print(f"  ✓ Uploaded: {media_data['source_url']} (ID: {media_data['id']})")
                    return media_data
                else:
                    print(f"  ✗ Failed: {response.status_code} {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def upload_directory(self, directory: str, recursive: bool = False, 
                        extensions: List[str] = None) -> List[Dict]:
        """
        Upload all media files in a directory.
        
        Args:
            directory: Directory path
            recursive: Include subdirectories
            extensions: Allowed file extensions (default: image extensions)
            
        Returns:
            List of uploaded media data
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', 
                         '.bmp', '.tiff', '.svg', '.pdf', '.mp4', 
                         '.mov', '.avi', '.wmv', '.mp3', '.wav', '.ogg']
        
        uploaded = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"✗ Directory not found: {directory}")
            return uploaded
        
        # Collect files
        files = []
        if recursive:
            for ext in extensions:
                files.extend(dir_path.rglob(f'*{ext}'))
                files.extend(dir_path.rglob(f'*{ext.upper()}'))
        else:
            for ext in extensions:
                files.extend(dir_path.glob(f'*{ext}'))
                files.extend(dir_path.glob(f'*{ext.upper()}'))
        
        files = list(set(files))  # Remove duplicates
        files.sort()
        
        print(f"Found {len(files)} media files in {directory}")
        
        # Upload each file
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] ", end='')
            
            # Generate metadata from filename
            file_stem = file_path.stem
            # Convert underscores and hyphens to spaces, capitalize
            title = ' '.join(word.capitalize() for word in file_stem.replace('_', ' ').replace('-', ' ').split())
            
            metadata = {
                'title': title,
                'alt_text': file_stem.replace('_', ' ').replace('-', ' ')  # Simple alt text
            }
            
            media_data = self.upload_single_file(str(file_path), metadata)
            if media_data:
                uploaded.append(media_data)
            
            # Small delay to avoid overwhelming server
            if i < len(files):
                time.sleep(1)
        
        return uploaded
    
    def upload_from_csv(self, csv_file: str) -> List[Dict]:
        """
        Upload media files specified in CSV.
        
        CSV format should have columns:
        - file_path: Path to file (required)
        - title: Media title (optional)
        - caption: Caption (optional)
        - alt_text: Alt text (optional)
        - description: Description (optional)
        - post: Post ID to attach to (optional)
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of uploaded media data
        """
        uploaded = []
        
        if not os.path.exists(csv_file):
            print(f"✗ CSV file not found: {csv_file}")
            return uploaded
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    print("CSV file is empty")
                    return uploaded
                
                print(f"Found {len(rows)} entries in CSV")
                
                for i, row in enumerate(rows, 1):
                    file_path = row.get('file_path', '').strip()
                    if not file_path:
                        print(f"\n[{i}/{len(rows)}] ✗ Skipping row {i}: No file_path")
                        continue
                    
                    print(f"\n[{i}/{len(rows)}] ", end='')
                    
                    # Prepare metadata
                    metadata = {}
                    for key in ['title', 'caption', 'alt_text', 'description', 'post']:
                        if key in row and row[key].strip():
                            metadata[key] = row[key].strip()
                    
                    media_data = self.upload_single_file(file_path, metadata)
                    if media_data:
                        uploaded.append(media_data)
                    
                    if i < len(rows):
                        time.sleep(1)
                        
        except Exception as e:
            print(f"\n✗ Error reading CSV: {e}")
        
        return uploaded
    
    def generate_import_report(self, uploaded_media: List[Dict], 
                              output_file: Optional[str] = None) -> str:
        """
        Generate report of uploaded media.
        
        Args:
            uploaded_media: List of media data dictionaries
            output_file: Optional file to save report
            
        Returns:
            Report string
        """
        if not uploaded_media:
            report = "No media uploaded."
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
            return report
        
        report_lines = [
            f"# WordPress Media Upload Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total uploaded: {len(uploaded_media)}",
            f"\n## Uploaded Media\n"
        ]
        
        for media in uploaded_media:
            report_lines.extend([
                f"### {media.get('title', 'Untitled')}",
                f"- ID: {media['id']}",
                f"- File: {media.get('source_url', 'N/A')}",
                f"- Size: {media.get('media_details', {}).get('filesize', 'N/A')} bytes",
                f"- Dimensions: {media.get('media_details', {}).get('width', 'N/A')}x{media.get('media_details', {}).get('height', 'N/A')}",
                f"- Date: {media.get('date', 'N/A')}",
                f"- URL: {media.get('link', 'N/A')}",
                f""
            ])
        
        # Add Gutenberg block examples
        report_lines.extend([
            f"\n## Gutenberg Block Examples\n",
            f"Use these IDs in your posts:\n"
        ])
        
        for media in uploaded_media:
            if 'image' in media.get('media_type', ''):
                report_lines.append(
                    f'<!-- wp:image {{"id":{media["id"]}}} -->'
                    f'<figure class="wp-block-image">'
                    f'<img src="{media.get("source_url")}" alt="{media.get("alt_text", "")}" class="wp-image-{media["id"]}"/>'
                    f'</figure><!-- /wp:image -->'
                )
        
        report = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✓ Report saved to: {output_file}")
        
        return report
    
    def update_media_metadata(self, media_id: int, metadata: Dict) -> bool:
        """
        Update metadata of existing media item.
        
        Args:
            media_id: Media ID
            metadata: Dict with keys: title, caption, alt_text, description
            
        Returns:
            True if successful
        """
        try:
            response = self.session.post(
                f"{self.api_url}/media/{media_id}",
                json=metadata
            )
            
            if response.status_code == 200:
                print(f"✓ Updated metadata for media ID {media_id}")
                return True
            else:
                print(f"✗ Failed to update media {media_id}: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error updating media {media_id}: {e}")
            return False


def parse_metadata_string(metadata_str: str) -> Dict:
    """
    Parse metadata from string in format "key1=value1;key2=value2".
    
    Args:
        metadata_str: Metadata string
        
    Returns:
        Dictionary of metadata
    """
    metadata = {}
    if not metadata_str:
        return metadata
    
    pairs = metadata_str.split(';')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            metadata[key.strip()] = value.strip()
    
    return metadata


def main():
    parser = argparse.ArgumentParser(description='Batch upload media to WordPress')
    parser.add_argument('files', nargs='*', help='Media files to upload')
    parser.add_argument('--directory', '-d', help='Upload all media files in directory')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Include subdirectories when using --directory')
    parser.add_argument('--csv', help='CSV file with media list and metadata')
    parser.add_argument('--metadata', help='Metadata for all files (format: "title=My Title;alt_text=Description")')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--extensions', default='jpg,jpeg,png,gif,webp,pdf,mp4',
                       help='Comma-separated file extensions (default: jpg,jpeg,png,gif,webp,pdf,mp4)')
    parser.add_argument('--test', action='store_true',
                       help='Test connection only')
    
    args = parser.parse_args()
    
    # Load environment variables
    wp_url = os.environ.get('WP_URL')
    wp_username = os.environ.get('WP_USERNAME')
    wp_password = os.environ.get('WP_APPLICATION_PASSWORD')
    
    if not all([wp_url, wp_username, wp_password]):
        print("Error: Environment variables not set.")
        print("Please set: WP_URL, WP_USERNAME, WP_APPLICATION_PASSWORD")
        sys.exit(1)
    
    # Initialize uploader
    uploader = MediaUploader(wp_url, wp_username, wp_password)
    
    # Test connection
    print("Testing WordPress connection...")
    try:
        response = uploader.session.get(f"{uploader.api_url}/users/me", timeout=10)
        if response.status_code == 200:
            print(f"✓ Connected to: {wp_url}")
            print(f"  User: {response.json().get('name')}")
        else:
            print(f"✗ Connection failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)
    
    if args.test:
        print("✓ Connection test successful")
        sys.exit(0)
    
    # Parse metadata
    global_metadata = parse_metadata_string(args.metadata) if args.metadata else {}
    
    uploaded = []
    
    # Upload from CSV
    if args.csv:
        print(f"\nUploading from CSV: {args.csv}")
        uploaded.extend(uploader.upload_from_csv(args.csv))
    
    # Upload directory
    if args.directory:
        extensions = [f'.{ext.strip()}' for ext in args.extensions.split(',')]
        print(f"\nUploading directory: {args.directory}")
        if args.recursive:
            print("  (including subdirectories)")
        uploaded.extend(uploader.upload_directory(
            args.directory, args.recursive, extensions
        ))
    
    # Upload individual files
    if args.files:
        print(f"\nUploading {len(args.files)} individual files")
        for file_path in args.files:
            media_data = uploader.upload_single_file(file_path, global_metadata)
            if media_data:
                uploaded.append(media_data)
            time.sleep(1)  # Delay between uploads
    
    # Generate report
    if uploaded:
        print(f"\n{'='*50}")
        print(f"Successfully uploaded {len(uploaded)} media files")
        
        report = uploader.generate_import_report(uploaded, args.output)
        
        if not args.output:
            print("\n" + report[:1000] + ("..." if len(report) > 1000 else ""))
            
        # Save media IDs to file for reference
        ids_file = 'uploaded_media_ids.json'
        ids = [{'id': m['id'], 'title': m.get('title', ''), 'url': m.get('source_url', '')} 
               for m in uploaded]
        with open(ids_file, 'w', encoding='utf-8') as f:
            json.dump(ids, f, indent=2)
        print(f"\n✓ Media IDs saved to: {ids_file}")
        
    else:
        print("\nNo media files were uploaded.")
        sys.exit(1)


if __name__ == "__main__":
    main()