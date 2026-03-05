#!/usr/bin/env python3
"""
check_agents.py - Core logic for check-agents.sh (dev-team skill).
Reads task registry, updates PR/session state, writes back and optional notifications.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="Check agents and advance PR pipeline")
    parser.add_argument("--tasks-file", required=True, help="Path to active-tasks.json (or temp copy)")
    parser.add_argument("--notify-file", required=True, help="Path to notifications.json")
    parser.add_argument("--repos-base", default="", help="Base dir for repo lookup")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--retry-delay", type=int, default=60)
    parser.add_argument("--auto-merge-default", type=int, default=0, help="0 or 1")
    args = parser.parse_args()

    tasks_file = os.path.abspath(args.tasks_file)
    notify_file = os.path.abspath(args.notify_file)
    tasks_dir = os.path.dirname(tasks_file)
    repos_base = args.repos_base or tasks_dir
    max_retries = args.max_retries
    retry_delay = args.retry_delay
    auto_merge_default = bool(args.auto_merge_default)

    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    needs_update = False
    notifications: list[dict] = []
    now_ms = int(time.time() * 1000)

    def gh_available() -> bool:
        return shutil.which("gh") is not None

    def gh_auth_ok() -> bool:
        if not gh_available():
            return False
        proc = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        if "token in default is invalid" in output.lower():
            return False
        if "not logged into any github hosts" in output.lower():
            return False
        return proc.returncode == 0

    GH_READY = gh_auth_ok()

    def set_cleanup_eligibility(agent: dict, now_ms: int) -> None:
        if agent.get("cleanupMode") != "session_ttl":
            return
        ttl = agent.get("cleanupAfterSeconds")
        try:
            ttl = int(ttl) if ttl is not None else 3600
        except Exception:
            ttl = 3600
        ttl = max(0, ttl)
        agent["cleanupEligibleAt"] = now_ms + (ttl * 1000)

    def restart_agent(agent: dict) -> tuple[bool, str]:
        session = agent.get("tmuxSession", "")
        worktree = agent.get("worktree", "")
        command_shell = agent.get("commandShell", "") or ""
        log_file = agent.get("logFile", "")
        launch_script = agent.get("launchScript", "")

        if not session or not worktree:
            return False, "missing session/worktree metadata"
        if not launch_script and not command_shell:
            return False, "missing launchScript and commandShell"

        if not os.path.isabs(worktree):
            worktree = os.path.abspath(os.path.join(tasks_dir, worktree))
        if not os.path.exists(worktree):
            return False, f"worktree not found: {worktree}"

        if launch_script:
            if not os.path.isabs(launch_script):
                launch_script = os.path.abspath(os.path.join(tasks_dir, launch_script))
            if os.path.exists(launch_script):
                proc = subprocess.run(
                    ["tmux", "new-session", "-d", "-s", session, f"bash {shlex.quote(launch_script)}"],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode == 0:
                    return True, ""
                return False, (proc.stderr or proc.stdout or "unknown tmux error").strip()

        if command_shell:
            if log_file:
                if not os.path.isabs(log_file):
                    log_file = os.path.abspath(os.path.join(tasks_dir, log_file))
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                wrapped_cmd = f"cd {shlex.quote(worktree)} && {command_shell} 2>&1 | tee -a {shlex.quote(log_file)}"
            else:
                wrapped_cmd = f"cd {shlex.quote(worktree)} && {command_shell}"
            proc = subprocess.run(
                ["tmux", "new-session", "-d", "-s", session, wrapped_cmd],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                return True, ""
            return False, (proc.stderr or proc.stdout or "unknown tmux error").strip()
        return False, "launchScript missing and commandShell empty"

    def get_log_observation(agent: dict) -> dict:
        log_file = agent.get("logFile", "")
        if not log_file:
            return {"exists": False, "size": 0, "mtime_ms": 0}
        if not os.path.isabs(log_file):
            log_file = os.path.abspath(os.path.join(tasks_dir, log_file))
        if not os.path.exists(log_file):
            return {"exists": False, "size": 0, "mtime_ms": 0}
        try:
            st = os.stat(log_file)
            return {"exists": True, "size": int(st.st_size), "mtime_ms": int(st.st_mtime * 1000)}
        except Exception:
            return {"exists": False, "size": 0, "mtime_ms": 0}

    def detect_empty_shell_session(agent: dict, now_ms: int) -> tuple[bool, str]:
        session = agent.get("tmuxSession", "")
        if not session:
            return False, ""
        checks = agent.setdefault("checks", {})
        pane = subprocess.run(
            ["tmux", "list-panes", "-t", session, "-F", "#{pane_current_command}"],
            capture_output=True,
            text=True,
        )
        if pane.returncode != 0:
            return False, ""
        current_cmd = (pane.stdout or "").splitlines()[:1]
        current_cmd = (current_cmd[0].strip().lower() if current_cmd else "")
        shell_like = current_cmd in {"zsh", "bash", "sh", "fish"}
        if not shell_like:
            checks["emptyShellStrikeCount"] = 0
            checks.pop("lastEmptyShellObservedAt", None)
            return False, ""
        obs = get_log_observation(agent)
        checks["lastObservedLogSize"] = obs["size"]
        checks["lastObservedLogMtime"] = obs["mtime_ms"]
        started_at = int(agent.get("startedAt") or 0)
        if started_at and (now_ms - started_at) < 15000:
            return False, ""
        strikes = int(checks.get("emptyShellStrikeCount") or 0)
        last_seen = int(checks.get("lastEmptyShellObservedAt") or 0)
        checks["lastEmptyShellObservedAt"] = now_ms
        if obs["size"] == 0:
            strikes += 1
            checks["emptyShellStrikeCount"] = strikes
            if strikes >= 2:
                return True, f"empty_shell_no_log(current={current_cmd})"
            return False, ""
        if last_seen and (now_ms - last_seen) < 10000:
            return False, ""
        strikes += 1
        checks["emptyShellStrikeCount"] = strikes
        if strikes >= 3:
            return True, f"empty_shell_after_output(current={current_cmd})"
        return False, ""

    def handle_retry_or_fail(
        agent: dict, now_ms: int, session: str, description: str, failure_reason: str
    ) -> None:
        nonlocal needs_update
        retry_count = int(agent.get("retryCount", 0) or 0)
        checks = agent.setdefault("checks", {})
        checks["lastFailureReason"] = failure_reason
        if retry_count >= max_retries:
            set_status(agent, "failed", now_ms, reason="retry_exhausted_without_pr")
            agent["failedAt"] = now_ms
            print(f"✗ Agent {session} failed after {retry_count} retries")
            maybe_notify(agent, "error", f"❌ 任务失败: {description}")
            return
        last_retry_at = agent.get("lastRetriedAt", 0)
        if retry_delay > 0 and last_retry_at and (now_ms - last_retry_at) < retry_delay * 1000:
            remaining = int(retry_delay - ((now_ms - last_retry_at) / 1000))
            print(f"⏳ Agent {session} retry delayed ({max(0, remaining)}s left)")
            return
        next_retry = retry_count + 1
        ok, reason = restart_agent(agent)
        agent["retryCount"] = next_retry
        agent["lastRetriedAt"] = now_ms
        if ok:
            checks["emptyShellStrikeCount"] = 0
            checks.pop("lastEmptyShellObservedAt", None)
            print(f"↻ Agent {session} restarted ({next_retry}/{max_retries})")
            maybe_notify(agent, "warning", f"⚠️ 任务重试中 ({next_retry}/{max_retries}): {description}")
            return
        print(f"⚠ Agent {session} restart failed ({next_retry}/{max_retries}): {reason}")
        checks["lastRestartError"] = reason
        if next_retry >= max_retries:
            set_status(agent, "failed", now_ms, reason="restart_failed")
            agent["failedAt"] = now_ms
            maybe_notify(agent, "error", f"❌ 任务失败(重启失败): {description}")

    def task_repo_cwd(agent: dict | None) -> str | None:
        if agent is None:
            return None
        repo = agent.get("repo", "")
        repo_path = agent.get("repoPath", os.path.join(repos_base, repo))
        return repo_path if repo_path and os.path.exists(repo_path) else None

    def gh_cmd(gh_args: list, agent: dict | None = None) -> tuple[str | None, str]:
        if not GH_READY:
            return None, "gh_not_ready"
        cwd = task_repo_cwd(agent)
        proc = subprocess.run(["gh"] + gh_args, capture_output=True, text=True, cwd=cwd)
        if proc.returncode != 0:
            return None, (proc.stderr or proc.stdout or "gh command failed").strip()
        return proc.stdout, ""

    def get_pr_info(agent: dict) -> tuple[dict | None, str]:
        branch = agent.get("branch", "")
        checks = agent.setdefault("checks", {})
        pr_num = checks.get("prNumber")
        if not pr_num:
            out, err = gh_cmd(
                ["pr", "list", "--head", branch, "--json", "number,url,headRefName,baseRefName"],
                agent=agent,
            )
            if out is None:
                checks["lastGhError"] = err
                return None, err
            try:
                arr = json.loads(out or "[]")
            except Exception:
                checks["lastGhError"] = "invalid gh pr list json"
                return None, "invalid gh pr list json"
            if not arr:
                return None, "pr_not_found"
            item = arr[0]
            pr_num = item.get("number")
            checks["prNumber"] = pr_num
            checks["prUrl"] = item.get("url")
            if item.get("baseRefName"):
                checks["prBaseRef"] = item.get("baseRefName")
        view_fields = "number,url,state,isDraft,reviewDecision,mergeStateStatus,mergedAt,updatedAt"
        out, err = gh_cmd(["pr", "view", str(pr_num), "--json", view_fields], agent=agent)
        if out is None:
            checks["lastGhError"] = err
            return None, err
        try:
            pr = json.loads(out)
        except Exception:
            checks["lastGhError"] = "invalid gh pr view json"
            return None, "invalid gh pr view json"
        checks["prNumber"] = pr.get("number")
        checks["prUrl"] = pr.get("url")
        checks["prState"] = pr.get("state")
        checks["reviewDecision"] = pr.get("reviewDecision")
        checks["mergeStateStatus"] = pr.get("mergeStateStatus")
        checks["prMergedAt"] = pr.get("mergedAt")
        return pr, ""

    def get_pr_checks(agent: dict, pr_number: int) -> tuple[dict, str]:
        checks = agent.setdefault("checks", {})
        out, err = gh_cmd(
            ["pr", "checks", str(pr_number), "--required", "--json", "bucket,name,state,workflow,link"],
            agent=agent,
        )
        if out is None:
            if "no required checks reported" in (err or "").lower():
                checks["requiredChecksSummary"] = {"bucket": "none", "total": 0}
                checks.pop("lastChecksError", None)
                return {"bucket": "none", "rows": []}, ""
            checks["lastChecksError"] = err
            return None, err
        try:
            rows = json.loads(out or "[]")
        except Exception:
            checks["lastChecksError"] = "invalid gh pr checks json"
            return None, "invalid gh pr checks json"
        if not rows:
            checks["requiredChecksSummary"] = {"bucket": "none", "total": 0}
            return {"bucket": "none", "rows": []}, ""
        buckets = [r.get("bucket") for r in rows]
        if any(b == "fail" for b in buckets):
            bucket = "fail"
        elif any(b in ("pending", "cancel") for b in buckets):
            bucket = "pending"
        elif all(b in ("pass", "skipping") for b in buckets):
            bucket = "pass"
        else:
            bucket = "pending"
        checks["requiredChecksSummary"] = {"bucket": bucket, "total": len(rows)}
        return {"bucket": bucket, "rows": rows}, ""

    def set_status(agent: dict, new_status: str, now_ms: int, reason: str | None = None) -> bool:
        nonlocal needs_update
        old_status = agent.get("status")
        if old_status != new_status:
            agent["status"] = new_status
            agent.setdefault("statusHistory", []).append(
                {"from": old_status, "to": new_status, "at": now_ms, "reason": reason}
            )
            needs_update = True
            return True
        return False

    def maybe_notify(agent: dict, ntype: str, message: str) -> None:
        notifications.append(
            {"type": ntype, "message": message, "repo": agent.get("repo", ""), "branch": agent.get("branch", "")}
        )

    def try_merge_pr(agent: dict, pr_number: int) -> tuple[bool, str]:
        checks = agent.setdefault("checks", {})
        merge_method = agent.get("mergeMethod") or "squash"
        merge_args = ["pr", "merge", str(pr_number), f"--{merge_method}", "--delete-branch"]
        if agent.get("autoMerge") or auto_merge_default:
            merge_args.append("--auto")
        out, err = gh_cmd(merge_args, agent=agent)
        if out is None:
            checks["lastMergeError"] = err
            return False, err
        checks["mergeTriggeredAt"] = now_ms
        checks["mergeCommand"] = " ".join(merge_args)
        return True, ""

    def advance_pr_pipeline(agent: dict) -> None:
        nonlocal needs_update
        description = agent.get("description", "")
        branch = agent.get("branch", "")
        checks = agent.setdefault("checks", {})
        pr, err = get_pr_info(agent)
        if pr is None:
            return
        pr_number = pr.get("number")
        pr_url = pr.get("url")
        review_decision = (pr.get("reviewDecision") or "").upper()
        merge_state_status = (pr.get("mergeStateStatus") or "").upper()
        merged_at = pr.get("mergedAt")
        pr_state = (pr.get("state") or "").upper()
        is_draft = bool(pr.get("isDraft"))
        checks_result, _ = get_pr_checks(agent, pr_number)
        checks_bucket = (checks_result or {}).get("bucket", "pending")

        if merged_at or pr_state == "MERGED":
            changed = set_status(agent, "merged", now_ms, reason="pr_merged")
            agent["completedAt"] = now_ms
            checks["prMerged"] = True
            checks["prMergedAt"] = merged_at or checks.get("prMergedAt")
            if changed:
                print(f"✓ PR merged for {branch} (#{pr_number})")
                maybe_notify(agent, "success", f"✅ PR 已合并: {description}")
            return
        checks["prUrl"] = pr_url
        checks["prNumber"] = pr_number
        checks["isDraft"] = is_draft
        checks["reviewDecision"] = review_decision or None
        checks["mergeStateStatus"] = merge_state_status or None
        needs_update = True
        if is_draft:
            set_status(agent, "waiting_pr_ready", now_ms, reason="draft_pr")
            return
        if checks_bucket == "fail":
            changed = set_status(agent, "checks_failed", now_ms, reason="required_checks_failed")
            if changed:
                print(f"✗ Required checks failed for {branch} (#{pr_number})")
                maybe_notify(agent, "error", f"❌ CI 检查失败: {description}")
            return
        if checks_bucket == "pending":
            set_status(agent, "waiting_checks", now_ms, reason="required_checks_pending")
            return
        if review_decision == "CHANGES_REQUESTED":
            changed = set_status(agent, "changes_requested", now_ms, reason="review_changes_requested")
            if changed:
                print(f"⚠ Changes requested for {branch} (#{pr_number})")
                maybe_notify(agent, "warning", f"⚠️ 审查要求修改: {description}")
            return
        ai_review_done = bool(checks.get("codeReviewDone"))
        ai_review_agg = checks.get("reviewAggregate") or {}
        ai_task_status = ai_review_agg.get("taskStatus")
        ai_reason = ai_review_agg.get("reason")
        if ai_task_status in ("review_changes_requested", "review_human_attention"):
            set_status(agent, ai_task_status, now_ms, reason=f"ai_review_aggregate:{ai_reason or 'unknown'}")
            return
        if not ai_review_done:
            set_status(agent, "waiting_review", now_ms, reason="checks_passed_waiting_ai_review")
            return
        if ai_task_status == "waiting_human_approve" and review_decision != "APPROVED":
            set_status(agent, "waiting_human_approve", now_ms, reason="ai_review_pass_waiting_human_approve")
            return
        if review_decision == "APPROVED" and merge_state_status in ("CLEAN", "HAS_HOOKS", "UNSTABLE", "UNKNOWN"):
            changed = set_status(agent, "merge_ready", now_ms, reason="checks_passed_review_ok")
            if changed:
                print(f"✓ PR merge-ready for {branch} (#{pr_number})")
                maybe_notify(agent, "success", f"✅ PR 可合并: {description}")
            if agent.get("autoMerge") or auto_merge_default:
                ok, merge_err = try_merge_pr(agent, pr_number)
                if ok:
                    if set_status(agent, "merge_queued", now_ms, reason="gh_pr_merge_auto"):
                        print(f"↻ Auto-merge queued for {branch} (#{pr_number})")
                        maybe_notify(agent, "success", f"✅ 已触发自动合并: {description}")
                else:
                    checks["lastMergeError"] = merge_err
                    print(f"⚠ Auto-merge failed for {branch}: {merge_err}")
            return
        set_status(agent, "waiting_human_approve", now_ms, reason="checks_passed_waiting_human_approve")

    pr_pipeline_statuses = {
        "waiting_pr_ready", "waiting_checks", "checks_failed", "waiting_review", "review_commented",
        "review_changes_requested", "review_human_attention", "waiting_human_approve",
        "changes_requested", "merge_ready", "merge_queued",
    }

    for agent in data.get("agents", []):
        session = agent.get("tmuxSession", "")
        repo = agent.get("repo", "")
        repo_path = agent.get("repoPath", os.path.join(repos_base, repo))
        branch = agent.get("branch", "")
        description = agent.get("description", "")
        completion_mode = agent.get("completionMode", "pr")
        status = agent.get("status")

        if completion_mode == "pr" and status in pr_pipeline_statuses:
            advance_pr_pipeline(agent)
            continue
        if status != "running":
            continue

        result = subprocess.run(["tmux", "has-session", "-t", session], capture_output=True)
        forced_unhealthy_reason = None
        if result.returncode == 0:
            unhealthy, unhealthy_reason = detect_empty_shell_session(agent, now_ms)
            if unhealthy:
                forced_unhealthy_reason = unhealthy_reason or "empty_shell"
                agent.setdefault("checks", {})["lastUnhealthySessionReason"] = forced_unhealthy_reason
                agent.setdefault("checks", {})["lastUnhealthyAt"] = now_ms
                print(f"⚠ Session {session} unhealthy ({forced_unhealthy_reason}), killing for retry")
                subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)
                result = subprocess.CompletedProcess(args=["tmux", "has-session", "-t", session], returncode=1)
                needs_update = True

        if result.returncode != 0:
            print(f"Session {session} died")
            if completion_mode == "session" and not forced_unhealthy_reason:
                agent["status"] = "done"
                agent["completedAt"] = int(time.time() * 1000)
                agent.setdefault("checks", {})["completedBy"] = "session_exit"
                set_cleanup_eligibility(agent, now_ms)
                print(f"✓ Agent {session} completed - session exit mode")
                notifications.append(
                    {"type": "success", "message": f"✅ 任务完成(本地会话模式): {description}", "repo": repo, "branch": branch}
                )
                needs_update = True
                continue
            if completion_mode == "session" and forced_unhealthy_reason:
                handle_retry_or_fail(agent, now_ms, session, description, forced_unhealthy_reason)
                needs_update = True
                continue
            pr_check = None
            if GH_READY and os.path.exists(repo_path):
                pr_check = subprocess.run(
                    ["gh", "pr", "list", "--head", branch],
                    capture_output=True, text=True, cwd=repo_path,
                )
            elif GH_READY:
                pr_check = subprocess.run(["gh", "pr", "list", "--head", branch], capture_output=True, text=True)
            if pr_check and pr_check.stdout and pr_check.stdout.strip():
                set_status(agent, "waiting_checks", now_ms, reason="pr_created")
                agent.setdefault("checks", {})["prCreated"] = True
                print(f"✓ Agent {session} completed - PR created, waiting checks")
                maybe_notify(agent, "success", f"✅ PR 已创建，等待 CI: {description}")
                needs_update = True
                advance_pr_pipeline(agent)
            else:
                failure_reason = forced_unhealthy_reason or "session_exit_without_pr"
                handle_retry_or_fail(agent, now_ms, session, description, failure_reason)
                needs_update = True

    if not GH_READY:
        print("GH not ready (not logged in or token invalid); PR/CI/review pipeline checks skipped")

    data["activeCount"] = len([a for a in data.get("agents", []) if a.get("status") == "running"])
    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Active agents: {data['activeCount']}")

    if notifications:
        with open(notify_file, "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
        print(f"Written {len(notifications)} notifications")


if __name__ == "__main__":
    main()
    sys.exit(0)
