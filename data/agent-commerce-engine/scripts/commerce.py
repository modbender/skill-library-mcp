import argparse
import json
import sys
import os
from pathlib import Path

try:
    import requests
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Missing dependency: 'requests' library is not installed.",
        "instruction": "Run 'pip install requests' to use this skill."
    }))
    sys.exit(1)

# 添加 lib 路径到 sys.path
sys.path.append(str(Path(__file__).parent))
from lib.commerce_client import BaseCommerceClient

# 从环境变量获取配置，方便开发者直接使用命令：COMMERCE_URL=... python3 commerce.py
BRAND_NAME = os.getenv("COMMERCE_BRAND_NAME", "Generic Commerce")
BASE_URL = os.getenv("COMMERCE_URL", "https://api.yourstore.com/v1")
BRAND_ID = os.getenv("COMMERCE_BRAND_ID", "generic_store")

client = BaseCommerceClient(BASE_URL, BRAND_ID)

def format_output(data):
    if isinstance(data, dict) and "error" in data:
        # 增加配置提示建议
        if "Connection error" in data["error"] and "yourstore.com" in BASE_URL:
            data["hint"] = "It looks like you are using the default URL. Set COMMERCE_URL environment variable to your API endpoint."
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description=f"{BRAND_NAME} AI-Native Commerce CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command type")

    # 1. Auth (login/logout/register/send-code)
    login_p = subparsers.add_parser("login", help="Login to your account")
    login_p.add_argument("--account", required=True, help="Username, Email, or Phone")
    login_p.add_argument("--password", required=True, help="Password")

    reg_p = subparsers.add_parser("register", help="Register a new account")
    reg_p.add_argument("--email", required=True)
    reg_p.add_argument("--password", required=True)
    reg_p.add_argument("--code", required=True, help="Verification code from email")
    reg_p.add_argument("--name", help="Display name")
    reg_p.add_argument("--invite", help="Invite code")
    reg_p.add_argument("--reset-visitor", action="store_true", help="Reset visitor ID before registration")

    code_p = subparsers.add_parser("send-code", help="Send verification code to email")
    code_p.add_argument("--email", required=True)

    subparsers.add_parser("reset-visitor", help="Manually reset visitor ID")
    subparsers.add_parser("logout", help="Logout and clear credentials")

    # 2. Products (search/list/get)
    search_p = subparsers.add_parser("search", help="Search for products")
    search_p.add_argument("query", help="Keywords")

    subparsers.add_parser("list", help="List all products")

    get_p = subparsers.add_parser("get", help="Get specific product details")
    get_p.add_argument("slug", help="Product unique identifier (slug)")

    # 3. Cart (cart/add-cart/update-cart/remove-cart/clear-cart)
    subparsers.add_parser("cart", help="View current shopping cart")

    add_p = subparsers.add_parser("add-cart", help="Add item to cart")
    add_p.add_argument("slug")
    add_p.add_argument("--variant", "-v", required=True, help="Variant specification (e.g., variant ID, SKU, or gram for legacy)")
    add_p.add_argument("--quantity", "-q", type=int, default=1)

    up_p = subparsers.add_parser("update-cart", help="Update item quantity in cart")
    up_p.add_argument("slug")
    up_p.add_argument("--variant", "-v", required=True)
    up_p.add_argument("--quantity", "-q", type=int, required=True)

    rem_p = subparsers.add_parser("remove-cart", help="Remove item from cart")
    rem_p.add_argument("slug")
    rem_p.add_argument("--variant", "-v", required=True)

    subparsers.add_parser("clear-cart", help="Clear the entire cart")

    # 4. Profile, Orders & Promotions
    subparsers.add_parser("get-profile", help="Get user profile")
    
    prof_p = subparsers.add_parser("update-profile", help="Update user profile")
    prof_p.add_argument("--name", help="Nickname/Display Name")
    prof_p.add_argument("--phone", help="Phone number")
    prof_p.add_argument("--email", help="Email address")
    prof_p.add_argument("--province", help="Province")
    prof_p.add_argument("--city", help="City")
    prof_p.add_argument("--address", help="Detailed address")
    prof_p.add_argument("--bio", help="User bio")
    prof_p.add_argument("--avatar", help="Avatar URL")

    subparsers.add_parser("promotions", help="View current promotions")
    subparsers.add_parser("orders", help="List recent orders")

    order_p = subparsers.add_parser("create-order", help="Create an order from cart")
    order_p.add_argument("--name", required=True, help="Recipient name")
    order_p.add_argument("--phone", required=True, help="Recipient phone")
    order_p.add_argument("--province", required=True, help="Province/State")
    order_p.add_argument("--city", required=True, help="City")
    order_p.add_argument("--address", required=True, help="Detailed address")

    subparsers.add_parser("brand-story", help="Get brand narrative/story")
    subparsers.add_parser("company-info", help="Get formal company information")
    subparsers.add_parser("contact-info", help="Get official contact details")

    args = parser.parse_args()

    # Execution logic
    if args.command == "login":
        # 升级：不再直接保存密码，而是换取 Token
        result = client.get_api_token(args.account, args.password)
        if result.get("success"):
            format_output({
                "success": True, 
                "message": f"Login successful. API Token for {BRAND_ID} saved.",
                "storage": str(client.creds_file),
                "permission": "0600 (Private)"
            })
        else:
            format_output(result)
    
    elif args.command == "register":
        if args.reset_visitor:
            client.reset_visitor_id()
        format_output(client.register(args.email, args.password, args.name, args.code, args.invite))

    elif args.command == "send-code":
        format_output(client.send_verification_code(args.email))

    elif args.command == "reset-visitor":
        new_id = client.reset_visitor_id()
        format_output({"success": True, "new_visitor_id": new_id})

    elif args.command == "logout":
        client.delete_credentials()
        format_output({"success": True, "message": f"Logged out from {BRAND_ID}."})

    elif args.command == "search":
        format_output(client.search_products(args.query))

    elif args.command == "list":
        format_output(client.list_products())

    elif args.command == "get":
        format_output(client.get_product(args.slug))

    elif args.command == "get-profile":
        format_output(client.get_profile())

    elif args.command == "update-profile":
        data = {k: v for k, v in vars(args).items() if v is not None and k not in ["command"]}
        format_output(client.update_profile(data))

    elif args.command == "cart":
        format_output(client.get_cart())

    elif args.command == "add-cart":
        format_output(client.modify_cart("add", args.slug, args.variant, args.quantity))

    elif args.command == "update-cart":
        format_output(client.modify_cart("update", args.slug, args.variant, args.quantity))

    elif args.command == "remove-cart":
        format_output(client.remove_from_cart(args.slug, args.variant))

    elif args.command == "clear-cart":
        format_output(client.clear_cart())

    elif args.command == "promotions":
        format_output(client.get_promotions())

    elif args.command == "orders":
        format_output(client.list_orders())

    elif args.command == "create-order":
        shipping_data = {
            "name": args.name,
            "phone": args.phone,
            "province": args.province,
            "city": args.city,
            "address": args.address
        }
        format_output(client.create_order(shipping_data))

    elif args.command == "brand-story":
        format_output(client.get_brand_info("story"))

    elif args.command == "company-info":
        format_output(client.get_brand_info("company"))

    elif args.command == "contact-info":
        format_output(client.get_brand_info("contact"))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
