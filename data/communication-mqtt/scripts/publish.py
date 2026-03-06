import json
import time
from textwrap import dedent

import typer
import paho.mqtt.publish as publish

app = typer.Typer(add_completion=False)

# 🔒 고정 MQTT 설정
BROKER = "localhost"
PORT = 1883
QOS = 1
RETAIN = True


def now_ts() -> int:
    return int(time.time())


def publish_message(topic: str, payload: dict):
    publish.single(
        topic=topic,
        payload=json.dumps(payload),
        hostname=BROKER,
        port=PORT,
        qos=QOS,
        retain=RETAIN,
    )
    typer.echo(f"Published to {topic}")
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def intro(
    agent_id: str = typer.Option(..., "--agent-id", "-i"),
    role: str = typer.Option(..., "--role", "-r"),
):
    """
    Publish agent introduction.
    Topic: agents/{agent_id}/intro
    """
    topic = f"agents/{agent_id}/intro"

    payload = {
        "agent_id": agent_id,
        "role": role,
        "channel": dedent(f"""
            You can speak to me directly using the following command.
            ```bash
            openclaw --agent {agent_id} --message "message_here"
            ```
        """).strip(),
        "created_at": now_ts(),
    }

    publish_message(topic, payload)


@app.command()
def status(
    agent_id: str = typer.Option(..., "--agent-id", "-i"),
    activity: str = typer.Option(..., "--activity", "-a"),
):
    """
    Publish agent status.
    Topic: agents/{agent_id}/status
    """
    topic = f"agents/{agent_id}/status"

    payload = {
        "agent_id": agent_id,
        "activity": activity,
        "ts": now_ts(),
    }

    publish_message(topic, payload)


if __name__ == "__main__":
    app()
