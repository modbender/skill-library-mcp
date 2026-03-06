# API Endpoint Tester

A command-line tool for testing REST API endpoints with various HTTP methods, headers, and payloads.

## Installation

This skill requires Python 3.x and the `requests` library.

```bash
pip install requests
```

## Quick Start

```bash
# Basic GET request
python3 scripts/main.py run --url "https://jsonplaceholder.typicode.com/posts/1" --method GET

# POST with JSON body
python3 scripts/main.py run --url "https://jsonplaceholder.typicode.com/posts" --method POST --body '{"title": "test", "body": "content"}'

# With custom headers
python3 scripts/main.py run --url "https://api.example.com/data" --method GET --headers '{"Authorization": "Bearer token123", "User-Agent": "MyApp"}'
```

## Command Reference

```
python3 scripts/main.py run [OPTIONS]
```

Options:
- `--url`: Target URL (required)
- `--method`: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS). Default: GET
- `--headers`: JSON string of headers. Default: {}
- `--body`: Request body (JSON or form data). Default: null
- `--timeout`: Request timeout in seconds. Default: 10
- `--expected-status`: Expected HTTP status code. If provided, will check against actual status.
- `--verify-ssl`: Verify SSL certificates. Default: true
- `--allow-redirects`: Follow redirects. Default: true
- `--output-file`: Save response to file (optional)

## Response Format

The tool returns a JSON object with the following structure:

```json
{
  "status": "success" | "error",
  "error_message": "Description if status is error",
  "status_code": 200,
  "headers": {},
  "body": {},
  "response_time_ms": 123,
  "url": "https://example.com",
  "method": "GET"
}
```

## Examples

### Basic GET Request

```bash
python3 scripts/main.py run --url "https://jsonplaceholder.typicode.com/posts/1"
```

### POST with JSON Body

```bash
python3 scripts/main.py run \
  --url "https://jsonplaceholder.typicode.com/posts" \
  --method POST \
  --body '{"title": "My Post", "body": "Content here", "userId": 1}' \
  --headers '{"Content-Type": "application/json"}'
```

### DELETE Request with Authentication

```bash
python3 scripts/main.py run \
  --url "https://api.example.com/users/123" \
  --method DELETE \
  --headers '{"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"}'
```

### Validate Status Code

```bash
python3 scripts/main.py run \
  --url "https://httpbin.org/status/404" \
  --expected-status 404
```

If the actual status code doesn't match the expected, the tool returns an error.

## Error Handling

- Invalid URLs: Returns error with message
- Connection errors: Returns error with details
- Timeouts: Returns error after specified timeout
- Invalid JSON in body/headers: Returns parse error
- SSL verification failures: Returns error

## Use Cases

1. **API Development**: Quickly test endpoints during development
2. **Monitoring**: Check if APIs are responding correctly
3. **Debugging**: Inspect response headers and bodies
4. **Integration Testing**: Validate API contracts in scripts
5. **Documentation Examples**: Generate example requests/responses

## Limitations

- Does not support WebSocket or streaming endpoints
- Limited to HTTP/HTTPS protocols
- No built-in authentication beyond headers (Basic Auth via headers)
- No cookie jar or session persistence
- Single request at a time (no batch processing)
- Response size limited by memory

## License

MIT