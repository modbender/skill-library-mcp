---
name: openclaw-plus
description: A modular super-skill combining developer and web capabilities. Use when the user needs Python execution, package management, git operations, URL fetching, or API interactions. Triggers include requests to run code, install packages, check git status, commit changes, fetch web content, or call APIs. This skill provides a unified workflow for development and web automation tasks.
license: Complete terms in LICENSE.txt
---

# OpenClaw+ 🚀

A modular super-skill that combines essential developer tools and web capabilities into a unified, powerful workflow.

## Overview

OpenClaw+ integrates seven core capabilities into one streamlined skill:

**Developer Skills:**
- `run_python` - Execute Python code with proper environment management
- `git_status` - Check repository status and track changes
- `git_commit` - Commit changes with meaningful messages
- `install_package` - Install Python packages with dependency handling

**Web Skills:**
- `fetch_url` - Retrieve web content with robust error handling
- `call_api` - Make API requests with authentication and response parsing

This modular design allows you to chain operations efficiently - install packages, run code, fetch data, commit results - all in one cohesive workflow.

---

## When to Use OpenClaw+

Use this skill when the user's request involves:

- Running Python scripts or code snippets
- Installing Python packages (pip, conda, system packages)
- Checking git repository status
- Committing code changes
- Fetching content from URLs
- Making API calls (REST, GraphQL, etc.)
- Combining any of the above in a workflow

**Common patterns:**
- "Install pandas and run this analysis"
- "Fetch data from this API and save it"
- "Check git status and commit my changes"
- "Run this script and call this endpoint"
- "Install these packages, run the code, then commit"

---

## Core Capabilities

### 1. Python Execution (`run_python`)

Execute Python code with proper environment management and output capture.

**Key features:**
- Captures stdout, stderr, and return values
- Handles exceptions gracefully
- Supports multi-line scripts
- Access to installed packages
- Environment variable support

**Usage patterns:**
```python
# Simple execution
result = run_python("print('Hello, world!')")

# With installed packages
run_python("""
import pandas as pd
import numpy as np

data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(data.describe())
""")

# File operations
run_python("""
with open('output.txt', 'w') as f:
    f.write('Results: ...')
""")
```

**Best practices:**
- Always check for syntax errors before execution
- Handle file paths carefully (use absolute paths when needed)
- Capture exceptions and provide clear error messages
- For large scripts, consider creating a .py file first

---

### 2. Package Installation (`install_package`)

Install Python packages with intelligent dependency resolution.

**Key features:**
- Pip package installation
- System package support (apt, brew, etc.)
- Conda environment support
- Dependency conflict detection
- Version pinning

**Usage patterns:**
```bash
# Install single package
install_package("pandas")

# Install specific version
install_package("numpy==1.24.0")

# Install multiple packages
install_package("requests beautifulsoup4 lxml")

# Install from requirements.txt
install_package("-r requirements.txt")

# System packages (when needed)
install_package("libpq-dev", system=True)
```

**Best practices:**
- Always use `--break-system-packages` flag for pip in this environment
- Check if package is already installed before installing
- Handle version conflicts explicitly
- Provide clear feedback on installation success/failure

**Implementation:**
```bash
pip install <package> --break-system-packages
```

---

### 3. Git Status (`git_status`)

Check repository status and track changes.

**Key features:**
- Shows modified, added, deleted files
- Displays untracked files
- Shows current branch
- Indicates if ahead/behind remote
- Supports custom git directories

**Usage patterns:**
```bash
# Check current directory
git_status()

# Check specific directory
git_status("/path/to/repo")

# Parse output for automation
status = git_status()
if "modified:" in status:
    print("Changes detected")
```

**Best practices:**
- Always check status before committing
- Parse output to detect specific changes
- Handle cases where directory isn't a git repo
- Provide context about what changed

**Implementation:**
```bash
git status
git diff --stat
git log -1 --oneline
```

---

### 4. Git Commit (`git_commit`)

Commit changes with meaningful messages following best practices.

**Key features:**
- Conventional commit format support
- Multi-line commit messages
- Automatic staging option
- Commit message validation
- Amend support

**Usage patterns:**
```bash
# Simple commit
git_commit("Add new feature")

# Conventional commit
git_commit("feat: add user authentication")

# Multi-line with description
git_commit("""
feat: add data processing pipeline

- Implement CSV reader
- Add data validation
- Create output formatter
""")

# Stage and commit
git_commit("fix: resolve parsing error", stage_all=True)
```

**Best practices:**
- Use conventional commit format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Keep first line under 50 characters
- Add detailed description if needed
- Reference issue numbers when applicable

**Implementation:**
```bash
git add <files>  # if stage_all
git commit -m "<message>"
git log -1 --oneline  # confirm commit
```

