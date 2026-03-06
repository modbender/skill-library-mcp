"""Mouse control commands."""
import typer
import pyautogui

app = typer.Typer(help="Mouse control commands")


@app.command()
def move(
    x: int = typer.Argument(..., help="X coordinate"),
    y: int = typer.Argument(..., help="Y coordinate"),
    duration: float = typer.Option(0.0, "--duration", "-d", help="Duration in seconds"),
):
    """Move mouse to specified coordinates."""
    pyautogui.moveTo(x, y, duration=duration)
    typer.echo(f"Mouse moved to ({x}, {y})")


@app.command()
def click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
    button: str = typer.Option("left", "--button", "-b", help="Mouse button: left, right, middle"),
    clicks: int = typer.Option(1, "--clicks", "-c", help="Number of clicks"),
):
    """Click at current position or specified coordinates."""
    if x is not None and y is not None:
        pyautogui.click(x, y, clicks=clicks, button=button)
        typer.echo(f"{button.capitalize()} clicked {clicks}x at ({x}, {y})")
    else:
        pyautogui.click(clicks=clicks, button=button)
        typer.echo(f"{button.capitalize()} clicked {clicks}x at current position")


@app.command()
def double_click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Double click at current position or specified coordinates."""
    if x is not None and y is not None:
        pyautogui.doubleClick(x, y)
        typer.echo(f"Double clicked at ({x}, {y})")
    else:
        pyautogui.doubleClick()
        typer.echo("Double clicked at current position")


@app.command()
def right_click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Right click at current position or specified coordinates."""
    if x is not None and y is not None:
        pyautogui.rightClick(x, y)
        typer.echo(f"Right clicked at ({x}, {y})")
    else:
        pyautogui.rightClick()
        typer.echo("Right clicked at current position")


@app.command()
def middle_click(
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Middle click at current position or specified coordinates."""
    if x is not None and y is not None:
        pyautogui.middleClick(x, y)
        typer.echo(f"Middle clicked at ({x}, {y})")
    else:
        pyautogui.middleClick()
        typer.echo("Middle clicked at current position")


@app.command()
def drag(
    x: int = typer.Argument(..., help="Target X coordinate"),
    y: int = typer.Argument(..., help="Target Y coordinate"),
    duration: float = typer.Option(0.0, "--duration", "-d", help="Duration in seconds"),
    button: str = typer.Option("left", "--button", "-b", help="Mouse button: left, right, middle"),
):
    """Drag mouse to specified coordinates."""
    pyautogui.drag(x, y, duration=duration, button=button)
    typer.echo(f"Dragged to ({x}, {y}) with {button} button")


@app.command()
def scroll(
    clicks: int = typer.Argument(..., help="Number of scroll clicks (negative for down)"),
    x: int = typer.Argument(None, help="X coordinate (optional)"),
    y: int = typer.Argument(None, help="Y coordinate (optional)"),
):
    """Scroll at current position or specified coordinates."""
    if x is not None and y is not None:
        pyautogui.scroll(clicks, x, y)
        typer.echo(f"Scrolled {clicks} clicks at ({x}, {y})")
    else:
        pyautogui.scroll(clicks)
        typer.echo(f"Scrolled {clicks} clicks at current position")


@app.command()
def position():
    """Get current mouse position."""
    pos = pyautogui.position()
    typer.echo(f"Mouse position: ({pos.x}, {pos.y})")
