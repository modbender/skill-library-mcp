"""Keyboard control commands."""
import typer
import pyautogui

app = typer.Typer(help="Keyboard control commands")


@app.command()
def write(
    text: str = typer.Argument(..., help="Text to type"),
    interval: float = typer.Option(0.0, "--interval", "-i", help="Interval between keystrokes"),
):
    """Type text with optional interval between keys."""
    pyautogui.write(text, interval=interval)
    typer.echo(f"Typed: {text}")


@app.command()
def press(
    keys: str = typer.Argument(..., help="Key(s) to press (comma-separated for sequence)"),
    presses: int = typer.Option(1, "--presses", "-p", help="Number of times to press"),
    interval: float = typer.Option(0.0, "--interval", "-i", help="Interval between presses"),
):
    """Press one or more keys."""
    key_list = [k.strip() for k in keys.split(",")]
    for key in key_list:
        pyautogui.press(key, presses=presses, interval=interval)
    typer.echo(f"Pressed: {keys} ({presses}x)")


@app.command()
def hotkey(
    keys: str = typer.Argument(..., help="Keys for hotkey (comma-separated, e.g., 'ctrl,c')"),
    interval: float = typer.Option(0.0, "--interval", "-i", help="Interval between key presses"),
):
    """Execute a hotkey combination."""
    key_list = [k.strip() for k in keys.split(",")]
    pyautogui.hotkey(*key_list, interval=interval)
    typer.echo(f"Executed hotkey: {' + '.join(key_list)}")


@app.command()
def keydown(
    key: str = typer.Argument(..., help="Key to hold down"),
):
    """Hold down a key."""
    pyautogui.keyDown(key)
    typer.echo(f"Key down: {key}")


@app.command()
def keyup(
    key: str = typer.Argument(..., help="Key to release"),
):
    """Release a held key."""
    pyautogui.keyUp(key)
    typer.echo(f"Key up: {key}")
