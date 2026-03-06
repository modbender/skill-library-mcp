"""Click CLI for Linear Todos."""

import json
import secrets
import sys
from datetime import datetime
from typing import Optional

import click

from linear_todos.config import Config
from linear_todos.api import LinearAPI, LinearError, LinearAPIError
from linear_todos.dates import DateParser
from linear_todos.setup_wizard import run_setup


# Priority option helper
PRIORITY_OPTIONS = ["urgent", "high", "normal", "low", "none"]


@click.group()
@click.version_option(version=Config.__module__)
@click.pass_context
def cli(ctx):
    """Linear Todo CLI - Manage todos with smart date parsing."""
    # Ensure context object is initialized
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config()


@cli.command()
def setup():
    """Run the interactive setup wizard for Linear Todos."""
    try:
        run_setup()
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"\n❌ Setup failed: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('title', required=True, nargs=-1)
@click.option('--when', type=click.Choice(['day', 'week', 'month']), 
              help='Set due date relative to now (day=end of today, week=7 days, month=28 days)')
@click.option('--date', 'date_input', metavar='DATE',
              help='Set specific due date (YYYY-MM-DD or natural language like "tomorrow", "next Monday")')
@click.option('--priority', type=click.Choice(PRIORITY_OPTIONS),
              help='Set priority: urgent, high, normal, low, none')
@click.option('--desc', '--description', 'description',
              help='Add description')
@click.option('--team', 'team_id',
              help='Override team ID (default from config)')
@click.option('--state', 'state_id',
              help='Override state ID (default from config)')
@click.pass_context
def create(ctx, title, when, date_input, priority, description, team_id, state_id):
    """Create a new todo.
    
    Examples:
        linear-todo create "Call mom" --when day
        linear-todo create "Pay taxes" --date 2025-04-15
        linear-todo create "Review PR" --priority high --when week
        linear-todo create "Urgent bug" --priority urgent --date "tomorrow"
    """
    config = ctx.obj['config']
    
    # Join title arguments
    title_str = ' '.join(title)
    if not title_str:
        click.echo("Error: Title is required", err=True)
        sys.exit(1)
    
    # Use config values as defaults
    team_id = team_id or config.team_id
    state_id = state_id or config.state_id
    
    if not team_id:
        click.echo("Error: Team ID not configured. Run 'uv run python main.py setup' first.", err=True)
        sys.exit(1)
    
    # Validate --when and --date conflict
    if when and date_input:
        click.echo("Error: Cannot use both --when and --date. Choose one.", err=True)
        sys.exit(1)
    
    # Calculate due date using configured timezone
    due_date = None
    display_timing = None

    # Get current time in configured timezone (or UTC if not set)
    tz = config.get_timezone()
    if tz:
        base_datetime = datetime.now(tz)
    else:
        base_datetime = datetime.utcnow()

    if when:
        due_date = DateParser.get_relative_date(when, base_datetime)
        display_timing = when.capitalize()
    elif date_input:
        parsed_date = DateParser.parse(date_input, base_datetime)
        if not parsed_date:
            click.echo(f"Error: Could not parse date: {date_input}", err=True)
            click.echo('Try formats like: YYYY-MM-DD, tomorrow, Friday, next Monday, in 3 days', err=True)
            sys.exit(1)
        due_date = DateParser.to_iso_datetime(parsed_date, end_of_day=True, tz=tz)
        display_timing = f"Due: {parsed_date}"
    
    # Convert priority to number
    priority_num = None
    if priority:
        priority_num = LinearAPI.priority_to_number(priority)
        if priority_num is None:
            click.echo(f"Error: Invalid priority: {priority}", err=True)
            click.echo("Valid priorities: urgent, high, normal, low, none", err=True)
            sys.exit(1)
    
    click.echo(f"Creating todo: {title_str}")
    
    try:
        api = LinearAPI(config=config)
        result = api.create_issue(
            team_id=team_id,
            title=title_str,
            description=description,
            state_id=state_id,
            priority=priority_num,
            due_date=due_date
        )
        
        if result.get('success'):
            issue = result['issue']
            click.echo(f"✓ Created: {issue['identifier']} - {title_str}")
            if priority_num is not None:
                click.echo(f"  Priority: {LinearAPI.priority_to_label(priority_num)}")
            if display_timing:
                click.echo(f"  Due: {display_timing}")
            elif issue.get('dueDate'):
                due = issue['dueDate'].split('T')[0]
                click.echo(f"  Due: {due}")
            click.echo(f"  URL: {issue['url']}")
        else:
            click.echo("Error: Failed to create issue", err=True)
            sys.exit(1)
            
    except LinearAPIError as e:
        click.echo(f"Error creating todo: {e}", err=True)
        if e.errors:
            click.echo(json.dumps(e.errors, indent=2), err=True)
        sys.exit(1)
    except LinearError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='list')
