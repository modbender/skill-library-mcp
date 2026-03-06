#!/usr/bin/env python3
"""
IssueFinder Command Line Tool
A standalone tool for interacting with IssueFinder API to parse logs
"""

__version__ = "1.1.3"

import sys
import os
import json
import argparse
import time
import urllib.request
import urllib.parse
import urllib.error
import http.client
from pathlib import Path
import mimetypes
import uuid
import subprocess
import tempfile
import shutil
import zipfile
import tarfile
import gzip
import re
from datetime import datetime


def parse_happen_time(time_str):
    """
    Parse happen time from various formats and convert to ISO format (YYYY-MM-DDTHH:MM)
    
    Supported formats:
    - 2025-10-27T18:43 (ISO format - already supported)
    - 2025-10-27 18:43 (space separator)
    - 2025/10/27 18:43 (slash separator)
    - 2025-10-27 18:43:00 (with seconds)
    - 2025/10/27 18:43:00 (slash with seconds)
    
    Args:
        time_str: Time string in various formats
        
    Returns:
        str: Normalized time string in ISO format (YYYY-MM-DDTHH:MM)
        
    Raises:
        ValueError: If time format is not supported
    """
    if not time_str:
        raise ValueError("Time string cannot be empty")
    
    # Remove extra spaces and normalize
    time_str = time_str.strip()
    
    # Define possible formats
    formats = [
        # ISO format (already supported)
        "%Y-%m-%dT%H:%M",
        # Space separator formats  
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        # Slash separator formats
        "%Y/%m/%d %H:%M", 
        "%Y/%m/%d %H:%M:%S",
        # Additional dash formats with seconds
        "%Y-%m-%dT%H:%M:%S"
    ]
    
    parsed_dt = None
    for fmt in formats:
        try:
            parsed_dt = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            continue
    
    if parsed_dt is None:
        raise ValueError(f"Unsupported time format: {time_str}. Supported formats: "
                        "YYYY-MM-DDTHH:MM, YYYY-MM-DD HH:MM, YYYY/MM/DD HH:MM, "
                        "YYYY-MM-DD HH:MM:SS, YYYY/MM/DD HH:MM:SS")
    
    # Convert to required ISO format (YYYY-MM-DDTHH:MM)
    return parsed_dt.strftime("%Y-%m-%dT%H:%M")


class IssuefinderClient:
    """Client for interacting with IssueFinder API"""
    
    def __init__(self, server_url="https://issuefinder-playground-init-dev.inner.chj.cloud"):
        self.server_url = server_url.rstrip('/')
        self.session_headers = {
            'User-Agent': 'IssueFinder-CLI/1.0'
        }
    
    def _make_request(self, method, url, data=None, headers=None, timeout=None, max_retries=3):
        """Make HTTP request with retry logic"""
        full_url = f"{self.server_url}{url}"
        req_headers = self.session_headers.copy()
        if headers:
            req_headers.update(headers)
        
        if timeout is None:
            timeout = 600
        
        last_exception = None
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    req = urllib.request.Request(full_url, headers=req_headers)
                else:
                    if isinstance(data, dict):
                        data = json.dumps(data).encode('utf-8')
                        req_headers['Content-Type'] = 'application/json'
                    elif isinstance(data, bytes):
                        pass
                    else:
                        data = str(data).encode('utf-8') if data else None
                    
                    req = urllib.request.Request(full_url, data=data, headers=req_headers)
                    req.get_method = lambda: method.upper()
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    content = response.read()
                    if response.headers.get('content-type', '').startswith('application/json'):
                        return json.loads(content.decode('utf-8'))
                    return content
                    
            except urllib.error.HTTPError as e:
                error_msg = e.read().decode('utf-8') if e.fp else str(e)
                try:
                    error_data = json.loads(error_msg)
                    raise Exception(f"HTTP {e.code}: {error_data.get('detail', error_msg)}")
                except json.JSONDecodeError:
                    raise Exception(f"HTTP {e.code}: {error_msg}")
            except (urllib.error.URLError, ConnectionResetError, http.client.IncompleteRead) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Request failed after {max_retries} retries: {str(e)}")
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1 and 'Remote end closed connection' in str(e):
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Request failed: {str(e)}")
        
        if last_exception:
            raise Exception(f"Request failed after {max_retries} retries: {str(last_exception)}")
    
    def create_environment(self):
        """Create a new environment"""
        return self._make_request('POST', '/api/environment/create')
    
    def upload_file(self, env_id, file_path):
        """Upload file to environment"""
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        
        # Create multipart form data
        boundary = f"----formdata-{uuid.uuid4().hex}"
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Build multipart body
        body_parts = []
        
        # File field
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        body_parts.append(f'Content-Type: {content_type}'.encode())
        body_parts.append(b'')
        body_parts.append(file_content)
        
        body_parts.append(f'--{boundary}--'.encode())
        
        body = b'\r\n'.join(body_parts)
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        return self._make_request('POST', f'/api/files/{env_id}/upload', data=body, headers=headers)
    
    def get_tool_status(self, env_id, tool_name):
        """Get tool status in environment"""
        return self._make_request('GET', f'/api/tools/{env_id}/{tool_name}/status')
    
    def run_tool(self, env_id, tool_name):
        """Run tool in environment"""
        return self._make_request('POST', f'/api/tools/{env_id}/{tool_name}/run')
    
    def list_files(self, env_id):
        """List files in environment"""
        return self._make_request('GET', f'/api/files/{env_id}/list')
    
    def download_file(self, env_id, file_path, local_path, chunk_size=8192):
        """Download file from environment with streaming support"""
        url_path = urllib.parse.quote(file_path)
        full_url = f"{self.server_url}/api/files/{env_id}/download?path={url_path}"
        
        req_headers = self.session_headers.copy()
        req = urllib.request.Request(full_url, headers=req_headers)
        
        local_dir = os.path.dirname(local_path)
        if local_dir:
            os.makedirs(local_dir, exist_ok=True)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=600) as response:
                    with open(local_path, 'wb') as f:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                return local_path
                
            except (urllib.error.URLError, ConnectionResetError, http.client.IncompleteRead, OSError) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Download failed after {max_retries} retries: {str(e)}")
            except Exception as e:
                if attempt < max_retries - 1 and 'Remote end closed connection' in str(e):
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Download failed: {str(e)}")
    
    def delete_environment(self, env_id):
        """Delete environment and cleanup resources"""
        return self._make_request('DELETE', f'/api/environment/{env_id}')
    
    def create_cloud_log_task(self, env_id, vin, happen_time, task_type):
        """Create cloud log task"""
        # Create multipart form data for cloud log request
        boundary = f"----formdata-{uuid.uuid4().hex}"
        
        body_parts = []
        
        # Add form fields
        for field_name, field_value in [('vin', vin), ('happen_time', happen_time), ('task_type', task_type)]:
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(f'Content-Disposition: form-data; name="{field_name}"'.encode())
            body_parts.append(b'')
            body_parts.append(str(field_value).encode())
        
        body_parts.append(f'--{boundary}--'.encode())
        body = b'\r\n'.join(body_parts)
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        return self._make_request('POST', f'/api/files/{env_id}/create_cloud_log/', data=body, headers=headers)
    
    def get_cloud_log_status(self, env_id):
        """Get cloud log task status"""
        return self._make_request('POST', f'/api/files/{env_id}/download_cloud_log/', data=b'{}', headers={'Content-Type': 'application/json'})
    
    def download_cloud_log(self, task_info):
        """Download cloud log files using task information"""
        data = {
            'task_id': str(task_info.get('task_id')),
            'happenTime': task_info.get('happenTime'),
            'vin': task_info.get('vin'),
            'issuefindermd': task_info.get('issuefindermd'),
            'reboot_rsn': task_info.get('reboot_rsn')
        }
        
        return self._make_request('POST', '/api/files/download_cloud_log/', data=data)


