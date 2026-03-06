# Spread image layout: canvas size, card positions/sizes, card image root URL
# Card image URL matches tarot_game/constants/tarotCards.ts IMG_ROOT

from .types import SpreadType

# Same as tarot_game IMG_ROOT: https://www.sacred-texts.com/tarot/pkt/img/
IMAGE_ROOT = "https://www.sacred-texts.com/tarot/pkt/img/"

CARD_RATIO = 2 / 3


def _card_size(width: int) -> tuple[int, int]:
    return width, round(width / CARD_RATIO)


def _slots_three() -> list[dict]:
    w, h = _card_size(220)
    y = 30
    gap = (900 - 3 * w) / 4
    return [
        {"x": int(gap), "y": y, "width": w, "height": h},
        {"x": int(gap * 2 + w), "y": y, "width": w, "height": h},
        {"x": int(gap * 3 + w * 2), "y": y, "width": w, "height": h},
    ]


def _slots_one() -> list[dict]:
    w, h = _card_size(320)
    return [
        {"x": (520 - w) // 2, "y": (820 - h) // 2, "width": w, "height": h}
    ]


def _slots_five() -> list[dict]:
    w, h = _card_size(180)
    y = 40
    gap = (1100 - 5 * w) / 6
    return [
        {"x": int(gap + i * (w + gap)), "y": y, "width": w, "height": h}
        for i in range(5)
    ]


def _slots_celtic() -> list[dict]:
    cw, ch = 100, round(100 / CARD_RATIO)
    cx, cy, d = 280, 300, 115
    return [
        {"x": cx - cw // 2, "y": cy - ch // 2, "width": cw, "height": ch},
        {"x": cx - cw // 2, "y": cy - d - ch, "width": cw, "height": ch},
        {"x": cx - cw // 2, "y": cy + d, "width": cw, "height": ch},
        {"x": cx - d - cw, "y": cy - ch // 2, "width": cw, "height": ch},
        {"x": cx + d, "y": cy - ch // 2, "width": cw, "height": ch},
        {"x": cx - cw // 2, "y": cy - 2 * d - ch, "width": cw, "height": ch},
        {"x": 750, "y": 50, "width": cw, "height": ch},
        {"x": 750, "y": 220, "width": cw, "height": ch},
        {"x": 750, "y": 390, "width": cw, "height": ch},
        {"x": 750, "y": 560, "width": cw, "height": ch},
    ]


SPREAD_LAYOUTS: dict[SpreadType, dict] = {
    "three": {
        "canvas_width": 900,
        "canvas_height": 420,
        "background_color": "#1a1a2e",
        "slots": _slots_three(),
    },
    "daily": {
        "canvas_width": 520,
        "canvas_height": 820,
        "background_color": "#1a1a2e",
        "slots": _slots_one(),
    },
    "single": {
        "canvas_width": 520,
        "canvas_height": 820,
        "background_color": "#1a1a2e",
        "slots": _slots_one(),
    },
    "relationship": {
        "canvas_width": 1100,
        "canvas_height": 420,
        "background_color": "#1a1a2e",
        "slots": _slots_five(),
    },
    "career": {
        "canvas_width": 1100,
        "canvas_height": 420,
        "background_color": "#1a1a2e",
        "slots": _slots_five(),
    },
    "celtic_cross": {
        "canvas_width": 1000,
        "canvas_height": 720,
        "background_color": "#1a1a2e",
        "slots": _slots_celtic(),
    },
}


def get_card_image_url(card_id: str) -> str:
    return f"{IMAGE_ROOT}{card_id}.jpg"