---

### 5. URL Fetching (`fetch_url`)

Retrieve content from URLs with robust error handling.

**Key features:**
- HTTP/HTTPS support
- Custom headers
- Authentication support
- Redirect following
- Timeout handling
- Response parsing (JSON, XML, HTML, text)

**Usage patterns:**
```python
# Fetch HTML
html = fetch_url("https://example.com")

# Fetch JSON
data = fetch_url("https://api.example.com/data", 
                 parse_json=True)

# With authentication
content = fetch_url("https://api.example.com/protected",
                    headers={"Authorization": "Bearer TOKEN"})

# With custom timeout
content = fetch_url("https://slow-site.com", timeout=30)

# POST request
response = fetch_url("https://api.example.com/submit",
                     method="POST",
                     data={"key": "value"})
```

**Best practices:**
- Always handle network errors gracefully
- Set appropriate timeouts
- Validate URLs before fetching
- Parse response based on content type
- Handle rate limiting
- Respect robots.txt

**Implementation:**
```python
import requests

response = requests.get(url, headers=headers, timeout=timeout)
response.raise_for_status()
return response.text  # or response.json()
```

---

### 6. API Calls (`call_api`)

Make API requests with authentication and response parsing.

**Key features:**
- REST API support
- GraphQL support
- Authentication (Bearer, Basic, API Key)
- Request/response logging
- Error handling with retries
- Response validation

**Usage patterns:**
```python
# Simple GET request
data = call_api("https://api.example.com/users")

# With authentication
data = call_api("https://api.example.com/data",
                auth_token="your-token")

# POST with JSON body
result = call_api("https://api.example.com/create",
                  method="POST",
                  json_data={"name": "John", "age": 30})

# With custom headers
data = call_api("https://api.example.com/endpoint",
                headers={"X-Custom-Header": "value"})

# GraphQL query
result = call_api("https://api.example.com/graphql",
                  method="POST",
                  json_data={
                      "query": "{ users { id name } }"
                  })
```

**Best practices:**
- Validate API keys/tokens before use
- Handle rate limits with exponential backoff
- Parse response format (JSON, XML, etc.)
- Log requests for debugging
- Handle pagination for large datasets
- Validate response schemas
- Use appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH)

**Implementation:**
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.request(
    method=method,
    url=url,
    headers=headers,
    json=json_data,
    timeout=30
)
response.raise_for_status()
return response.json()
```

---

## Workflow Patterns

OpenClaw+ shines when combining multiple capabilities:

### Pattern 1: Data Pipeline
```python
# 1. Install dependencies
install_package("pandas requests")

# 2. Fetch data from API
data = call_api("https://api.example.com/dataset")

# 3. Process with Python
run_python("""
import pandas as pd
import json

with open('raw_data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df_cleaned = df.dropna()
df_cleaned.to_csv('cleaned_data.csv', index=False)
print(f'Processed {len(df_cleaned)} records')
""")

# 4. Commit results
git_commit("feat: add cleaned dataset")
```

### Pattern 2: Web Scraping & Analysis
```python
# 1. Install scraping tools
install_package("beautifulsoup4 lxml requests")

# 2. Fetch webpage
html = fetch_url("https://example.com/data-page")

# 3. Parse and analyze
run_python("""
from bs4 import BeautifulSoup
import json

with open('page.html', 'r') as f:
    soup = BeautifulSoup(f, 'lxml')

data = []
for item in soup.find_all('div', class_='data-item'):
    data.append({
        'title': item.find('h2').text,
        'value': item.find('span', class_='value').text
    })

with open('scraped_data.json', 'w') as f:
    json.dump(data, f, indent=2)
""")

# 4. Check and commit
git_status()
git_commit("chore: update scraped data")
```

### Pattern 3: API Integration Testing
```python
# 1. Install testing tools
install_package("pytest requests-mock")

# 2. Run tests
run_python("""
import requests
import json

# Test API endpoint
response = requests.get('https://api.example.com/health')
assert response.status_code == 200

# Test with authentication
headers = {'Authorization': 'Bearer test-token'}
response = requests.get('https://api.example.com/data', headers=headers)
print(f'Status: {response.status_code}')
print(f'Data: {response.json()}')
""")

# 3. Commit test results
git_commit("test: add API integration tests")
```

### Pattern 4: Automated Reporting
```python
# 1. Fetch data from multiple sources
api_data = call_api("https://api.example.com/metrics")
web_data = fetch_url("https://example.com/reports/latest")

# 2. Process and generate report
install_package("matplotlib pandas")
run_python("""
import pandas as pd
import matplotlib.pyplot as plt
import json

with open('api_data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['value'])
plt.title('Metrics Over Time')
plt.savefig('report.png')
print('Report generated')
""")

