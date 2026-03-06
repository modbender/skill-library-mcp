#!/usr/bin/env python3
"""Analyze PyTorch memory snapshot JSON and profiler trace JSON/JSON.GZ."""

from __future__ import annotations

import argparse
import gzip
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _format_bytes(num: float) -> str:
    if num is None or math.isnan(num):
        return "n/a"
    step = 1024.0
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(num)
    idx = 0
    while value >= step and idx < len(units) - 1:
        value /= step
        idx += 1
    return f"{value:.2f} {units[idx]}"


def _load_json_maybe_gzip(path: Path) -> Any:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def analyze_memory_snapshot(path: Path, top_n: int = 15) -> dict[str, Any]:
    data = _load_json_maybe_gzip(path)

    result: dict[str, Any] = {
        "path": str(path),
        "summary": {},
        "segment_types": {},
        "largest_segments": [],
        "trace_actions": {},
        "annotations": {},
    }

    if not isinstance(data, dict):
        result["error"] = f"Unexpected memory snapshot root type: {type(data).__name__}"
        return result

    segments = data.get("segments", [])
    if isinstance(segments, list):
        total_reserved = 0
        total_allocated = 0
        total_active = 0
        total_requested = 0
        by_type: dict[str, dict[str, float]] = defaultdict(
            lambda: {"segments": 0, "reserved": 0, "allocated": 0, "active": 0, "requested": 0}
        )
        largest = []

        for seg in segments:
            if not isinstance(seg, dict):
                continue
            reserved = float(seg.get("total_size", 0) or 0)
            allocated = float(seg.get("allocated_size", 0) or 0)
            active = float(seg.get("active_size", 0) or 0)
            requested = float(seg.get("requested_size", 0) or 0)
            stype = str(seg.get("segment_type", "unknown"))

            total_reserved += reserved
            total_allocated += allocated
            total_active += active
            total_requested += requested

            item = by_type[stype]
            item["segments"] += 1
            item["reserved"] += reserved
            item["allocated"] += allocated
            item["active"] += active
            item["requested"] += requested

            largest.append(
                {
                    "device": seg.get("device"),
                    "segment_type": stype,
                    "reserved": reserved,
                    "allocated": allocated,
                    "active": active,
                    "requested": requested,
                    "slack": max(reserved - allocated, 0),
                    "address": seg.get("address"),
                }
            )

        result["summary"] = {
            "segments": len(segments),
            "reserved_bytes": total_reserved,
            "allocated_bytes": total_allocated,
            "active_bytes": total_active,
            "requested_bytes": total_requested,
            "reserved_vs_allocated_ratio": (total_reserved / total_allocated) if total_allocated else None,
            "allocated_vs_requested_ratio": (total_allocated / total_requested) if total_requested else None,
        }

        type_result: dict[str, Any] = {}
        for seg_type, vals in by_type.items():
            allocated = vals["allocated"]
            requested = vals["requested"]
            reserved = vals["reserved"]
            type_result[seg_type] = {
                "segments": int(vals["segments"]),
                "reserved_bytes": reserved,
                "allocated_bytes": allocated,
                "active_bytes": vals["active"],
                "requested_bytes": requested,
                "reserved_vs_allocated_ratio": (reserved / allocated) if allocated else None,
                "allocated_vs_requested_ratio": (allocated / requested) if requested else None,
            }
        result["segment_types"] = type_result

        result["largest_segments"] = sorted(
            largest,
            key=lambda x: (x["reserved"], x["slack"]),
            reverse=True,
        )[:top_n]

    device_traces = data.get("device_traces", [])
    if isinstance(device_traces, list):
        action_counter = Counter()
        first_ts = None
        last_ts = None
        for trace in device_traces:
            if not isinstance(trace, list):
                continue
            for event in trace:
                if not isinstance(event, dict):
                    continue
                action = str(event.get("action", "unknown"))
                action_counter[action] += 1
                ts = event.get("time_us")
                if isinstance(ts, (int, float)):
                    first_ts = ts if first_ts is None else min(first_ts, ts)
                    last_ts = ts if last_ts is None else max(last_ts, ts)

        result["trace_actions"] = {
            "counts": dict(action_counter.most_common()),
            "first_time_us": first_ts,
            "last_time_us": last_ts,
            "span_us": (last_ts - first_ts) if first_ts is not None and last_ts is not None else None,
        }

    annotations = data.get("external_annotations", [])
    if isinstance(annotations, list):
        name_counter = Counter()
        for annotation in annotations:
            if isinstance(annotation, dict):
                name_counter[str(annotation.get("name", "unknown"))] += 1
        result["annotations"] = {
            "count": len(annotations),
            "top_names": dict(name_counter.most_common(10)),
        }

    return result


