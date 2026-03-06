#!/usr/bin/env python3
"""
Dialogflow CX Conversations CLI - Sessions and testing

Usage:
    python conversations.py detect-intent --agent AGENT_NAME --text "Hello"
    python conversations.py match-intent --agent AGENT_NAME --text "Hello"

Requires:
    - google-cloud-dialogflow-cx
    - google-auth

Install:
    pip install google-cloud-dialogflow-cx google-auth
"""

import argparse
import json
import sys

try:
    from google.cloud.dialogflowcx_v3beta1 import SessionsClient, TextInput, QueryInput, DetectIntentRequest, MatchIntentRequest
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("Error: google-cloud-dialogflow-cx not installed")
    print("Run: pip install google-cloud-dialogflow-cx google-auth")
    sys.exit(1)


def detect_intent(agent_name: str, text: str, session_id: str = "test-session"):
    """Send a message to the agent and get response."""
    client = SessionsClient()
    session = f"{agent_name}/sessions/{session_id}"
    
    text_input = TextInput(text=text)
    query_input = QueryInput(text=text_input, language_code="en")
    
    request = DetectIntentRequest(
        session=session,
        query_input=query_input
    )
    
    response = client.detect_intent(request=request)
    result = response.query_result
    
    print(f"User: {text}")
    print(f"Intent: {result.intent.display_name if result.intent else 'None'}")
    print(f"Confidence: {result.intent_detection_confidence:.2f}")
    print(f"Agent Response:")
    for msg in result.response_messages:
        if msg.text:
            for t in msg.text.text:
                print(f"  {t}")


def match_intent(agent_name: str, text: str, session_id: str = "test-session"):
    """Match intent without advancing conversation state."""
    client = SessionsClient()
    session = f"{agent_name}/sessions/{session_id}"
    
    text_input = TextInput(text=text)
    query_input = QueryInput(text=text_input, language_code="en")
    
    request = MatchIntentRequest(
        session=session,
        query_input=query_input
    )
    
    response = client.match_intent(request=request)
    
    print(f"User: {text}")
    print("Matching intents:")
    for match in response.matches:
        print(f"  Intent: {match.intent.display_name}")
        print(f"  Confidence: {match.confidence:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Dialogflow CX Conversations CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # detect-intent
    p = subparsers.add_parser("detect-intent", help="Send message to agent")
    p.add_argument("--agent", required=True, help="Full agent name")
    p.add_argument("--text", required=True, help="User message")
    p.add_argument("--session", default="cli-session", help="Session ID")
    
    # match-intent
    p = subparsers.add_parser("match-intent", help="Match intent without state change")
    p.add_argument("--agent", required=True, help="Full agent name")
    p.add_argument("--text", required=True, help="User message")
    p.add_argument("--session", default="cli-session", help="Session ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "detect-intent":
        detect_intent(args.agent, args.text, args.session)
    elif args.command == "match-intent":
        match_intent(args.agent, args.text, args.session)


if __name__ == "__main__":
    main()