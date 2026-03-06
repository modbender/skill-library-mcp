#!/bin/bash
FORMAT="${1:-openapi}"
OUTPUT="${2:-docs/api.json}"

mkdir -p docs

cat > "$OUTPUT" << 'JSON'
{
  "openapi": "3.0.0",
  "info": {
    "title": "My API",
    "version": "1.0.0"
  },
  "paths": {
    "/users": {
      "get": {
        "summary": "Get all users",
        "responses": {
          "200": {
            "description": "OK"
          }
        }
      }
    }
  }
}
JSON

echo "✅ API docs generated at $OUTPUT"
