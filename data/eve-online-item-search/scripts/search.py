#!/usr/bin/env python3
import argparse
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SEARCH_URL = "https://www.ceve-market.org/api/searchname"
TYPE_URL_TMPL = "https://esi.evetech.net/latest/universe/types/{type_id}/?datasource=tranquility&language=zh"
GROUP_URL_TMPL = "https://esi.evetech.net/latest/universe/groups/{group_id}?datasource=tranquility&language=zh"


def http_post_form(url, data, timeout=15):
    body = urlencode(data).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def http_get(url, timeout=15):
    req = Request(url)
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def fail(message):
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="EVE item search via API")
    parser.add_argument("name", nargs="?", default="", help="item name")
    parser.add_argument("--limit", type=int, default=10, help="max results from step1 list")
    args = parser.parse_args()

    name = (args.name or "").strip()
    if not name:
        print(json.dumps([], ensure_ascii=False))
        return

    try:
        step1_text = http_post_form(SEARCH_URL, {"name": name})
    except (URLError, HTTPError) as e:
        fail(f"Step1 failed: {e}")

    try:
        step1 = json.loads(step1_text)
    except json.JSONDecodeError:
        fail("Step1 failed: response is not valid JSON")

    if not isinstance(step1, list) or len(step1) == 0:
        print(json.dumps([], ensure_ascii=False))
        return

    first = step1[0]
    if not isinstance(first, dict) or "typeid" not in first:
        fail("Step1 failed: missing typeid")

    type_id = first["typeid"]

    try:
        step2_text = http_get(TYPE_URL_TMPL.format(type_id=type_id))
    except (URLError, HTTPError) as e:
        fail(f"Step2 failed: {e}")

    try:
        step2 = json.loads(step2_text)
    except json.JSONDecodeError:
        fail("Step2 failed: response is not valid JSON")

    group_id = step2.get("group_id")
    if group_id is None:
        fail("Step2 failed: missing group_id")

    try:
        step3_text = http_get(GROUP_URL_TMPL.format(group_id=group_id))
    except (URLError, HTTPError) as e:
        fail(f"Step3 failed: {e}")

    try:
        step3 = json.loads(step3_text)
    except json.JSONDecodeError:
        fail("Step3 failed: response is not valid JSON")

    result = {
        "name": step2.get("name", ""),
        "description": step2.get("description", ""),
        "category_name": step3.get("name", ""),
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