def analyze_cpu_trace(path: Path, top_n: int = 20) -> dict[str, Any]:
    data = _load_json_maybe_gzip(path)
    result: dict[str, Any] = {
        "path": str(path),
        "summary": {},
        "top_ops": [],
        "top_threads": [],
    }

    if not isinstance(data, dict):
        result["error"] = f"Unexpected trace root type: {type(data).__name__}"
        return result

    events = data.get("traceEvents")
    if not isinstance(events, list):
        result["error"] = "traceEvents not found or not a list"
        return result

    op_stats: dict[str, dict[str, float]] = defaultdict(
        lambda: {"count": 0, "total_dur_us": 0.0, "max_dur_us": 0.0}
    )
    thread_dur: dict[tuple[Any, Any], float] = defaultdict(float)

    min_ts = None
    max_ts = None
    total_x_events = 0
    cpu_x_events = 0

    for event in events:
        if not isinstance(event, dict):
            continue
        ph = event.get("ph")
        if ph != "X":
            continue
        total_x_events += 1

        dur = event.get("dur")
        ts = event.get("ts")
        if not isinstance(dur, (int, float)):
            continue

        if isinstance(ts, (int, float)):
            min_ts = ts if min_ts is None else min(min_ts, ts)
            max_ts_end = ts + dur
            max_ts = max_ts_end if max_ts is None else max(max_ts, max_ts_end)

        cat = str(event.get("cat", ""))
        name = str(event.get("name", "unknown"))
        pid = event.get("pid")
        tid = event.get("tid")

        if "cpu" in cat.lower():
            cpu_x_events += 1
            stat = op_stats[name]
            stat["count"] += 1
            stat["total_dur_us"] += float(dur)
            stat["max_dur_us"] = max(stat["max_dur_us"], float(dur))
            thread_dur[(pid, tid)] += float(dur)

    top_ops = []
    for name, stat in op_stats.items():
        cnt = int(stat["count"])
        total = stat["total_dur_us"]
        top_ops.append(
            {
                "name": name,
                "count": cnt,
                "total_dur_us": total,
                "avg_dur_us": (total / cnt) if cnt else None,
                "max_dur_us": stat["max_dur_us"],
            }
        )
    top_ops.sort(key=lambda x: x["total_dur_us"], reverse=True)

    top_threads = [
        {"pid": pid, "tid": tid, "total_dur_us": dur}
        for (pid, tid), dur in sorted(thread_dur.items(), key=lambda x: x[1], reverse=True)[:top_n]
    ]

    result["summary"] = {
        "events_total": len(events),
        "x_events_total": total_x_events,
        "cpu_x_events": cpu_x_events,
        "time_window_us": (max_ts - min_ts) if min_ts is not None and max_ts is not None else None,
        "unique_cpu_ops": len(op_stats),
    }
    result["top_ops"] = top_ops[:top_n]
    result["top_threads"] = top_threads
    return result


