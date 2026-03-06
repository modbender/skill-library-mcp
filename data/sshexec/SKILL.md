---
name: ssh-exec
description: A skill to execute SSH commands on remote servers, supporting both password and key-based authentication. It includes error handling and logging for command execution results.
---
# SSH Command Executor
This skill allows you to execute SSH commands on remote servers securely. It supports both password and key-based authentication methods, making it versatile for various use cases.
## Features
- **Authentication**: Supports both password and key-based authentication.
- **Command Execution**: Execute any command on the remote server and retrieve the output.
- **Error Handling**: Provides detailed error messages for failed command executions.
- **Logging**: Logs all executed commands and their results for auditing purposes.
## Prerequisites
- **SSH Client**: Ensure you have an SSH client installed on your local machine.
- **Remote Server Access**: You must have access to the remote server with the necessary credentials.
- **Python Environment**: This skill is implemented in Python, so ensure you have Python installed on your local machine.
## Usage
To execute a command on a remote server using password authentication:
```bash
python3 skills/sshexec/ssh_exec.py --host "remote-server.com" --user "username" --password "password" --command "ls -la"
``` 
To execute a command using key-based authentication:
```bash
python3 skills/sshexec/ssh_exec.py --host "remote-server.com" --user "username" --key "path/to/private/key" --command "ls -la"
```
## Error Handling
The skill will provide detailed error messages if the command execution fails, such as authentication errors, connection issues, or command errors. All errors will be logged for further analysis.
## Future Expansion
- Support for executing multiple commands in a single session.
- Integration with task schedulers for automated command execution.
- Enhanced logging with timestamps and command output storage.