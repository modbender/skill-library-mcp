from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

import redis


def ensure_group(r: redis.Redis, stream: str, group: str) -> None:
    try:
        r.xgroup_create(stream, group, id="0-0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            return
        raise


def read_group(
    r: redis.Redis,
    stream: str,
    group: str,
    consumer: str,
    count: int,
    block_ms: int,
    use_pending: bool,
) -> List[Tuple[str, List[Tuple[str, Dict[bytes, bytes]]]]]:
    # '>' for new messages, '0' to claim pending backlog
    stream_id = "0" if use_pending else ">"
    return r.xreadgroup(group, consumer, {stream: stream_id}, count=count, block=block_ms)


def ack(r: redis.Redis, stream: str, group: str, event_id: str) -> None:
    r.xack(stream, group, event_id)
