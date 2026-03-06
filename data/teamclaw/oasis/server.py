"""
OASIS Forum - FastAPI Server

A standalone discussion forum service where resident expert agents
debate user-submitted questions in parallel.

Start with:
    uvicorn oasis.server:app --host 0.0.0.0 --port 51202
    or
    python -m oasis.server
"""

import os
import sys
import asyncio
import uuid
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import uvicorn

from dotenv import load_dotenv

# --- Path setup ---
_this_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_this_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

env_path = os.path.join(_project_root, "config", ".env")
load_dotenv(dotenv_path=env_path)

from oasis.models import (
    CreateTopicRequest,
    TopicDetail,
    TopicSummary,
    PostInfo,
    TimelineEventInfo,
    DiscussionStatus,
)
from oasis.forum import DiscussionForum
from oasis.engine import DiscussionEngine


# --- In-memory storage ---
discussions: dict[str, DiscussionForum] = {}
engines: dict[str, DiscussionEngine] = {}
tasks: dict[str, asyncio.Task] = {}


# --- Helpers ---

def _get_forum_or_404(topic_id: str) -> DiscussionForum:
    forum = discussions.get(topic_id)
    if not forum:
        raise HTTPException(404, "Topic not found")
    return forum


def _check_owner(forum: DiscussionForum, user_id: str):
    """Verify the requester owns this discussion."""
    if forum.user_id != user_id:
        raise HTTPException(403, "You do not own this discussion")


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    loaded = DiscussionForum.load_all()
    discussions.update(loaded)
    print(f"[OASIS] 🏛️ Forum server started (loaded {len(loaded)} historical discussions)")
    yield
    for tid, forum in discussions.items():
        if forum.status == "discussing":
            forum.status = "error"
            forum.conclusion = "服务关闭，讨论被终止"
        forum.save()
    print("[OASIS] 🏛️ Forum server stopped (all discussions saved)")


app = FastAPI(
    title="OASIS Discussion Forum",
    description="Multi-expert parallel discussion service",
    lifespan=lifespan,
)


# ------------------------------------------------------------------
# Background task runner
# ------------------------------------------------------------------
async def _run_discussion(topic_id: str, engine: DiscussionEngine):
    """Run a discussion engine in the background, then fire callback if configured."""
    forum = discussions.get(topic_id)
    try:
        await engine.run()
    except Exception as e:
        print(f"[OASIS] ❌ Topic {topic_id} background error: {e}")
        if forum:
            forum.status = "error"
            forum.conclusion = f"讨论出错: {str(e)}"

    if forum:
        forum.save()

    # Fire callback notification
    cb_url = getattr(engine, "callback_url", None)
    if cb_url:
        conclusion = forum.conclusion if forum else "（无结论）"
        status = forum.status if forum else "error"
        cb_session = getattr(engine, "callback_session_id", "default") or "default"
        user_id = forum.user_id if forum else "anonymous"
        internal_token = os.getenv("INTERNAL_TOKEN", "")

        text = (
            f"[OASIS 子任务完成通知]\n"
            f"Topic ID: {topic_id}\n"
            f"状态: {status}\n"
            f"主题: {forum.question if forum else '?'}\n\n"
            f"📋 结论:\n{conclusion}"
        )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    cb_url,
                    json={"user_id": user_id, "text": text, "session_id": cb_session},
                    headers={"X-Internal-Token": internal_token},
                )
            print(f"[OASIS] 📨 Callback sent for {topic_id} → {cb_session}")
        except Exception as cb_err:
            print(f"[OASIS] ⚠️ Callback failed for {topic_id}: {cb_err}")


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@app.post("/topics", response_model=dict)
async def create_topic(req: CreateTopicRequest):
    """Create a new discussion topic. Returns topic_id for tracking."""
    topic_id = str(uuid.uuid4())[:8]

    forum = DiscussionForum(
        topic_id=topic_id,
        question=req.question,
        user_id=req.user_id,
        max_rounds=req.max_rounds,
    )
    discussions[topic_id] = forum
    forum.save()

    engine = DiscussionEngine(
        forum=forum,
        schedule_yaml=req.schedule_yaml,
        schedule_file=req.schedule_file,
        bot_enabled_tools=req.bot_enabled_tools,
        bot_timeout=req.bot_timeout,
        user_id=req.user_id,
        early_stop=req.early_stop,
        discussion=req.discussion,
    )
    engine.callback_url = req.callback_url
    engine.callback_session_id = req.callback_session_id
    engines[topic_id] = engine

    task = asyncio.create_task(_run_discussion(topic_id, engine))
    tasks[topic_id] = task

    return {
        "topic_id": topic_id,
        "status": "pending",
        "message": f"Discussion started with {len(engine.experts)} experts",
    }


