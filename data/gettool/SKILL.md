---
name: pywayne-bin-gettool
description: Fetch and install C++ tools/libraries from cpp_tools repository. Use when users need to download or clone third-party C++ libraries such as eigen, opencv, pcl, fmt. Use for building tools from source using CMake, installing tools with installation scripts, listing available tools, or managing cpp_tools repository URL. Triggered by requests to fetch, get, download, clone, or install C++ tools or libraries.
---

# Pywayne Bin Gettool

Tool fetcher for C++ libraries from cpp_tools repository. Supports sparse checkout, optional building with CMake/make, and installation scripts.

## Quick Start

```bash
# List all supported tools
gettool -l

# Fetch a tool to default path (based on name_to_path_map.yaml)
gettool <tool_name>

# Fetch to specific path
gettool <tool_name> -t <target_path>

# Fetch and build (if buildable)
gettool <tool_name> -b

# Fetch and install (if installable)
gettool <tool_name> -i
```

## Usage Patterns

### 1. List Available Tools

When user wants to see what tools are available:

```bash
gettool -l
```

### 2. Simple Fetch

Download tool source code to default path (determined by name_to_path_map.yaml in current directory):

```bash
gettool opencv
gettool eigen
```

### 3. Fetch with Custom Target

Download tool to a specific directory:

```bash
gettool opencv -t third_party/opencv
gettool eigen -t external/eigen
```

### 4. Build from Source

Build the tool using CMake and make. Requirements:
- Tool must be marked as `buildable: true` in name_to_path_map.yaml
- Tool must have a `CMakeLists.txt` file
- Build output (lib/) is copied to target directory

```bash
gettool apriltag_detection -b
gettool <tool_name> -b -t build/<tool_name>
```

### 5. Clean Copy (src + include only)

Fetch only `src/` and `include/` directories if they exist:

```bash
gettool eigen -c
```

### 6. Fetch and Install

After fetching, execute the tool's installation script (if configured):

```bash
gettool pcl -i
gettool pcl -i --global-install-flag true  # Use sudo make install
```

### 7. Fetch Specific Version

Check out a specific version/tag/branch (only works for tools that are submodules):

```bash
gettool fmt -v 9.1.0
```

### 8. Manage Repository URL

```bash
# Show current URL
gettool --get-url

# Set custom URL
gettool --set-url <URL>

# Reset to default URL
gettool --reset-url
```

## Command Reference

| Argument | Description |
|----------|-------------|
| `<name>` or `-n <name>` | Tool name from name_to_path_map.yaml |
| `-t <path>` | Target output directory (default: based on mapping) |
| `-b` / `--build` | Build using CMake + make (if buildable) |
| `-c` / `--clean` | Copy only src/include directories |
| `-v <version>` | Checkout specific version (submodules only) |
| `-i` / `--install` | Run installation script (if installable) |
| `--global-install-flag` | Set to `true` for sudo make install |
| `-l` / `--list` | List all supported tools |
| `--get-url` | Show current repository URL |
| `--set-url <URL>` | Set repository URL |
| `--reset-url` | Reset to default URL |

## Tool Types and Behavior

### Submodule Tools
- Cloned as full independent repositories
- Support `-v` for version checkout
- Not built via CMake (use `-b` for source-level build if configured)

### Non-Submodule Tools (Sparse Checkout)
- Fetched via git sparse-checkout from cpp_tools repo
- Can be built with `-b` (requires buildable=true and CMakeLists.txt)
- Build output (`lib/`) copied to target directory

## Default Path Mapping

When `-t` is not specified, the target path is determined by the `path` field in `name_to_path_map.yaml` relative to the current working directory.

Example: If `opencv` maps to `third_party/opencv`, running `gettool opencv` creates `./third_party/opencv`.

## Prerequisites

- Git
- CMake and make (for `-b` flag)
- Appropriate C++ toolchain (for building)
- Write permissions for target directory

## Common Tool Names

Typical tools available (run `gettool -l` for current list):
- `eigen` - Linear algebra library
- `opencv` - Computer vision library
- `pcl` - Point Cloud Library
- `fmt` - Formatting library
- `apriltag_detection` - AprilTag detection
- `spdlog` - Fast C++ logging library
