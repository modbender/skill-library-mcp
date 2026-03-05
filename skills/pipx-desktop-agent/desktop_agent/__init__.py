"""Desktop Agent - Main entry point."""
import typer
from desktop_agent.commands import mouse, keyboard, screen, app as app_cmd, message

app = typer.Typer(help="Desktop automation agent")

app.add_typer(mouse.app, name="mouse")
app.add_typer(keyboard.app, name="keyboard")
app.add_typer(screen.app, name="screen")
app.add_typer(app_cmd.app, name="app")
app.add_typer(message.app, name="message")

def app_cli():
    app()

if __name__ == "__main__":
    app()
