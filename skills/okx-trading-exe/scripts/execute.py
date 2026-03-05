import os
import sys
import argparse
import json
from dotenv import load_dotenv

# 添加父目录到 sys.path 以便能够导入 providers
script_dir = os.path.dirname(os.path.abspath(__file__))
skill_dir = os.path.dirname(script_dir)
sys.path.insert(0, skill_dir)

from providers.okx_provider import OKXProvider

def main():
    parser = argparse.ArgumentParser(description="Trading Execution Interface (TAS Standard)")
    parser.add_argument("--action", required=True, choices=[
        "get_balance", "get_positions", "place_market_order", 
        "place_limit_order", "get_recent_trades"
    ], help="The action to perform")
    
    parser.add_argument("--provider", required=True, choices=["okx_demo", "okx_live"], 
                        help="The execution provider environment")
    
    # action 对应的额外参数
    parser.add_argument("--symbol", type=str, help="Trading pair, e.g. BTC-USDT")
    parser.add_argument("--side", type=str, choices=["buy", "sell"], help="Order side")
    parser.add_argument("--size", type=float, help="Order size (USDT amount for market buy, crypto amount for others)")
    parser.add_argument("--price", type=float, help="Order price (for limit orders)")
    parser.add_argument("--limit", type=int, default=20, help="Limit for history query")
    
    args = parser.parse_args()
    
    # 尝试加载环境所在目录的 .env 文件 (优先向上层找)
    env_path = os.path.join(skill_dir, '.env')
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(os.path.dirname(skill_dir)), '.env')
    load_dotenv(env_path)

    api_key = os.getenv("OKX_API_KEY", "")
    api_secret = os.getenv("OKX_API_SECRET", "")
    passphrase = os.getenv("OKX_PASSPHRASE", "")
    
    if args.provider in ["okx_demo", "okx_live"]:
        if not all([api_key, api_secret, passphrase]):
            print(json.dumps({"error": "Missing OKX API credentials in environment variables."}))
            sys.exit(1)
            
        is_demo = (args.provider == "okx_demo")
        provider = OKXProvider(api_key, api_secret, passphrase, is_demo)
    else:
        print(json.dumps({"error": f"Unsupported provider: {args.provider}"}))
        sys.exit(1)
        
    # 执行对应的操作
    try:
        if args.action == "get_balance":
            cash = provider.get_cash()
            print(json.dumps({"balance_usdt": cash}))
            
        elif args.action == "get_positions":
            positions = provider.get_positions()
            print(json.dumps({"positions": positions}))
            
        elif args.action == "place_market_order":
            if not all([args.symbol, args.side, args.size]):
                print(json.dumps({"error": "Missing required arguments: --symbol, --side, --size"}))
                sys.exit(1)
            result = provider.place_market_order(args.symbol, args.side, args.size)
            print(json.dumps(result))
            
        elif args.action == "place_limit_order":
            if not all([args.symbol, args.side, args.size, args.price]):
                print(json.dumps({"error": "Missing required arguments: --symbol, --side, --size, --price"}))
                sys.exit(1)
            result = provider.place_limit_order(args.symbol, args.side, args.size, args.price)
            print(json.dumps(result))
            
        elif args.action == "get_recent_trades":
            if not args.symbol:
                print(json.dumps({"error": "Missing required argument: --symbol"}))
                sys.exit(1)
            trades = provider.get_recent_trades(args.symbol, args.limit)
            print(json.dumps({"trades": trades}))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
