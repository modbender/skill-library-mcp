# Docker Container Cleaner

A command-line tool to clean up Docker resources (containers, images, volumes, networks) to free up disk space.

## Installation

This skill requires:
- Python 3.x
- **Docker**: Must be installed and the Docker daemon must be running
- **Docker CLI**: Must be available in PATH (`docker` command)

Optional but recommended:
```bash
pip install docker
```

The Docker SDK for Python provides better performance and more reliable operations than shelling out to the `docker` CLI.

## Quick Start

```bash
# Interactive cleanup (recommended for first use)
python3 scripts/main.py clean

# Show current Docker resource usage
python3 scripts/main.py status

# Remove stopped containers only
python3 scripts/main.py clean --containers

# Remove dangling images only
python3 scripts/main.py clean --images --dangling

# Force cleanup of everything (no confirmation)
python3 scripts/main.py clean --all --force

# Dry run (show what would be removed)
python3 scripts/main.py clean --all --dry-run
```

## Command Reference

### `status` command
Show current Docker resource usage.

```
python3 scripts/main.py status [OPTIONS]
```

Options:
- `--format`: Output format: `table` (human-readable) or `json`. Default: `table`
- `--verbose`: Show detailed information

### `clean` command
Clean up Docker resources.

```
python3 scripts/main.py clean [OPTIONS]
```

Options:
- `--containers`: Remove stopped containers
- `--images`: Remove images (requires --dangling or --unused)
- `--dangling`: Remove dangling images (images with no tag)
- `--unused`: Remove unused images (not used by any container)
- `--volumes`: Remove unused volumes
- `--networks`: Remove unused networks
- `--all`: Clean all resource types (equivalent to --containers --images --volumes --networks)
- `--force`: Skip confirmation prompts
- `--dry-run`: Show what would be removed without actually removing
- `--yes`: Auto-answer "yes" to all prompts
- `--no-interactive`: Disable interactive mode (use with --yes for scripts)
- `--timeout`: Timeout in seconds for Docker operations. Default: 30

## Examples

### Basic Usage

```bash
# Check current Docker resource usage
python3 scripts/main.py status

# Interactive cleanup
python3 scripts/main.py clean

# Output:
# Docker Cleanup Tool
# ===================
# 
# Found resources:
# - Stopped containers: 3 (using 1.2GB)
# - Dangling images: 5 (using 850MB)
# - Unused images: 2 (using 450MB)
# - Unused volumes: 1 (using 100MB)
# - Unused networks: 0
# 
# Total disk space that can be freed: 2.6GB
# 
# What would you like to clean up?
# 1. Remove stopped containers
# 2. Remove dangling images
# 3. Remove unused images
# 4. Remove unused volumes
# 5. Remove unused networks
# 6. All of the above
# 7. Cancel
```

### Script Usage

```bash
# Remove stopped containers without prompting
python3 scripts/main.py clean --containers --force

# Remove dangling images and show what was removed
python3 scripts/main.py clean --images --dangling --yes

# JSON output for scripting
python3 scripts/main.py status --format json

# Dry run to see what would be removed
python3 scripts/main.py clean --all --dry-run
```

### Advanced Examples

```bash
# Clean up everything except volumes
python3 scripts/main.py clean --containers --images --networks --force

# Only clean images (both dangling and unused)
python3 scripts/main.py clean --images --dangling --unused --yes

# Clean with a timeout for slow Docker daemons
python3 scripts/main.py clean --all --timeout 60 --yes
```

## How It Works

1. **Resource Detection**: The tool uses the Docker API (via `docker` CLI or Docker SDK) to inspect current resources.

2. **Resource Types**:
   - **Stopped containers**: Containers that are not running
   - **Dangling images**: Images with no tag (usually intermediate build layers)
   - **Unused images**: Images not referenced by any container
   - **Unused volumes**: Volumes not mounted by any container
   - **Unused networks**: Networks not used by any container

3. **Safety Features**:
   - Interactive mode by default (asks for confirmation)
   - Dry run option to preview changes
   - Clear reporting of what will be removed
   - Size estimates for reclaimed space

4. **Cleanup Operations**:
   - Uses `docker container prune` for containers
   - Uses `docker image prune` for images
   - Uses `docker volume prune` for volumes
   - Uses `docker network prune` for networks

## Error Handling

.

If Docker is not running:
```
❌ Docker daemon is not running. Please start Docker and try again.
```

If permission denied:
```
❌ Permission denied. You may need to run with sudo or add your user to the docker group.
```

If timeout occurs:
```
❌ Operation timed out. Docker daemon may be busy. Try increasing timeout with --timeout.
```

If resource is in use:
```
❌ Cannot remove resource [name] because it is in use. Stop using containers first.
```

## Security Considerations

1. **Permission requirements**: Some operations may require `sudo` or membership in the `docker` group.

2. **Data loss**: Removing containers, images, or volumes can result in data loss. Always ensure you have backups.

3. **Production environments**: Use with caution in production. Consider:
   - Running during maintenance windows
   - Using `--dry-run` first
   - Setting up backups before cleanup
   - Testing in staging first

4. **Automation**: When automating in CI/CD:
   - Use `--dry-run` in pipelines
   - Set appropriate timeouts
   - Log all operations
   - Have rollback plans

## Limitations

- **Docker daemon required**: Must have access to running Docker daemon
- **Performance**: Large numbers of resources can slow down detection
- **Size calculations**: Approximate; actual freed space may vary
- **Build cache**: Does not clean Docker build cache (use `docker builder prune`)
- **Swarm mode**: Limited support for Docker Swarm resources
- **Windows containers**: Primarily tested with Linux containers

## Development

The tool is designed to be extensible. To add support for additional resource types:

1. Add detection logic in `detect_resources()`
2. Add cleanup function following the pattern `clean_<resource_type>()`
3. Add command-line argument parsing
4. Update documentation

## License

MIT