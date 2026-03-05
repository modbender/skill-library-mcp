# 


import os
import uuid
import json
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn
from dotenv import load_dotenv

# --- 路径配置 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
TASKS_FILE = os.path.join(root_dir, "data", "timeset", "tasks.json")

# 加载 .env 配置
load_dotenv(dotenv_path=os.path.join(root_dir, "config", ".env"))

# 确保目录存在
os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)

# --- JSON 持久化 ---
def load_tasks() -> dict:
    """从 JSON 文件加载任务配置"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tasks(tasks: dict):
    """保存任务配置到 JSON 文件"""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# --- 数据模型 ---
class CronTask(BaseModel):
    user_id: str
    cron: str  # 格式: "分 时 日 月 周"
    text: str
    session_id: str = "default"

class TaskResponse(BaseModel):
    task_id: str
    user_id: str
    cron: str
    text: str
    next_run: Optional[str]

# --- 全局调度器 ---
# misfire_grace_time: 错过触发后，在该秒数内仍会补触发（None=永远补触发）
# coalesce: 多次错过合并为一次执行
scheduler = AsyncIOScheduler(job_defaults={
    "misfire_grace_time": 3600,  # 错过1小时内仍补触发
    "coalesce": True,
})
PORT_AGENT = int(os.getenv("PORT_AGENT", "51200"))
AGENT_URL = f"http://127.0.0.1:{PORT_AGENT}/system_trigger"
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")

async def trigger_agent(user_id: str, text: str, session_id: str = "default"):
    """到达定时时间，向 Agent 发送 HTTP 请求"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(AGENT_URL, json={
                "user_id": user_id,
                "text": text,
                "session_id": session_id,
            }, headers={"X-Internal-Token": INTERNAL_TOKEN}, timeout=10.0)
            print(f"[{datetime.now()}] 任务触发：用户={user_id}, session={session_id}, 状态码={resp.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] 任务触发失败: {e}")

def restore_tasks():
    """从 JSON 文件恢复所有定时任务到调度器"""
    tasks = load_tasks()
    if not tasks:
        print("📭 无已保存的定时任务")
        return
    
    restored = 0
    for task_id, info in tasks.items():
        try:
            c = info["cron"].split()
            scheduler.add_job(
                trigger_agent,
                'cron',
                minute=c[0], hour=c[1], day=c[2], month=c[3], day_of_week=c[4],
                args=[info["user_id"], info["text"], info.get("session_id", "default")],
                id=task_id,
                replace_existing=True
            )
            restored += 1
            print(f"   - [ID: {task_id}] 用户: {info['user_id']}, cron: {info['cron']}, session: {info.get('session_id', 'default')}, 内容: {info['text']}")
        except Exception as e:
            print(f"   ⚠️ 恢复任务 {task_id} 失败: {e}")
    
    print(f"✅ 已从 {TASKS_FILE} 恢复 {restored} 个定时任务")

# --- 生命周期 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("定时调度中心启动...")
    scheduler.start()
    restore_tasks()
    yield
    print("定时调度中心关闭...")
    scheduler.shutdown()

app = FastAPI(title="Xavier Scheduler", lifespan=lifespan)

@app.post("/tasks", response_model=TaskResponse)
async def add_task(task: CronTask):
    task_id = str(uuid.uuid4())[:8]
    try:
        c = task.cron.split()
        scheduler.add_job(
            trigger_agent,
            'cron',
            minute=c[0], hour=c[1], day=c[2], month=c[3], day_of_week=c[4],
            args=[task.user_id, task.text, task.session_id],
            id=task_id,
            replace_existing=True
        )
        # 持久化到 JSON
        tasks = load_tasks()
        tasks[task_id] = {
            "user_id": task.user_id,
            "cron": task.cron,
            "text": task.text,
            "session_id": task.session_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_tasks(tasks)

        return {**task.model_dump(), "task_id": task_id, "next_run": "已激活"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cron 格式错误: {e}")

@app.get("/tasks")
async def list_tasks():
    tasks = load_tasks()
    return [
        {
            "task_id": j.id, 
            "user_id": j.args[0], 
            "text": j.args[1], 
            "cron": tasks.get(j.id, {}).get("cron", str(j.trigger)),
            "next_run": str(j.next_run_time)
        } for j in scheduler.get_jobs()
    ]

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)
        # 从 JSON 中删除
        tasks = load_tasks()
        tasks.pop(task_id, None)
        save_tasks(tasks)
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="未找到任务")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT_SCHEDULER", "51201")))