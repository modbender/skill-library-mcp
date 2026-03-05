#!/bin/bash
LANG="${1:-node}"

cat > Makefile << 'MK'
.PHONY: install test build clean dev

install:
	npm install

test:
	npm test

build:
	npm run build

dev:
	npm run dev

clean:
	rm -rf node_modules dist
MK

echo "✅ Makefile generated!"
