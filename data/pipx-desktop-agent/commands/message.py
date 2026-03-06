"""Message box commands."""
import typer
import pyautogui

app = typer.Typer(help="Message box commands")


@app.command()
def alert(
    text: str = typer.Argument(..., help="Alert message"),
    title: str = typer.Option("Alert", "--title", "-t", help="Window title"),
    button: str = typer.Option("OK", "--button", "-b", help="Button text"),
):
    """Display an alert message box."""
    result = pyautogui.alert(text=text, title=title, button=button)
    typer.echo(f"Alert shown: {result}")


@app.command()
def confirm(
    text: str = typer.Argument(..., help="Confirmation message"),
    title: str = typer.Option("Confirm", "--title", "-t", help="Window title"),
    buttons: str = typer.Option("OK,Cancel", "--buttons", "-b", help="Button texts (comma-separated)"),
):
    """Display a confirmation dialog."""
    button_list = [b.strip() for b in buttons.split(",")]
    result = pyautogui.confirm(text=text, title=title, buttons=button_list)
    typer.echo(f"User selected: {result}")


@app.command()
def prompt(
    text: str = typer.Argument(..., help="Prompt message"),
    title: str = typer.Option("Input", "--title", "-t", help="Window title"),
    default: str = typer.Option("", "--default", "-d", help="Default value"),
):
    """Display a prompt dialog for text input."""
    result = pyautogui.prompt(text=text, title=title, default=default)
    if result is not None:
        typer.echo(f"User entered: {result}")
    else:
        typer.echo("User cancelled")


@app.command()
def password(
    text: str = typer.Argument(..., help="Password prompt message"),
    title: str = typer.Option("Password", "--title", "-t", help="Window title"),
    default: str = typer.Option("", "--default", "-d", help="Default value"),
    mask: str = typer.Option("*", "--mask", "-m", help="Mask character"),
):
    """Display a password input dialog."""
    result = pyautogui.password(text=text, title=title, default=default, mask=mask)
    if result is not None:
        typer.echo(f"Password entered (length: {len(result)})")
    else:
        typer.echo("User cancelled")
