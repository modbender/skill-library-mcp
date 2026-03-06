# Changelog

## 1.0.0 (2025-01-18)

### Features
- Initial release of agent-weave
- Master-Worker agent cluster architecture
- Parallel task execution with MapReduce support
- CLI tool for agent management
- Thread-based secure communication
- Partition strategies (round-robin, hash, range)

### Technical Details
- CommonJS compatible (Node.js >= 18)
- Event-driven architecture
- TypeScript-friendly (type definitions planned)

### Known Issues
- ESM-only dependencies require CommonJS versions (chalk@4, ora@5)