@click.option('--all', 'show_all', is_flag=True, help='Show all todos including completed')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.option('--team', 'team_id', help='Override team ID')
@click.pass_context
def list_command(ctx, show_all, output_json, team_id):
    """List all todos."""
    config = ctx.obj['config']
    team_id = team_id or config.team_id
    
    if not team_id:
        click.echo("Error: Team ID not configured. Run 'uv run python main.py setup' first.", err=True)
        sys.exit(1)
    
    try:
        api = LinearAPI(config=config)
        issues = api.get_team_issues(team_id, include_completed=show_all)
        
        if output_json:
            click.echo(json.dumps(issues, indent=2))
            return
        
        if not issues:
            click.echo("No todos found.")
            return
        
        # Pretty print table
        click.echo(f"{'ID':<10} {'State':<12} {'Prio':<8} {'Due Date':<20} Title")
        click.echo("-" * 80)
        
        for issue in issues:
            issue_id = issue.get('identifier', 'N/A')
            state = issue.get('state', {}).get('name', 'Unknown')[:11]
            prio = LinearAPI.priority_to_label(issue.get('priority', 0)) or 'None'
            due = issue.get('dueDate')
            due = due.split('T')[0] if due else '-'
            title = issue.get('title', 'Untitled')
            if len(title) > 30:
                title = title[:27] + '...'
            
            click.echo(f"{issue_id:<10} {state:<12} {prio:<8} {due:<20} {title}")
            
    except LinearAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except LinearError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('issue_id', required=True)
@click.pass_context
def done(ctx, issue_id):
    """Mark a todo as done.
    
    ISSUE_ID is the Linear issue identifier (e.g., TODO-123)
    """
    config = ctx.obj['config']
    done_state_id = config.done_state_id
    
    if not done_state_id:
        click.echo("Error: Done state ID not configured. Run 'uv run python main.py setup' first.", err=True)
        sys.exit(1)
    
    click.echo(f"Marking {issue_id} as done...")
    
    try:
        api = LinearAPI(config=config)
        result = api.update_issue(issue_id, state_id=done_state_id)
        
        if result.get('success'):
            issue = result['issue']
            click.echo(f"✓ {issue['identifier']} marked as {issue['state']['name']}: {issue['title']}")
        else:
            click.echo("Error: Failed to update issue", err=True)
            sys.exit(1)
            
    except LinearAPIError as e:
        click.echo(f"Error: {e}", err=True)
        if e.errors:
            click.echo(json.dumps(e.errors, indent=2), err=True)
        sys.exit(1)
    except LinearError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('issue_id', required=True)
@click.argument('when', required=False, default='tomorrow')
@click.pass_context
def snooze(ctx, issue_id, when):
    """Snooze a todo to a later date.

    ISSUE_ID is the Linear issue identifier (e.g., TODO-123)
    WHEN is a natural language date (default: tomorrow)

    Examples:
        linear-todo snooze TODO-123 "tomorrow"
        linear-todo snooze TODO-123 "next Friday"
        linear-todo snooze TODO-123 "in 3 days"
    """
    config = ctx.obj['config']

    # Get current time in configured timezone (or UTC if not set)
    tz = config.get_timezone()
    if tz:
        base_datetime = datetime.now(tz)
    else:
        base_datetime = datetime.utcnow()

    # Parse the new date
    new_date = DateParser.parse(when, base_datetime)
    if not new_date:
        click.echo(f"Error: Could not parse date: {when}", err=True)
        click.echo('Try formats like: tomorrow, Friday, next Monday, in 3 days', err=True)
        sys.exit(1)

    click.echo(f"Snoozing {issue_id} to {new_date}...")

    try:
        api = LinearAPI(config=config)
        due_date = DateParser.to_iso_datetime(new_date, end_of_day=True, tz=tz)
        result = api.update_issue(issue_id, due_date=due_date)
        
        if result.get('success'):
            issue = result['issue']
            click.echo(f"✓ {issue['identifier']} snoozed to {new_date}: {issue['title']}")
        else:
            click.echo("Error: Failed to update issue", err=True)
            sys.exit(1)
            
    except LinearAPIError as e:
        click.echo(f"Error: {e}", err=True)
        if e.errors:
            click.echo(json.dumps(e.errors, indent=2), err=True)
        sys.exit(1)
    except LinearError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Fun morning greetings for digest
# Note: secrets.choice used below for security scan compliance (B311)
MORNING_GREETINGS = [
    "🌅 Rise and grind!",
    "☕ Morning! Coffee's brewing, here's what's cooking:",
    "🌞 Good morning — let's knock these out:",
    "✨ Today's the day to tackle:",
    "🚀 Morning! Here's your hit list:",
    "🎯 Locked and loaded for today:",
    "🌤️ Rise and shine, here's what's due:",
]

NO_TASK_GREETINGS = [
    "🌅 Morning! Nothing urgent today — you're free.",
    "☕ Coffee time, no fires to put out today.",
    "🌞 Good morning! Clear skies, zero TODOs.",
    "✨ Morning! Looks like a chill day ahead.",
]


