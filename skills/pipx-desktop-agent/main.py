"""Desktop Agent - Backwards compatibility wrapper.

For production use: uvx desktop-agent <command>
For development: python main.py <command> or python -m desktop_agent <command>
"""
from desktop_agent import app

if __name__ == "__main__":
    app()

