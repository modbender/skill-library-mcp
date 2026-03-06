"""Screen and screenshot commands."""
import typer
import pyautogui
from pathlib import Path

app = typer.Typer(help="Screen and screenshot commands")


@app.command()
def screenshot(
    filename: str = typer.Argument("screenshot.png", help="Output filename"),
    region: str = typer.Option(None, "--region", "-r", help="Region as 'x,y,width,height'"),
):
    """Take a screenshot of the entire screen or a region."""
    if region:
        try:
            x, y, width, height = map(int, region.split(","))
            img = pyautogui.screenshot(region=(x, y, width, height))
            img.save(filename)
            typer.echo(f"Screenshot saved to {filename} (region: {region})")
        except ValueError:
            typer.echo("Error: Region must be in format 'x,y,width,height'", err=True)
            raise typer.Exit(1)
    else:
        img = pyautogui.screenshot()
        img.save(filename)
        typer.echo(f"Screenshot saved to {filename}")


@app.command()
def locate(
    image: str = typer.Argument(..., help="Path to image to locate"),
    confidence: float = typer.Option(0.9, "--confidence", "-c", help="Match confidence (0.0-1.0)"),
):
    """Locate an image on the screen."""
    try:
        location = pyautogui.locateOnScreen(image, confidence=confidence)
        if location:
            typer.echo(f"Found at: x={location.left}, y={location.top}, width={location.width}, height={location.height}")
        else:
            typer.echo("Image not found on screen")
    except pyautogui.ImageNotFoundException:
        typer.echo("Image not found on screen")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def locate_center(
    image: str = typer.Argument(..., help="Path to image to locate"),
    confidence: float = typer.Option(0.9, "--confidence", "-c", help="Match confidence (0.0-1.0)"),
):
    """Get the center coordinates of an image on the screen."""
    try:
        location = pyautogui.locateCenterOnScreen(image, confidence=confidence)
        if location:
            typer.echo(f"Center at: ({location.x}, {location.y})")
        else:
            typer.echo("Image not found on screen")
    except pyautogui.ImageNotFoundException:
        typer.echo("Image not found on screen")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def pixel(
    x: int = typer.Argument(..., help="X coordinate"),
    y: int = typer.Argument(..., help="Y coordinate"),
):
    """Get the RGB color of a pixel at specified coordinates."""
    color = pyautogui.pixel(x, y)
    typer.echo(f"Pixel at ({x}, {y}): RGB{color}")


@app.command()
def size():
    """Get the screen size."""
    screen_size = pyautogui.size()
    typer.echo(f"Screen size: {screen_size.width}x{screen_size.height}")


@app.command()
def on_screen(
    x: int = typer.Argument(..., help="X coordinate"),
    y: int = typer.Argument(..., help="Y coordinate"),
):
    """Check if coordinates are on the screen."""
    is_on_screen = pyautogui.onScreen(x, y)
    if is_on_screen:
        typer.echo(f"({x}, {y}) is on screen")
    else:
        typer.echo(f"({x}, {y}) is NOT on screen")