# 3. Commit report
git_commit("docs: add automated metrics report")
```

---

## Error Handling

Each capability includes robust error handling:

### Python Execution Errors
```python
try:
    result = run_python(code)
except SyntaxError as e:
    print(f"Syntax error: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
```

### Package Installation Errors
```bash
# Handle already installed
if package_installed("pandas"):
    print("Package already installed")
else:
    install_package("pandas")

# Handle installation failure
try:
    install_package("nonexistent-package")
except Exception as e:
    print(f"Installation failed: {e}")
```

### Git Operation Errors
```bash
# Not a git repository
if not is_git_repo():
    print("Not a git repository")
    exit(1)

# Nothing to commit
status = git_status()
if "nothing to commit" in status:
    print("No changes to commit")
```

### Network Errors
```python
# Handle timeouts
try:
    data = fetch_url(url, timeout=5)
except TimeoutError:
    print("Request timed out")

# Handle HTTP errors
try:
    response = call_api(url)
except requests.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
```

---

## Best Practices

### 1. **Environment Management**
- Always use `--break-system-packages` for pip
- Check if packages are installed before installing
- Use virtual environments when appropriate
- Document package versions

### 2. **Git Operations**
- Check status before committing
- Use meaningful commit messages
- Follow conventional commit format
- Stage only relevant files

### 3. **Code Execution**
- Validate syntax before running
- Handle exceptions gracefully
- Capture and log output
- Clean up temporary files

### 4. **API/Web Requests**
- Set appropriate timeouts
- Handle rate limiting
- Validate responses
- Log requests for debugging
- Respect API usage limits

### 5. **Workflow Composition**
- Chain operations logically
- Handle errors at each step
- Provide progress feedback
- Document dependencies

---

## Security Considerations

### API Keys & Credentials
- Never hardcode credentials
- Use environment variables
- Validate before use
- Rotate regularly

### Code Execution
- Validate input code
- Sandbox when possible
- Limit resource usage
- Monitor execution

### Web Requests
- Validate URLs
- Use HTTPS when possible
- Handle redirects carefully
- Respect robots.txt

---

## Debugging & Troubleshooting

### Common Issues

**Python execution fails:**
- Check syntax with `python -m py_compile script.py`
- Verify packages are installed
- Check file paths
- Review error messages

**Package installation fails:**
- Ensure pip is up to date
- Check internet connectivity
- Verify package name
- Review dependencies

**Git operations fail:**
- Verify it's a git repository
- Check file permissions
- Ensure clean working directory
- Review git configuration

**API/URL requests fail:**
- Verify URL is correct
- Check authentication
- Review rate limits
- Check network connectivity

---

## Examples

### Example 1: Complete Data Pipeline
```python
# User request: "Fetch weather data, analyze it, and commit results"

# Step 1: Install dependencies
install_package("requests pandas matplotlib")

# Step 2: Fetch data
weather_data = call_api(
    "https://api.weather.com/data",
    auth_token="your-api-key"
)

# Step 3: Save and analyze
run_python("""
import pandas as pd
import matplotlib.pyplot as plt
import json

# Load data
with open('weather_data.json', 'r') as f:
    data = json.load(f)

# Create DataFrame
df = pd.DataFrame(data['forecast'])
df['date'] = pd.to_datetime(df['date'])

# Analyze
avg_temp = df['temperature'].mean()
max_temp = df['temperature'].max()
min_temp = df['temperature'].min()

# Generate plot
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['temperature'], marker='o')
plt.title('Temperature Forecast')
plt.xlabel('Date')
plt.ylabel('Temperature (°F)')
plt.grid(True)
plt.savefig('temperature_forecast.png')

# Save summary
summary = {
    'avg_temp': avg_temp,
    'max_temp': max_temp,
    'min_temp': min_temp,
    'records': len(df)
}

with open('weather_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f'Analysis complete: {len(df)} records processed')
print(f'Average temperature: {avg_temp:.1f}°F')
""")

# Step 4: Commit results
git_status()
git_commit("""
feat: add weather data analysis

- Fetch 7-day forecast from API
- Generate temperature plot
- Create summary statistics
""")
```

### Example 2: Web Scraping & Storage
```python
# User request: "Scrape product data and save to database"

# Step 1: Install tools
install_package("beautifulsoup4 lxml requests sqlite3")

# Step 2: Fetch webpage
html = fetch_url("https://example-shop.com/products")

# Step 3: Parse and store
run_python("""
from bs4 import BeautifulSoup
import sqlite3
import json

# Parse HTML
with open('products.html', 'r') as f:
    soup = BeautifulSoup(f, 'lxml')

products = []
for item in soup.find_all('div', class_='product'):
    product = {
        'name': item.find('h3').text.strip(),
        'price': float(item.find('span', class_='price').text.strip('$')),
        'rating': float(item.find('span', class_='rating').text),
        'url': item.find('a')['href']
    }
    products.append(product)

# Store in SQLite
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        rating REAL,
        url TEXT
    )
''')

for p in products:
    cursor.execute('''
        INSERT INTO products (name, price, rating, url)
        VALUES (?, ?, ?, ?)
    ''', (p['name'], p['price'], p['rating'], p['url']))

conn.commit()
conn.close()

print(f'Scraped and stored {len(products)} products')
""")

# Step 4: Commit
git_commit("chore: update product database")
```

### Example 3: API Testing Suite
```python
# User request: "Test our API endpoints and generate report"

# Step 1: Install testing framework
install_package("pytest requests pytest-html")

# Step 2: Create test file and run
run_python("""
import requests
import json
from datetime import datetime

BASE_URL = "https://api.example.com"
results = []

# Test 1: Health check
try:
    response = requests.get(f"{BASE_URL}/health")
    results.append({
        'test': 'Health Check',
        'status': response.status_code,
        'passed': response.status_code == 200,
        'response_time': response.elapsed.total_seconds()
    })
except Exception as e:
    results.append({
        'test': 'Health Check',
        'status': 'Error',
        'passed': False,
        'error': str(e)
    })

# Test 2: Authentication
try:
    headers = {'Authorization': 'Bearer test-token'}
    response = requests.get(f"{BASE_URL}/auth/validate", headers=headers)
    results.append({
        'test': 'Authentication',
        'status': response.status_code,
        'passed': response.status_code == 200,
        'response_time': response.elapsed.total_seconds()
    })
except Exception as e:
    results.append({
        'test': 'Authentication',
        'status': 'Error',
        'passed': False,
        'error': str(e)
    })

# Test 3: Data retrieval
try:
    response = requests.get(f"{BASE_URL}/data/users")
    data = response.json()
    results.append({
        'test': 'Data Retrieval',
        'status': response.status_code,
        'passed': response.status_code == 200 and len(data) > 0,
        'records': len(data) if response.status_code == 200 else 0,
        'response_time': response.elapsed.total_seconds()
    })
except Exception as e:
    results.append({
        'test': 'Data Retrieval',
        'status': 'Error',
        'passed': False,
        'error': str(e)
    })

# Generate report
report = {
    'timestamp': datetime.now().isoformat(),
    'total_tests': len(results),
    'passed': sum(1 for r in results if r.get('passed')),
    'failed': sum(1 for r in results if not r.get('passed')),
    'results': results
}

with open('api_test_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"Tests complete: {report['passed']}/{report['total_tests']} passed")
for r in results:
    status = '✓' if r.get('passed') else '✗'
    print(f"{status} {r['test']}")
""")

# Step 3: Check and commit
git_status()
git_commit("test: add API endpoint tests")
```

---

## Integration with Other Skills

OpenClaw+ works seamlessly with other skills:

### With `docx` skill:
```python
# Generate data, then create report
call_api("https://api.example.com/stats")
run_python("process_stats.py")
# Then use docx skill to create formatted report
```

### With `xlsx` skill:
```python
# Fetch data, process with Python, export to Excel
fetch_url("https://data-source.com/raw.csv")
run_python("clean_and_transform.py")
# Then use xlsx skill to create formatted spreadsheet
```

### With `pptx` skill:
```python
# Generate charts and data visualizations
install_package("matplotlib seaborn")
run_python("generate_charts.py")
# Then use pptx skill to create presentation
```

---

## Quick Reference

### Python Execution
```python
run_python(code_string)
```

### Package Management
```bash
install_package("package_name")
install_package("package==1.0.0")
install_package("-r requirements.txt")
```

### Git Operations
```bash
git_status()
git_commit("message")
git_commit("message", stage_all=True)
```

### Web Requests
```python
fetch_url(url, timeout=30)
call_api(url, method="GET", auth_token="token")
```

---

## Conclusion

OpenClaw+ provides a unified, powerful toolkit for development and web automation workflows. By combining Python execution, package management, git operations, and web capabilities, it enables complex multi-step workflows with a single cohesive skill.

**Key strengths:**
- ✅ Modular design - use only what you need
- ✅ Error handling - robust failure recovery
- ✅ Workflow composition - chain operations easily
- ✅ Production-ready - follows best practices
- ✅ Well-documented - clear examples and patterns

Use OpenClaw+ whenever your task involves code execution, package management, version control, or web interactions - or any combination thereof!
