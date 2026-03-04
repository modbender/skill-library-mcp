#!/usr/bin/env python3
"""
Discord Project Manager - Main CLI

Unified interface for thread, meeting, and permission management.
"""

import sys
from pathlib import Path

# Add lib to path
lib_path = Path(__file__).parent.parent / 'lib'
sys.path.insert(0, str(lib_path))

# Import without relative imports
import registry
import thread
import permissions
import forum
import projects


def print_usage():
    """Print usage information."""
    print("""Discord Project Manager CLI

Usage: discord-pm.py <command> [args]

Commands:
  config init                             - Initialize configuration from OpenClaw
  config get                              - Show current configuration
  config set-guild <id>                   - Set guild ID
  config set-forum <id>                   - Set default forum ID
  
  registry init                           - Initialize agent registry from OpenClaw config
  registry list                           - List all agents
  registry add <id> <account> <user> <channel> <patterns...>
  registry set-guild <id>                 - Set guild ID (deprecated, use config set-guild)
  registry set-default-forum <id>         - Set default forum channel ID (deprecated, use config set-forum)
  
  forum-channel create <name> [--emoji <emoji>] [--description <text>]
  forum-channel guide <name> [--emoji <emoji>] [--description <text>]  (legacy)
  forum-channel set-default <channel_id>  - Set default forum channel
  forum-channel add <channel_id> <name>   - Add forum channel to registry
  forum-channel remove <name>             - Remove forum channel from registry
  forum-channel list                      - List all forum channels
  
  thread create --name <name> --owner <agent> --participants <agents...> [--forum-channel <id>] [--no-mention] [--message <text>] [--description <text>]
  thread archive <thread_id>              - Archive thread (remove all permissions)
  thread status <thread_id>               - Show thread permissions and participants
  thread list [--active] [--archived] [--owner <agent>]
  
  permissions add <thread_id> <agent1> [agent2...] [--no-mention]
  permissions remove <thread_id> <agent1> [agent2...]
  permissions mention-mode <thread_id> <on|off> <agents...|--all>
  
  project list [--active] [--archived] [--agent <name>]  - List projects
  project info <thread_id>                - Show project details
  project describe <thread_id> <text>     - Update project description
  project update <thread_id> --next-action <text>  - Update next action

Examples:
  # Initialize registry
  ./discord-pm.py registry init
  
  # Create a new forum channel directly
  ./discord-pm.py forum-channel create casino \\
    --emoji "🏗️" \\
    --description "Casino project development"
  
  # Or get guide for manual creation (legacy)
  ./discord-pm.py forum-channel guide casino \\
    --emoji "🏗️" \\
    --description "Casino project development"
  
  # Then create it in agent session using message tool
  # Finally register the channel_id
  ./discord-pm.py forum-channel add <channel_id> casino
  
  # Set default forum channel (for small projects)
  ./discord-pm.py forum-channel set-default <forum_channel_id>
  
  # Create small project thread (uses default forum)
  ./discord-pm.py thread create \\
    --name "fix-bug-123" \\
    --owner agent-a \\
    --participants "agent-a,agent-b"
  
  # Create sub-project thread (in specific forum channel)
  ./discord-pm.py thread create \\
    --name "backend" \\
    --owner agent-a \\
    --participants "agent-a,agent-b" \\
    --forum-channel <forum_channel_id> \\
    --description "Backend development" \\
    --message "Project kickoff"
  
  # Archive thread
  ./discord-pm.py thread archive <thread_id>
  
  # Check thread status
  ./discord-pm.py thread status <thread_id>
  
  # Add participant
  ./discord-pm.py permissions add <thread_id> agent-c
  
  # Remove participant
  ./discord-pm.py permissions remove <thread_id> agent-c
  
  # Toggle mention mode
  ./discord-pm.py permissions mention-mode <thread_id> off agent-a agent-b
  
  # List your projects
  ./discord-pm.py project list --agent agent-a
  
  # Update next action
  ./discord-pm.py project update <thread_id> --next-action "Waiting for API integration"
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'config':
        if len(sys.argv) < 3:
            print("Error: config command required")
            print_usage()
            sys.exit(1)
        
        sys.argv = ['skill_config.py'] + sys.argv[2:]
        import skill_config
        skill_config.main()
    
    elif command == 'registry':
        if len(sys.argv) < 3:
            print("Error: registry command required")
            print_usage()
            sys.exit(1)
        
        sys.argv = ['registry.py'] + sys.argv[2:]
        registry.main()
    
    elif command == 'forum-channel':
        if len(sys.argv) < 3:
            print("Error: forum-channel command required")
            print_usage()
            sys.exit(1)
        
        sys.argv = ['forum.py'] + sys.argv[2:]
        forum.main()
    
    elif command == 'thread':
        if len(sys.argv) < 3:
            print("Error: thread command required")
            print_usage()
            sys.exit(1)
        
        sys.argv = ['thread.py'] + sys.argv[2:]
        thread.main()
    
    elif command == 'permissions':
        if len(sys.argv) < 3:
            print("Error: permissions command required")
            print_usage()
            sys.exit(1)
        
        sys.argv = ['permissions.py'] + sys.argv[2:]
        permissions.main()
    
    elif command == 'project':
        if len(sys.argv) < 3:
            print("Error: project command required")
            print_usage()
            sys.exit(1)
        
        subcmd = sys.argv[2]
        
        if subcmd == 'list':
            status = None
            agent = None
            if '--active' in sys.argv:
                status = 'active'
            elif '--archived' in sys.argv:
                status = 'archived'
            if '--agent' in sys.argv:
                idx = sys.argv.index('--agent')
                if idx + 1 < len(sys.argv):
                    agent = sys.argv[idx + 1]
            
            if agent:
                result = projects.list_by_agent(agent, status)
            else:
                result = projects.list_projects(status)
            
            if not result:
                print("No projects found.")
            else:
                for tid, info in result.items():
                    status_icon = "✅" if info.get("status") == "active" else "📦"
                    desc = info.get("description", "")
                    desc_str = f" — {desc}" if desc else ""
                    role = info.get("role", "")
                    role_str = f" [{role}]" if role else ""
                    next_action = info.get("nextAction", "")
                    print(f"{status_icon} {info['name']}{desc_str}{role_str}")
                    print(f"   ID: {tid} | Owner: {info['owner']} | Participants: {', '.join(info.get('participants', []))}")
                    if next_action:
                        print(f"   Next: {next_action}")
                    print()
        
        elif subcmd == 'info':
            if len(sys.argv) < 4:
                print("Error: thread_id required")
                sys.exit(1)
            info = projects.get_thread(sys.argv[3])
            if not info:
                print(f"Project not found: {sys.argv[3]}")
                sys.exit(1)
            import json
            print(json.dumps(info, indent=2, ensure_ascii=False))
        
        elif subcmd == 'describe':
            if len(sys.argv) < 5:
                print("Error: thread_id and description required")
                sys.exit(1)
            ok = projects.update_description(sys.argv[3], sys.argv[4])
            if ok:
                print(f"✅ Description updated for {sys.argv[3]}")
            else:
                print(f"Project not found: {sys.argv[3]}")
                sys.exit(1)
        
        elif subcmd == 'update':
            if len(sys.argv) < 4:
                print("Error: thread_id required")
                sys.exit(1)
            thread_id = sys.argv[3]
            args = sys.argv[4:]
            i = 0
            while i < len(args):
                if args[i] == '--next-action' and i + 1 < len(args):
                    ok = projects.update_next_action(thread_id, args[i + 1])
                    if ok:
                        print(f"✅ Next action updated for {thread_id}")
                    else:
                        print(f"Project not found: {thread_id}")
                        sys.exit(1)
                    i += 2
                else:
                    i += 1
        
        else:
            print(f"Unknown project command: {subcmd}")
            print_usage()
            sys.exit(1)
    
    elif command in ('help', '--help', '-h'):
        print_usage()
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
