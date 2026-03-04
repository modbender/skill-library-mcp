"""Application control commands - cross-platform app launching and focusing."""
import platform
import subprocess
import time
import typer
from typing import Optional
from desktop_agent.utils import CommandResponse, ErrorCode, DesktopAgentError

app = typer.Typer(help="Application control commands")


def _get_platform() -> str:
    """Get the current platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def _handle_command(command: str, func, *args, **kwargs):
    start = time.time()
    try:
        result = func(*args, **kwargs)
        duration_ms = int((time.time() - start) * 1000)
        response = CommandResponse.success_response(
            command=command,
            data=result,
            duration_ms=duration_ms,
        )
        response.print()
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        error = DesktopAgentError(
            code=ErrorCode.from_exception(e),
            message=str(e),
        )
        response = CommandResponse.error_response(
            command=command,
            code=error.code.to_string(),
            message=error.message,
            details=error.details,
            duration_ms=duration_ms,
         )
        response.print()
        raise sys.exit(error.exit_code())


@app.command()
def open(
    name: str = typer.Argument(..., help="Application name or path to open"),
    args: Optional[list[str]] = typer.Option(None, "--arg", "-a", help="Arguments to pass to the application"),
):
    """Open an application by name or path."""
    def execute():
        current_platform = _get_platform()
        args_list = args or []

        if current_platform == "windows":
            if args_list:
                subprocess.Popen(
                    f'start "" "{name}" {" ".join(args_list)}',
                    shell=True,
                )
            else:
                subprocess.Popen(f'start "" "{name}"', shell=True)

        elif current_platform == "macos":
            cmd = ["open", "-a", name]
            if args_list:
                cmd.extend(["--args"] + args_list)
            subprocess.Popen(cmd)

        else:
            cmd = [name] + args_list
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        return {"application": name, "args": args_list}
    _handle_command("app.open", execute)


@app.command()
def focus(name: str = typer.Argument(..., help="Window title or application name to focus")):
    """Focus on a window by title or application name."""
    def execute():
        current_platform = _get_platform()

        if current_platform == "windows":
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                wintypes.HWND,
                wintypes.LPARAM
            )

            found_hwnd = None

            def enum_callback(hwnd, lparam):
                nonlocal found_hwnd
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        title = buffer.value
                        if name.lower() in title.lower():
                            found_hwnd = hwnd
                            return False
                return True

            user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

            if found_hwnd:
                SW_RESTORE = 9
                user32.ShowWindow(found_hwnd, SW_RESTORE)
                user32.SetForegroundWindow(found_hwnd)
                return {"window_title": name, "focused": True}
            else:
                raise DesktopAgentError(
                    code=ErrorCode.WINDOW_NOT_FOUND,
                    message=f"Window '{name}' not found",
                )

        elif current_platform == "macos":
            script = f'''
            tell application "{name}"
                activate
            end tell
            '''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return {"application": name, "focused": True}
            else:
                raise DesktopAgentError(
                    code=ErrorCode.WINDOW_NOT_FOUND,
                    message=f"Could not focus '{name}'",
                    details={"stderr": result.stderr},
                )

        else:
            try:
                result = subprocess.run(
                    ["wmctrl", "-a", name],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return {"window_title": name, "focused": True}
                else:
                    raise FileNotFoundError("wmctrl failed")
            except FileNotFoundError:
                result = subprocess.run(
                    ["xdotool", "search", "--name", name, "windowactivate"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return {"window_title": name, "focused": True}
                else:
                    raise DesktopAgentError(
                        code=ErrorCode.WINDOW_NOT_FOUND,
                        message=f"Could not focus '{name}'. Install wmctrl or xdotool.",
                    )
    _handle_command("app.focus", execute)


@app.command()
def list():
    """List all visible windows."""
    def execute():
        current_platform = _get_platform()
        windows = []

        if current_platform == "windows":
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                wintypes.HWND,
                wintypes.LPARAM
            )

            def enum_callback(hwnd, lparam):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        title = buffer.value
                        if title.strip():
                            windows.append(title)
                return True

            user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

        elif current_platform == "macos":
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in (every process whose background only is false)
                    repeat with win in (every window of proc)
                        set end of windowList to (name of proc) & " - " & (name of win)
                    end repeat
                end repeat
                return windowList
            end tell
            '''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                if output:
                    windows = [w.strip() for w in output.split(",")]

        else:
            result = subprocess.run(
                ["wmctrl", "-l"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append(parts[3])
            else:
                raise DesktopAgentError(
                    code=ErrorCode.PLATFORM_NOT_SUPPORTED,
                    message="wmctrl not found. Install it with: sudo apt install wmctrl",
                )

        return {"windows": windows}
    _handle_command("app.list", execute)


import sys