@app.delete("/topics/{topic_id}")
async def cancel_topic(topic_id: str, user_id: str = Query(...)):
    """Force-cancel a running discussion."""
    forum = _get_forum_or_404(topic_id)
    _check_owner(forum, user_id)

    if forum.status != "discussing":
        return {"topic_id": topic_id, "status": forum.status, "message": "Discussion already finished"}

    engine = engines.get(topic_id)
    if engine:
        engine.cancel()

    task = tasks.get(topic_id)
    if task and not task.done():
        task.cancel()

    forum.save()
    return {"topic_id": topic_id, "status": "cancelled", "message": "Discussion cancelled"}


@app.post("/topics/{topic_id}/purge")
async def purge_topic(topic_id: str, user_id: str = Query(...)):
    """Permanently delete a discussion record."""
    forum = _get_forum_or_404(topic_id)
    _check_owner(forum, user_id)

    if forum.status in ("pending", "discussing"):
        engine = engines.get(topic_id)
        if engine:
            engine.cancel()
        task = tasks.get(topic_id)
        if task and not task.done():
            task.cancel()

    storage_path = forum._storage_path()
    if os.path.exists(storage_path):
        os.remove(storage_path)

    discussions.pop(topic_id, None)
    engines.pop(topic_id, None)
    tasks.pop(topic_id, None)

    return {"topic_id": topic_id, "message": "Discussion permanently deleted"}


@app.delete("/topics")
async def purge_all_topics(user_id: str = Query(...)):
    """Delete all topics for a specific user."""
    global discussions, engines, tasks

    to_delete = [
        tid for tid, forum in discussions.items()
        if forum.user_id == user_id
    ]

    deleted_count = 0
    for tid in to_delete:
        forum = discussions.get(tid)
        if forum:
            if forum.status in ("pending", "discussing"):
                engine = engines.get(tid)
                if engine:
                    engine.cancel()
                task = tasks.get(tid)
                if task and not task.done():
                    task.cancel()

            storage_path = forum._storage_path()
            if os.path.exists(storage_path):
                os.remove(storage_path)

            discussions.pop(tid, None)
            engines.pop(tid, None)
            tasks.pop(tid, None)
            deleted_count += 1

    return {"deleted_count": deleted_count, "message": f"Deleted {deleted_count} topics"}


@app.get("/topics/{topic_id}", response_model=TopicDetail)
async def get_topic(topic_id: str, user_id: str = Query(...)):
    """Get full discussion detail."""
    forum = _get_forum_or_404(topic_id)
    _check_owner(forum, user_id)

    posts = await forum.browse()
    return TopicDetail(
        topic_id=forum.topic_id,
        question=forum.question,
        user_id=forum.user_id,
        status=DiscussionStatus(forum.status),
        current_round=forum.current_round,
        max_rounds=forum.max_rounds,
        posts=[
            PostInfo(
                id=p.id,
                author=p.author,
                content=p.content,
                reply_to=p.reply_to,
                upvotes=p.upvotes,
                downvotes=p.downvotes,
                timestamp=p.timestamp,
                elapsed=p.elapsed,
            )
            for p in posts
        ],
        timeline=[
            TimelineEventInfo(
                elapsed=e.elapsed,
                event=e.event,
                agent=e.agent,
                detail=e.detail,
            )
            for e in forum.timeline
        ],
        discussion=forum.discussion,
        conclusion=forum.conclusion,
    )


