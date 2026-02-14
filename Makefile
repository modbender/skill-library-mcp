.PHONY: test build ci dev clean mcp-test

test:        ## Run vitest
	pnpm test

build:       ## Build with tsup
	pnpm build

ci: test build  ## Run CI locally (test + build)

dev:         ## Run MCP server locally via tsx
	pnpm dev

clean:       ## Remove dist/ node_modules/ coverage/
	rm -rf dist/ node_modules/ coverage/

mcp-test: build  ## Build and test MCP server with initialize request
	@echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | node dist/index.js 2>/dev/null
