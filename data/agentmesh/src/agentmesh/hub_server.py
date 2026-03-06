"""
AgentMesh Hub Server – standalone entry point.

Usage:
  python -m agentmesh.hub_server
  python -m agentmesh.hub_server --host 0.0.0.0 --port 7700
"""

import argparse
import logging
from .hub import NetworkHubServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(
        description="AgentMesh Hub Server – encrypted AI-agent message broker"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7700, help="Bind port (default: 7700)")
    args = parser.parse_args()

    server = NetworkHubServer(host=args.host, port=args.port)
    server.start(block=True)


if __name__ == "__main__":
    main()
