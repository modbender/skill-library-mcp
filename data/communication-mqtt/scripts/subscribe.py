import json
import time
import typer
import threading
import paho.mqtt.client as mqtt

app = typer.Typer(add_completion=False)

# 🔒 고정 MQTT 설정
BROKER = "localhost"
PORT = 1883
KEEPALIVE = 30
QOS = 1

# wait=0이어도 retained 수신을 위해 최소로 기다릴 시간(초)
DEFAULT_GRACE_SEC = 0.3


def _topic(kind: str, agent_id: str | None) -> str:
    return f"agents/{agent_id}/{kind}" if agent_id else f"agents/+/{kind}"


def _print_msg(msg: mqtt.MQTTMessage):
    retained = " (retained)" if getattr(msg, "retain", False) else ""
    payload_raw = msg.payload.decode(errors="replace")
    try:
        data = json.loads(payload_raw)
    except Exception:
        data = payload_raw
    print(f"[RECV{retained}] {msg.topic} -> {data}")


def _run_subscribe(kind: str, agent_id: str | None, wait_sec: float):
    topic = _topic(kind, agent_id)

    connected = threading.Event()

    def on_connect(client, userdata, flags, rc):
        print("Connected:", rc)
        print(f"Subscribing: {topic}")
        client.subscribe(topic, qos=QOS)
        connected.set()

    def on_message(client, userdata, msg):
        _print_msg(msg)

    client = mqtt.Client(client_id=f"sub-{kind}", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=KEEPALIVE)

    # loop_forever 대신 수동 루프
    # 1) connect + subscribe 완료될 때까지 잠깐 돌림 (최대 2초)
    deadline_connect = time.time() + 2.0
    while not connected.is_set() and time.time() < deadline_connect:
        client.loop(timeout=0.1)

    if not connected.is_set():
        print("Failed to connect/subscribe within 2 seconds.")
        client.disconnect()
        return

    # 2) 메시지 수신 대기(기본 0초지만 grace는 줌)
    run_for = max(float(wait_sec), DEFAULT_GRACE_SEC)
    deadline = time.time() + run_for
    while time.time() < deadline:
        client.loop(timeout=0.1)

    client.disconnect()


@app.command()
def intro(
    agent_id: str = typer.Option(
        None,
        "--agent-id",
        "-i",
        help="If provided: agents/<agent_id>/intro. Otherwise: agents/+/intro",
    ),
    wait: float = typer.Option(
        0.0,
        "--wait",
        "-w",
        help="Seconds to keep listening after subscribe (default: 0, one-shot).",
    ),
):
    """
    Subscribe and print intro messages, then exit.
    """
    _run_subscribe("intro", agent_id, wait)


@app.command()
def status(
    agent_id: str = typer.Option(
        None,
        "--agent-id",
        "-i",
        help="If provided: agents/<agent_id>/status. Otherwise: agents/+/status",
    ),
    wait: float = typer.Option(
        0.0,
        "--wait",
        "-w",
        help="Seconds to keep listening after subscribe (default: 0, one-shot).",
    ),
):
    """
    Subscribe and print status messages, then exit.
    """
    _run_subscribe("status", agent_id, wait)


if __name__ == "__main__":
    app()