class ProgressBar:
    """Simple progress bar implementation"""
    
    def __init__(self, total, description="Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.width = 50
    
    def update(self, increment=1):
        self.current += increment
        self._display()
    
    def _display(self):
        if self.total == 0:
            percent = 100
        else:
            percent = min(100, (self.current / self.total) * 100)
        
        filled = int(self.width * percent / 100)
        bar = '█' * filled + '░' * (self.width - filled)
        
        print(f'\r{self.description}: |{bar}| {percent:.1f}%', end='', flush=True)
        
        if percent >= 100:
            print()  # New line when complete


def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    status_colors = {
        "INFO": "",
        "SUCCESS": "",
        "ERROR": "",
        "WARNING": ""
    }
    print(f"[{timestamp}] [{status}] {message}")


def download_files_from_env(client, env_id, output_dir, output_subdir=None, verbose=False):
    """
    统一的文件下载逻辑
    
    Args:
        client: IssuefinderClient instance
        env_id: Environment ID
        output_dir: Base output directory
        output_subdir: Optional subdirectory name
        verbose: Enable verbose output
        
    Returns:
        tuple: (output_path, downloaded_files list)
    """
    # Wait a moment for files to be ready
    time.sleep(2)
    
    # List files in environment
    print_status("Retrieving files from environment...")
    files_response = client.list_files(env_id)
    files = files_response.get('files', [])
    
    if not files:
        print_status("No files found in environment", "WARNING")
        return output_dir, []
    
    print_status(f"Found {len(files)} files to download")
    
    # Determine output directory
    final_output_dir = os.path.abspath(output_dir)
    if output_subdir:
        final_output_dir = os.path.join(final_output_dir, output_subdir)
    os.makedirs(final_output_dir, exist_ok=True)
    
    # Download files with progress
    progress = ProgressBar(len(files), "Downloading")
    downloaded_files = []
    
    for file_info in files:
        file_name = file_info['name']
        local_path = os.path.join(final_output_dir, file_name)
        
        # Create subdirectories if needed
        local_dir = os.path.dirname(local_path)
        if local_dir and local_dir != final_output_dir:
            os.makedirs(local_dir, exist_ok=True)
        
        try:
            client.download_file(env_id, file_name, local_path)
            downloaded_files.append(local_path)
            if verbose:
                print_status(f"Downloaded: {file_name}")
        except Exception as e:
            print_status(f"Failed to download {file_name}: {e}", "ERROR")
        
        progress.update()
    
    print_status(f"Download completed. {len(downloaded_files)} files saved to: {final_output_dir}", "SUCCESS")
    
    return final_output_dir, downloaded_files


def print_summary(mode, result, output_dir, downloaded_files, args):
    """
    统一的摘要打印逻辑
    
    Args:
        mode: Mode name ('cloud_log', 'direct_download', 'local_processing')
        result: Result dictionary from mode function
        output_dir: Output directory path
        downloaded_files: List of downloaded file paths
        args: Command line arguments
    """
    print("\n" + "="*60)
    
    if mode == 'cloud_log':
        mode_name = "ISSUEFINDER ANALYSIS SUMMARY" if hasattr(args, 'issuefinder') and args.issuefinder else "CLOUD LOG DOWNLOAD SUMMARY"
        print(mode_name)
        print("="*60)
        print(f"VIN: {result.get('vin', 'N/A')}")
        print(f"Happen Time: {result.get('happen_time', 'N/A')}")
        print(f"Task ID: {result.get('task_id', 'N/A')}")
        print(f"Environment ID: {result.get('env_id', 'N/A')}")
        print(f"Output directory: {output_dir}")
        print(f"Files downloaded: {len(downloaded_files)}")
        
        if result.get('task_info') and 'reboot_rsn' in result['task_info']:
            try:
                reboot_info = json.loads(result['task_info']['reboot_rsn'])
                print(f"Analysis Result: {reboot_info.get('final_res', 'N/A')}")
                print(f"Reboot Reason: {reboot_info.get('reboot_rsn', 'N/A')}")
            except json.JSONDecodeError:
                pass
    
    elif mode == 'direct_download':
        print("DIRECT CLOUD LOG DOWNLOAD SUMMARY")
        print("="*60)
        print(f"VIN: {result.get('vin', 'N/A')}")
        print(f"Happen Time: {result.get('happen_time', 'N/A')}")
        print(f"Log Type: {result.get('log_type', 'N/A')}")
        print(f"Time Range: ±{result.get('time_range', 'N/A')} minutes")
        print(f"File Count: {result.get('file_count', 'N/A')}")
        print(f"Environment ID: {result.get('env_id', 'N/A')}")
        print(f"Output directory: {output_dir}")
        print(f"Files downloaded: {len(downloaded_files)}")
    
    elif mode == 'local_processing':
        print("PROCESSING SUMMARY")
        print("="*60)
        print(f"Tool used: {result.get('tool', 'N/A')}")
        print(f"Input file: {result.get('input_file', 'N/A')}")
        print(f"Environment ID: {result.get('env_id', 'N/A')}")
        print(f"Output directory: {output_dir}")
        print(f"Files downloaded: {len(downloaded_files)}")
        print(f"Environment cleanup: {'Skipped (--keep-env)' if args.keep_env else 'Completed'}")
    
    if args.verbose and downloaded_files:
        print("\nDownloaded files:")
        for file_path in downloaded_files:
            file_size = os.path.getsize(file_path)
            print(f"  - {file_path} ({file_size} bytes)")
    
    print("="*60)


def detect_tool_type(file_path, verbose=False):
    """
    Detect tool type based on file name and content
    
    Args:
        file_path: Path to the file
        verbose: Enable verbose output
        
    Returns:
        str: Tool name or None if not detected
    """
    filename = os.path.basename(file_path).lower()
    
    if verbose:
        print_status(f"Detecting tool type for: {filename}")
    
    # Check for lastlog files
    if 'lastlog' in filename:
        if verbose:
            print_status("Detected lastlog file pattern")
        return 'lastlog_unpack'
    
    # Check for minidump files
    if 'minidump' in filename:
        if verbose:
            print_status("Detected minidump file pattern")
        return 'minidump_unpack'
    
    # Check for CLP files
    if filename.endswith('.clp') or filename.endswith('.clp.zst'):
        if verbose:
            print_status("Detected CLP file pattern")
        return 'clp_decompress'
    
    # Check for SLOG files
    if 'md_qx_slog2.bin' in filename:
        if verbose:
            print_status("Detected SLOG file pattern")
        return 'md_parser_slog'
    
    # Check for xbllog files
    if 'xbllog' in filename:
        if verbose:
            print_status("Detected xbllog file pattern")
        return 'xbllog_unpack'
    
    # Check for logfs files
    if 'logfs' in filename:
        if verbose:
            print_status("Detected logfs file pattern")
        return 'logfs_unpack'
    
    # Check for ftrace console log files (gvmbootlog or gvmlog)
    if 'gvmbootlog' in filename or 'gvmlog' in filename:
        if verbose:
            print_status("Detected ftrace console log file pattern")
        return 'ftrace_console_parser'
    
    if verbose:
        print_status("No matching tool pattern found")
    
    return None


def is_archive_file(file_path):
    """Check if file is an archive that needs extraction"""
    filename = os.path.basename(file_path).lower()
    archive_extensions = ('.zip', '.7z', '.gz', '.tar', '.tar.gz', '.tgz')
    return filename.endswith(archive_extensions)


def extract_archive_with_system_tools(archive_path, extract_to=None, verbose=False):
    """
    Extract archive using system tools with fallback to Python standard library
    
    Args:
        archive_path: Path to archive file
        extract_to: Directory to extract to (creates temp dir if None)
        verbose: Enable verbose output
        
    Returns:
        str: Path to extraction directory
    """
    if extract_to is None:
        extract_to = tempfile.mkdtemp(prefix='issuefinder_extract_')
    
    os.makedirs(extract_to, exist_ok=True)
    filename = os.path.basename(archive_path).lower()
    
    if verbose:
        print_status(f"Extracting {filename} to {extract_to}")
    
    try:
        # Try system tools first
        if filename.endswith('.zip'):
            try:
                subprocess.run(['unzip', '-q', archive_path, '-d', extract_to], 
                             check=True, capture_output=True, text=True)
                if verbose:
                    print_status("Extracted using system unzip")
                return extract_to
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python zipfile
                if verbose:
                    print_status("System unzip failed, using Python zipfile")
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                return extract_to
        
        elif filename.endswith(('.tar.gz', '.tgz')):
            try:
                subprocess.run(['tar', '-xzf', archive_path, '-C', extract_to], 
                             check=True, capture_output=True, text=True)
                if verbose:
                    print_status("Extracted using system tar")
                return extract_to
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python tarfile
                if verbose:
                    print_status("System tar failed, using Python tarfile")
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_to)
                return extract_to
        
        elif filename.endswith('.tar'):
            try:
                subprocess.run(['tar', '-xf', archive_path, '-C', extract_to], 
                             check=True, capture_output=True, text=True)
                if verbose:
                    print_status("Extracted using system tar")
                return extract_to
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python tarfile
                if verbose:
                    print_status("System tar failed, using Python tarfile")
                with tarfile.open(archive_path, 'r') as tar_ref:
                    tar_ref.extractall(extract_to)
                return extract_to
        
        elif filename.endswith('.gz') and not filename.endswith('.tar.gz'):
            # Single gzip file
            output_filename = filename[:-3] if filename.endswith('.gz') else filename + '_extracted'
            output_path = os.path.join(extract_to, output_filename)
            
            try:
                with open(output_path, 'wb') as output_file:
                    subprocess.run(['gunzip', '-c', archive_path], 
                                 stdout=output_file, check=True)
                if verbose:
                    print_status("Extracted using system gunzip")
                return extract_to
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python gzip
                if verbose:
                    print_status("System gunzip failed, using Python gzip")
                with gzip.open(archive_path, 'rb') as gz_file:
                    with open(output_path, 'wb') as output_file:
                        shutil.copyfileobj(gz_file, output_file)
                return extract_to
        
        elif filename.endswith('.7z'):
            try:
                subprocess.run(['7z', 'x', archive_path, f'-o{extract_to}', '-y'], 
                             check=True, capture_output=True, text=True)
                if verbose:
                    print_status("Extracted using system 7z")
                return extract_to
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise Exception("7z format requires 7z tool to be installed on the system")
        
        else:
            raise ValueError(f"Unsupported archive format: {filename}")
            
    except Exception as e:
        # Clean up on failure
        if os.path.exists(extract_to):
            shutil.rmtree(extract_to, ignore_errors=True)
        raise Exception(f"Extraction failed: {str(e)}")


