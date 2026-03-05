# Concurrency Traps

## GIL
- Only one thread executes Python — CPU-bound = no speedup from threads
- I/O releases GIL — threads help for I/O-bound (network, disk)
- Use `multiprocessing` for CPU — separate processes, no GIL

## Threading
- Race conditions — shared mutable state without locks corrupts data
- Daemon threads killed abruptly — no cleanup on main thread exit
- `threading.local()` for thread-local — but watch for leaks in pools

## Asyncio
- `await` in sync function fails — must be in `async def`
- Blocking call in async — `time.sleep()` blocks event loop, use `asyncio.sleep()`
- Forgotten `await` — coroutine never runs, just returns coroutine object
- `asyncio.run()` in running loop — fails, use `await` or `create_task`
