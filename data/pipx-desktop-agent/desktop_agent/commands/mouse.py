"""Mouse control commands."""
import time
import typer
import pyautogui
from desktop_agent.utils import CommandResponse, ErrorCode, DesktopAgentError

app = typer.Typer(help="Mouse control commands")


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
def move(
    x: int = typer.Argument(..., help="X coordinate"),
    y: int = typer.Argument(..., help="Y coordinate"),
    duration: float = typer.Option(0.0, "--duration", "-d", help="Duration in seconds"),
):
    """Move mouse to specified coordinates."""
    def execute():
        pyautogui.moveTo(x, y, duration=duration)
        return {"x": x, "y": y, "duration": duration}
    _handle_command("mouse.move", execute)


@app.command()
def click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
    button: str = typer.Option("left", "--button", "-b", help="Mouse button: left, right, middle"),
    clicks: int = typer.Option(1, "--clicks", "-c", help="Number of clicks"),
):
    """Click at current position or specified coordinates."""
    def execute():
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
            return {"position": {"x": x, "y": y}, "button": button, "clicks": clicks}
        else:
            pyautogui.click(clicks=clicks, button=button)
            return {"position": None, "button": button, "clicks": clicks}
    _handle_command("mouse.click", execute)


@app.command()
def double_click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Double click at current position or specified coordinates."""
    def execute():
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
            return {"position": {"x": x, "y": y}}
        else:
            pyautogui.doubleClick()
            return {"position": None}
    _handle_command("mouse.double_click", execute)


@app.command()
def right_click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Right click at current position or specified coordinates."""
    def execute():
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
            return {"position": {"x": x, "y": y}}
        else:
            pyautogui.rightClick()
            return {"position": None}
    _handle_command("mouse.right_click", execute)


@app.command()
def middle_click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Middle click at current position or specified coordinates."""
    def execute():
        if x is not None and y is not None:
            pyautogui.middleClick(x, y)
            return {"position": {"x": x, "y": y}}
        else:
            pyautogui.middleClick()
            return {"position": None}
    _handle_command("mouse.middle_click", execute)


@app.command()
def drag(
    x: int = typer.Argument(..., help="Target X coordinate"),
    y: int = typer.Argument(..., help="Target Y coordinate"),
    duration: float = typer.Option(0.0, "--duration", "-d", help="Duration in seconds"),
    button: str = typer.Option("left", "--button", "-b", help="Mouse button: left, right, middle"),
):
    """Drag mouse to specified coordinates."""
    def execute():
        pyautogui.drag(x, y, duration=duration, button=button)
        return {"x": x, "y": y, "duration": duration, "button": button}
    _handle_command("mouse.drag", execute)


@app.command()
def scroll(
    clicks: int = typer.Argument(..., help="Number of scroll clicks (negative for down)"),
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Scroll at current position or specified coordinates."""
    def execute():
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x, y)
            return {"clicks": clicks, "position": {"x": x, "y": y}}
        else:
            pyautogui.scroll(clicks)
            return {"clicks": clicks, "position": None}
    _handle_command("mouse.scroll", execute)


@app.command()
def position():
    """Get current mouse position."""
    def execute():
        pos = pyautogui.position()
        return {"position": {"x": pos.x, "y": pos.y}}
    _handle_command("mouse.position", execute)


import sys