def _render_markdown(memory: dict[str, Any] | None, cpu: dict[str, Any] | None) -> str:
    lines = ["# Model Resource Profile Report", ""]

    if memory:
        lines.extend(["## GPU Memory Snapshot", ""])
        if memory.get("error"):
            lines.append(f"- Error: {memory['error']}")
        else:
            summary = memory.get("summary", {})
            lines.append(f"- Segments: {summary.get('segments', 0)}")
            lines.append(
                f"- Reserved / Allocated / Active: {_format_bytes(summary.get('reserved_bytes', float('nan')))} / "
                f"{_format_bytes(summary.get('allocated_bytes', float('nan')))} / "
                f"{_format_bytes(summary.get('active_bytes', float('nan')))}"
            )
            ratio = summary.get("reserved_vs_allocated_ratio")
            lines.append(
                f"- Reserved:Allocated ratio: {ratio:.2f}"
                if isinstance(ratio, (int, float))
                else "- Reserved:Allocated ratio: n/a"
            )
            lines.append("")

            lines.append("### Segment Types")
            seg_types = memory.get("segment_types", {})
            if seg_types:
                for seg_type, values in sorted(
                    seg_types.items(), key=lambda kv: kv[1].get("reserved_bytes", 0), reverse=True
                ):
                    lines.append(
                        f"- {seg_type}: segments={values.get('segments', 0)}, "
                        f"reserved={_format_bytes(values.get('reserved_bytes', 0))}, "
                        f"allocated={_format_bytes(values.get('allocated_bytes', 0))}"
                    )
            else:
                lines.append("- n/a")
            lines.append("")

            lines.append("### Largest Segments")
            largest = memory.get("largest_segments", [])
            if largest:
                for seg in largest[:10]:
                    lines.append(
                        f"- device={seg.get('device')} type={seg.get('segment_type')} "
                        f"reserved={_format_bytes(seg.get('reserved'))} "
                        f"allocated={_format_bytes(seg.get('allocated'))} "
                        f"slack={_format_bytes(seg.get('slack'))}"
                    )
            else:
                lines.append("- n/a")
            lines.append("")

            action_counts = memory.get("trace_actions", {}).get("counts", {})
            if action_counts:
                lines.append("### Allocator Actions")
                for name, count in list(action_counts.items())[:10]:
                    lines.append(f"- {name}: {count}")
                lines.append("")

    if cpu:
        lines.extend(["## CPU Trace Summary", ""])
        if cpu.get("error"):
            lines.append(f"- Error: {cpu['error']}")
        else:
            summary = cpu.get("summary", {})
            lines.append(f"- Total events: {summary.get('events_total', 0)}")
            lines.append(f"- CPU X-events: {summary.get('cpu_x_events', 0)}")
            lines.append(f"- Unique CPU ops: {summary.get('unique_cpu_ops', 0)}")
            window = summary.get("time_window_us")
            lines.append(
                f"- Trace window: {(window / 1e6):.3f} s"
                if isinstance(window, (int, float))
                else "- Trace window: n/a"
            )
            lines.append("")

            lines.append("### Top CPU Ops (by total duration)")
            top_ops = cpu.get("top_ops", [])
            if top_ops:
                for op in top_ops[:15]:
                    lines.append(
                        f"- {op.get('name')}: total={op.get('total_dur_us', 0):.1f} us, "
                        f"count={op.get('count', 0)}, avg={op.get('avg_dur_us', 0):.1f} us, "
                        f"max={op.get('max_dur_us', 0):.1f} us"
                    )
            else:
                lines.append("- n/a")
            lines.append("")

            lines.append("### Top Threads")
            threads = cpu.get("top_threads", [])
            if threads:
                for thread in threads[:10]:
                    lines.append(
                        f"- pid={thread.get('pid')} tid={thread.get('tid')}: "
                        f"total={thread.get('total_dur_us', 0):.1f} us"
                    )
            else:
                lines.append("- n/a")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze model GPU memory snapshots (JSON) and CPU profiler traces."
    )
    parser.add_argument(
        "--memory-json",
        type=Path,
        help="Path to torch CUDA memory snapshot JSON/JSON.GZ",
    )
    parser.add_argument(
        "--memory-pickle",
        type=Path,
        help="Deprecated and disabled for security. Convert snapshot to JSON instead.",
    )
    parser.add_argument("--cpu-trace", type=Path, help="Path to PyTorch profiler trace json/json.gz")
    parser.add_argument("--top-n", type=int, default=20, help="Top entries for ops/segments")
    parser.add_argument("--json-out", type=Path, help="Write full analysis json to this file")
    parser.add_argument("--md-out", type=Path, help="Write markdown report to this file")
    args = parser.parse_args()

    if args.memory_pickle is not None:
        raise SystemExit(
            "--memory-pickle is disabled for security. "
            "Please export the snapshot as JSON/JSON.GZ and use --memory-json."
        )

    if not args.memory_json and not args.cpu_trace:
        raise SystemExit("At least one of --memory-json or --cpu-trace is required")

    memory = analyze_memory_snapshot(args.memory_json, args.top_n) if args.memory_json else None
    cpu = analyze_cpu_trace(args.cpu_trace, args.top_n) if args.cpu_trace else None

    report = {"memory": memory, "cpu": cpu}
    md = _render_markdown(memory, cpu)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(md, encoding="utf-8")

    print(md)


if __name__ == "__main__":
    main()