def find_files_in_directory(directory, verbose=False):
    """
    Recursively find all files in directory and detect their types
    
    Args:
        directory: Directory to search
        verbose: Enable verbose output
        
    Returns:
        list: List of (file_path, detected_tool) tuples
    """
    found_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                detected_tool = detect_tool_type(file_path, verbose)
                if detected_tool:
                    found_files.append((file_path, detected_tool))
                    if verbose:
                        print_status(f"Found {detected_tool} file: {file}")
    
    return found_files


def check_and_update_version(server_url, skip_check=False, verbose=False):
    """Check version and update if needed"""
    if skip_check:
        if verbose:
            print_status("Skipping version check (--skip-version-check specified)")
        return True
    
    try:
        # Get server version
        version_url = f"{server_url.rstrip('/')}/api/cli/version"
        req = urllib.request.Request(version_url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            server_version = data.get('version', 'unknown')
        
        if verbose:
            print_status(f"Local version: {__version__}, Server version: {server_version}")
        
        # Compare versions
        if server_version == 'unknown' or server_version == __version__:
            if verbose:
                print_status("Version is up to date")
            return True
        
        # Download new version
        print_status(f"New version available: {server_version} (current: {__version__})", "INFO")
        print_status("Downloading latest version...")
        
        # Get home directory and create .issuefinder folder
        home_dir = os.path.expanduser("~")
        issuefinder_dir = os.path.join(home_dir, ".issuefinder")
        os.makedirs(issuefinder_dir, exist_ok=True)
        
        # Download new version
        download_url = f"{server_url.rstrip('/')}/api/cli/download"
        new_tool_path = os.path.join(issuefinder_dir, "issuefinder-tool.py")
        
        req = urllib.request.Request(download_url)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(new_tool_path, 'wb') as f:
                f.write(response.read())
        
        # Make it executable
        os.chmod(new_tool_path, 0o755)
        
        print_status(f"Downloaded new version to: {new_tool_path}", "SUCCESS")
        print_status("Restarting with new version...")
        
        # Re-execute with the new version
        os.execv(sys.executable, [sys.executable, new_tool_path] + sys.argv[1:])
        
    except Exception as e:
        if verbose:
            print_status(f"Version check failed: {e}", "WARNING")
            print_status("Continuing with current version...")
        return True


def run_cloud_log_mode(client, env_id, args):
    """
    Run cloud log download workflow
    
    Args:
        client: IssuefinderClient instance
        env_id: Environment ID
        args: Command line arguments
        
    Returns:
        dict: Result information including task_id, task_info, etc.
    """
    # Check if we're in IssueFinder mode
    mode_name = "IssueFinder analysis" if hasattr(args, 'issuefinder') and args.issuefinder else "cloud log download"
    print_status(f"Starting {mode_name} workflow", "INFO")
    
    # Parse and normalize happen_time to required format
    try:
        normalized_happen_time = parse_happen_time(args.happen_time)
        print_status(f"VIN: {args.vin}, Time: {normalized_happen_time} (normalized from: {args.happen_time}), Task Type: {args.task_type}")
    except ValueError as e:
        raise Exception(f"Invalid happen_time format: {e}")
    
    # Create cloud log task
    print_status("Creating cloud log task...")
    task_response = client.create_cloud_log_task(env_id, args.vin, normalized_happen_time, args.task_type)
    
    if not task_response.get('success'):
        raise Exception(f"Failed to create cloud log task: {task_response}")
    
    task_id = task_response['data']['taskId']
    print_status(f"Cloud log task created successfully: {task_id}", "SUCCESS")
    
    # Poll for task completion
    print_status(f"Waiting for task completion (polling every {args.poll_interval}s)...")
    task_info = None
    
    while True:
        try:
            status_response = client.get_cloud_log_status(env_id)
            
            if isinstance(status_response, dict) and task_id in status_response:
                task_status = status_response[task_id]
                
                if isinstance(task_status, dict) and task_status.get('status') == '已完成':
                    task_info = task_status
                    print_status("Task completed successfully!", "SUCCESS")
                    
                    # Display analysis results
                    if 'reboot_rsn' in task_info:
                        try:
                            reboot_info = json.loads(task_info['reboot_rsn'])
                            print_status(f"Analysis Result: {reboot_info.get('final_res', 'N/A')}")
                            print_status(f"Reboot Reason: {reboot_info.get('reboot_rsn', 'N/A')}")
                            print_status(f"Screen Status: {reboot_info.get('screen_res', 'N/A')}")
                        except json.JSONDecodeError:
                            print_status(f"Raw analysis result: {task_info['reboot_rsn']}")
                    
                    break
                elif task_status == "进行中" or (isinstance(task_status, dict) and task_status.get('status') != '已完成'):
                    print_status("Task is still in progress...", "INFO")
                else:
                    print_status(f"Unexpected task status: {task_status}", "WARNING")
            
            time.sleep(args.poll_interval)
            
        except KeyboardInterrupt:
            raise Exception("Task monitoring cancelled by user")
        except Exception as e:
            print_status(f"Error checking task status: {e}", "ERROR")
            time.sleep(args.poll_interval)
    
    # Trigger download from cloud to environment if issuefindermd exists
    if task_info and 'issuefindermd' in task_info and task_info['issuefindermd']:
        try:
            print_status("Triggering cloud log download to environment...")
            download_response = client.download_cloud_log(task_info)
            if args.verbose:
                print_status(f"Download triggered: {download_response}")
            # Wait a moment for files to be downloaded
            time.sleep(5)
            print_status("Waiting for files to be processed...")
        except Exception as e:
            print_status(f"Warning: Failed to trigger cloud log download: {e}", "WARNING")
            if args.verbose:
                import traceback
                traceback.print_exc()
    else:
        print_status("No issuefindermd field found in task_info, skipping cloud download trigger", "WARNING")
    
    # Return result information
    return {
        'env_id': env_id,
        'vin': args.vin,
        'happen_time': normalized_happen_time,
        'task_id': task_id,
        'task_info': task_info
    }


def run_direct_download_mode(client, env_id, args):
    """
    Run direct cloud log download workflow
    
    Args:
        client: IssuefinderClient instance
        env_id: Environment ID
        args: Command line arguments
        
    Returns:
        dict: Result information
    """
    print_status("Starting direct cloud log download workflow", "INFO")
    
    # Parse and normalize happen_time
    try:
        time_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S"
        ]
        
        parsed_dt = None
        for fmt in time_formats:
            try:
                parsed_dt = datetime.strptime(args.happen_time.strip(), fmt)
                break
            except ValueError:
                continue
        
        if parsed_dt is None:
            raise Exception(f"Invalid happen_time format: {args.happen_time}")
        
        standard_time = parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
        print_status(f"VIN: {args.vin}, Time: {standard_time}, Log Type: {args.log_type}, Time Range: ±{args.time_range} min")
        
    except Exception as e:
        raise Exception(f"Time parsing error: {e}")
    
    # Download cloud logs to environment
    print_status("Downloading cloud logs to environment...")
    
    # Set file_count to a large value to download all logs in the time range
    # This ensures we get all available logs without limiting by count
    file_count = 999
    
    # Prepare multipart form data
    boundary = f"----formdata-{uuid.uuid4().hex}"
    body_parts = []
    
    for field_name, field_value in [
        ('vin', args.vin),
        ('happen_time', standard_time),
        ('log_type', args.log_type),
        ('file_count', str(file_count)),
        ('time_range', str(args.time_range)),
        ('env', args.env)
    ]:
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="{field_name}"'.encode())
        body_parts.append(b'')
        body_parts.append(str(field_value).encode())
    
    body_parts.append(f'--{boundary}--'.encode())
    body = b'\r\n'.join(body_parts)
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }
    
    # Call API
    response = client._make_request(
        'POST',
        f'/api/files/{env_id}/direct_download_cloud_log/',
        data=body,
        headers=headers,
        timeout=300
    )
    
    if not response.get('success'):
        raise Exception(f"Cloud log download failed: {response}")
    
    print_status("Cloud logs downloaded to environment successfully", "SUCCESS")
    if args.verbose and response.get('result', {}).get('message'):
        print_status(f"Result: {response['result']['message']}")
    
    # Return result information
    return {
        'env_id': env_id,
        'vin': args.vin,
        'happen_time': standard_time,
        'log_type': args.log_type,
        'time_range': args.time_range,
        'file_count': file_count
    }


