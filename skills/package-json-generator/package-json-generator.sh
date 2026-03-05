#!/bin/bash
NAME="${1:-my-project}"
VERSION="${2:-1.0.0}"

cat > package.json << JSON
{
  "name": "$NAME",
  "version": "$VERSION",
  "description": "",
  "main": "index.js",
  "scripts": {
    "dev": "node index.js",
    "start": "node index.js",
    "test": "echo \"Error: no test specified\" && exit 1",
    "lint": "eslint .",
    "build": "echo \"No build step\""
  },
  "keywords": [],
  "author": "",
  "license": "MIT"
}
JSON

echo "✅ package.json generated!"
