# Changelog

## [0.2.0] - 2026-02-27

### Added
- **Multi-GPU host pool** (`hosts[]` config) with per-host names, URLs, and API keys
- **Load balancing**: `round-robin` and `least-busy` (VRAM-based) strategies
- **Automatic failover**: requests reroute to healthy hosts when one goes down
- **Periodic health checks** with configurable interval (`healthCheckIntervalSeconds`)
- **`gpu_status` tool**: new tool exposing queue depth, active jobs, and batch progress
- **On-demand model loading**: GPU service caches models in memory after first use
- **Request-level model override**: pass `model` / `model_type` per request
- **Embed batch progress logging**: large embedding jobs report chunk progress
- **503 Retry-After support**: honors `Retry-After` header on backpressure responses
- **Input size validation**: rejects oversized payloads before sending to GPU service
- **Integration test suite**: 10 tests using real HTTP servers for end-to-end validation

### Changed
- Default BERTScore model upgraded to `microsoft/deberta-xlarge-mnli`
- Default embed model upgraded to `all-MiniLM-L6-v2`
- Python GPU service refactored for model cache and status tracking

### Backward Compatibility
- v0.1 config (`serviceUrl` / `url` + single `apiKey`) still works unchanged
- All existing tools (`gpu_health`, `gpu_info`, `gpu_bertscore`, `gpu_embed`) retain the same interface

## [0.1.0] - 2026-02-22

### Added
- Initial release
- TypeScript OpenClaw plugin with 4 tools: `gpu_health`, `gpu_info`, `gpu_bertscore`, `gpu_embed`
- Python FastAPI GPU service with CUDA auto-detection
- BERTScore and sentence embedding endpoints
- X-API-Key authentication middleware
- Concurrency control via asyncio semaphore
- Request timeout handling with AbortController
