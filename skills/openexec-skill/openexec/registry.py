from typing import Callable, Dict

_actions: Dict[str, Callable] = {}

def register_action(name: str, handler: Callable):
    _actions[name] = handler

def get_action(name: str) -> Callable:
    handler = _actions.get(name)
    if handler is None:
        raise ValueError(f"Unknown action: {name}")
    return handler

def list_actions():
    return list(_actions.keys())

def _demo_echo(payload: dict) -> dict:
    return {"echo": payload}

def _demo_add(payload: dict) -> dict:
    a = payload.get("a", 0)
    b = payload.get("b", 0)
    return {"sum": a + b}

register_action("echo", _demo_echo)
register_action("add", _demo_add)
