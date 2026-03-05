"""Bring! shopping list CLI — add, remove, complete, and list items."""

import argparse
import asyncio
import json
import os

import aiohttp
from bring_api import Bring
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.environ["BRING_EMAIL"]
PASSWORD = os.environ["BRING_PASSWORD"]


async def get_bring():
    session = aiohttp.ClientSession()
    bring = Bring(session, EMAIL, PASSWORD)
    await bring.login()
    return bring, session


async def get_default_list(bring):
    response = await bring.load_lists()
    if not response.lists:
        raise RuntimeError("No shopping lists found in Bring account")
    return response.lists[0]


async def cmd_list(args):
    bring, session = await get_bring()
    try:
        lst = await get_default_list(bring)
        items = await bring.get_list(lst.listUuid)
        result = {
            "list_name": lst.name,
            "items": [
                {"name": item.itemId, "spec": item.specification}
                for item in items.items.purchase
            ],
            "recently_completed": [
                {"name": item.itemId, "spec": item.specification}
                for item in items.items.recently
            ],
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result["items"]:
                print(f"{result['list_name']}:")
                for item in result["items"]:
                    spec = f" ({item['spec']})" if item["spec"] else ""
                    print(f"  - {item['name']}{spec}")
            else:
                print("Shopping list is empty!")
    finally:
        await session.close()


async def cmd_add(args):
    bring, session = await get_bring()
    try:
        lst = await get_default_list(bring)
        for item in args.items:
            parts = item.split(":", 1)
            name = parts[0].strip()
            spec = parts[1].strip() if len(parts) > 1 else ""
            await bring.save_item(lst.listUuid, name, spec)
        names = [i.split(":")[0].strip() for i in args.items]
        print(json.dumps({"added": names, "list": lst.name}))
    finally:
        await session.close()


async def cmd_remove(args):
    bring, session = await get_bring()
    try:
        lst = await get_default_list(bring)
        for item in args.items:
            await bring.remove_item(lst.listUuid, item.strip())
        print(json.dumps({"removed": args.items, "list": lst.name}))
    finally:
        await session.close()


async def cmd_complete(args):
    bring, session = await get_bring()
    try:
        lst = await get_default_list(bring)
        for item in args.items:
            await bring.complete_item(lst.listUuid, item.strip())
        print(json.dumps({"completed": args.items, "list": lst.name}))
    finally:
        await session.close()


def main():
    parser = argparse.ArgumentParser(description="Bring! shopping list CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="Show current shopping list")
    p_list.add_argument("--json", action="store_true", help="JSON output")

    p_add = sub.add_parser("add", help="Add items to the list")
    p_add.add_argument("items", nargs="+", help="Items to add (use 'name:spec' for details)")

    p_remove = sub.add_parser("remove", help="Remove items from the list")
    p_remove.add_argument("items", nargs="+", help="Items to remove")

    p_complete = sub.add_parser("complete", help="Mark items as completed")
    p_complete.add_argument("items", nargs="+", help="Items to complete")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "add": cmd_add,
        "remove": cmd_remove,
        "complete": cmd_complete,
    }
    asyncio.run(commands[args.command](args))


if __name__ == "__main__":
    main()
