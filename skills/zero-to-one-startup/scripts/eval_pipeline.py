#!/usr/bin/env python3
from __future__ import annotations  # Python 3.9 compatibility
"""
Eval Pipeline — LLM 평가 vs 실제 심사결과 비교

Usage:
  # 실제 결과 등록
  python3 eval_pipeline.py add --file plan.pdf --program TIPS --result pass --score 82

  # LLM 평가 실행 + 결과 저장
  python3 eval_pipeline.py run --file plan.pdf [--model qwen3:8b]

  # 정확도 리포트
  python3 eval_pipeline.py report

  # 특정 파일 비교
  python3 eval_pipeline.py compare --file plan.pdf
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GROUND_TRUTH = BASE_DIR / "ground_truth.jsonl"
EVAL_RESULTS = BASE_DIR / "eval_results.jsonl"
HISTORY = BASE_DIR / "history.jsonl"
EVALUATE_PY = BASE_DIR / "scripts" / "evaluate.py"

# --- helpers ---

def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().strip().split("\n"):
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries

def append_jsonl(path: Path, entry: dict):
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def find_ground_truth(filename: str) -> dict | None:
    for gt in load_jsonl(GROUND_TRUTH):
        if gt.get("file") == filename:
            return gt
    return None

def find_eval_scores(filename: str) -> list[dict]:
    """Find all LLM eval scores for a file from history.jsonl and eval_results.jsonl."""
    results = []
    for entry in load_jsonl(HISTORY):
        files = entry.get("files", [])
        if filename in files and entry.get("score") is not None:
            results.append(entry)
    for entry in load_jsonl(EVAL_RESULTS):
        if entry.get("file") == filename:
            results.append(entry)
    return results

# --- commands ---

def cmd_add(args):
    """Register actual review result."""
    entry = {
        "file": args.file,
        "program": args.program or "TIPS",
        "actual_result": args.result,  # pass/fail
        "actual_score": args.score,     # optional numeric
        "notes": args.notes or "",
        "added_at": datetime.now().isoformat(),
    }
    append_jsonl(GROUND_TRUTH, entry)
    print(f"✅ Ground truth 등록: {args.file} → {args.result}" +
          (f" ({args.score}점)" if args.score else ""))

def cmd_run(args):
    """Run LLM evaluation and store result."""
    if not os.path.exists(args.file):
        print(f"❌ 파일 없음: {args.file}")
        sys.exit(1)

    model = args.model or "qwen3:8b"
    cmd = [sys.executable, str(EVALUATE_PY), "--mode", "evaluate",
           "--model", model, "--json", args.file]

    print(f"🔍 평가 중: {args.file} (model={model})")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"❌ 평가 실패: {result.stderr[:200]}")
        sys.exit(1)

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ JSON 파싱 실패: {result.stdout[:200]}")
        sys.exit(1)

    score = output.get("score")
    entry = {
        "file": os.path.basename(args.file),
        "model": model,
        "llm_score": score,
        "timestamp": datetime.now().isoformat(),
        "mode": "evaluate",
    }
    append_jsonl(EVAL_RESULTS, entry)
    print(f"📊 LLM 점수: {score}/100 → eval_results.jsonl 저장")

    # Auto-compare if ground truth exists
    gt = find_ground_truth(os.path.basename(args.file))
    if gt:
        _print_comparison(os.path.basename(args.file), [entry], gt)

def cmd_compare(args):
    """Compare LLM scores vs ground truth for a file."""
    filename = os.path.basename(args.file)
    gt = find_ground_truth(filename)
    if not gt:
        print(f"⚠️ Ground truth 없음: {filename}")
        print(f"   → eval_pipeline.py add --file {filename} --result pass/fail --score XX")
        return

    evals = find_eval_scores(filename)
    if not evals:
        print(f"⚠️ 평가 기록 없음: {filename}")
        return

    _print_comparison(filename, evals, gt)

def _print_comparison(filename: str, evals: list[dict], gt: dict):
    """Print comparison between LLM evals and ground truth."""
    actual = gt.get("actual_score")
    actual_result = gt.get("actual_result", "?")
    program = gt.get("program", "?")

    print(f"\n{'='*50}")
    print(f"📋 {filename} ({program})")
    print(f"   실제: {actual_result.upper()}" +
          (f" ({actual}점)" if actual else ""))
    print(f"{'─'*50}")

    for ev in evals:
        llm_score = ev.get("llm_score") or ev.get("score")
        model = ev.get("model", "?")
        if llm_score is not None and actual is not None:
            diff = llm_score - actual
            sign = "+" if diff > 0 else ""
            accuracy_icon = "✅" if abs(diff) <= 10 else "⚠️" if abs(diff) <= 20 else "❌"
            print(f"   {accuracy_icon} LLM({model}): {llm_score}점 (차이: {sign}{diff})")
        elif llm_score is not None:
            # No actual score, check pass/fail prediction
            predicted = "pass" if llm_score >= 70 else "fail"
            match = "✅" if predicted == actual_result else "❌"
            print(f"   {match} LLM({model}): {llm_score}점 → 예측={predicted}, 실제={actual_result}")

    print(f"{'='*50}\n")

def _compute_confusion(gt_entries: list[dict], eval_getter) -> dict:
    """Compute confusion matrix stats. Returns dict keyed by program (and '__all__')."""
    from collections import defaultdict
    programs = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0,
                                     "score_diffs": [], "total": 0})

    for gt in gt_entries:
        filename = gt["file"]
        evals = eval_getter(filename)
        actual_result = gt.get("actual_result")
        actual_score = gt.get("actual_score")
        program = gt.get("program", "기타")

        for ev in evals:
            llm_score = ev.get("llm_score") or ev.get("score")
            if llm_score is None:
                continue
            predicted = "pass" if llm_score >= 70 else "fail"

            for key in [program, "__all__"]:
                bucket = programs[key]
                bucket["total"] += 1
                if actual_score is not None:
                    bucket["score_diffs"].append(abs(llm_score - actual_score))
                if actual_result:
                    if predicted == "pass" and actual_result == "pass":
                        bucket["tp"] += 1
                    elif predicted == "pass" and actual_result == "fail":
                        bucket["fp"] += 1
                    elif predicted == "fail" and actual_result == "fail":
                        bucket["tn"] += 1
                    elif predicted == "fail" and actual_result == "pass":
                        bucket["fn"] += 1

    return dict(programs)


def _print_confusion_block(label: str, s: dict):
    """Print confusion matrix + metrics for one bucket."""
    tp, fp, tn, fn = s["tp"], s["fp"], s["tn"], s["fn"]
    total_pf = tp + fp + tn + fn
    accuracy = (tp + tn) / total_pf * 100 if total_pf else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print(f"\n┌─ {label} (n={total_pf})")
    print(f"│  Confusion Matrix:")
    print(f"│              예측Pass  예측Fail")
    print(f"│  실제Pass      {tp:>4}     {fn:>4}")
    print(f"│  실제Fail      {fp:>4}     {tn:>4}")
    print(f"│")
    print(f"│  Accuracy:  {accuracy:5.1f}%")
    print(f"│  Precision: {precision:5.3f}")
    print(f"│  Recall:    {recall:5.3f}")
    print(f"│  F1 Score:  {f1:5.3f}")

    diffs = s["score_diffs"]
    if diffs:
        avg_d = sum(diffs) / len(diffs)
        within_10 = sum(1 for d in diffs if d <= 10)
        print(f"│  평균 점수 차이: {avg_d:.1f}점  (±10점 이내: {within_10}/{len(diffs)})")

    print(f"└{'─'*50}")


def cmd_report(args):
    """Generate accuracy report across all files with ground truth."""
    gt_entries = load_jsonl(GROUND_TRUTH)
    if not gt_entries:
        print("⚠️ Ground truth 데이터 없음. 먼저 실제 심사 결과를 등록하세요:")
        print("   python3 eval_pipeline.py add --file plan.pdf --result pass --score 82")
        return

    # Count by program
    from collections import Counter
    program_counts = Counter(gt.get("program", "기타") for gt in gt_entries)

    print(f"\n{'='*60}")
    print(f"📊 Eval Pipeline 정확도 리포트")
    print(f"   Ground Truth: {len(gt_entries)}건")
    for prog, cnt in sorted(program_counts.items()):
        pass_cnt = sum(1 for g in gt_entries if g.get("program") == prog and g.get("actual_result") == "pass")
        fail_cnt = cnt - pass_cnt
        print(f"     {prog}: {cnt}건 (합격 {pass_cnt} / 불합격 {fail_cnt})")
    print(f"{'='*60}")

    # Check if any evals exist
    stats = _compute_confusion(gt_entries, find_eval_scores)
    has_evals = stats.get("__all__", {}).get("total", 0) > 0

    if not has_evals:
        # No eval results yet — show ground truth summary only
        print("\n⏳ LLM 평가 결과 없음 — ground truth만 표시합니다.")
        print("   평가 실행: python3 eval_pipeline.py run --file <plan.pdf>")

        # Show score distribution per program
        for prog in sorted(program_counts.keys()):
            entries = [g for g in gt_entries if g.get("program") == prog]
            scores = [g["actual_score"] for g in entries if g.get("actual_score") is not None]
            if scores:
                avg_s = sum(scores) / len(scores)
                print(f"\n   {prog}: 평균 {avg_s:.1f}점 (범위 {min(scores)}–{max(scores)})")
                pass_scores = [g["actual_score"] for g in entries if g.get("actual_result") == "pass" and g.get("actual_score")]
                fail_scores = [g["actual_score"] for g in entries if g.get("actual_result") == "fail" and g.get("actual_score")]
                if pass_scores:
                    print(f"     합격 평균: {sum(pass_scores)/len(pass_scores):.1f}점")
                if fail_scores:
                    print(f"     불합격 평균: {sum(fail_scores)/len(fail_scores):.1f}점")

        print(f"\n{'='*60}\n")
        return

    # Per-file comparison (verbose mode)
    if getattr(args, 'verbose', False):
        for gt in gt_entries:
            evals = find_eval_scores(gt["file"])
            if evals:
                _print_comparison(gt["file"], evals, gt)

    # Per-program breakdown
    for prog in sorted(program_counts.keys()):
        if prog in stats:
            _print_confusion_block(prog, stats[prog])

    # Overall
    if "__all__" in stats:
        _print_confusion_block("전체 (Overall)", stats["__all__"])

    # Recommendations
    all_s = stats.get("__all__", {})
    diffs = all_s.get("score_diffs", [])
    if diffs and sum(diffs) / len(diffs) > 15:
        print("\n💡 평균 차이 15점 초과 → 프롬프트 튜닝 권장")
        print("   참고: references/ 디렉토리에 심사기준서 추가 시 정확도 향상 기대")

    f1 = 0
    tp, fp, fn = all_s.get("tp", 0), all_s.get("fp", 0), all_s.get("fn", 0)
    if tp + fp and tp + fn:
        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    if f1 and f1 < 0.7:
        print(f"\n⚠️ F1 = {f1:.3f} < 0.7 — 모델/프롬프트 개선 필요")

    print(f"\n{'='*60}\n")

# --- main ---

def main():
    parser = argparse.ArgumentParser(description="Eval Pipeline: LLM 평가 vs 실제 심사 비교")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="실제 심사 결과 등록")
    p_add.add_argument("--file", required=True, help="파일명")
    p_add.add_argument("--program", default="TIPS", help="지원사업명")
    p_add.add_argument("--result", required=True, choices=["pass", "fail"])
    p_add.add_argument("--score", type=int, help="실제 점수 (선택)")
    p_add.add_argument("--notes", help="비고")

    # run
    p_run = sub.add_parser("run", help="LLM 평가 실행 + 저장")
    p_run.add_argument("--file", required=True, help="사업계획서 파일")
    p_run.add_argument("--model", default="qwen3:8b")

    # compare
    p_cmp = sub.add_parser("compare", help="특정 파일 비교")
    p_cmp.add_argument("--file", required=True)

    # report
    p_report = sub.add_parser("report", help="전체 정확도 리포트")
    p_report.add_argument("--verbose", "-v", action="store_true", help="파일별 상세 비교 포함")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"add": cmd_add, "run": cmd_run, "compare": cmd_compare, "report": cmd_report}[args.command](args)

if __name__ == "__main__":
    main()