@app.get("/topics/{topic_id}/stream")
async def stream_topic(topic_id: str, user_id: str = Query(...)):
    """SSE stream for real-time discussion updates."""
    forum = _get_forum_or_404(topic_id)
    _check_owner(forum, user_id)

    async def event_generator():
        last_count = 0
        last_round = 0
        last_timeline_idx = 0      # 已发送的 timeline 事件索引

        while forum.status in ("pending", "discussing"):
            if forum.discussion:
                # ── 讨论模式：原有逻辑，按帖子轮询 ──
                posts = await forum.browse()

                if forum.current_round > last_round:
                    last_round = forum.current_round
                    yield f"data: 📢 === 第 {last_round} 轮讨论 ===\n\n"

                if len(posts) > last_count:
                    for p in posts[last_count:]:
                        prefix = f"↳回复#{p.reply_to}" if p.reply_to else "📌"
                        yield (
                            f"data: {prefix} [{p.author}] "
                            f"(👍{p.upvotes}): {p.content}\n\n"
                        )
                    last_count = len(posts)
            else:
                # ── 执行模式：timeline 事件当普通消息发送 ──
                tl = forum.timeline

                while last_timeline_idx < len(tl):
                    ev = tl[last_timeline_idx]
                    last_timeline_idx += 1

                    if ev.event == "start":
                        yield f"data: 🚀 执行开始\n\n"
                    elif ev.event == "round":
                        yield f"data: 📢 {ev.detail}\n\n"
                    elif ev.event == "agent_call":
                        yield f"data: ⏳ {ev.agent} 开始执行...\n\n"
                    elif ev.event == "agent_done":
                        yield f"data: ✅ {ev.agent} 执行完成\n\n"
                    elif ev.event == "conclude":
                        yield f"data: 🏁 执行完成\n\n"

            await asyncio.sleep(1)

        if forum.discussion:
            if forum.conclusion:
                yield f"data: \n🏆 === 讨论结论 ===\n{forum.conclusion}\n\n"
        else:
            yield f"data: ✅ 已完成\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/topics", response_model=list[TopicSummary])
async def list_topics(user_id: str = Query(...)):
    """List discussion topics for a specific user."""
    items = []
    for f in discussions.values():
        if f.user_id != user_id:
            continue
        items.append(
            TopicSummary(
                topic_id=f.topic_id,
                question=f.question,
                user_id=f.user_id,
                status=DiscussionStatus(f.status),
                post_count=len(f.posts),
                current_round=f.current_round,
                max_rounds=f.max_rounds,
                created_at=f.created_at,
            )
        )
    items.sort(key=lambda x: x.created_at, reverse=True)
    return items


@app.get("/topics/{topic_id}/conclusion")
async def get_conclusion(topic_id: str, user_id: str = Query(...), timeout: int = 300):
    """Get the final conclusion (blocks until discussion finishes)."""
    forum = _get_forum_or_404(topic_id)
    _check_owner(forum, user_id)

    elapsed = 0
    while forum.status not in ("concluded", "error") and elapsed < timeout:
        await asyncio.sleep(1)
        elapsed += 1

    if forum.status == "error":
        raise HTTPException(500, f"Discussion failed: {forum.conclusion}")
    if forum.status != "concluded":
        raise HTTPException(504, "Discussion timed out")

    return {
        "topic_id": topic_id,
        "question": forum.question,
        "conclusion": forum.conclusion,
        "rounds": forum.current_round,
        "total_posts": len(forum.posts),
    }


# ------------------------------------------------------------------
# Expert persona CRUD
# ------------------------------------------------------------------

@app.get("/experts")
async def list_experts(user_id: str = ""):
    """List all available expert agents (public + user custom)."""
    from oasis.experts import get_all_experts
    configs = get_all_experts(user_id or None)
    return {
        "experts": [
            {
                "name": c["name"],
                "tag": c["tag"],
                "persona": c["persona"],
                "source": c.get("source", "public"),
            }
            for c in configs
        ]
    }


class UserExpertRequest(BaseModel):
    user_id: str
    name: str = ""
    tag: str = ""
    persona: str = ""
    temperature: float = 0.7


@app.post("/experts/user")
async def add_user_expert_route(req: UserExpertRequest):
    from oasis.experts import add_user_expert
    try:
        expert = add_user_expert(req.user_id, req.model_dump())
        return {"status": "ok", "expert": expert}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/experts/user/{tag}")
async def update_user_expert_route(tag: str, req: UserExpertRequest):
    from oasis.experts import update_user_expert
    try:
        expert = update_user_expert(req.user_id, tag, req.model_dump())
        return {"status": "ok", "expert": expert}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/experts/user/{tag}")
async def delete_user_expert_route(tag: str, user_id: str = Query(...)):
    from oasis.experts import delete_user_expert
    try:
        deleted = delete_user_expert(user_id, tag)
        return {"status": "ok", "deleted": deleted}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Entrypoint ---
if __name__ == "__main__":
    port = int(os.getenv("PORT_OASIS", "51202"))
    uvicorn.run(app, host="127.0.0.1", port=port)
