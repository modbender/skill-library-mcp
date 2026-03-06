#!/usr/bin/env python3
"""
LimeSurvey CLI tool
Common operations via RemoteControl 2 API
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from limesurvey_client import LimeSurveyClient, LimeSurveySession, LimeSurveyError


def get_config():
    """Load LimeSurvey configuration from environment or config file"""
    config = {
        'url': os.getenv('LIMESURVEY_URL'),
        'username': os.getenv('LIMESURVEY_USER'),
        'password': os.getenv('LIMESURVEY_PASSWORD'),
    }
    
    # Check for missing config
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"Error: Missing configuration: {', '.join(missing)}", file=sys.stderr)
        print("\nSet environment variables:", file=sys.stderr)
        print("  LIMESURVEY_URL - e.g., https://survey.example.com/index.php/admin/remotecontrol", file=sys.stderr)
        print("  LIMESURVEY_USER - your username", file=sys.stderr)
        print("  LIMESURVEY_PASSWORD - your password", file=sys.stderr)
        sys.exit(1)
    
    return config


def cmd_list_surveys(args):
    """List all surveys accessible to the user"""
    config = get_config()
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        surveys = client.call('list_surveys', client.session_key, args.username)
        
        if not surveys:
            print("No surveys found")
            return
        
        if args.json:
            print(json.dumps(surveys, indent=2))
        else:
            print(f"{'ID':<10} {'Active':<8} {'Title'}")
            print("-" * 80)
            for survey in surveys:
                sid = survey.get('sid', 'N/A')
                active = survey.get('active', 'N/A')
                title = survey.get('surveyls_title', 'N/A')
                print(f"{sid:<10} {active:<8} {title}")


def cmd_export_responses(args):
    """Export survey responses"""
    config = get_config()
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        result = client.call(
            'export_responses',
            client.session_key,
            args.survey_id,
            args.format,
            args.language or None,
            args.completion_status,
            args.heading_type,
            args.response_type
        )
        
        if isinstance(result, dict) and 'status' in result:
            print(f"Error: {result['status']}", file=sys.stderr)
            sys.exit(1)
        
        # Decode base64 response
        decoded = client.decode_base64(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(decoded)
            print(f"Exported to: {args.output}")
        else:
            print(decoded)


def cmd_list_participants(args):
    """List survey participants"""
    config = get_config()
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        participants = client.call(
            'list_participants',
            client.session_key,
            args.survey_id,
            args.start,
            args.limit,
            args.unused,
            args.attributes if args.attributes else False
        )
        
        if not participants:
            print("No participants found")
            return
        
        if args.json:
            print(json.dumps(participants, indent=2))
        else:
            print(f"{'Token ID':<10} {'Token':<20} {'Email'}")
            print("-" * 80)
            for p in participants:
                tid = p.get('tid', 'N/A')
                token = p.get('token', 'N/A')
                info = p.get('participant_info', {})
                email = info.get('email', 'N/A')
                print(f"{tid:<10} {token:<20} {email}")


def cmd_add_participants(args):
    """Add participants to a survey"""
    config = get_config()
    
    # Read participant data from JSON file or stdin
    if args.file:
        with open(args.file, 'r') as f:
            participant_data = json.load(f)
    else:
        participant_data = json.load(sys.stdin)
    
    if not isinstance(participant_data, list):
        participant_data = [participant_data]
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        result = client.call(
            'add_participants',
            client.session_key,
            args.survey_id,
            participant_data,
            args.create_token
        )
        
        print(json.dumps(result, indent=2))


def cmd_invite_participants(args):
    """Send invitation emails to participants"""
    config = get_config()
    
    # Parse token IDs
    token_ids = None
    if args.token_ids:
        token_ids = [int(tid) for tid in args.token_ids.split(',')]
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        result = client.call(
            'invite_participants',
            client.session_key,
            args.survey_id,
            token_ids
        )
        
        print(json.dumps(result, indent=2))


def cmd_activate_survey(args):
    """Activate a survey"""
    config = get_config()
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        result = client.call(
            'activate_survey',
            client.session_key,
            args.survey_id
        )
        
        if isinstance(result, dict) and 'status' in result:
            print(f"Status: {result['status']}")
        else:
            print(json.dumps(result, indent=2))


def cmd_get_summary(args):
    """Get survey summary statistics"""
    config = get_config()
    
    with LimeSurveySession(config['url'], config['username'], config['password']) as client:
        result = client.call(
            'get_summary',
            client.session_key,
            args.survey_id,
            args.stat_name
        )
        
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(f"{args.stat_name}: {result}")


def main():
    parser = argparse.ArgumentParser(
        description='LimeSurvey RemoteControl CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # list-surveys
    p_list = subparsers.add_parser('list-surveys', help='List all surveys')
    p_list.add_argument('--username', help='Filter by username (admin only)')
    p_list.add_argument('--json', action='store_true', help='Output as JSON')
    p_list.set_defaults(func=cmd_list_surveys)
    
    # export-responses
    p_export = subparsers.add_parser('export-responses', help='Export survey responses')
    p_export.add_argument('survey_id', type=int, help='Survey ID')
    p_export.add_argument('--format', default='csv', choices=['csv', 'pdf', 'xls', 'json'], help='Export format')
    p_export.add_argument('--language', help='Language code')
    p_export.add_argument('--completion-status', default='all', choices=['all', 'complete', 'incomplete'])
    p_export.add_argument('--heading-type', default='code', choices=['code', 'full', 'abbreviated'])
    p_export.add_argument('--response-type', default='short', choices=['short', 'long'])
    p_export.add_argument('-o', '--output', help='Output file (default: stdout)')
    p_export.set_defaults(func=cmd_export_responses)
    
    # list-participants
    p_participants = subparsers.add_parser('list-participants', help='List survey participants')
    p_participants.add_argument('survey_id', type=int, help='Survey ID')
    p_participants.add_argument('--start', type=int, default=0, help='Start index')
    p_participants.add_argument('--limit', type=int, default=100, help='Max results')
    p_participants.add_argument('--unused', action='store_true', help='Show only unused tokens')
    p_participants.add_argument('--attributes', nargs='+', help='Additional attributes to fetch')
    p_participants.add_argument('--json', action='store_true', help='Output as JSON')
    p_participants.set_defaults(func=cmd_list_participants)
    
    # add-participants
    p_add = subparsers.add_parser('add-participants', help='Add participants to survey')
    p_add.add_argument('survey_id', type=int, help='Survey ID')
    p_add.add_argument('--file', help='JSON file with participant data (default: stdin)')
    p_add.add_argument('--create-token', action='store_true', default=True, help='Create access tokens')
    p_add.set_defaults(func=cmd_add_participants)
    
    # invite-participants
    p_invite = subparsers.add_parser('invite-participants', help='Send invitation emails')
    p_invite.add_argument('survey_id', type=int, help='Survey ID')
    p_invite.add_argument('--token-ids', help='Comma-separated token IDs (default: all)')
    p_invite.set_defaults(func=cmd_invite_participants)
    
    # activate-survey
    p_activate = subparsers.add_parser('activate-survey', help='Activate a survey')
    p_activate.add_argument('survey_id', type=int, help='Survey ID')
    p_activate.set_defaults(func=cmd_activate_survey)
    
    # get-summary
    p_summary = subparsers.add_parser('get-summary', help='Get survey statistics')
    p_summary.add_argument('survey_id', type=int, help='Survey ID')
    p_summary.add_argument('--stat-name', default='all', help='Statistic name (default: all)')
    p_summary.set_defaults(func=cmd_get_summary)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except LimeSurveyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
