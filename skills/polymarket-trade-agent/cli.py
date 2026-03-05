#!/usr/bin/env python3
"""
Polymarket Trade Agent CLI
Usage: polymarket <command>
"""
import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import trade

app = typer.Typer(
    name="polymarket",
    help="🎰 Polymarket Trade Agent",
    rich_markup_mode="markdown",
)
console = Console()


@app.command()
def address():
    """Show your wallet address"""
    addr = trade.get_wallet_address()
    funder = trade.get_funder_address()
    if addr:
        content = f"[bold green]{addr}[/bold green]"
        if funder:
            content += f"\n\n[bold]Funder:[/bold] {funder}"
        console.print(Panel(
            content,
            title="💼 Wallet Address",
            border_style="cyan"
        ))
    else:
        console.print("[red]Could not get address. Check POLYMARKET_PRIVATE_KEY[/red]")


@app.command()
def balance():
    """Check your USDC balance"""
    bal = trade.get_balance()
    if bal is not None:
        console.print(Panel(
            f"[bold green]${bal:.2f} USDC[/bold green]",
            title="💵 Balance",
            border_style="green"
        ))
    else:
        console.print("[red]Failed to get balance[/red]")


@app.command()
def markets(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of markets to show"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search markets"),
):
    """List active markets"""
    markets = trade.get_markets(limit=limit, search=search)
    if not markets:
        console.print("[red]No markets found[/red]")
        return
    
    table = Table(title="📊 Polymarket Markets")
    table.add_column("Question", style="cyan", max_width=50)
    table.add_column("Yes", justify="right")
    table.add_column("No", justify="right")
    table.add_column("Volume", justify="right")
    
    for m in markets:
        question = m.get("question", "Unknown")[:45]
        yes = m.get("yes_price", "N/A")
        no = m.get("no_price", "N/A")
        volume = m.get("volume", "0")
        try:
            vol = float(volume)
            if vol > 1e6:
                volume = f"${vol/1e6:.1f}M"
            elif vol > 1e3:
                volume = f"${vol/1e3:.1f}K"
            else:
                volume = f"${vol:.0f}"
        except:
            pass
        table.add_row(question, f"${yes}", f"${no}", volume)
    
    console.print(table)


@app.command()
def search(query: str):
    """Search for markets"""
    markets = trade.get_markets(limit=20, search=query)
    if not markets:
        console.print(f"[yellow]No markets found for: {query}[/yellow]")
        return
    
    table = Table(title=f"🔍 Search Results: {query}")
    table.add_column("Question", style="cyan", max_width=50)
    table.add_column("Yes", justify="right")
    table.add_column("Volume", justify="right")
    
    for m in markets:
        question = m.get("question", "Unknown")[:45]
        yes = m.get("yes_price", "N/A")
        volume = m.get("volume", "0")
        try:
            vol = float(volume)
            if vol > 1e6:
                volume = f"${vol/1e6:.1f}M"
            elif vol > 1e3:
                volume = f"${vol/1e3:.1f}K"
            else:
                volume = f"${vol:.0f}"
        except:
            pass
        table.add_row(question, f"${yes}", volume)
    
    console.print(table)


@app.command()
def buy(
    token_id: str = typer.Argument(..., help="Token ID"),
    price: float = typer.Argument(..., help="Price to buy at"),
    size: float = typer.Argument(..., help="Size in USDC"),
):
    """Buy YES on a market"""
    console.print(f"[cyan]Buying YES: {size} @ ${price}[/cyan]")
    result = trade.place_order(token_id, "BUY", price, size)
    if result:
        console.print(Panel(
            f"[green]Order placed successfully![/green]\n{result}",
            title="✅ Success",
            border_style="green"
        ))
    else:
        console.print("[red]Order failed[/red]")


@app.command()
def sell(
    token_id: str = typer.Argument(..., help="Token ID"),
    price: float = typer.Argument(..., help="Price to sell at"),
    size: float = typer.Argument(..., help="Size in USDC"),
):
    """Sell YES on a market"""
    console.print(f"[cyan]Selling YES: {size} @ ${price}[/cyan]")
    result = trade.place_order(token_id, "SELL", price, size)
    if result:
        console.print(Panel(
            f"[green]Order placed successfully![/green]\n{result}",
            title="✅ Success",
            border_style="green"
        ))
    else:
        console.print("[red]Order failed[/red]")


@app.command()
def positions():
    """View your open positions"""
    pos = trade.get_positions()
    if pos:
        console.print(pos)
    else:
        console.print("[yellow]No positions found[/yellow]")


@app.command()
def doctor():
    """Health check"""
    console.print(Panel(
        "[bold]Polymarket Trade Agent Health Check[/bold]",
        border_style="cyan"
    ))
    
    # Check Python
    console.print("✓ Python")
    
    # Check private key
    key = os.getenv("POLYMARKET_PRIVATE_KEY")
    if key:
        console.print(f"✓ POLYMARKET_PRIVATE_KEY set")
        addr = trade.get_wallet_address()
        console.print(f"  Address: {addr}")
    else:
        console.print("✗ POLYMARKET_PRIVATE_KEY not set")
    
    # Check balance
    bal = trade.get_balance()
    if bal is not None:
        console.print(f"✓ Balance: ${bal:.2f} USDC")
    else:
        console.print("✗ Could not fetch balance")


@app.command()
def setup():
    """Setup instructions"""
    console.print(Panel(
        """[bold]Setup Instructions:[/bold]

1. Get your Polygon private key from MetaMask:
   - Open MetaMask
   - Click 3 dots → Account details
   - Export private key

2. Set the environment variable:
   [cyan]export POLYMARKET_PRIVATE_KEY=0xYOUR_KEY_HERE[/cyan]

3. Check balance:
   [cyan]polymarket balance[/cyan]

4. Fund your account:
   - Go to Polymarket.com
   - Deposit USDC to your address
   - Use: polymarket address
""",
        title="⚙️ Setup",
        border_style="green"
    ))


if __name__ == "__main__":
    app()