@cli.command()
@click.pass_context
def digest(ctx):
    """Show morning digest of today's todos with fun greetings."""
    import random
    from datetime import datetime
    
    config = ctx.obj['config']
    team_id = config.team_id
    
    if not team_id:
        click.echo("Error: Team ID not configured. Run 'uv run python main.py setup' first.", err=True)
        sys.exit(1)
    
    try:
        api = LinearAPI(config=config)
        issues = api.get_team_issues(team_id, include_completed=False)
        
        # Get today's date
        today = datetime.utcnow().date()
        today_epoch = today.toordinal()
        
        due_today = []
        
        for issue in issues:
            issue_id = issue.get('identifier')
            title = issue.get('title', 'Untitled')
            due_date = issue.get('dueDate')
            archived_at = issue.get('archivedAt')
            
            # Skip archived issues
            if archived_at:
                continue
            
            # Check if due today or overdue
            if due_date:
                due_date_str = due_date.split('T')[0]
                try:
                    due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    due_epoch = due_date_obj.toordinal()
                    
                    # Include overdue and today
                    if due_epoch <= today_epoch:
                        line = f"  • [{issue_id}](https://linear.app/issue/{issue_id}): {title}"
                        due_today.append(line)
                except ValueError:
                    pass
        
        # Pick random greeting
        if due_today:
            greeting = secrets.choice(MORNING_GREETINGS)
            click.echo(greeting)
            click.echo("")
            for line in due_today:
                click.echo(line)
        else:
            greeting = secrets.choice(NO_TASK_GREETINGS)
            click.echo(greeting)
            
    except LinearAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except LinearError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def review(ctx):
    """Show daily review of todos organized by urgency."""
    from datetime import datetime
    
    config = ctx.obj['config']
    team_id = config.team_id
    
    if not team_id:
        click.echo("Error: Team ID not configured. Run 'uv run python main.py setup' first.", err=True)
        sys.exit(1)
    
    try:
        api = LinearAPI(config=config)
        issues = api.get_team_issues(team_id, include_completed=False)
        
        # Get today's date boundaries
        today = datetime.utcnow().date()
        today_epoch = today.toordinal()
        next_7_days_epoch = today_epoch + 7
        next_28_days_epoch = today_epoch + 28
        
        # Categorize issues
        due_today = []
        due_this_week = []
        due_this_month = []
        no_due_date = []
        
        for issue in issues:
            issue_id = issue.get('identifier')
            title = issue.get('title', 'Untitled')
            due_date = issue.get('dueDate')
            archived_at = issue.get('archivedAt')
            
            # Skip archived issues
            if archived_at:
                continue
            
            line = f"  • [{issue_id}](https://linear.app/issue/{issue_id}): {title}"
            
            # Categorize by due date
            if not due_date:
                no_due_date.append(line)
            else:
                # Parse due date (format: 2024-02-11T23:59:59.000Z)
                due_date_str = due_date.split('T')[0]
                try:
                    due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    due_epoch = due_date_obj.toordinal()
                    
                    if due_epoch <= today_epoch:
                        # Overdue or due today
                        due_today.append(line)
                    elif due_epoch <= next_7_days_epoch:
                        due_this_week.append(line)
                    elif due_epoch <= next_28_days_epoch:
                        due_this_month.append(line)
                except ValueError:
                    no_due_date.append(line)
        
        # Build output - match daily-todo-review.sh format
        output = []
        
        # DO TODAY section
        output.append("**🚨 Do Today:**")
        if due_today:
            output.extend(due_today)
        else:
            output.append("  • nothing to see here")
        output.append("")
        
        # Board overview by due date ranges
        output.append("**📊 Board Overview:**")
        output.append("")
        
        output.append("**By End of Week:**")
        if due_this_week:
            output.extend(due_this_week)
        else:
            output.append("  • nothing to see here")
        output.append("")
        
        output.append("**By End of Month:**")
        if due_this_month:
            output.extend(due_this_month)
        else:
            output.append("  • nothing to see here")
        
        # Tickets without due dates
        if no_due_date:
            output.append("")
            output.append("**No Due Date:**")
            output.extend(no_due_date)
        
        click.echo("\n".join(output))
            
    except LinearAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except LinearError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Keep aliases for backward compatibility
@cli.command(name='ls', hidden=True)
@click.pass_context
def ls_alias(ctx):
    """Alias for list command."""
    ctx.invoke(list_command)


@cli.command(name='complete', hidden=True)
@click.argument('issue_id', required=True)
@click.pass_context
def complete_alias(ctx, issue_id):
    """Alias for done command."""
    ctx.invoke(done, issue_id=issue_id)


@cli.command(name='finish', hidden=True)
@click.argument('issue_id', required=True)
@click.pass_context
def finish_alias(ctx, issue_id):
    """Alias for done command."""
    ctx.invoke(done, issue_id=issue_id)


@cli.command(name='defer', hidden=True)
@click.argument('issue_id', required=True)
@click.argument('when', required=False, default='tomorrow')
@click.pass_context
def defer_alias(ctx, issue_id, when):
    """Alias for snooze command."""
    ctx.invoke(snooze, issue_id=issue_id, when=when)


# Entry point for the CLI
def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
