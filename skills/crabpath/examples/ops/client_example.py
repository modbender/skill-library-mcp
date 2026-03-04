#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess


def main() -> None:
    proc = subprocess.Popen(
        [
            "python3",
            "-m",
            "crabpath",
            "daemon",
            "--state",
            "~/.crabpath/main/state.json",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    def call(method: str, params: dict | None = None, req_id: str = "1") -> dict:
        if proc.stdin is None or proc.stdout is None:
            raise RuntimeError("daemon process pipes are not available")
        payload = {"id": req_id, "method": method, "params": params or {}}
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    result = call("query", {"query": "how to deploy", "top_k": 4})
    print(result)

    fired_nodes = result["result"].get("fired_nodes", [])
    if fired_nodes:
        result = call("learn", {"fired_nodes": fired_nodes, "outcome": 1.0}, req_id="2")
        print(result)

    result = call("shutdown", {}, req_id="3")
    print(result)


if __name__ == "__main__":
    main()
