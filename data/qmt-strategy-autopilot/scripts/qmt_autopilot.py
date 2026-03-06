#!/usr/bin/env python3
"""OpenClaw skill wrapper: qmt strategy autopilot."""

import importlib.util
import json
import os
import sys

PLANNER_PATH = os.getenv("STRATEGY_PLANNER_PATH", "/opt/production_ready_skills/qmt-strategy-planner-skill/scripts/strategy_planner.py")


def load_planner():
    spec = importlib.util.spec_from_file_location("qmt_strategy_planner_cli", PLANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载策略规划器: {PLANNER_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) < 3:
        print('{"error":"用法: qmt_autopilot.py <plan|clarify|run> <args...>"}')
        sys.exit(1)
    cmd = sys.argv[1]
    planner = load_planner()
    if cmd == "plan":
        print(planner.execute_strategy_plan(sys.argv[2]))
        return
    if cmd == "clarify":
        if len(sys.argv) < 4:
            print('{"error":"clarify 需要 requirement 与 answers_json"}')
            sys.exit(1)
        print(planner.process_clarification_answers(sys.argv[2], sys.argv[3]))
        return
    if cmd == "run":
        request_id = sys.argv[3] if len(sys.argv) > 3 else ""
        print(planner.run_execution_plan(sys.argv[2], request_id))
        return
    print(json.dumps({"error": f"未知命令: {cmd}"}, ensure_ascii=False))
    sys.exit(1)


if __name__ == "__main__":
    main()
