"""Keyboard control commands."""
import time
import typer
import pyautogui
from desktop_agent.utils import CommandResponse, ErrorCode, DesktopAgentError

app = typer.Typer(help="Keyboard control commands")


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
def write(
    text: str = typer.Argument(..., help="Text to type"),
    interval: float = typer.Option(0.0, "--interval", "-i", help="Interval between keystrokes"),
):
    """Type text with optional interval between keys."""
    def execute():
        pyautogui.write(text, interval=interval)
        return {"text": text, "interval": interval}
    _handle_command("keyboard.write", execute)


@app.command()
def press(
    keys: str = typer.Argument(..., help="Key(s) to press (comma-separated for sequence)"),
    presses: int = typer.Option(1, "--presses", "-p", help="Number of times to press"),
    interval: float = typer.Option(0.0, "--interval", "-i", help="Interval between presses"),
):
    """Press one or more keys."""
    def execute():
        key_list = [k.strip() for k in keys.split(",")]
        for key in key_list:
            pyautogui.press(key, presses=presses, interval=interval)
        return {"keys": key_list, "presses": presses, "interval": interval}
    _handle_command("keyboard.press", execute)


@app.command()
def hotkey(
    keys: str = typer.Argument(..., help="Keys for hotkey (comma-separated, e.g., 'ctrl,c')"),
    interval: float = typer.Option(0.0, "--interval", "-i", help="Interval between key presses"),
):
    """Execute a hotkey combination."""
    def execute():
        key_list = [k.strip() for k in keys.split(",")]
        pyautogui.hotkey(*key_list, interval=interval)
        return {"keys": key_list, "interval": interval}
    _handle_command("keyboard.hotkey", execute)


@app.command()
def keydown(key: str = typer.Argument(..., help="Key to hold down")):
    """Hold down a key."""
    def execute():
        pyautogui.keyDown(key)
        return {"key": key}
    _handle_command("keyboard.keydown", execute)


@app.command()
def keyup(key: str = typer.Argument(..., help="Key to release")):
    """Release a held key."""
    def execute():
        pyautogui.keyUp(key)
        return {"key": key}
    _handle_command("keyboard.keyup", execute)


import sys
