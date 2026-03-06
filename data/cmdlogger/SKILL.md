---
name: pywayne-bin-cmdlogger
description: Execute commands with full I/O logging. Use when users need to record the complete execution of a command including stdin, stdout, and stderr to a log file while maintaining real-time console output. Triggered by requests to log, record, monitor, or trace command execution, especially for builds, long-running scripts, debugging sessions, or CI/CD processes.
---

# Pywayne Bin Cmdlogger

Execute a command and log all stdin, stdout, stderr to a file while forwarding I/O to console in real-time.

## Quick Start

```bash
# Log command execution to default file (io_log.log in script directory)
cmdlogger <command> [args...]

# Specify custom log file path
cmdlogger --log-path <log_path> <command> [args...]
```

## Usage Examples

### Build Process Recording

```bash
# Log CMake configuration
cmdlogger --log-path cmake_config.log cmake ..

# Log build process
cmdlogger --log-path build.log make -j$(nproc)
```

### Script Execution Monitoring

```bash
# Log Python script execution
cmdlogger --log-path script_run.log python3 my_script.py --arg1 value1

# Log shell script execution
cmdlogger --log-path deploy.log ./deploy.sh production
```

### Debugging Sessions

```bash
# Log GDB debug session
cmdlogger --log-path debug_session.log gdb ./my_program

# Log Python interactive session
cmdlogger --log-path python_debug.log python3 -i my_module.py
```

### Network Operations

```bash
# Log curl request with verbose output
cmdlogger --log-path api_test.log curl -v https://api.example.com/data

# Log SSH connection process
cmdlogger --log-path ssh_session.log ssh user@remote-host
```

### Simple Command Logging

```bash
# Log git status
cmdlogger git status

# Log echo command
cmdlogger echo "Hello World"
```

## Command Reference

| Argument | Description |
|----------|-------------|
| `command` | The command to execute |
| `[args...]` | Command arguments |
| `--log-path <path>` | Optional log file path. Default: `io_log.log` in script directory |

## Log Format

Each line in the log file is prefixed with stream type:

- `输入: <content>` - Standard input
- `输出: <content>` - Standard output
- `错误: <content>` - Standard error

### Example Log Output

Running `cmdlogger echo "Hello World"` produces:

```
输出: Hello World
```

Running `cmdlogger python3 -c "import sys; print('stdout'); print('stderr', file=sys.stderr)"` produces:

```
输出: stdout
错误: stderr
```

## Features

- **Full I/O Recording**: Captures all stdin, stdout, stderr
- **Real-time Forwarding**: Forwards I/O to console while logging
- **Multi-threaded**: Uses separate threads for stdin, stdout, stderr
- **Encoding Handling**: Gracefully handles non-UTF-8 data
- **Resource Cleanup**: Automatically cleans up processes and files

## Use Cases

- Recording complex build processes for later analysis
- Monitoring long-running scripts with full logging
- Debugging with complete input/output history
- CI/CD pipeline execution logging
- Performance analysis with execution traces

## Important Notes

- **Interactive Commands**: User input (including passwords) is logged. Be careful with sensitive information.
- **Large Output**: Log files can become large for commands with heavy output. Ensure sufficient disk space.
- **Default Log Location**: If `--log-path` is not specified, log file is created in the script directory as `io_log.log`.
- **Exit Codes**: Returns the exit code of the executed command (127 if command not found).
