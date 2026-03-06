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

# 从环境变量获取配置，方便本地测试
BRAND_NAME = "辣匪兔 (Lafeitu)"
BASE_URL = os.getenv("LAFEITU_URL", "https://lafeitu.cn/api/v1")
BRAND_ID = "lafeitu"

client = BaseCommerceClient(BASE_URL, BRAND_ID)

def format_output(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description=f"{BRAND_NAME} 官方 AI 助手命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="命令类型")

    # 1. 认证相关 (login/logout/register/send-code)
    login_p = subparsers.add_parser("login", help="登录账户")
    login_p.add_argument("--account", required=True, help="手机号或邮箱")
    login_p.add_argument("--password", required=True, help="密码")

    reg_p = subparsers.add_parser("register", help="注册新账户")
    reg_p.add_argument("--email", required=True, help="邮箱地址")
    reg_p.add_argument("--password", required=True, help="设置密码 (至少6位)")
    reg_p.add_argument("--code", required=True, help="邮箱验证码")
    reg_p.add_argument("--name", help="昵称 (可选)")
    reg_p.add_argument("--invite", help="邀请码 (可选)")
    reg_p.add_argument("--reset-visitor", action="store_true", help="注册前重置访客ID (防止继承旧购物车)")

    code_p = subparsers.add_parser("send-code", help="发送邮箱验证码")
    code_p.add_argument("--email", required=True, help="目标邮箱")

    subparsers.add_parser("reset-visitor", help="手动重置访客ID")
    subparsers.add_parser("logout", help="登出并清除凭据")

    # 2. 产品相关 (search/list/get)
    search_p = subparsers.add_parser("search", help="搜索美食")
    search_p.add_argument("query", help="关键词")

    subparsers.add_parser("list", help="查看所有美食")

    get_p = subparsers.add_parser("get", help="查看特定美食详情")
    get_p.add_argument("slug", help="产品标识符")

    # 3. 购物车相关 (cart/add-cart/update-cart/remove-cart/clear-cart)
    subparsers.add_parser("cart", help="查看当前购物车")

    add_p = subparsers.add_parser("add-cart", help="添加商品到购物车")
    add_p.add_argument("slug")
    add_p.add_argument("--variant", "-v", required=True, help="商品的变体或规格标识 (如: gram)")
    add_p.add_argument("--quantity", "-q", type=int, default=1)

    up_p = subparsers.add_parser("update-cart", help="修改购物车商品数量")
    up_p.add_argument("slug")
    up_p.add_argument("--variant", "-v", required=True)
    up_p.add_argument("--quantity", "-q", type=int, required=True)

    rem_p = subparsers.add_parser("remove-cart", help="从购物车移除商品")
    rem_p.add_argument("slug")
    rem_p.add_argument("--variant", "-v", required=True)

    subparsers.add_parser("clear-cart", help="清空购物车")

    # 4. 资料、订单与促销
    subparsers.add_parser("get-profile", help="获取个人资料")
    
    prof_p = subparsers.add_parser("update-profile", help="修改个人资料")
    prof_p.add_argument("--name", help="昵称")
    prof_p.add_argument("--phone", help="手机号")
    prof_p.add_argument("--email", help="邮箱")
    prof_p.add_argument("--province", help="省份")
    prof_p.add_argument("--city", help="城市")
    prof_p.add_argument("--address", help="详细地址")
    prof_p.add_argument("--bio", help="个人简介")
    prof_p.add_argument("--avatar", help="头像 URL")

    subparsers.add_parser("promotions", help="查看当前优惠政策")
    subparsers.add_parser("orders", help="查看历史订单")

    # 订单创建 (用于人机交接等流程)
    order_p = subparsers.add_parser("create-order", help="使用购物车中的商品创建订单")
    order_p.add_argument("--name", required=True, help="收货人姓名")
    order_p.add_argument("--phone", required=True, help="收货人手机号")
    order_p.add_argument("--province", required=True, help="省份")
    order_p.add_argument("--city", required=True, help="城市")
    order_p.add_argument("--address", required=True, help="详细地址")

    subparsers.add_parser("brand-story", help="查看品牌故事")
    subparsers.add_parser("company-info", help="查看公司信息")
    subparsers.add_parser("contact-info", help="查看联系方式")

    args = parser.parse_args()

    # 处理逻辑
    if args.command == "login":
        # 升级：不再直接保存密码，而是换取 Token
        result = client.get_api_token(args.account, args.password)
        if result.get("success"):
            format_output({
                "success": True, 
                "message": "登录成功，已保存安全 API 令牌。",
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
        format_output({"success": True, "message": "Logged out and credentials cleared."})

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
