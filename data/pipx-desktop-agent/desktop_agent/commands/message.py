"""Message box commands."""
import time
import typer
import pyautogui
from desktop_agent.utils import CommandResponse, ErrorCode, DesktopAgentError

app = typer.Typer(help="Message box commands")


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
def alert(
    text: str = typer.Argument(..., help="Alert message"),
    title: str = typer.Option("Alert", "--title", "-t", help="Window title"),
    button: str = typer.Option("OK", "--button", "-b", help="Button text"),
):
    """Display an alert message box."""
    def execute():
        result = pyautogui.alert(text=text, title=title, button=button)
        return {"button_pressed": result}
    _handle_command("message.alert", execute)


@app.command()
def confirm(
    text: str = typer.Argument(..., help="Confirmation message"),
    title: str = typer.Option("Confirm", "--title", "-t", help="Window title"),
    buttons: str = typer.Option("OK,Cancel", "--buttons", "-b", help="Button texts (comma-separated)"),
):
    """Display a confirmation dialog."""
    def execute():
        button_list = [b.strip() for b in buttons.split(",")]
        result = pyautogui.confirm(text=text, title=title, buttons=button_list)
        return {"button_pressed": result}
    _handle_command("message.confirm", execute)


@app.command()
def prompt(
    text: str = typer.Argument(..., help="Prompt message"),
    title: str = typer.Option("Input", "--title", "-t", help="Window title"),
    default: str = typer.Option("", "--default", "-d", help="Default value"),
):
    """Display a prompt dialog for text input."""
    def execute():
        result = pyautogui.prompt(text=text, title=title, default=default)
        if result is not None:
            return {"user_input": result, "cancelled": False}
        else:
            return {"user_input": None, "cancelled": True}
    _handle_command("message.prompt", execute)


@app.command()
def password(
    text: str = typer.Argument(..., help="Password prompt message"),
    title: str = typer.Option("Password", "--title", "-t", help="Window title"),
    default: str = typer.Option("", "--default", "-d", help="Default value"),
    mask: str = typer.Option("*", "--mask", "-m", help="Mask character"),
):
    """Display a password input dialog."""
    def execute():
        result = pyautogui.password(text=text, title=title, default=default, mask=mask)
        if result is not None:
            return {"entered": True, "length": len(result)}
        else:
            return {"entered": False, "length": 0}
    _handle_command("message.password", execute)


import sys
