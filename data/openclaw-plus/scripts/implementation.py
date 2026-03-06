#!/usr/bin/env python3
"""
OpenClaw+ Implementation Examples

This script demonstrates how to implement each of the core capabilities
in OpenClaw+. These are reference implementations that Claude can use
when executing the skill.
"""

import subprocess
import sys
import os
import json
from typing import Optional, Dict, Any, List


class OpenClawPlus:
    """Main class implementing OpenClaw+ capabilities"""
    
    def __init__(self):
        self.verbose = True
    
    def log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[OpenClaw+] {message}")
    
    # ===== Python Execution =====
    
    def run_python(self, code: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute Python code and return results.
        
        Args:
            code: Python code to execute
            filename: Optional filename to save code to before execution
            
        Returns:
            Dict with 'stdout', 'stderr', 'returncode', and 'success' keys
        """
        self.log("Executing Python code...")
        
        if filename:
            # Save code to file
            with open(filename, 'w') as f:
                f.write(code)
            cmd = [sys.executable, filename]
        else:
            # Execute directly
            cmd = [sys.executable, '-c', code]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Execution timed out after 30 seconds',
                'returncode': -1,
                'success': False
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False
            }
    
    # ===== Package Management =====
    
    def install_package(self, package: str, system: bool = False) -> Dict[str, Any]:
        """
        Install a Python package using pip.
        
        Args:
            package: Package name or requirement specification
            system: Whether to install system package (apt/brew)
            
        Returns:
            Dict with 'success', 'output', and 'error' keys
        """
        if system:
            self.log(f"Installing system package: {package}")
            # Attempt apt-get for Debian/Ubuntu systems
            cmd = ['sudo', 'apt-get', 'install', '-y', package]
        else:
            self.log(f"Installing Python package: {package}")
            # Always use --break-system-packages in this environment
            cmd = [sys.executable, '-m', 'pip', 'install', 
                   package, '--break-system-packages']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Installation timed out after 120 seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def package_installed(self, package: str) -> bool:
        """Check if a Python package is installed"""
        cmd = [sys.executable, '-m', 'pip', 'show', package]
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    
    # ===== Git Operations =====
    
    def is_git_repo(self, path: str = '.') -> bool:
        """Check if directory is a git repository"""
        git_dir = os.path.join(path, '.git')
        return os.path.isdir(git_dir)
    
    def git_status(self, path: str = '.') -> Dict[str, Any]:
        """
        Get git repository status.
        
        Args:
            path: Path to git repository
            
        Returns:
            Dict with 'success', 'status', 'modified', 'untracked', 'branch' keys
        """
        self.log("Checking git status...")
        
        if not self.is_git_repo(path):
            return {
                'success': False,
                'error': 'Not a git repository'
            }
        
        try:
            # Get status
            result = subprocess.run(
                ['git', '-C', path, 'status', '--porcelain'],
                capture_output=True,
                text=True
            )
            
            # Get current branch
            branch_result = subprocess.run(
                ['git', '-C', path, 'branch', '--show-current'],
                capture_output=True,
                text=True
            )
            
            # Parse status output
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            modified = [l[3:] for l in lines if l.startswith(' M')]
            untracked = [l[3:] for l in lines if l.startswith('??')]
            
            return {
                'success': True,
                'status': result.stdout,
                'modified': modified,
                'untracked': untracked,
                'branch': branch_result.stdout.strip(),
                'clean': len(lines) == 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def git_commit(self, message: str, path: str = '.', 
                   stage_all: bool = False, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Commit changes to git repository.
        
        Args:
            message: Commit message
            path: Path to git repository
            stage_all: Whether to stage all changes
            files: Specific files to stage
            
        Returns:
            Dict with 'success', 'commit_hash', 'output' keys
        """
        self.log(f"Committing changes: {message[:50]}...")
        
        if not self.is_git_repo(path):
            return {
                'success': False,
                'error': 'Not a git repository'
            }
        
        try:
            # Stage files
            if stage_all:
                subprocess.run(['git', '-C', path, 'add', '-A'], check=True)
            elif files:
                for f in files:
                    subprocess.run(['git', '-C', path, 'add', f], check=True)
            
            # Commit
            result = subprocess.run(
                ['git', '-C', path, 'commit', '-m', message],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr or 'Commit failed'
                }
            
            # Get commit hash
            hash_result = subprocess.run(
                ['git', '-C', path, 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True
            )
            
            return {
                'success': True,
                'commit_hash': hash_result.stdout.strip(),
                'output': result.stdout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # ===== Web Operations =====
    
    def fetch_url(self, url: str, timeout: int = 30, 
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            headers: Optional HTTP headers
            
        Returns:
            Dict with 'success', 'content', 'status_code', 'error' keys
        """
        self.log(f"Fetching URL: {url}")
        
        try:
            import requests
        except ImportError:
            return {
                'success': False,
                'error': 'requests package not installed'
            }
        
        try:
            response = requests.get(
                url,
                headers=headers or {},
                timeout=timeout
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'content': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
        except requests.Timeout:
            return {
                'success': False,
                'error': f'Request timed out after {timeout} seconds'
            }
        except requests.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP error: {e.response.status_code}',
                'status_code': e.response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def call_api(self, url: str, method: str = 'GET', 
                 json_data: Optional[Dict] = None,
                 headers: Optional[Dict[str, str]] = None,
                 auth_token: Optional[str] = None,
                 timeout: int = 30) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            json_data: JSON data to send
            headers: Optional HTTP headers
            auth_token: Optional Bearer token
            timeout: Request timeout in seconds
            
        Returns:
            Dict with 'success', 'data', 'status_code', 'error' keys
        """
        self.log(f"Calling API: {method} {url}")
        
        try:
            import requests
        except ImportError:
            return {
                'success': False,
                'error': 'requests package not installed'
            }
        
        # Prepare headers
        req_headers = headers or {}
        if auth_token:
            req_headers['Authorization'] = f'Bearer {auth_token}'
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=req_headers,
                json=json_data,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                data = response.json()
            except ValueError:
                data = response.text
            
            return {
                'success': True,
                'data': data,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
        except requests.Timeout:
            return {
                'success': False,
                'error': f'Request timed out after {timeout} seconds'
            }
        except requests.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP error: {e.response.status_code}',
                'status_code': e.response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# ===== Example Usage =====

def example_workflow():
    """Example workflow demonstrating all capabilities"""
    
    oc = OpenClawPlus()
    
    print("=== OpenClaw+ Example Workflow ===\n")
    
    # 1. Install package
    print("1. Installing requests package...")
    result = oc.install_package("requests")
    if result['success']:
        print("   ✓ Package installed successfully")
    else:
        print(f"   ✗ Installation failed: {result['error']}")
    
    # 2. Fetch URL
    print("\n2. Fetching URL...")
    result = oc.fetch_url("https://httpbin.org/get")
    if result['success']:
        print(f"   ✓ Fetched {len(result['content'])} bytes")
    else:
        print(f"   ✗ Fetch failed: {result['error']}")
    
    # 3. Call API
    print("\n3. Calling API...")
    result = oc.call_api("https://jsonplaceholder.typicode.com/posts/1")
    if result['success']:
        print(f"   ✓ API returned data: {result['data'].get('title', 'N/A')[:50]}")
    else:
        print(f"   ✗ API call failed: {result['error']}")
    
    # 4. Run Python
    print("\n4. Running Python code...")
    code = """
import sys
print(f"Python {sys.version.split()[0]}")
print("Hello from OpenClaw+!")
    """
    result = oc.run_python(code)
    if result['success']:
        print(f"   ✓ Code executed:\n{result['stdout']}")
    else:
        print(f"   ✗ Execution failed: {result['stderr']}")
    
    # 5. Git status
    print("\n5. Checking git status...")
    result = oc.git_status()
    if result['success']:
        if result['clean']:
            print("   ✓ Working directory is clean")
        else:
            print(f"   ✓ {len(result['modified'])} modified, {len(result['untracked'])} untracked")
    else:
        print(f"   ℹ {result.get('error', 'Unknown error')}")
    
    print("\n=== Workflow Complete ===")


if __name__ == '__main__':
    example_workflow()
