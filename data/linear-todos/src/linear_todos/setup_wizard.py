"""Setup wizard for Linear Todos."""

import click

from linear_todos.config import Config
from linear_todos.api import LinearAPI, LinearError, LinearAPIError


def run_setup():
    """Run the interactive setup wizard."""
    click.echo("🚀 Linear Todo Setup")
    click.echo("====================")
    click.echo()
    
    config = Config()
    
    # Check for API key
    api_key = config.api_key
    
    if not api_key:
        click.echo("❌ No Linear API key found!")
        click.echo()
        click.echo("Please get an API key from: https://linear.app/settings/api")
        click.echo()
        click.echo("You can store it in one of these ways:")
        click.echo("  1. Environment variable: export LINEAR_API_KEY='lin_api_...'")
        click.echo("  2. Config file (created by this wizard): ~/.config/linear-todos/config.json")
        click.echo("     (Recommended: use env var for better security)")
        click.echo()
        api_key = click.prompt("Enter your Linear API key", hide_input=True)
        
        if not api_key:
            click.echo("Error: API key is required")
            raise click.Abort()
    
    # Test API key
    click.echo()
    click.echo("🔑 Testing API key...")
    
    try:
        # Temporarily set the API key for testing
        import os
        os.environ['LINEAR_API_KEY'] = api_key
        test_config = Config()
        test_config._config['apiKey'] = api_key
        api = LinearAPI(config=test_config)
        viewer = api.get_viewer()
    except LinearAPIError as e:
        click.echo(f"❌ API key is invalid!")
        click.echo(f"Error: {e}")
        raise click.Abort()
    except LinearError as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()
    
    click.echo(f"✓ Authenticated as: {viewer['name']} ({viewer['email']})")
    
    # Fetch teams
    click.echo()
    click.echo("📊 Fetching teams...")
    
    try:
        teams = api.get_teams()
    except LinearAPIError as e:
        click.echo(f"❌ Error fetching teams: {e}")
        raise click.Abort()
    
    if not teams:
        click.echo("No teams found in your Linear workspace.")
        click.echo("Please create a team first at https://linear.app")
        raise click.Abort()
    
    # Display teams
    click.echo()
    click.echo("Available teams:")
    click.echo("----------------")
    for team in teams:
        click.echo(f"  {team['key']} - {team['name']} (ID: {team['id']})")
    
    # Select team
    click.echo()
    team_key = click.prompt("Enter the KEY of the team for your todos (e.g., TODO)")
    
    team_info = None
    for team in teams:
        if team['key'] == team_key:
            team_info = team
            break
    
    if not team_info:
        click.echo(f"❌ Team '{team_key}' not found!")
        raise click.Abort()
    
    team_id = team_info['id']
    team_name = team_info['name']
    
    click.echo(f"✓ Selected team: {team_name} ({team_key})")
    
    # Fetch states for this team
    click.echo()
    click.echo(f"📋 Fetching workflow states for {team_name}...")
    
    try:
        states = api.get_team_states(team_id)
    except LinearAPIError as e:
        click.echo(f"❌ Error fetching states: {e}")
        raise click.Abort()
    
    # Display states
    click.echo()
    click.echo("Available states:")
    click.echo("-----------------")
    for state in states:
        click.echo(f"  {state['name']} (Type: {state['type']}, ID: {state['id']})")
    
    # Select initial state (todo/unstarted)
    click.echo()
    state_name = click.prompt(
        "Select the state for NEW todos (usually 'Todo' or 'Backlog')",
        default=""
    )
    
    state_info = None
    if state_name:
        for state in states:
            if state['name'] == state_name:
                state_info = state
                break
    else:
        # Auto-select first unstarted state
        for state in states:
            if state['type'] == 'unstarted':
                state_info = state
                break
        if not state_info and states:
            state_info = states[0]
    
    if not state_info:
        click.echo("❌ State not found!")
        raise click.Abort()
    
    state_id = state_info['id']
    state_name = state_info['name']
    
    click.echo(f"✓ Selected initial state: {state_name}")
    
    # Select done state
    click.echo()
    done_state_name = click.prompt(
        "Select the state for DONE todos (usually 'Done' or 'Completed')",
        default=""
    )
    
    done_state_info = None
    done_state_id = None
    
    if done_state_name:
        for state in states:
            if state['name'] == done_state_name:
                done_state_info = state
                break
    else:
        # Auto-select first completed state
        for state in states:
            if state['type'] == 'completed':
                done_state_info = state
                break
    
    if done_state_info:
        done_state_id = done_state_info['id']
        done_state_name = done_state_info['name']
        click.echo(f"✓ Selected done state: {done_state_name}")
    else:
        click.echo("⚠️  No completed state found. You'll need to manually update issue status.")
    
    # Save configuration
    click.echo()
    click.echo("💾 Saving configuration...")
    
    config.save(
        api_key=api_key,
        team_id=team_id,
        state_id=state_id,
        done_state_id=done_state_id
    )
    
    click.echo(f"✓ Configuration saved to {config.CONFIG_FILE}")
    
    # Summary
    click.echo()
    click.echo("🎉 Setup complete!")
    click.echo("==================")
    click.echo()
    click.echo("Your Linear Todo configuration:")
    click.echo(f"  Team: {team_name} ({team_key})")
    click.echo(f"  Team ID: {team_id}")
    click.echo(f"  New Todo State: {state_name}")
    if done_state_name:
        click.echo(f"  Done State: {done_state_name}")
    click.echo()
    click.echo("Try these commands:")
    click.echo('  uv run python main.py create "My first todo" --when day')
    click.echo('  uv run python main.py create "Important task" --priority high --date tomorrow')
    click.echo("  uv run python main.py list")
    click.echo("  uv run python main.py review")
    click.echo()
    click.echo("For help: uv run python main.py --help")


@click.command()
def setup():
    """Run the interactive setup wizard for Linear Todos."""
    try:
        run_setup()
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"\n❌ Setup failed: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    setup()
