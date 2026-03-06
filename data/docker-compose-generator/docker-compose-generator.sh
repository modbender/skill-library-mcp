#!/bin/bash
SERVICES="${1:-mysql redis}"
OUTPUT="${2:-docker-compose.yml}"

cat > "$OUTPUT" << 'YML'
version: '3.8'

services:
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: app
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
YML

echo "✅ Docker Compose generated: $OUTPUT"
