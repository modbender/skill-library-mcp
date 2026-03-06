"""
推特自动化运营 — 一键执行入口

串联 Watcher → Processor → Action 三节点管线。

使用方式：
  python run_pipeline.py                      # 使用 input_urls.txt 中的 URL
  python run_pipeline.py <url1> <url2> ...    # 直接传入 URL
  python run_pipeline.py --watch-only         # 仅执行抓取（跳过提炼和通知）
  python run_pipeline.py --process-only       # 仅执行提炼（跳过抓取和通知）
  python run_pipeline.py --notify-only        # 仅发送通知（跳过抓取和提炼）
"""

import sys

def run(urls=None, watch=True, process=True, notify_flag=True):
    """执行管线"""
    results = {"watch": 0, "process": 0, "notify": 0}

    if watch:
        print("=" * 50)
        print("📡 阶段一：Watcher 巡逻抓取")
        print("=" * 50)
        from watcher import watch as do_watch
        results["watch"] = do_watch(urls)
        print()

    if process:
        print("=" * 50)
        print("🧠 阶段二：Processor LLM 提炼")
        print("=" * 50)
        from processor import process as do_process
        results["process"] = do_process()
        print()

    if notify_flag:
        print("=" * 50)
        print("🔔 阶段三：Action 通知审阅")
        print("=" * 50)
        from notifier import notify as do_notify
        results["notify"] = do_notify()
        print()

    print("=" * 50)
    print(f"✅ 管线执行完毕")
    print(f"   抓取: {results['watch']} 条 | 提炼: {results['process']} 条 | 待审: {results['notify']} 条")
    print("=" * 50)

    return results


if __name__ == "__main__":
    args = sys.argv[1:]

    # 分离 flag 和 URL 参数
    flags = [a for a in args if a.startswith("--")]
    urls = [a for a in args if not a.startswith("--")]

    if "--watch-only" in flags:
        run(urls=urls or None, watch=True, process=False, notify_flag=False)
    elif "--process-only" in flags:
        run(watch=False, process=True, notify_flag=False)
    elif "--notify-only" in flags:
        run(watch=False, process=False, notify_flag=True)
    elif urls:
        # 直接传入 URL，完整执行管线
        run(urls=urls)
    else:
        run()
