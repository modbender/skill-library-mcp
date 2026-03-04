# OpenClaw+ Capability Reference

Complete reference for all OpenClaw+ capabilities with detailed specifications.

## Table of Contents

1. [Python Execution](#python-execution)
2. [Package Management](#package-management)
3. [Git Operations](#git-operations)
4. [URL Fetching](#url-fetching)
5. [API Calls](#api-calls)

---

## Python Execution

### `run_python(code: str) -> Dict`

Execute Python code and capture output.

**Parameters:**
- `code` (str): Python code to execute

**Returns:**
```python
{
    'stdout': str,      # Standard output
    'stderr': str,      # Standard error
    'returncode': int,  # Exit code (0 = success)
    'success': bool     # Whether execution succeeded
}
```

**Example:**
```python
result = run_python("""
import math
print(f"Pi is approximately {math.pi:.2f}")
""")

if result['success']:
    print(result['stdout'])  # "Pi is approximately 3.14"
else:
    print(f"Error: {result['stderr']}")
```

**Features:**
- Multi-line code support
- Exception handling
- Timeout protection (30s)
- Access to installed packages
- Environment variable access

**Limitations:**
- No interactive input
- Limited to 30 second execution
- Runs in subprocess (no shared state)

**Error Handling:**
```python
try:
    result = run_python("invalid syntax here")
    if not result['success']:
        print(f"Execution failed: {result['stderr']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Package Management

### `install_package(package: str, system: bool = False) -> Dict`

Install Python or system packages.

**Parameters:**
- `package` (str): Package name or requirement specification
- `system` (bool): Whether to install system package (default: False)

**Returns:**
```python
{
    'success': bool,  # Whether installation succeeded
    'output': str,    # Installation output
    'error': str      # Error message if failed
}
```

**Examples:**

Simple package:
```python
result = install_package("pandas")
```

Specific version:
```python
result = install_package("numpy==1.24.0")
```

Multiple packages:
```python
result = install_package("requests beautifulsoup4 lxml")
```

From requirements file:
```python
result = install_package("-r requirements.txt")
```

System package:
```python
result = install_package("libpq-dev", system=True)
```

**Implementation Details:**
```bash
# Python packages
pip install <package> --break-system-packages

# System packages (Ubuntu/Debian)
sudo apt-get install -y <package>
```

**Features:**
- Dependency resolution
- Version pinning
- Requirements file support
- System package installation
- Progress feedback

**Limitations:**
- Requires internet connectivity
- System packages need sudo access
- Some packages require system dependencies
- Timeout after 120 seconds

**Best Practices:**
```python
# Check if already installed
if not package_installed("pandas"):
    install_package("pandas")

# Handle installation errors
result = install_package("my-package")
if not result['success']:
    print(f"Installation failed: {result['error']}")
    # Fallback or alternative approach
```

---

## Git Operations

### `git_status(path: str = '.') -> Dict`

Check git repository status.

**Parameters:**
- `path` (str): Path to git repository (default: current directory)

**Returns:**
```python
{
    'success': bool,           # Whether operation succeeded
    'status': str,             # Raw git status output
    'modified': List[str],     # List of modified files
    'untracked': List[str],    # List of untracked files
    'branch': str,             # Current branch name
    'clean': bool,             # Whether working directory is clean
    'error': str               # Error message if failed (optional)
}
```

**Example:**
```python
status = git_status()

if status['success']:
    print(f"Branch: {status['branch']}")
    
    if status['clean']:
        print("Working directory is clean")
    else:
        print(f"Modified files: {', '.join(status['modified'])}")
        print(f"Untracked files: {', '.join(status['untracked'])}")
else:
    print(f"Error: {status['error']}")
```

**Features:**
- Parse status output
- Identify file states
- Show current branch
- Detect clean/dirty state
- Custom repository path

**Limitations:**
- Requires git repository
- Only works with local repos
- No remote status

**Use Cases:**
```python
# Before committing
status = git_status()
if not status['clean']:
    # Files to commit
    files_to_commit = status['modified'] + status['untracked']
    
# Check specific directory
status = git_status("/path/to/repo")
```

---

### `git_commit(message: str, path: str = '.', stage_all: bool = False, files: List[str] = None) -> Dict`

Commit changes to git repository.

**Parameters:**
- `message` (str): Commit message
- `path` (str): Path to git repository (default: current directory)
- `stage_all` (bool): Stage all changes before committing (default: False)
- `files` (List[str]): Specific files to stage (optional)

**Returns:**
```python
{
    'success': bool,       # Whether commit succeeded
    'commit_hash': str,    # SHA of the commit
    'output': str,         # Git output
    'error': str           # Error message if failed (optional)
}
```

**Examples:**

Simple commit:
```python
result = git_commit("Add new feature")
```

Conventional commit:
```python
result = git_commit("feat: add user authentication")
```

Multi-line commit:
```python
result = git_commit("""
feat: add data processing pipeline

- Implement CSV reader
- Add data validation
- Create output formatter
""")
```

Stage all and commit:
```python
result = git_commit("fix: resolve bug", stage_all=True)
```

Commit specific files:
```python
result = git_commit("docs: update README", files=["README.md", "CHANGELOG.md"])
```

**Commit Message Format:**

Follow conventional commit format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Features:**
- Automatic staging
- Selective file staging
- Multi-line messages
- Commit hash capture
- Conventional commit support

**Limitations:**
- Requires git repository
- Must have changes to commit
- No interactive commits

**Best Practices:**
```python
# Always check status first
status = git_status()
if not status['clean']:
    result = git_commit(
        "feat: add new feature",
        stage_all=True
    )
    
    if result['success']:
        print(f"Committed: {result['commit_hash'][:7]}")
```

---

## URL Fetching

### `fetch_url(url: str, timeout: int = 30, headers: Dict[str, str] = None) -> Dict`

Fetch content from a URL.

**Parameters:**
- `url` (str): URL to fetch
- `timeout` (int): Request timeout in seconds (default: 30)
- `headers` (Dict[str, str]): Optional HTTP headers

**Returns:**
```python
{
    'success': bool,          # Whether fetch succeeded
    'content': str,           # Response content
    'status_code': int,       # HTTP status code
    'headers': Dict[str, str],# Response headers
    'error': str              # Error message if failed (optional)
}
```

**Examples:**

Simple fetch:
```python
result = fetch_url("https://example.com")
if result['success']:
    print(result['content'])
```

With custom headers:
```python
result = fetch_url(
    "https://api.example.com/data",
    headers={
        "User-Agent": "OpenClaw+/1.0",
        "Accept": "application/json"
    }
)
```

With timeout:
```python
result = fetch_url("https://slow-site.com", timeout=60)
```

Parse HTML:
```python
result = fetch_url("https://example.com")
if result['success']:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(result['content'], 'html.parser')
    title = soup.find('title').text
```

**Features:**
- HTTP/HTTPS support
- Custom headers
- Timeout control
- Response header access
- Redirect following
- SSL verification

**Limitations:**
- Text content only (no binary)
- No POST/PUT/DELETE (use call_api)
- No authentication (use call_api)
- Single request (no retries built-in)

**Error Handling:**
```python
result = fetch_url("https://example.com")

if not result['success']:
    if 'timeout' in result['error'].lower():
        print("Request timed out")
    elif 'status_code' in result:
        print(f"HTTP error: {result['status_code']}")
    else:
        print(f"Network error: {result['error']}")
```

**Use Cases:**
```python
# Fetch and parse JSON
result = fetch_url("https://api.example.com/data.json")
if result['success']:
    import json
    data = json.loads(result['content'])

# Fetch HTML and extract data
result = fetch_url("https://news.example.com")
if result['success']:
    # Parse and extract headlines
    pass

# Download text file
result = fetch_url("https://example.com/data.csv")
if result['success']:
    with open('data.csv', 'w') as f:
        f.write(result['content'])
```

---

## API Calls

### `call_api(url: str, method: str = 'GET', json_data: Dict = None, headers: Dict[str, str] = None, auth_token: str = None, timeout: int = 30) -> Dict`

Make API requests with authentication and parsing.

**Parameters:**
- `url` (str): API endpoint URL
- `method` (str): HTTP method (default: 'GET')
- `json_data` (Dict): JSON data to send (optional)
- `headers` (Dict[str, str]): Optional HTTP headers
- `auth_token` (str): Optional Bearer token
- `timeout` (int): Request timeout in seconds (default: 30)

**Returns:**
```python
{
    'success': bool,          # Whether request succeeded
    'data': Any,              # Parsed response (JSON or text)
    'status_code': int,       # HTTP status code
    'headers': Dict[str, str],# Response headers
    'error': str              # Error message if failed (optional)
}
```

**Examples:**

Simple GET:
```python
result = call_api("https://api.example.com/users")
if result['success']:
    users = result['data']
    print(f"Found {len(users)} users")
```

With authentication:
```python
result = call_api(
    "https://api.example.com/protected",
    auth_token="your-api-token-here"
)
```

POST request:
```python
result = call_api(
    "https://api.example.com/users",
    method="POST",
    json_data={
        "name": "John Doe",
        "email": "john@example.com"
    }
)
```

PUT request:
```python
result = call_api(
    "https://api.example.com/users/123",
    method="PUT",
    json_data={"name": "Jane Doe"}
)
```

DELETE request:
```python
result = call_api(
    "https://api.example.com/users/123",
    method="DELETE"
)
```

Custom headers:
```python
result = call_api(
    "https://api.example.com/data",
    headers={
        "X-API-Key": "your-api-key",
        "X-Custom-Header": "value"
    }
)
```

GraphQL query:
```python
result = call_api(
    "https://api.example.com/graphql",
    method="POST",
    json_data={
        "query": """
        query {
            users {
                id
                name
                email
            }
        }
        """
    }
)
```

**Features:**
- Multiple HTTP methods
- JSON request/response
- Bearer token authentication
- Custom headers
- Automatic JSON parsing
- Timeout control

**Limitations:**
- No file upload support
- No OAuth flow
- No retry logic (implement manually)
- No rate limit handling (implement manually)

**Authentication Patterns:**

Bearer token:
```python
result = call_api(url, auth_token="token")
```

API key in header:
```python
result = call_api(
    url,
    headers={"X-API-Key": "key"}
)
```

Basic auth:
```python
import base64
auth = base64.b64encode(b"user:pass").decode()
result = call_api(
    url,
    headers={"Authorization": f"Basic {auth}"}
)
```

**Error Handling:**
```python
result = call_api("https://api.example.com/endpoint")

if not result['success']:
    if result.get('status_code') == 401:
        print("Authentication failed")
    elif result.get('status_code') == 429:
        print("Rate limit exceeded")
    elif 'timeout' in result['error'].lower():
        print("Request timed out")
    else:
        print(f"API error: {result['error']}")
```

**Pagination Example:**
```python
all_data = []
page = 1

while True:
    result = call_api(f"https://api.example.com/data?page={page}")
    
    if not result['success']:
        break
    
    data = result['data']
    if not data:
        break
    
    all_data.extend(data)
    page += 1

print(f"Fetched {len(all_data)} total records")
```

**Rate Limiting Example:**
```python
import time

def call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        result = call_api(url)
        
        if result['success']:
            return result
        
        if result.get('status_code') == 429:
            # Rate limited, wait and retry
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            # Other error, don't retry
            return result
    
    return {'success': False, 'error': 'Max retries exceeded'}
```

---

## Common Patterns

### Pattern: Check Package → Install → Use

```python
# 1. Check if installed
if not package_installed("requests"):
    # 2. Install if needed
    result = install_package("requests")
    if not result['success']:
        print(f"Installation failed: {result['error']}")
        return

# 3. Use the package
result = call_api("https://api.example.com/data")
```

### Pattern: Fetch → Process → Save → Commit

```python
# 1. Fetch data
result = call_api("https://api.example.com/data")
if not result['success']:
    print(f"Fetch failed: {result['error']}")
    return

# 2. Process with Python
process_result = run_python("""
import json

with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Process data
processed = [item for item in data if item['active']]

with open('processed_data.json', 'w') as f:
    json.dump(processed, f, indent=2)
""")

# 3. Check status
status = git_status()

# 4. Commit if changes
if not status['clean']:
    git_commit("chore: update processed data")
```

### Pattern: Error Recovery

```python
# Try primary method
result = fetch_url("https://primary-api.com/data")

if not result['success']:
    # Fallback to secondary
    result = fetch_url("https://secondary-api.com/data")
    
    if not result['success']:
        # Final fallback
        print("Both APIs failed, using cached data")
        with open('cached_data.json') as f:
            data = json.load(f)
```

---

## Performance Tips

1. **Package Installation**: Check if already installed before installing
2. **API Calls**: Use appropriate timeouts, implement retries for transient failures
3. **Python Execution**: For large operations, write to file first, then execute
4. **Git Operations**: Check status before committing to avoid unnecessary operations
5. **URL Fetching**: Set reasonable timeouts, handle large responses in chunks

---

## Security Guidelines

1. **Never hardcode credentials** - Use environment variables or secure storage
2. **Validate URLs** - Check URL format before fetching
3. **Handle errors gracefully** - Don't expose sensitive information in error messages
4. **Use HTTPS** - Prefer secure connections when available
5. **Sanitize inputs** - Validate user inputs before passing to system commands
