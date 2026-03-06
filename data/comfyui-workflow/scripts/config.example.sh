# comfy_control.sh configuration
# Copy this file to config.sh and customize for your setup

# ComfyUI server address
COMFY_HOST="127.0.0.1:8188"

# Startup timeout in seconds (larger models take longer)
STARTUP_TIMEOUT=180

# ── Start/Stop Commands ──────────────────────────────────────────────────────
# Choose ONE of the following examples and customize:

# Example 1: Local ComfyUI (Linux/Mac)
# COMFY_START_CMD="cd /path/to/ComfyUI && python main.py --listen --port 8188"
# COMFY_STOP_CMD="pkill -f 'python.*main.py'"

# Example 2: Windows Portable via WSL
# COMFY_START_CMD="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -WindowStyle Hidden -Command \"Start-Process -FilePath cmd.exe -ArgumentList '/c', 'D:\\ComfyUI_windows_portable\\run_nvidia_gpu.bat' -WorkingDirectory 'D:\\ComfyUI_windows_portable'\""
# COMFY_STOP_CMD="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command \"Get-Process | Where-Object {\\$_.MainWindowTitle -like '*ComfyUI*' -or \\$_.Name -eq 'python'} | Stop-Process -Force -ErrorAction SilentlyContinue\""

# Example 3: Docker
# COMFY_START_CMD="docker start comfyui"
# COMFY_STOP_CMD="docker stop comfyui"

# Example 4: Systemd service
# COMFY_START_CMD="systemctl --user start comfyui"
# COMFY_STOP_CMD="systemctl --user stop comfyui"