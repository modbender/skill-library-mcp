import asyncio, sys, time
sys.path.insert(0, '.')
from yfinance_ai import Tools

t = Tools()

async def fetch():
    return await t.get_key_ratios(ticker='UNH')

async def main():
    max_tries = 8
    delay = 2
    for i in range(1, max_tries+1):
        try:
            r = await fetch()
            print(r)
            return 0
        except Exception as e:
            print(f"Attempt {i} failed: {e}", file=sys.stderr)
        time.sleep(delay)
        delay = min(delay*2, 60)
    print("All retries failed.", file=sys.stderr)
    return 1

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
