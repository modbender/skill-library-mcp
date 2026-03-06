#!/usr/bin/env python3
"""
Canvas LMS 监控模块

从 JHU Canvas 获取未来作业列表，返回标准化事件。

API 文档: https://canvas.instructure.com/doc/api/
认证: Bearer token (从 config/.env 读取 CANVAS_API_TOKEN)
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests

logger = logging.getLogger("heartbeat.canvas")

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_settings() -> dict:
    import yaml
    p = CONFIG_DIR / "settings.yaml"
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("monitoring", {}).get("canvas", {})


def _load_token() -> str:
    from dotenv import dotenv_values
    env_path = CONFIG_DIR / ".env"
    if not env_path.exists():
        return ""
    values = dotenv_values(env_path)
    return values.get("CANVAS_API_TOKEN", "").strip()


def is_configured() -> bool:
    """检查 Canvas token 是否已配置"""
    settings = _load_settings()
    if not settings.get("enabled", True):
        return False
    return bool(_load_token())


def sync() -> list[dict]:
    """
    从 Canvas API 获取未来作业列表。

    返回:
        [{"id": "canvas-{id}", "date": "YYYY-MM-DD", "description": "课程: 作业名",
          "category": "作业", "time": "HH:MM", "src": "canvas"}]

    如果 token 未配置或功能禁用，返回空列表。
    """
    settings = _load_settings()
    if not settings.get("enabled", True):
        logger.debug("Canvas 监控已禁用")
        return []

    token = _load_token()
    if not token:
        logger.warning("CANVAS_API_TOKEN 未配置，跳过 Canvas 同步")
        return []

    base_url = settings.get("base_url", "https://jhu.instructure.com")
    lookahead = settings.get("lookahead_days", 30)
    api_url = f"{base_url}/api/v1"
    headers = {"Authorization": f"Bearer {token}"}
    timeout = 30

    events = []

    try:
        # 1. 获取活跃课程
        courses = _get_active_courses(api_url, headers, timeout)
        logger.info("Canvas: 获取到 %d 个活跃课程", len(courses))

        # 2. 获取每个课程的作业
        deadline = datetime.now() + timedelta(days=lookahead)
        now = datetime.now()

        for course in courses:
            course_id = course["id"]
            course_name = course.get("name", f"Course {course_id}")
            try:
                assignments = _get_assignments(
                    api_url, headers, timeout, course_id, now, deadline
                )
                for a in assignments:
                    events.append(_normalize_assignment(a, course_name))
            except requests.RequestException as e:
                logger.warning("Canvas: 课程 %s 作业获取失败: %s", course_name, e)

        logger.info("Canvas: 共获取 %d 个待完成作业", len(events))

    except requests.RequestException as e:
        logger.error("Canvas API 请求失败: %s", e)

    return events


def _get_active_courses(api_url: str, headers: dict, timeout: int) -> list:
    """获取当前学期活跃课程"""
    courses = []
    url = f"{api_url}/courses"
    params = {
        "enrollment_state": "active",
        "per_page": 100,
    }

    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
        courses.extend(resp.json())

        # Canvas 分页通过 Link header
        url = _next_page_url(resp)
        params = {}  # 后续页不需要 params

    return courses


def _get_assignments(
    api_url: str, headers: dict, timeout: int,
    course_id: int, now: datetime, deadline: datetime,
) -> list:
    """获取课程中未来的未完成作业"""
    url = f"{api_url}/courses/{course_id}/assignments"
    params = {
        "per_page": 100,
        "order_by": "due_at",
        "include[]": "submission",
    }

    assignments = []

    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()

        for a in resp.json():
            due_at = a.get("due_at")
            if not due_at:
                continue

            try:
                due_dt = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
                due_local = due_dt.astimezone()  # 转换为本地时区
            except (ValueError, TypeError):
                continue

            # 筛选：在范围内且未完成
            if due_local.replace(tzinfo=None) > deadline:
                continue

            # 检查是否已提交
            submission = a.get("submission", {})
            if submission and submission.get("workflow_state") == "graded":
                if submission.get("score") is not None:
                    continue  # 已评分，跳过

            # 已提交的也包含（可能还没评分但已交）
            if a.get("has_submitted_submissions"):
                submitted = submission.get("submitted_at") if submission else None
                if submitted:
                    continue  # 已提交

            assignments.append({
                "id": a["id"],
                "name": a.get("name", "Untitled"),
                "due_at": due_local,
            })

        url = _next_page_url(resp)
        params = {}

    return assignments


def _normalize_assignment(assignment: dict, course_name: str) -> dict:
    """将 Canvas 作业标准化为事件格式"""
    due = assignment["due_at"]
    return {
        "id": f"canvas-{assignment['id']}",
        "date": due.strftime("%Y-%m-%d"),
        "description": f"{course_name}: {assignment['name']}",
        "category": "作业",
        "time": due.strftime("%H:%M"),
        "src": "canvas",
    }


def _next_page_url(resp: requests.Response) -> str | None:
    """从 Canvas Link header 解析下一页 URL"""
    link = resp.headers.get("Link", "")
    for part in link.split(","):
        if 'rel="next"' in part:
            url = part.split(";")[0].strip().strip("<>")
            return url
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = sync()
    for r in results:
        print(f"  {r['date']} | {r['description']} | [{r['category']}] @time:{r['time']} @src:{r['src']} @id:{r['id']}")
    if not results:
        print("  (无结果 - 请检查 CANVAS_API_TOKEN 配置)")
