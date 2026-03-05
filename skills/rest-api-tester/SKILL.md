---
name: api-tester
description: Test REST APIs with customizable headers, authentication, and request bodies. Use when debugging API endpoints, testing authentication flows, validating responses, or automating API checks. Supports GET, POST, PUT, DELETE, PATCH methods with JSON, form-data, and raw body formats. Ideal for developers testing webhooks, microservices, and third-party integrations.
---

# API Tester

Test REST APIs with custom headers, auth, and request bodies.

## When to Use

- Debugging API endpoints during development
- Testing authentication flows
- Validating webhook payloads
- Checking API response times
- Automating health checks
- Testing third-party integrations

## Quick Start

### Simple GET Request

```python
import requests

def test_get(url, headers=None):
    """Test a GET endpoint"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        return {
            'status': response.status_code,
            'headers': dict(response.headers),
            'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'time': response.elapsed.total_seconds()
        }
    except Exception as e:
        return {'error': str(e)}

# Usage
test_get('https://api.github.com/users/octocat')
```

### POST with JSON Body

```python
def test_post(url, data, headers=None):
    """Test POST endpoint with JSON body"""
    default_headers = {'Content-Type': 'application/json'}
    if headers:
        default_headers.update(headers)
    
    try:
        response = requests.post(
            url, 
            json=data, 
            headers=default_headers,
            timeout=30
        )
        return {
            'status': response.status_code,
            'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {'error': str(e)}

# Usage
test_post('https://httpbin.org/post', {'key': 'value'})
```

### Test with Authentication

```python
def test_with_auth(url, token=None, username=None, password=None):
    """Test API with Bearer token or Basic auth"""
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    elif username and password:
        import base64
        credentials = base64.b64encode(f'{username}:{password}'.encode()).decode()
        headers['Authorization'] = f'Basic {credentials}'
    
    return test_get(url, headers)

# Bearer token
test_with_auth('https://api.example.com/data', token='your_token_here')

# Basic auth
test_with_auth('https://api.example.com/data', username='admin', password='secret')
```

### Full API Test Suite

```python
def comprehensive_api_test(base_url, endpoints):
    """Test multiple endpoints"""
    results = {}
    
    for endpoint, config in endpoints.items():
        url = f"{base_url}{config['path']}"
        method = config.get('method', 'GET')
        headers = config.get('headers', {})
        data = config.get('data')
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            results[endpoint] = {
                'status': response.status_code,
                'success': 200 <= response.status_code < 300,
                'time': response.elapsed.total_seconds()
            }
        except Exception as e:
            results[endpoint] = {'error': str(e), 'success': False}
    
    return results

# Usage
endpoints = {
    'health': {'path': '/health', 'method': 'GET'},
    'create_user': {'path': '/users', 'method': 'POST', 'data': {'name': 'Test'}},
    'get_user': {'path': '/users/1', 'method': 'GET'}
}

comprehensive_api_test('https://api.example.com', endpoints)
```

## Common Testing Scenarios

### Webhook Testing

```python
from flask import Flask, request

def create_webhook_listener(port=5000):
    """Create local webhook receiver for testing"""
    app = Flask(__name__)
    received_data = []
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        data = request.json
        received_data.append(data)
        print(f"Received webhook: {data}")
        return {'status': 'ok'}
    
    @app.route('/received', methods=['GET'])
    def get_received():
        return {'data': received_data}
    
    return app

# Run: app.run(port=5000)
# Use ngrok to expose: ngrok http 5000
```

### Performance Testing

```python
import time

def test_api_performance(url, iterations=10):
    """Test API response times"""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        requests.get(url, timeout=30)
        times.append(time.time() - start)
    
    return {
        'min': min(times),
        'max': max(times),
        'avg': sum(times) / len(times),
        'times': times
    }
```

## Response Validation

```python
def validate_response(response, expected_status=200, required_fields=None):
    """Validate API response structure"""
    errors = []
    
    if response.get('status') != expected_status:
        errors.append(f"Expected status {expected_status}, got {response.get('status')}")
    
    body = response.get('body', {})
    if required_fields:
        for field in required_fields:
            if field not in body:
                errors.append(f"Missing required field: {field}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
```

## Dependencies

```bash
pip install requests flask
```
