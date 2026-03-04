#!/usr/bin/env python3
"""
Agent Avengers - Execute Script
실행 계획에 따라 에이전트 스폰/디스패치 실행
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = os.environ.get("AVENGERS_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
MISSION_DIR = Path(WORKSPACE) / "avengers-missions"


def load_mission(mission_id: str) -> tuple:
    """미션 및 실행 계획 로드"""
    mission_path = MISSION_DIR / mission_id
    
    with open(mission_path / "mission.json") as f:
        mission = json.load(f)
    
    with open(mission_path / "execution_plan.json") as f:
        plan = json.load(f)
    
    return mission, plan


def update_mission_status(mission_path: Path, status: str, updates: dict = None):
    """미션 상태 업데이트"""
    with open(mission_path / "mission.json") as f:
        mission = json.load(f)
    
    mission["status"] = status
    mission["updated_at"] = datetime.now().isoformat()
    
    if updates:
        mission.update(updates)
    
    with open(mission_path / "mission.json", "w") as f:
        json.dump(mission, f, indent=2, ensure_ascii=False)


def log_event(mission_path: Path, event: str, data: dict = None):
    """이벤트 로깅"""
    log_file = mission_path / "logs" / "execution.jsonl"
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "data": data or {}
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate_openclaw_commands(plan: dict) -> list:
    """OpenClaw에서 실행할 명령어 생성"""
    commands = []
    
    for phase in plan["phases"]:
        phase_commands = []
        
        for agent in phase["agents"]:
            # 해당 에이전트의 명령어 찾기
            cmd_info = next(
                (c for c in plan["commands"] if c["agent_id"] == agent["id"]),
                None
            )
            
            if cmd_info:
                if cmd_info["type"] == "spawn":
                    phase_commands.append({
                        "type": "spawn",
                        "agent_id": agent["id"],
                        "code": f"""sessions_spawn({{
  task: `{cmd_info['params']['task']}`,
  model: "{cmd_info['params']['model']}",
  runTimeoutSeconds: {cmd_info['params']['runTimeoutSeconds']},
  cleanup: "{cmd_info['params']['cleanup']}",
  label: "{cmd_info['params']['label']}"
}})"""
                    })
                    
                elif cmd_info["type"] == "send":
                    phase_commands.append({
                        "type": "send",
                        "agent_id": agent["id"],
                        "code": f"""sessions_send({{
  label: "{cmd_info['params']['label']}",
  message: `{cmd_info['params']['message']}`,
  timeoutSeconds: {cmd_info['params']['timeoutSeconds']}
}})"""
                    })
        
        commands.append({
            "phase": phase["phase"],
            "parallel": phase["parallel"],
            "commands": phase_commands
        })
    
    return commands


def print_execution_script(commands: list, mission_id: str):
    """실행 스크립트 출력"""
    print("\n" + "="*70)
    print("🦸 AVENGERS EXECUTE - OpenClaw 실행 명령어")
    print("="*70)
    print(f"미션: {mission_id}")
    print()
    print("아래 명령어들을 OpenClaw 세션에서 순서대로 실행하세요:")
    print("-"*70)
    
    for phase_info in commands:
        phase = phase_info["phase"]
        parallel = phase_info["parallel"]
        cmds = phase_info["commands"]
        
        print(f"\n### Phase {phase} {'(병렬 실행)' if parallel else '(순차 실행)'}")
        print()
        
        if parallel:
            print("// 아래 명령어들을 동시에 실행")
        
        for cmd in cmds:
            print(f"// {cmd['agent_id']}")
            print(cmd["code"])
            print()
        
        if phase_info != commands[-1]:
            print("// ⏳ 위 에이전트들 완료 대기 후 다음 Phase 진행")
            print("// sessions_list({ kinds: ['spawn'], messageLimit: 1 })")
    
    print("-"*70)
    print("\n📊 진행 모니터링:")
    print(f"   python3 scripts/monitor.py --mission {mission_id}")
    print("\n📦 결과 통합:")
    print(f"   python3 scripts/consolidate.py --mission {mission_id}")
    print("="*70)


def save_execution_script(commands: list, mission_path: Path):
    """실행 스크립트를 파일로 저장"""
    script_path = mission_path / "execute_commands.md"
    
    with open(script_path, "w") as f:
        f.write("# Avengers Execute Commands\n\n")
        f.write("OpenClaw 세션에서 아래 명령어들을 실행하세요.\n\n")
        
        for phase_info in commands:
            phase = phase_info["phase"]
            parallel = phase_info["parallel"]
            cmds = phase_info["commands"]
            
            f.write(f"## Phase {phase} {'(병렬)' if parallel else '(순차)'}\n\n")
            
            for cmd in cmds:
                f.write(f"### {cmd['agent_id']}\n\n")
                f.write("```javascript\n")
                f.write(cmd["code"])
                f.write("\n```\n\n")
    
    return script_path


def main():
    parser = argparse.ArgumentParser(description="Agent Avengers - Execute")
    parser.add_argument("--mission", "-m", required=True, help="미션 ID")
    parser.add_argument("--dry-run", "-d", action="store_true", help="명령어만 출력")
    parser.add_argument("--save", "-s", action="store_true", help="스크립트 파일 저장")
    
    args = parser.parse_args()
    
    try:
        mission, plan = load_mission(args.mission)
    except FileNotFoundError:
        print(f"❌ 미션을 찾을 수 없습니다: {args.mission}")
        print(f"   경로: {MISSION_DIR / args.mission}")
        sys.exit(1)
    
    mission_path = Path(mission["path"])
    
    # 실행 명령어 생성
    commands = generate_openclaw_commands(plan)
    
    # 실행 시작 로깅
    log_event(mission_path, "execution_started", {
        "total_phases": len(commands),
        "total_agents": plan["total_agents"]
    })
    
    # 상태 업데이트
    update_mission_status(mission_path, "executing")
    
    # 명령어 출력
    print_execution_script(commands, args.mission)
    
    # 파일 저장
    if args.save:
        script_path = save_execution_script(commands, mission_path)
        print(f"\n📄 스크립트 저장됨: {script_path}")


if __name__ == "__main__":
    main()
