import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "geizhals.py"

spec = importlib.util.spec_from_file_location("geizhals_module", SCRIPT_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def _fixture(name: str) -> str:
    return (ROOT / "tests" / "fixtures" / name).read_text(encoding="utf-8")


def test_embedded_offer_price_and_shop():
    html = _fixture("offer_raw_price.html")
    price, shop = mod.parse_cheapest_shop(html)
    assert price == 767.98
    assert shop == "BA-Computer"

    enriched = mod.enrich_item(html)
    assert enriched["min_price_eur"] == 767.98
    assert enriched["price_confidence"] == "high"
    assert enriched["price_source"] == "embedded_offer_raw_price"
    assert enriched["offer_count"] == 37


def test_meta_price_fallback():
    html = _fixture("meta_price.html")
    enriched = mod.enrich_item(html)
    assert enriched["min_price_eur"] == 599.00
    assert enriched["price_confidence"] == "medium"
    assert enriched["price_source"] == "meta_product_price"


def test_title_price_fallback():
    html = _fixture("title_only.html")
    enriched = mod.enrich_item(html)
    assert enriched["min_price_eur"] == 1234.56
    assert enriched["price_confidence"] == "low"
    assert enriched["price_source"] == "title_ab_price"
