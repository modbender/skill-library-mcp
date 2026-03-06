"""CounterClaw CLI"""
import sys
import asyncio
sys.path.insert(0, sys.path.insert(0, 'src') or 'src')
sys.path.insert(0, 'src')

from counterclaw import CounterClawInterceptor

async def main():
    text = sys.argv[1] if len(sys.argv) > 1 else ""
    interceptor = CounterClawInterceptor()
    result = await interceptor.check_input(text)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
