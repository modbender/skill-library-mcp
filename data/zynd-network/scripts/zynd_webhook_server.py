#!/usr/bin/env python3
"""
Start a webhook server to receive incoming messages from other Zynd agents.

Listens for HTTP POST requests on the configured port, processes incoming
agent messages, and prints them to stdout for the OpenClaw agent to read.

Usage:
    python3 zynd_webhook_server.py --port 6000
    python3 zynd_webhook_server.py --port 6000 --config-dir .zynd-agent
"""

import argparse
import json
import os
import sys
import signal
import time
import threading


def main():
    parser = argparse.ArgumentParser(
        description="Start a webhook server to receive messages from other Zynd agents"
    )
    parser.add_argument(
        "--port", type=int, default=6000, help="Port to listen on (default: 6000)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--config-dir",
        required=True,
        help="Config directory with agent identity (e.g., .agent-my-bot)",
    )
    parser.add_argument(
        "--registry-url",
        default="https://registry.zynd.ai",
        help="Zynd registry URL (default: https://registry.zynd.ai)",
    )
    parser.add_argument(
        "--auto-respond",
        action="store_true",
        help="Automatically acknowledge received messages",
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("ZYND_API_KEY")
    if not api_key:
        print("ERROR: ZYND_API_KEY environment variable is not set.")
        print("Get your API key from https://dashboard.zynd.ai")
        sys.exit(1)

    try:
        from zyndai_agent.config_manager import ConfigManager
        from zyndai_agent.message import AgentMessage
        from flask import Flask, request, jsonify

        # Load agent config
        config = ConfigManager.load_config(args.config_dir)
        if config is None:
            print("ERROR: No agent identity found.")
            print(
                f'Register first with: python3 zynd_register.py --name \'My Agent\' --capabilities \'{{"ai":["nlp"],"protocols":["http"],"services":["general"]}}\''
            )
            sys.exit(1)

        agent_id = config["id"]
        identity_credential = config["did"]
        agent_name = config.get("name", "Unknown Agent")

        # Track received messages
        received_messages = []
        lock = threading.Lock()

        # Create Flask app
        app = Flask(f"zynd-webhook-{agent_id}")

        # Suppress Flask request logs
        import logging

        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        @app.route("/webhook", methods=["POST"])
        def handle_webhook():
            """Handle async incoming messages."""
            try:
                if not request.is_json:
                    return jsonify(
                        {"error": "Content-Type must be application/json"}
                    ), 400

                payload = request.get_json()
                message = AgentMessage.from_dict(payload)

                # Print the message for the OpenClaw agent to read
                print(f"\n{'=' * 60}")
                print(f"  INCOMING MESSAGE")
                print(f"{'=' * 60}")
                print(f"  From     : {message.sender_id}")
                print(f"  Type     : {message.message_type}")
                print(f"  ID       : {message.message_id}")
                print(f"  Content  :")
                print(f"  {message.content}")
                print(f"{'=' * 60}\n")

                with lock:
                    received_messages.append(
                        {
                            "message": message.to_dict(),
                            "received_at": time.time(),
                            "source_ip": request.remote_addr,
                        }
                    )

                return jsonify(
                    {
                        "status": "received",
                        "message_id": message.message_id,
                        "agent_id": agent_id,
                        "timestamp": time.time(),
                    }
                ), 200

            except Exception as e:
                print(f"ERROR handling message: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route("/webhook/sync", methods=["POST"])
        def handle_webhook_sync():
            """Handle sync incoming messages (waits for response)."""
            try:
                if not request.is_json:
                    return jsonify(
                        {"error": "Content-Type must be application/json"}
                    ), 400

                payload = request.get_json()
                message = AgentMessage.from_dict(payload)

                # Print the message
                print(f"\n{'=' * 60}")
                print(f"  INCOMING SYNC REQUEST")
                print(f"{'=' * 60}")
                print(f"  From     : {message.sender_id}")
                print(f"  Type     : {message.message_type}")
                print(f"  ID       : {message.message_id}")
                print(f"  Content  :")
                print(f"  {message.content}")
                print(f"{'=' * 60}\n")

                with lock:
                    received_messages.append(
                        {
                            "message": message.to_dict(),
                            "received_at": time.time(),
                            "source_ip": request.remote_addr,
                            "sync": True,
                        }
                    )

                if args.auto_respond:
                    return jsonify(
                        {
                            "status": "success",
                            "message_id": message.message_id,
                            "response": f"Message received by {agent_name}. Processing your request.",
                            "timestamp": time.time(),
                        }
                    ), 200
                else:
                    # Return acknowledgment without a processed response
                    return jsonify(
                        {
                            "status": "success",
                            "message_id": message.message_id,
                            "response": f"Message received by {agent_name}. This agent is in listen-only mode.",
                            "timestamp": time.time(),
                        }
                    ), 200

            except Exception as e:
                print(f"ERROR handling sync message: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify(
                {
                    "status": "ok",
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "messages_received": len(received_messages),
                    "timestamp": time.time(),
                }
            ), 200

        @app.route("/messages", methods=["GET"])
        def list_messages():
            """List received messages."""
            with lock:
                return jsonify(
                    {
                        "count": len(received_messages),
                        "messages": received_messages[-20:],  # Last 20
                    }
                ), 200

        # Start the server
        print("=" * 60)
        print("  ZYND WEBHOOK SERVER")
        print("=" * 60)
        print(f"  Agent    : {agent_name}")
        print(f"  Agent ID : {agent_id}")
        print(f"  Listening: http://{args.host}:{args.port}")
        print(f"  Endpoints:")
        print(f"    POST /webhook      - Receive async messages")
        print(f"    POST /webhook/sync - Receive sync messages")
        print(f"    GET  /health       - Health check")
        print(f"    GET  /messages     - List received messages")
        print("=" * 60)
        print()
        print("Waiting for incoming messages... (Ctrl+C to stop)")
        print()

        # Handle graceful shutdown
        def handle_sigint(sig, frame):
            print("\nShutting down webhook server...")
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_sigint)

        # Run Flask
        app.run(
            host=args.host,
            port=args.port,
            debug=False,
            use_reloader=False,
            threaded=True,
        )

    except ImportError as e:
        if "flask" in str(e).lower():
            print("ERROR: Flask is not installed.")
            print("Run: pip install flask")
        else:
            print("ERROR: zyndai-agent SDK is not installed.")
            print("Run the setup script first: bash scripts/setup.sh")
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"ERROR: Port {args.port} is already in use.")
            print(f"Try a different port: --port {args.port + 1}")
        else:
            print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
