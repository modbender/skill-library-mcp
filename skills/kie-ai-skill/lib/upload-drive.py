#!/usr/bin/env python3
"""
Upload files to Google Drive via Maton API gateway.

Security manifest:
  Env vars:  MATON_API_KEY (required)
  Endpoints: https://gateway.maton.ai/google-drive/upload/drive/v3/files (POST - sends file bytes and filename)
  File I/O:  reads the local file specified as argument (read only)
  No data is sent to any endpoint other than those listed above.
"""
import sys
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

def upload_file(file_path, folder_id=None, filename=None):
    """
    Upload a file to Google Drive.
    
    Args:
        file_path: Path to the local file
        folder_id: Optional Google Drive folder ID
        filename: Optional custom filename (defaults to original filename)
    
    Returns:
        dict: Response from Google Drive API with file metadata
    """
    api_key = os.environ.get('MATON_API_KEY')
    if not api_key:
        print('Error: MATON_API_KEY not set', file=sys.stderr)
        sys.exit(1)
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f'Error: File not found: {file_path}', file=sys.stderr)
        sys.exit(1)
    
    # Use provided filename or original
    upload_name = filename or file_path.name
    
    # Determine MIME type based on extension
    ext = file_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.pdf': 'application/pdf',
    }
    mime_type = mime_types.get(ext, 'application/octet-stream')
    
    try:
        # Step 1: Create file metadata
        metadata = {
            'name': upload_name,
            'mimeType': mime_type
        }
        
        if folder_id:
            metadata['parents'] = [folder_id]
        
        # Step 2: Use multipart upload (simpler for smaller files)
        # Google Drive API supports simple upload via POST with uploadType=media
        # Then patch metadata separately
        
        # First, upload the file content
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Upload with metadata using multipart upload
        boundary = '----WebKitFormBoundary' + os.urandom(16).hex()
        
        # Build multipart body
        parts = []
        
        # Part 1: Metadata
        parts.append(f'--{boundary}')
        parts.append('Content-Type: application/json; charset=UTF-8')
        parts.append('')
        parts.append(json.dumps(metadata))
        
        # Part 2: File content
        parts.append(f'--{boundary}')
        parts.append(f'Content-Type: {mime_type}')
        parts.append('')
        
        # Join text parts
        body_text = '\r\n'.join(parts) + '\r\n'
        body_bytes = body_text.encode('utf-8')
        
        # Add binary file data
        body_bytes += file_data
        body_bytes += f'\r\n--{boundary}--\r\n'.encode('utf-8')
        
        # Make the upload request
        url = 'https://gateway.maton.ai/google-drive/upload/drive/v3/files?uploadType=multipart'
        req = urllib.request.Request(url, data=body_bytes, method='POST')
        req.add_header('Authorization', f'Bearer {api_key}')
        req.add_header('Content-Type', f'multipart/related; boundary={boundary}')
        
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            return result
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        print(f'HTTP Error {e.code}: {error_body}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error uploading file: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload file to Google Drive')
    parser.add_argument('file', help='Path to file to upload')
    parser.add_argument('--folder-id', help='Google Drive folder ID')
    parser.add_argument('--filename', help='Custom filename (optional)')
    parser.add_argument('--json', action='store_true', help='Output JSON response')
    
    args = parser.parse_args()
    
    result = upload_file(args.file, args.folder_id, args.filename)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        file_id = result.get('id', 'unknown')
        name = result.get('name', 'unknown')
        web_link = result.get('webViewLink', result.get('webContentLink', ''))
        print(f'✓ Uploaded: {name}')
        print(f'  File ID: {file_id}')
        if web_link:
            print(f'  URL: {web_link}')