def run_local_processing_mode(client, env_id, args):
    """
    Run local file processing workflow
    
    Args:
        client: IssuefinderClient instance
        env_id: Environment ID
        args: Command line arguments
        
    Returns:
        dict: Result information including tool name, input file, etc.
    """
    # Validate input file
    if not os.path.exists(args.upload):
        raise Exception(f"Input file not found: {args.upload}")
    
    # Variables to track temporary directories for cleanup
    temp_dirs_to_cleanup = []
    
    try:
        # Step 1: Handle file processing (extraction if needed, tool detection)
        files_to_process = []
        detected_tool = args.tool
        
        if is_archive_file(args.upload):
            # Extract archive first
            print_status(f"Detected archive file: {os.path.basename(args.upload)}")
            extract_dir = extract_archive_with_system_tools(args.upload, verbose=args.verbose)
            temp_dirs_to_cleanup.append(extract_dir)
            print_status(f"Archive extracted successfully", "SUCCESS")
            
            # If user specified archive_extractor, just extract locally and return
            if detected_tool == 'archive_extractor':
                # Copy extracted files to output directory
                input_file_basename = os.path.basename(args.upload)
                file_output_dir = os.path.join(args.output, input_file_basename)
                os.makedirs(file_output_dir, exist_ok=True)
                
                copied_files = []
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, extract_dir)
                        dest_path = os.path.join(file_output_dir, rel_path)
                        
                        dest_dir = os.path.dirname(dest_path)
                        if dest_dir:
                            os.makedirs(dest_dir, exist_ok=True)
                        
                        shutil.copy2(src_path, dest_path)
                        copied_files.append(dest_path)
                
                print_status(f"Extraction completed. {len(copied_files)} files saved to: {file_output_dir}", "SUCCESS")
                
                # Return special result for archive_extractor
                return {
                    'env_id': env_id,
                    'tool': 'archive_extractor',
                    'input_file': args.upload,
                    'local_extraction': True
                }
            
            # If user specified tool type explicitly, use it and find matching files
            if detected_tool:
                print_status(f"Using user-specified tool: {detected_tool}", "INFO")
                # Find all files in extracted directory
                all_files = []
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            all_files.append(file_path)
                
                if not all_files:
                    raise Exception("No files found in archive")
                
                # Use the first file (or all files, depending on tool)
                files_to_process = [all_files[0]]
                print_status(f"Processing file: {os.path.basename(files_to_process[0])} with {detected_tool}", "SUCCESS")
            else:
                # Auto-detect tool type from files in archive
                found_files = find_files_in_directory(extract_dir, args.verbose)
                
                if not found_files:
                    raise Exception("No processable files found in archive. Supported file patterns: lastlog, minidump, *.clp, md_qx_slog2.bin, xbllog, logfs")
                
                if len(found_files) > 1:
                    print_status(f"Found {len(found_files)} processable files:", "INFO")
                    for file_path, tool in found_files:
                        print_status(f"  - {os.path.basename(file_path)} -> {tool}")
                    
                    # Process ALL files grouped by tool type
                    print_status(f"Will process all {len(found_files)} files", "INFO")
                    
                    # Group files by tool type
                    files_by_tool = {}
                    for file_path, tool in found_files:
                        if tool not in files_by_tool:
                            files_by_tool[tool] = []
                        files_by_tool[tool].append(file_path)
                    
                    # For now, process the first group (can be extended to process all)
                    detected_tool = list(files_by_tool.keys())[0]
                    files_to_process = files_by_tool[detected_tool]
                    
                    if len(files_by_tool) > 1:
                        print_status(f"Note: Found files for {len(files_by_tool)} different tools", "INFO")
                        print_status(f"Processing {len(files_to_process)} files with {detected_tool} first", "INFO")
                else:
                    files_to_process = [found_files[0][0]]
                    detected_tool = found_files[0][1]
                    print_status(f"Found file: {os.path.basename(files_to_process[0])} -> {detected_tool}", "SUCCESS")
        
        else:
            # Single file - detect tool if not specified
            if not detected_tool:
                detected_tool = detect_tool_type(args.upload, args.verbose)
                if not detected_tool:
                    raise Exception("Could not auto-detect tool type for file. Supported patterns: lastlog, minidump, *.clp, md_qx_slog2.bin, xbllog, logfs. Use -t parameter to specify tool manually")
                print_status(f"Auto-detected tool: {detected_tool}", "SUCCESS")
            
            files_to_process = [args.upload]
        
        # Step 2: Upload file(s)
        uploaded_files = []
        for file_path in files_to_process:
            print_status(f"Uploading file: {os.path.basename(file_path)}")
            upload_response = client.upload_file(env_id, file_path)
            uploaded_files.append(upload_response['filename'])
            print_status(f"File uploaded: {upload_response['filename']}", "SUCCESS")
        
        # Step 3: Check tool status
        print_status(f"Checking tool status: {detected_tool}")
        tool_status = client.get_tool_status(env_id, detected_tool)
        
        if not tool_status['available']:
            error_msg = f"Tool not available: {tool_status['reason']}"
            if tool_status.get('missing_files'):
                error_msg += f". Missing files: {', '.join(tool_status['missing_files'])}"
            raise Exception(error_msg)
        
        print_status(f"Tool is available. Matching files: {len(tool_status['matching_files'])}")
        if args.verbose:
            for file in tool_status['matching_files']:
                print_status(f"  - {file}")
        
        # Step 4: Run tool
        print_status(f"Running tool: {detected_tool}")
        run_response = client.run_tool(env_id, detected_tool)
        
        if 'error' in run_response:
            raise Exception(f"Tool execution failed: {run_response['error']}")
        
        print_status("Tool execution completed", "SUCCESS")
        if args.verbose and 'output_file' in run_response:
            print_status(f"Output file: {run_response['output_file']}")
        
        # Return result information
        return {
            'env_id': env_id,
            'tool': detected_tool,
            'input_file': args.upload,
            'temp_dirs': temp_dirs_to_cleanup
        }
        
    except Exception as e:
        # Clean up temporary directories on error
        for temp_dir in temp_dirs_to_cleanup:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if args.verbose:
                        print_status(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as cleanup_error:
                if args.verbose:
                    print_status(f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}", "WARNING")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="IssueFinder Command Line Tool - Auto-detects file types when -t is not specified",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect tool type for local processing:
  %(prog)s -u /path/to/lastlog_file
  %(prog)s -u /path/to/archive.zip
  
  # Specify tool type manually:
  %(prog)s -t lastlog_unpack -u /path/to/lastlog_file
  %(prog)s -t minidump_unpack -u /path/to/minidump_file --verbose
  
  # Direct cloud log download (new, bypasses IssueFinder API):
  %(prog)s --direct-download --vin HLX14B175S1996368 --happen-time "2025-11-06 18:00"
  %(prog)s --direct-download --vin HLX14B175S1996368 --happen-time "2025-11-06 18:00" --log-type log_HUF_Klog --file-count 2 --time-range 120
  
  # Cloud log download (multiple time formats supported):
  %(prog)s --cloud-log --vin HLX33B124P1767770 --happen-time "2025-10-27T18:43" --task-type 1731484362257596488
  %(prog)s --cloud-log --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43" --task-type 1731484362257596488
  %(prog)s --cloud-log --vin HLX33B124P1767770 --happen-time "2025/10/27 18:43:00" --task-type 1731484362257596488
  
  # IssueFinder analysis (automatically uses task type 1731484362257596488):
  %(prog)s --issuefinder --vin HLX33B124P1767770 --happen-time "2025-10-27T18:43"
  %(prog)s --issuefinder --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43"
  %(prog)s --issuefinder --vin HLX33B124P1767770 --happen-time "2025/10/27 18:43:00"
  
  # With custom server:
  %(prog)s -u /path/to/file --server http://192.168.1.100:8080
        """
    )
    
    # Main operation mode
    parser.add_argument('--cloud-log', action='store_true',
                       help='Enable cloud log download mode instead of local file processing')
    parser.add_argument('--issuefinder', action='store_true',
                       help='Enable IssueFinder analysis mode (automatically uses task type 1731484362257596488). Requires --vin and --happen-time.')
    parser.add_argument('--direct-download', action='store_true',
                       help='Enable direct cloud log download mode (bypasses IssueFinder API, downloads directly from cloud). Requires --vin and --happen-time.')
    
    # Local file processing arguments
    parser.add_argument('-t', '--tool', 
                       help='Tool type to use (e.g., lastlog_unpack, minidump_unpack, clp_decompress, md_parser_slog). If not specified, auto-detects based on file name.')
    parser.add_argument('-u', '--upload',
                       help='Path to the file to upload and process. Supports archives (.zip, .tar.gz, .7z, etc.) which will be extracted automatically.')
    
    # Cloud log arguments
    parser.add_argument('--vin',
                       help='Vehicle VIN code for cloud log download (required for --cloud-log and --direct-download)')
    parser.add_argument('--happen-time',
                       help='Time when issue happened. Supports multiple formats: '
                            'YYYY-MM-DDTHH:MM, "YYYY-MM-DD HH:MM", "YYYY/MM/DD HH:MM", '
                            '"YYYY-MM-DD HH:MM:SS", "YYYY/MM/DD HH:MM:SS" (required for --cloud-log and --direct-download)')
    parser.add_argument('--log-type', default='log_HUF_Klog',
                       help='Log type for direct download (default: log_HUF_Klog). Common types: log_HUF_Klog, log_HUR_Klog, log_HUF_kernel, log_HUF_8155_android, etc.')
    parser.add_argument('--time-range', type=int, default=60,
                       help='Time range in minutes to search for logs around happen-time (default: 60, meaning ±60 minutes)')
    parser.add_argument('--env', choices=['prod', 'testtwo', 'ontest'], default='prod',
                       help='Environment for cloud log download (default: prod). Options: prod, testtwo, ontest')
    parser.add_argument('--task-type', default='1731484362257596488',
                       help='Task type (Flow ID) for cloud log download (default: 1731484362257596488)')
    parser.add_argument('--poll-interval', type=int, default=30,
                       help='Polling interval in seconds for cloud log status (default: 30)')
    
    # Common arguments
    parser.add_argument('--server', default='https://issuefinder-playground-init-dev.inner.chj.cloud',
                       help='Server URL (default: https://issuefinder-playground-init-dev.inner.chj.cloud)')
    parser.add_argument('--output', default='./results',
                       help='Output directory for downloaded files (default: ./results)')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout for tool execution in seconds (default: 300)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--keep-env', action='store_true',
                       help='Keep the cloud environment after download (default: auto-cleanup)')
    parser.add_argument('--skip-version-check', action='store_true',
                       help='Skip version check and update')
    
    args = parser.parse_args()
    
    # Check and update version before processing
    check_and_update_version(args.server, args.skip_version_check, args.verbose)
    
    # Validate mutually exclusive modes
    if sum([args.cloud_log, args.issuefinder, args.direct_download]) > 1:
        print_status("Cannot specify multiple modes: --cloud-log, --issuefinder, or --direct-download", "ERROR")
        print_status("Use one of: --cloud-log (custom task), --issuefinder (automatic analysis), or --direct-download (direct cloud download)", "INFO")
        return 1
    
    # Validate arguments based on mode
    if args.cloud_log or args.issuefinder:
        if not args.vin or not args.happen_time:
            mode_name = "IssueFinder" if args.issuefinder else "Cloud log"
            print_status(f"{mode_name} mode requires --vin and --happen-time parameters", "ERROR")
            return 1
        # Set the task type automatically for IssueFinder mode
        if args.issuefinder:
            args.task_type = '1731484362257596488'
    elif args.direct_download:
        if not args.vin or not args.happen_time:
            print_status("Direct download mode requires --vin and --happen-time parameters", "ERROR")
            return 1
    else:
        if not args.upload:
            print_status("Local processing mode requires -u/--upload parameter", "ERROR")
            return 1
    
    # Initialize client
    client = IssuefinderClient(args.server)
    env_id = None
    result = None
    mode = None
    output_subdir = None
    temp_dirs_to_cleanup = []
    
    try:
        # Step 1: Create environment
        print_status(f"Connecting to server: {args.server}")
        env_response = client.create_environment()
        env_id = env_response['environment_id']
        print_status(f"Created environment: {env_id}", "SUCCESS")
        
        # Step 2: Execute mode-specific logic
        if args.cloud_log or args.issuefinder:
            mode = 'cloud_log'
            result = run_cloud_log_mode(client, env_id, args)
            output_subdir = None  # Use default output directory
        elif args.direct_download:
            mode = 'direct_download'
            result = run_direct_download_mode(client, env_id, args)
            output_subdir = f"VIN_{args.vin}"
        else:
            mode = 'local_processing'
            result = run_local_processing_mode(client, env_id, args)
            # Store temp dirs for cleanup
            temp_dirs_to_cleanup = result.get('temp_dirs', [])
            # Check if this was a local extraction only
            if result.get('local_extraction'):
                print_status("Local extraction completed, skipping cloud processing", "INFO")
                return 0
            # Use input file basename as subdirectory
            output_subdir = os.path.basename(result['input_file'])
        
        # Step 3: Download files from environment
        output_dir, downloaded_files = download_files_from_env(
            client, env_id, args.output, output_subdir, args.verbose
        )
        
        # Step 4: Print summary
        print_summary(mode, result, output_dir, downloaded_files, args)
        
        return 0
        
    except KeyboardInterrupt:
        print_status("\nOperation cancelled by user", "WARNING")
        return 1
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    finally:
        # Clean up temporary directories
        for temp_dir in temp_dirs_to_cleanup:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if args.verbose:
                        print_status(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                if args.verbose:
                    print_status(f"Failed to cleanup temp directory {temp_dir}: {e}", "WARNING")
        
        # Cleanup environment unless --keep-env is specified
        if env_id and not args.keep_env:
            try:
                print_status("Cleaning up cloud environment...")
                client.delete_environment(env_id)
                print_status("Environment cleanup completed", "SUCCESS")
            except Exception as e:
                print_status(f"Environment cleanup failed: {e}", "WARNING")
                print_status("Environment will be auto-cleaned after 1 hour of inactivity", "INFO")


if __name__ == "__main__":
    # Check if there's a newer version in ~/.issuefinder/
    home_dir = os.path.expanduser("~")
    updated_tool = os.path.join(home_dir, ".issuefinder", "issuefinder-tool.py")
    current_script = os.path.abspath(__file__)
    
    # If we're not already running from ~/.issuefinder/ and the updated version exists
    if updated_tool != current_script and os.path.exists(updated_tool):
        # Check if updated version is newer by comparing file modification time
        # or if it's different from current script
        try:
            # Re-execute with the updated version
            os.execv(sys.executable, [sys.executable, updated_tool] + sys.argv[1:])
        except Exception:
            pass  # If re-execution fails, continue with current version
    
    sys.exit(main())
