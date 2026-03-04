import os
import json
import hashlib
import asyncio
import secrets
import base64
import time
import uuid
from contextlib import asynccontextmanager

import aiosqlite
import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Any
import uvicorn

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from dotenv import load_dotenv

# API patch（提供音频格式适配和 MIME 修复）
from api_patch import patch_langchain_file_mime, build_audio_part
patch_langchain_file_mime()

from agent import MiniTimeAgent
from llm_factory import extract_text as _extract_text

# --- Path setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

env_path = os.path.join(root_dir, "config", ".env")
db_path = os.path.join(root_dir, "data", "agent_memory.db")
users_path = os.path.join(root_dir, "config", "users.json")
prompts_dir = os.path.join(root_dir, "data", "prompts")

load_dotenv(dotenv_path=env_path)


# --- Internal token for service-to-service auth ---
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "").strip()
if not INTERNAL_TOKEN:
    # Auto-generate a token and append to .env (replacing any empty INTERNAL_TOKEN= line)
    INTERNAL_TOKEN = secrets.token_hex(32)
    # Read existing content, replace empty placeholder if present
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "INTERNAL_TOKEN=" in content:
        # Replace empty or placeholder line with real value
        import re
        content = re.sub(
            r"^INTERNAL_TOKEN=\s*$",
            f"INTERNAL_TOKEN={INTERNAL_TOKEN}",
            content,
            flags=re.MULTILINE,
        )
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"\n# 内部服务间通信密钥（自动生成，勿泄露）\nINTERNAL_TOKEN={INTERNAL_TOKEN}\n")
    print(f"🔑 已自动生成 INTERNAL_TOKEN 并写入 {env_path}")


def verify_internal_token(token: str | None):
    """校验内部服务通信 token，失败抛 403"""
    if not token or token != INTERNAL_TOKEN:
        raise HTTPException(status_code=403, detail="无效的内部通信凭证")


# --- User auth helpers ---
def load_users() -> dict:
    """加载用户名-密码哈希配置"""
    if not os.path.exists(users_path):
        print(f"⚠️ 未找到用户配置文件 {users_path}，请先运行 python tools/gen_password.py 创建用户")
        return {}
    with open(users_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_password(username: str, password: str) -> bool:
    """验证用户密码：对输入密码做 sha256 后与配置中的哈希比对"""
    users = load_users()
    if username not in users:
        return False
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pw_hash == users[username]


# --- Create agent instance ---
agent = MiniTimeAgent(src_dir=current_dir, db_path=db_path)


# --- FastAPI lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.startup()
    await _init_group_db()   # 初始化群聊数据库（on_event 与 lifespan 不兼容）
    yield
    await agent.shutdown()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# --- CORS: 允许前端直连 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# --- Request models ---
class LoginRequest(BaseModel):
    user_id: str
    password: str

class UserRequest(BaseModel):
    user_id: str
    password: str
    text: str
    enabled_tools: Optional[list[str]] = None
    session_id: str = "default"
    images: Optional[list[str]] = None  # list of base64 data URIs
    files: Optional[list[dict]] = None  # list of {name: str, content: str}
    audios: Optional[list[dict]] = None  # list of {base64: str, name: str, format: str}

class SystemTriggerRequest(BaseModel):
    user_id: str
    text: str = "summary"
    session_id: str = "default"

class CancelRequest(BaseModel):
    user_id: str
    password: str
    session_id: str = "default"


# ------------------------------------------------------------------
# OpenAI-compatible request/response models
# ------------------------------------------------------------------

class ChatMessageContent(BaseModel):
    """OpenAI 消息内容部分（text / image_url / input_audio / file）"""
    type: str
    text: Optional[str] = None
    image_url: Optional[dict] = None
    input_audio: Optional[dict] = None
    file: Optional[dict] = None

class ChatMessage(BaseModel):
    """OpenAI 格式的消息"""
    role: str  # "system" | "user" | "assistant" | "tool"
    content: Optional[Any] = None  # str 或 list[ChatMessageContent]
    name: Optional[str] = None
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    """OpenAI /v1/chat/completions 请求格式"""
    model: Optional[str] = None
    messages: list[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    # OpenAI function calling 字段
    tools: Optional[list[dict]] = None       # [{type:"function", function:{name,description,parameters}}]
    tool_choice: Optional[Any] = None        # "auto" | "none" | "required" | {type:"function",function:{name:...}}
    # 扩展字段：认证 & 会话
    user: Optional[str] = None  # user_id
    # 自定义扩展（通过 extra_body 传入）
    session_id: Optional[str] = "default"
    password: Optional[str] = None
    enabled_tools: Optional[list[str]] = None


def _decode_pdf_data_uri(data_uri: str) -> bytes:
    """从 base64 data URI 解码出 PDF 字节。"""
    if "," in data_uri:
        data_uri = data_uri.split(",", 1)[1]
    return base64.b64decode(data_uri)


def _extract_pdf_text(data_uri: str) -> str:
    """从 base64 data URI 中提取 PDF 文本内容（纯文本模式）。"""
    try:
        import fitz  # pymupdf
        pdf_bytes = _decode_pdf_data_uri(data_uri)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages.append(f"--- 第{i+1}页 ---\n{text.strip()}")
        doc.close()
        if not pages:
            return "(PDF 未提取到文本内容，可能是扫描件/纯图片 PDF)"
        return "\n\n".join(pages)
    except ImportError:
        return "(服务端未安装 pymupdf，无法解析 PDF。请运行: pip install pymupdf)"
    except Exception as e:
        return f"(PDF 解析失败: {str(e)})"



def _is_vision_model() -> bool:
    """根据 LLM_VISION_SUPPORT 环境变量或模型名自动判断是否支持视觉。

    优先级：
    1. LLM_VISION_SUPPORT 显式设置 → 以用户配置为准
    2. 未设置 → 根据模型名自动推断
       - gpt-4o / gpt-4-vision / gpt-5 / o1 / o3 / o4 / gemini / claude → True
       - deepseek / qwen / glm / moonshot / yi- / minimax / ernie 等 → False
    """
    explicit = os.getenv("LLM_VISION_SUPPORT", "").strip().lower()
    if explicit:
        return explicit == "true"

    # 自动推断
    model = os.getenv("LLM_MODEL", "").lower()
    # 已知支持视觉的模型关键词
    vision_patterns = (
        "gpt-4o", "gpt-4-vision", "gpt-5", "gpt-o",
        "o1", "o3", "o4",
        "gemini",
        "claude",
    )
    for pat in vision_patterns:
        if pat in model:
            return True
    return False


def _build_human_message(text: str, images: list[str] | None = None, files: list[dict] | None = None, audios: list[dict] | None = None) -> HumanMessage:
    """构造 HumanMessage，支持图片、文件附件（文本/PDF）和音频。
    - 图片：当模型支持视觉时构造 OpenAI vision 格式；否则降级提示。
    - 文本文件：将文件内容以 markdown 代码块形式拼接到消息文本中。
    - PDF 文件：
        * 视觉模式：以 file content part 直传原始 PDF + 提取文本
        * 非视觉模式：pymupdf 提取纯文本
    - 音频：以 file content part 格式传入（data URI，兼容 OpenAI 代理）
    """
    vision_supported = _is_vision_model()

    # 收集需要以 file content part 直传的文件（PDF 视觉模式 + 媒体文件）
    direct_file_parts: list[dict] = []

    # MIME 类型映射（媒体文件）
    _MEDIA_MIME = {
        ".avi": "video/x-msvideo", ".mp4": "video/mp4", ".mkv": "video/x-matroska",
        ".mov": "video/quicktime", ".webm": "video/webm",
        ".mp3": "audio/mpeg", ".wav": "audio/wav", ".flac": "audio/flac",
        ".ogg": "audio/ogg", ".aac": "audio/aac",
    }

    # 拼接文件内容到消息末尾
    file_text = ""
    if files:
        file_parts = []
        for f in files:
            fname = f.get("name", "未知文件")
            ftype = f.get("type", "text")
            fcontent = f.get("content", "")

            if ftype == "pdf":
                if vision_supported:
                    # 视觉模式：以 file content part 直传 PDF + 提取文本备用
                    pdf_text = _extract_pdf_text(fcontent)
                    if len(pdf_text) > 50000:
                        pdf_text = pdf_text[:50000] + f"\n\n... (文件过长，已截断)"
                    pdf_data_uri = fcontent if fcontent.startswith("data:") else f"data:application/pdf;base64,{fcontent}"
                    direct_file_parts.append({
                        "type": "file",
                        "file": {
                            "filename": fname,
                            "file_data": pdf_data_uri,
                        },
                    })
                    file_parts.append(f"📄 **附件: {fname}** (已上传原始 PDF 供分析，同时附上提取的文本)\n```\n{pdf_text}\n```")
                else:
                    pdf_text = _extract_pdf_text(fcontent)
                    if len(pdf_text) > 50000:
                        pdf_text = pdf_text[:50000] + f"\n\n... (文件过长，已截断)"
                    file_parts.append(f"📄 **附件: {fname}**\n```\n{pdf_text}\n```")
            elif ftype == "media":
                # 媒体文件（视频/音频）：以 file content part 直传，不展开为文本
                ext = os.path.splitext(fname)[1].lower()
                mime = _MEDIA_MIME.get(ext, "application/octet-stream")
                data_uri = fcontent if fcontent.startswith("data:") else f"data:{mime};base64,{fcontent}"
                direct_file_parts.append({
                    "type": "file",
                    "file": {
                        "filename": fname,
                        "file_data": data_uri,
                    },
                })
                file_parts.append(f"🎬 **附件: {fname}** (已上传原始媒体文件供分析)")
            else:
                # 普通文本文件
                if len(fcontent) > 50000:
                    fcontent = fcontent[:50000] + f"\n\n... (文件过长，已截断，共 {len(f.get('content', ''))} 字符)"
                file_parts.append(f"📄 **附件: {fname}**\n```\n{fcontent}\n```")

        if file_parts:
            file_text = "\n\n" + "\n\n".join(file_parts)

    combined_text = (text or "") + file_text

    # 用户上传的图片
    all_images = list(images or [])

    # 判断是否有多模态内容（图片、直传文件、音频）
    has_multimodal = bool(all_images) or bool(direct_file_parts) or bool(audios)

    if not has_multimodal:
        return HumanMessage(content=combined_text or "(空消息)")

    if not vision_supported and (all_images or audios):
        hints = []
        if all_images:
            hints.append(f"你发送了{len(images or [])}张图片，但当前模型不支持图片识别，图片已忽略。")
            all_images = []
        if audios:
            hints.append(f"你发送了{len(audios)}条语音，但当前模型不支持音频输入，语音已忽略。")
            audios = None
        combined_text += f"\n\n[系统提示：{'；'.join(hints)}请切换到支持多模态的模型（如 gemini-2.0-flash、gpt-4o）后重试。]"
        # 如果没有直传文件 part，直接返回纯文本
        if not direct_file_parts:
            return HumanMessage(content=combined_text)

    # 多模态：构造 content list
    content_parts = []
    if combined_text:
        content_parts.append({"type": "text", "text": combined_text})
    elif audios:
        # 用户只发了语音没有文字，添加占位 text（API 代理要求至少有一个 text part）
        content_parts.append({"type": "text", "text": "请听取并处理以下音频："})

    # 图片：OpenAI vision 格式
    for img_data in all_images:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": img_data},
        })

    # 直传文件（PDF + 媒体文件）：以 file content part 传入
    content_parts.extend(direct_file_parts)

    # 音频：根据模式自动选择格式
    # 标准模式 -> type: "input_audio"，非标准模式 -> type: "file"
    if audios:
        for audio in audios:
            audio_b64 = audio.get("base64", "")
            audio_fmt = audio.get("format", "webm")
            audio_name = audio.get("name", f"recording.{audio_fmt}")
            content_parts.append(build_audio_part(audio_b64, audio_fmt, audio_name))

    return HumanMessage(content=content_parts)


# --- Routes ---

@app.get("/tools")
async def get_tools_list(
    x_internal_token: str | None = Header(None),
    authorization: str | None = Header(None),
):
    """返回当前 Agent 加载的所有 MCP 工具信息。
    认证方式（任选其一）：
    - X-Internal-Token 头部
    - Authorization: Bearer <user>:<password>
    """
    # 优先检查内部 token
    if x_internal_token and x_internal_token == INTERNAL_TOKEN:
        return {"status": "success", "tools": agent.get_tools_info()}
    # 再检查 Bearer 用户认证
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        parts = token.split(":")
        if token == INTERNAL_TOKEN:
            return {"status": "success", "tools": agent.get_tools_info()}
        if len(parts) >= 2 and verify_password(parts[0], parts[1]):
            return {"status": "success", "tools": agent.get_tools_info()}
    raise HTTPException(status_code=403, detail="认证失败")


@app.post("/login")
async def login(req: LoginRequest):
    if verify_password(req.user_id, req.password):
        return {"status": "success", "message": "登录成功"}
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.post("/ask", deprecated=True)
async def ask_agent(req: UserRequest):
    """[已弃用] 请使用 POST /v1/chat/completions (非流式, stream=false)"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # Compose thread_id: user_id#session_id for conversation isolation
    thread_id = f"{req.user_id}#{req.session_id}"
    config = {"configurable": {"thread_id": thread_id}}
    user_input = {
        "messages": [_build_human_message(req.text, req.images, req.files, req.audios)],
        "trigger_source": "user",
        "enabled_tools": req.enabled_tools,
        "user_id": req.user_id,
        "session_id": req.session_id,
    }

    result = await agent.agent_app.ainvoke(user_input, config)
    return {"status": "success", "response": _extract_text(result["messages"][-1].content)}


@app.post("/ask_stream", deprecated=True)
async def ask_agent_stream(req: UserRequest):
    """[已弃用] 请使用 POST /v1/chat/completions (流式, stream=true)"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # Cancel previous active task for this user+session
    task_key = f"{req.user_id}#{req.session_id}"
    await agent.cancel_task(task_key)

    # Compose thread_id: user_id#session_id for conversation isolation
    thread_id = f"{req.user_id}#{req.session_id}"
    config = {"configurable": {"thread_id": thread_id}}
    user_input = {
        "messages": [_build_human_message(req.text, req.images, req.files, req.audios)],
        "trigger_source": "user",
        "enabled_tools": req.enabled_tools,
        "user_id": req.user_id,
        "session_id": req.session_id,
    }

    queue: asyncio.Queue[str | None] = asyncio.Queue()

    async def _stream_worker(task_key=task_key):
        """在独立 Task 中运行 astream_events，产出数据写入 queue"""
        collected_tokens = []
        try:
            async for event in agent.agent_app.astream_events(user_input, config, version="v2"):
                kind = event.get("event", "")
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        text = _extract_text(chunk.content)
                        if text:
                            collected_tokens.append(text)
                            text = text.replace("\\", "\\\\").replace("\n", "\\n")
                            await queue.put(f"data: {text}\n\n")
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "")
                    await queue.put(f"data: \\n🔧 调用工具: {tool_name}...\\n\n\n")
                elif kind == "on_tool_end":
                    await queue.put(f"data: \\n✅ 工具执行完成\\n\n\n")
            await queue.put("data: [DONE]\n\n")
        except asyncio.CancelledError:
            # 终止时，修复 checkpoint 中可能不完整的消息序列
            try:
                snapshot = await agent.agent_app.aget_state(config)
                last_msgs = snapshot.values.get("messages", [])
                if last_msgs:
                    last_msg = last_msgs[-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        tool_messages = [
                            ToolMessage(
                                content="⚠️ 工具调用被用户终止",
                                tool_call_id=tc["id"],
                            )
                            for tc in last_msg.tool_calls
                        ]
                        await agent.agent_app.aupdate_state(config, {"messages": tool_messages})
            except Exception:
                pass

            partial_text = "".join(collected_tokens)
            if partial_text:
                partial_text += "\n\n⚠️ （回复被用户终止）"
                partial_msg = AIMessage(content=partial_text)
                await agent.agent_app.aupdate_state(config, {"messages": [partial_msg]})
            await queue.put(f"data: \\n\\n⚠️ 已终止思考\n\n")
            await queue.put("data: [DONE]\n\n")
        except Exception as e:
            await queue.put(f"data: \\n❌ 流式响应异常: {str(e)}\n\n")
            await queue.put("data: [DONE]\n\n")
        finally:
            await queue.put(None)
            agent.unregister_task(task_key)

    task = asyncio.create_task(_stream_worker())
    agent.register_task(task_key, task)

    async def event_generator():
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/cancel")
async def cancel_agent(req: CancelRequest):
    """终止指定用户的智能体思考"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    task_key = f"{req.user_id}#{req.session_id}"
    await agent.cancel_task(task_key)
    return {"status": "success", "message": "已终止"}


# ------------------------------------------------------------------
# TTS: 文本转语音
# ------------------------------------------------------------------

class TTSRequest(BaseModel):
    user_id: str
    password: str
    text: str
    voice: Optional[str] = None

@app.post("/tts")
async def text_to_speech(req: TTSRequest):
    """将文本转为语音，返回 mp3 音频流"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    tts_text = req.text.strip()
    if not tts_text:
        raise HTTPException(status_code=400, detail="文本不能为空")

    # 限制长度，避免过长文本
    if len(tts_text) > 4000:
        tts_text = tts_text[:4000]

    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    tts_model = os.getenv("TTS_MODEL", "gemini-2.5-flash-preview-tts")
    tts_voice = req.voice or os.getenv("TTS_VOICE", "charon")

    if not api_key or not base_url:
        raise HTTPException(status_code=500, detail="TTS API 未配置")

    tts_url = f"{base_url}/audio/speech"

    async def audio_stream():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                tts_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": tts_model,
                    "input": tts_text,
                    "voice": tts_voice,
                    "response_format": "mp3",
                },
            ) as resp:
                if resp.status_code != 200:
                    error_body = await resp.aread()
                    raise HTTPException(
                        status_code=resp.status_code,
                        detail=f"TTS API 错误: {error_body.decode('utf-8', errors='replace')[:200]}",
                    )
                async for chunk in resp.aiter_bytes(chunk_size=4096):
                    yield chunk

    return StreamingResponse(
        audio_stream(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=tts_output.mp3"},
    )


# ------------------------------------------------------------------
# Session history: 从 checkpoint DB 读取会话列表和历史消息
# ------------------------------------------------------------------

class SessionListRequest(BaseModel):
    user_id: str
    password: str

class SessionHistoryRequest(BaseModel):
    user_id: str
    password: str
    session_id: str

class DeleteSessionRequest(BaseModel):
    user_id: str
    password: str
    session_id: str = ""  # 为空则删除该用户所有会话


@app.post("/sessions")
async def list_sessions(req: SessionListRequest):
    """列出用户的所有会话，返回 session_id 列表及每个会话的摘要信息。"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    prefix = f"{req.user_id}#"
    sessions = []

    # 从 checkpoint DB 中查询该用户的所有 thread_id
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE ? ORDER BY thread_id",
            (f"{prefix}%",),
        )
        rows = await cursor.fetchall()

    for (thread_id,) in rows:
        sid = thread_id[len(prefix):]

        # 获取最新 checkpoint 中的第一条和最后一条用户消息作为摘要
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = await agent.agent_app.aget_state(config)
        msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []

        # 找第一条用户消息作为标题
        first_human = ""
        last_human = ""
        msg_count = 0
        for m in msgs:
            if hasattr(m, "content") and type(m).__name__ == "HumanMessage":
                # 多模态 content 可能是 list，提取其中的文本部分
                raw = m.content
                if isinstance(raw, str):
                    content = raw
                elif isinstance(raw, list):
                    content = " ".join(
                        p.get("text", "") for p in raw if isinstance(p, dict) and p.get("type") == "text"
                    ) or "(图片消息)"
                else:
                    content = str(raw)
                # 跳过系统触发消息
                if content.startswith("[系统触发]") or content.startswith("[外部学术会议邀请]"):
                    continue
                msg_count += 1
                if not first_human:
                    first_human = content[:50]
                last_human = content[:50]

        if not first_human:
            continue  # 空会话或纯系统会话，不展示

        sessions.append({
            "session_id": sid,
            "title": first_human,
            "last_message": last_human,
            "message_count": msg_count,
        })

    return {"status": "success", "sessions": sessions}


@app.post("/sessions_status")
async def sessions_status(req: SessionListRequest):
    """返回用户所有 session 的忙碌状态、来源和待处理系统消息数。"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    prefix = f"{req.user_id}#"
    # 从 agent 内存中获取所有已知 thread 的状态
    all_status = agent.get_all_thread_status(prefix)

    result = []
    for thread_id, info in all_status.items():
        sid = thread_id[len(prefix):]
        result.append({
            "session_id": sid,
            "busy": info["busy"],
            "source": info["source"],       # "user" | "system" | ""
            "pending_system": info["pending_system"],
        })

    return {"status": "success", "sessions": result}


@app.post("/session_history")
async def get_session_history(req: SessionHistoryRequest):
    """获取指定会话的完整对话历史（仅返回 Human/AI 消息）。"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    thread_id = f"{req.user_id}#{req.session_id}"
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent.agent_app.aget_state(config)

    if not snapshot or not snapshot.values:
        return {"status": "success", "messages": []}

    msgs = snapshot.values.get("messages", [])
    result = []
    for m in msgs:
        msg_type = type(m).__name__
        if msg_type == "HumanMessage":
            # 多模态消息 content 可能是 list（含 text+image_url），直接透传
            content = m.content
            result.append({"role": "user", "content": content})
        elif msg_type == "AIMessage":
            content = _extract_text(m.content)
            # 提取 tool_calls 信息
            tool_calls = []
            if hasattr(m, "tool_calls") and m.tool_calls:
                for tc in m.tool_calls:
                    tool_calls.append({
                        "name": tc.get("name", ""),
                        "args": tc.get("args", {}),
                    })
            if content or tool_calls:
                entry = {"role": "assistant", "content": content}
                if tool_calls:
                    entry["tool_calls"] = tool_calls
                result.append(entry)
        elif msg_type == "ToolMessage":
            content = _extract_text(m.content)
            tool_name = getattr(m, "name", "")
            result.append({
                "role": "tool",
                "content": content,
                "tool_name": tool_name,
            })

    return {"status": "success", "messages": result}


@app.post("/delete_session")
async def delete_session(
    req: DeleteSessionRequest,
    x_internal_token: str | None = Header(None),
):
    """删除指定会话或用户的全部会话历史。

    - session_id 非空：删除该用户的指定会话
    - session_id 为空：删除该用户的所有会话

    认证：用户密码 或 INTERNAL_TOKEN (via X-Internal-Token header)
    """
    # 支持内部 token 认证（OASIS 专家 session 清理使用）
    internal_auth = x_internal_token and x_internal_token == INTERNAL_TOKEN
    if not internal_auth and not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    try:
        async with aiosqlite.connect(db_path) as db:
            if req.session_id:
                # 取消该会话正在运行的 agent task（避免删了 checkpoint 又被写回）
                task_key = f"{req.user_id}#{req.session_id}"
                await agent.cancel_task(task_key)

                # 删除单个会话
                thread_id = f"{req.user_id}#{req.session_id}"
                for table in ("checkpoints", "writes"):
                    await db.execute(f"DELETE FROM {table} WHERE thread_id = ?", (thread_id,))
                await db.commit()
                return {"status": "success", "message": f"会话 {req.session_id} 已删除"}
            else:
                # 取消该用户所有正在运行的 agent tasks
                prefix = f"{req.user_id}#"
                keys_to_cancel = [k for k in agent._active_tasks if k.startswith(prefix)]
                for k in keys_to_cancel:
                    await agent.cancel_task(k)

                # 删除该用户所有会话
                pattern = f"{req.user_id}#%"
                for table in ("checkpoints", "writes"):
                    await db.execute(f"DELETE FROM {table} WHERE thread_id LIKE ?", (pattern,))
                await db.commit()
                return {"status": "success", "message": f"用户 {req.user_id} 的所有会话已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")


# ------------------------------------------------------------------
# Session status: 前端轮询是否有系统触发的新消息
# ------------------------------------------------------------------

class SessionStatusRequest(BaseModel):
    user_id: str
    password: str
    session_id: str = "default"

@app.post("/session_status")
async def session_status(req: SessionStatusRequest):
    """前端轮询接口：检查是否有系统触发产生的新消息。"""
    if not verify_password(req.user_id, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    thread_id = f"{req.user_id}#{req.session_id}"
    has_new = agent.has_pending_system_messages(thread_id)
    busy = agent.is_thread_busy(thread_id)
    pending_count = agent.consume_pending_system_messages(thread_id) if has_new else 0
    busy_source = agent.get_thread_busy_source(thread_id) if busy else ""
    return {
        "has_new_messages": has_new,
        "pending_count": pending_count,
        "busy": busy,
        "busy_source": busy_source,
    }


@app.post("/system_trigger")
async def system_trigger(req: SystemTriggerRequest, x_internal_token: str | None = Header(None)):
    verify_internal_token(x_internal_token)
    thread_id = f"{req.user_id}#{req.session_id}"
    config = {"configurable": {"thread_id": thread_id}}
    system_input = {
        "messages": [HumanMessage(content=req.text)],
        "trigger_source": "system",
        "enabled_tools": None,
        "user_id": req.user_id,
        "session_id": req.session_id,
    }

    async def _wait_and_invoke():
        task_key = f"{req.user_id}#{req.session_id}"
        lock = await agent.get_thread_lock(thread_id)
        print(f"[SystemTrigger] ⏳ Waiting for lock on {thread_id} ...")
        async with lock:
            agent.set_thread_busy_source(thread_id, "system")
            print(f"[SystemTrigger] 🔒 Acquired lock on {thread_id}, invoking graph ...")
            try:
                await agent.agent_app.ainvoke(system_input, config)
                agent.add_pending_system_message(thread_id)
                print(f"[SystemTrigger] ✅ Done for {thread_id}")
            except asyncio.CancelledError:
                print(f"[SystemTrigger] 🛑 Cancelled for {thread_id}")
                # 修复 checkpoint 中可能不完整的消息序列
                try:
                    snapshot = await agent.agent_app.aget_state(config)
                    last_msgs = snapshot.values.get("messages", [])
                    if last_msgs:
                        last_msg = last_msgs[-1]
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            tool_messages = [
                                ToolMessage(
                                    content="⚠️ 系统调用被用户终止",
                                    tool_call_id=tc["id"],
                                )
                                for tc in last_msg.tool_calls
                            ]
                            await agent.agent_app.aupdate_state(config, {"messages": tool_messages})
                except Exception:
                    pass
            except Exception as e:
                print(f"[SystemTrigger] ❌ Error for {thread_id}: {e}")
            finally:
                agent.clear_thread_busy_source(thread_id)
                agent.unregister_task(task_key)

    # fire-and-forget：立刻返回，graph 在后台异步执行
    task_key = f"{req.user_id}#{req.session_id}"
    await agent.cancel_task(task_key)  # 取消该会话可能正在运行的任务
    task = asyncio.create_task(_wait_and_invoke())
    agent.register_task(task_key, task)
    return {"status": "received", "message": f"系统触发已收到，用户 {req.user_id}"}


# ------------------------------------------------------------------
# OpenAI-compatible API: /v1/chat/completions
# ------------------------------------------------------------------

def _openai_msg_to_human_message(msg: ChatMessage) -> HumanMessage:
    """将 OpenAI 格式的 user message 转为 LangChain HumanMessage。
    支持纯文本和多模态（图片、音频、文件）content parts。"""
    content = msg.content
    if content is None:
        return HumanMessage(content="(空消息)")
    if isinstance(content, str):
        return HumanMessage(content=content)

    # content 是 list[dict]，遍历构造多模态 parts
    text_parts = []
    image_parts = []
    audio_parts = []
    file_parts = []
    for part in content:
        p = part if isinstance(part, dict) else part.dict()
        ptype = p.get("type", "")
        if ptype == "text":
            text_parts.append(p.get("text", ""))
        elif ptype == "image_url":
            image_parts.append(p)
        elif ptype == "input_audio":
            audio_data = p.get("input_audio", {})
            audio_parts.append(audio_data)
        elif ptype == "file":
            file_parts.append(p)

    # 纯文本
    if not image_parts and not audio_parts and not file_parts:
        return HumanMessage(content="\n".join(text_parts) or "(空消息)")

    # 多模态：用 _build_human_message 的逻辑构造
    combined_text = "\n".join(text_parts)

    # 提取图片 base64 列表
    images = []
    for ip in image_parts:
        url = ip.get("image_url", {}).get("url", "")
        if url:
            images.append(url)

    # 提取音频列表
    audios = []
    for ad in audio_parts:
        audios.append({
            "base64": ad.get("data", ""),
            "format": ad.get("format", "webm"),
            "name": f"recording.{ad.get('format', 'webm')}",
        })

    # 提取文件列表
    # 媒体文件扩展名：以 file content part 直传，不当文本展开
    _MEDIA_EXTS = {".avi", ".mp4", ".mkv", ".mov", ".webm", ".mp3", ".wav", ".flac", ".ogg", ".aac"}
    files = []
    for fp in file_parts:
        fdata = fp.get("file", {})
        fname = fdata.get("filename", "file")
        ext = os.path.splitext(fname)[1].lower()
        if fname.endswith(".pdf"):
            ftype = "pdf"
        elif ext in _MEDIA_EXTS:
            ftype = "media"
        else:
            ftype = "text"
        files.append({
            "name": fname,
            "content": fdata.get("file_data", ""),
            "type": ftype,
        })

    return _build_human_message(combined_text, images or None, files or None, audios or None)


def _make_completion_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:24]}"


def _make_openai_response(content: str, model: str = "mini-timebot",
                          finish_reason: str = "stop",
                          tool_calls: list[dict] | None = None) -> dict:
    """构造标准 OpenAI chat completion 响应。"""
    message: dict = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls
        finish_reason = "tool_calls"
    return {
        "id": _make_completion_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": finish_reason,
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _make_openai_chunk(content: str = "", model: str = "mini-timebot",
                       finish_reason: str | None = None,
                       completion_id: str = "",
                       meta: dict | None = None) -> str:
    """构造标准 OpenAI SSE chunk（streaming）。

    meta: 可选的自定义元数据，前端用于结构化渲染。
    """
    delta = {}
    if content:
        delta["content"] = content
    if meta:
        delta["meta"] = meta
    if finish_reason is None and not content and not meta:
        delta["role"] = "assistant"
    chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": delta,
            "finish_reason": finish_reason,
        }],
    }
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"


def _extract_external_tool_names(tools: list[dict] | None) -> set[str]:
    """从 OpenAI tools 定义列表中提取工具名称集合。"""
    if not tools:
        return set()
    names = set()
    for t in tools:
        if t.get("type") == "function":
            names.add(t["function"]["name"])
        elif t.get("name"):
            names.add(t["name"])
    return names


def _format_tool_calls_for_openai(ai_msg: AIMessage, external_names: set[str]) -> list[dict] | None:
    """
    从 LangChain AIMessage 的 tool_calls 中提取属于外部工具的调用，
    格式化为 OpenAI chat completion 的 tool_calls 格式。
    """
    if not hasattr(ai_msg, "tool_calls") or not ai_msg.tool_calls:
        return None
    external_calls = []
    for tc in ai_msg.tool_calls:
        if tc["name"] in external_names:
            external_calls.append({
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": json.dumps(tc.get("args", {}), ensure_ascii=False),
                },
            })
    return external_calls or None


def _auth_openai_request(req: ChatCompletionRequest, auth_header: str | None):
    """从 OpenAI 请求中提取认证信息并验证。
    支持格式：
    1. Authorization: Bearer <user_id>:<password>
    2. Authorization: Bearer <user_id>:<password>:<session_id>
    3. Authorization: Bearer <INTERNAL_TOKEN>                — 内部调用，user_id 取 req.user 或 "system"
    4. Authorization: Bearer <INTERNAL_TOKEN>:<user_id>      — 管理员级，以指定用户身份操作
    5. Authorization: Bearer <INTERNAL_TOKEN>:<user_id>:<session_id>  — 同上，附带 session 覆盖
    6. 请求体中的 user + password 字段
    返回 (user_id, authenticated, session_override)
    """
    user_id = req.user
    password = req.password
    session_override = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        parts = token.split(":")

        # Check if first part is the INTERNAL_TOKEN (admin-level auth)
        if parts[0] == INTERNAL_TOKEN:
            if len(parts) >= 3:
                # INTERNAL_TOKEN:user_id:session_id
                return parts[1], True, parts[2]
            elif len(parts) == 2:
                # INTERNAL_TOKEN:user_id
                return parts[1], True, None
            else:
                # INTERNAL_TOKEN alone
                return user_id or "system", True, None

        # Normal user auth: user_id:password[:session_id]
        if len(parts) >= 3:
            user_id, password, session_override = parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            user_id, password = parts[0], parts[1]

    if not user_id or not password:
        return None, False, None
    if not verify_password(user_id, password):
        return None, False, None
    return user_id, True, session_override


@app.post("/v1/chat/completions")
async def openai_chat_completions(
    req: ChatCompletionRequest,
    authorization: str | None = Header(None),
):
    """OpenAI 兼容的 /v1/chat/completions 端点。

    认证方式（任选其一）：
    - Header: Authorization: Bearer <user_id>:<password>
    - Header: Authorization: Bearer <user_id>:<password>:<session_id>
    - Header: Authorization: Bearer <INTERNAL_TOKEN>                (内部调用，user="system")
    - Header: Authorization: Bearer <INTERNAL_TOKEN>:<user_id>      (管理员级，以指定用户身份)
    - Header: Authorization: Bearer <INTERNAL_TOKEN>:<user_id>:<session_id>  (同上+session)
    - Body: user + password 字段

    请求格式完全兼容 OpenAI API，扩展字段通过顶层或 extra_body 传入：
    - session_id: 会话 ID (默认 "default"，也可通过 key 第三段指定)
    - enabled_tools: 启用的工具列表 (null=全部)
    - tools: 外部工具定义（OpenAI function calling 格式）
    - tool_choice: 工具选择策略
    """
    user_id, authenticated, session_override = _auth_openai_request(req, authorization)
    if not authenticated:
        raise HTTPException(status_code=401, detail="认证失败")

    session_id = session_override or req.session_id or "default"
    thread_id = f"{user_id}#{session_id}"
    config = {"configurable": {"thread_id": thread_id}}

    external_tool_names = _extract_external_tool_names(req.tools)

    # --- 构造输入消息 ---
    # 多轮 tool calling 时，最新消息可能是 role=tool（调用方回传结果）
    # 或 role=assistant+tool_calls（恢复上下文）
    # 需要从 messages 尾部提取所有 tool result 消息
    input_messages = []
    last_user_msg = None

    # 从后往前扫描，收集尾部连续的 tool messages 和 assistant messages
    trailing_tool_msgs = []
    i = len(req.messages) - 1
    while i >= 0:
        msg = req.messages[i]
        if msg.role == "tool":
            trailing_tool_msgs.insert(0, msg)
            i -= 1
        elif msg.role == "assistant" and msg.tool_calls and trailing_tool_msgs:
            # 跳过 assistant 消息（已在 checkpoint 中），只取 tool results
            i -= 1
        else:
            break

    if trailing_tool_msgs:
        # 多轮 tool calling 模式：调用方回传了 tool results
        # 将 ToolMessage 注入 checkpoint 继续执行
        tool_result_messages = []
        for tmsg in trailing_tool_msgs:
            tool_result_messages.append(
                ToolMessage(
                    content=tmsg.content if isinstance(tmsg.content, str) else json.dumps(tmsg.content, ensure_ascii=False),
                    tool_call_id=tmsg.tool_call_id or "",
                    name=tmsg.name or "",
                )
            )
        input_messages = tool_result_messages
    else:
        # 正常模式：取最后一条 user message
        # 同时收集请求中的 system messages（如 SessionExpert 的指令上下文）
        system_parts = []
        for msg in req.messages:
            if msg.role == "system" and msg.content:
                system_parts.append(msg.content if isinstance(msg.content, str) else str(msg.content))

        for msg in reversed(req.messages):
            if msg.role == "user":
                last_user_msg = msg
                break
        if not last_user_msg:
            raise HTTPException(status_code=400, detail="messages 中缺少 user 或 tool 消息")

        human_msg = _openai_msg_to_human_message(last_user_msg)
        # 将 system messages 内容前置到 user message 中
        if system_parts:
            sys_text = "\n".join(system_parts)
            if isinstance(human_msg.content, list):
                # 多模态消息：在开头插入 text part
                human_msg.content.insert(0, {"type": "text", "text": f"[来自调度方的指令]\n{sys_text}\n\n---\n"})
            else:
                human_msg.content = f"[来自调度方的指令]\n{sys_text}\n\n---\n{human_msg.content}"
        input_messages = [human_msg]

    user_input = {
        "messages": input_messages,
        "trigger_source": "user",
        "enabled_tools": req.enabled_tools,
        "user_id": user_id,
        "session_id": session_id,
        "external_tools": req.tools,
    }

    model_name = req.model or "mini-timebot"
    thread_lock = await agent.get_thread_lock(thread_id)

    # --- 非流式 ---
    if not req.stream:
        async with thread_lock:
            agent.set_thread_busy_source(thread_id, "user")
            try:
                result = await agent.agent_app.ainvoke(user_input, config)
            finally:
                agent.clear_thread_busy_source(thread_id)
        last_msg = result["messages"][-1]

        # 检测是否有外部工具调用需要返回
        ext_tool_calls = _format_tool_calls_for_openai(last_msg, external_tool_names)
        if ext_tool_calls:
            return _make_openai_response(
                _extract_text(last_msg.content), model=model_name, tool_calls=ext_tool_calls)

        reply = _extract_text(last_msg.content)
        return _make_openai_response(reply, model=model_name)

    # --- 流式 (SSE) ---
    task_key = f"{user_id}#{session_id}"
    await agent.cancel_task(task_key)

    queue: asyncio.Queue[str | None] = asyncio.Queue()
    completion_id = _make_completion_id()

    async def _stream_worker():
        collected_tokens = []
        _chatbot_round = 0          # chatbot 节点轮次计数
        _active_tool_names = []     # 当前批次的工具名称列表
        async with thread_lock:
            agent.set_thread_busy_source(thread_id, "user")
            try:
                # 发送 role chunk
                await queue.put(_make_openai_chunk("", model=model_name, completion_id=completion_id))

                async for event in agent.agent_app.astream_events(user_input, config, version="v2"):
                    kind = event.get("event", "")
                    ev_name = event.get("name", "")

                    # --- 节点级事件：chatbot / tools 的进入与退出 ---
                    if kind == "on_chain_start" and ev_name == "chatbot":
                        _chatbot_round += 1
                        if _chatbot_round > 1:
                            # 非首轮 chatbot = 工具返回后 LLM 再次思考
                            await queue.put(_make_openai_chunk(
                                model=model_name, completion_id=completion_id,
                                meta={"type": "ai_start", "round": _chatbot_round}))

                    elif kind == "on_chain_end" and ev_name == "chatbot":
                        # chatbot 结束：可能进入 tools 或直接结束
                        pass  # 由 on_chain_start tools 触发分界

                    elif kind == "on_chain_start" and ev_name == "tools":
                        # 即将执行工具 → 通知前端封存当前文本气泡
                        _active_tool_names = []
                        await queue.put(_make_openai_chunk(
                            model=model_name, completion_id=completion_id,
                            meta={"type": "tools_start"}))

                    elif kind == "on_chain_end" and ev_name == "tools":
                        # 工具批次执行完毕
                        await queue.put(_make_openai_chunk(
                            model=model_name, completion_id=completion_id,
                            meta={"type": "tools_end", "tools": _active_tool_names}))

                    # --- 单个工具的开始/结束 ---
                    elif kind == "on_tool_start":
                        tool_name = ev_name
                        if tool_name not in external_tool_names:
                            _active_tool_names.append(tool_name)
                            await queue.put(_make_openai_chunk(
                                model=model_name, completion_id=completion_id,
                                meta={"type": "tool_start", "name": tool_name}))
                    elif kind == "on_tool_end":
                        tool_name = ev_name
                        if tool_name not in external_tool_names:
                            # 提取工具返回内容的摘要（截断）
                            output = event.get("data", {}).get("output", "")
                            if hasattr(output, "content"):
                                output = output.content
                            output_str = str(output)[:200] if output else ""
                            await queue.put(_make_openai_chunk(
                                model=model_name, completion_id=completion_id,
                                meta={"type": "tool_end", "name": tool_name, "result": output_str}))

                    # --- LLM 流式 token ---
                    elif kind == "on_chat_model_stream":
                        chunk = event.get("data", {}).get("chunk")
                        if chunk and hasattr(chunk, "content") and chunk.content:
                            text = _extract_text(chunk.content)
                            if text:
                                collected_tokens.append(text)
                                await queue.put(_make_openai_chunk(
                                text, model=model_name, completion_id=completion_id))

                # 流式结束后，检查是否有外部工具调用
                snapshot = await agent.agent_app.aget_state(config)
                last_msgs = snapshot.values.get("messages", [])
                if last_msgs:
                    last_msg_item = last_msgs[-1]
                    ext_tool_calls = _format_tool_calls_for_openai(last_msg_item, external_tool_names)
                    if ext_tool_calls:
                        # 以非流式格式发送 tool_calls（流式 tool_calls 较复杂，这里用简单方案）
                        tc_response = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model_name,
                            "choices": [{
                                "index": 0,
                                "delta": {
                                    "tool_calls": ext_tool_calls,
                                },
                                "finish_reason": "tool_calls",
                            }],
                        }
                        await queue.put(f"data: {json.dumps(tc_response, ensure_ascii=False)}\n\n")
                        await queue.put("data: [DONE]\n\n")
                        return

                # 正常结束
                await queue.put(_make_openai_chunk(
                    "", model=model_name, finish_reason="stop", completion_id=completion_id))
                await queue.put("data: [DONE]\n\n")
            except asyncio.CancelledError:
                try:
                    snapshot = await agent.agent_app.aget_state(config)
                    last_msgs = snapshot.values.get("messages", [])
                    if last_msgs:
                        last_msg_item = last_msgs[-1]
                        if hasattr(last_msg_item, "tool_calls") and last_msg_item.tool_calls:
                            tool_messages = [
                                ToolMessage(
                                    content="⚠️ 工具调用被用户终止",
                                    tool_call_id=tc["id"],
                                )
                                for tc in last_msg_item.tool_calls
                            ]
                            await agent.agent_app.aupdate_state(config, {"messages": tool_messages})
                except Exception:
                    pass
                partial_text = "".join(collected_tokens)
                if partial_text:
                    partial_text += "\n\n⚠️ （回复被用户终止）"
                    partial_msg = AIMessage(content=partial_text)
                    await agent.agent_app.aupdate_state(config, {"messages": [partial_msg]})
                await queue.put(_make_openai_chunk(
                    "\n\n⚠️ 已终止思考", model=model_name, completion_id=completion_id))
                await queue.put(_make_openai_chunk(
                    "", model=model_name, finish_reason="stop", completion_id=completion_id))
                await queue.put("data: [DONE]\n\n")
            except Exception as e:
                await queue.put(_make_openai_chunk(
                    f"\n❌ 响应异常: {str(e)}", model=model_name, completion_id=completion_id))
                await queue.put(_make_openai_chunk(
                    "", model=model_name, finish_reason="stop", completion_id=completion_id))
                await queue.put("data: [DONE]\n\n")
            finally:
                agent.clear_thread_busy_source(thread_id)
                await queue.put(None)
                agent.unregister_task(task_key)

    task = asyncio.create_task(_stream_worker())
    agent.register_task(task_key, task)

    async def event_generator():
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ------------------------------------------------------------------
# OpenAI-compatible: /v1/models (列出可用模型)
# ------------------------------------------------------------------

@app.get("/v1/models")
async def list_models():
    """返回可用模型列表（OpenAI 兼容）"""
    return {
        "object": "list",
        "data": [{
            "id": "mini-timebot",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "mini-timebot",
        }],
    }


# ------------------------------------------------------------------
# Group Chat (群聊) — SQLite 存储，REST API
# ------------------------------------------------------------------

_GROUP_DB_PATH = os.path.join(root_dir, "data", "group_chat.db")

async def _init_group_db():
    """初始化群聊数据库表结构"""
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL DEFAULT 'default',
                is_agent INTEGER NOT NULL DEFAULT 1,
                joined_at REAL NOT NULL,
                PRIMARY KEY (group_id, user_id, session_id),
                FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                sender_session TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE
            )
        """)
        await db.commit()


# --- Pydantic models ---

class GroupCreateRequest(BaseModel):
    name: str
    members: list[dict] = Field(default_factory=list)  # [{user_id, session_id}]

class GroupUpdateRequest(BaseModel):
    name: Optional[str] = None
    members: Optional[list[dict]] = None  # [{user_id, session_id, action:"add"|"remove"}]

class GroupMessageRequest(BaseModel):
    content: str
    sender: Optional[str] = None       # 人类发消息时可省略（自动取 owner）
    sender_session: Optional[str] = ""
    mentions: Optional[list[str]] = None  # 被 @ 的 agent session key 列表 (格式: "user_id#session_id")


# --- Helpers ---

_group_muted: set[str] = set()  # 被静音的群 group_id 集合，广播时跳过

def _parse_group_auth(authorization: str | None):
    """从 Bearer token 解析用户认证，返回 (user_id, password, session_id)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization[7:]
    # 格式: user_id:password 或 user_id:password:session_id
    parts = token.split(":")
    if len(parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid token format")
    uid, pw = parts[0], parts[1]
    sid = parts[2] if len(parts) > 2 else "default"
    if not verify_password(uid, pw):
        raise HTTPException(status_code=401, detail="认证失败")
    return uid, pw, sid


async def _get_agent_title(user_id: str, session_id: str) -> str:
    """从 checkpoint 提取 agent 的 session title（第一条非系统触发 HumanMessage 前50字）"""
    tid = f"{user_id}#{session_id}"
    try:
        config = {"configurable": {"thread_id": tid}}
        snapshot = await agent.agent_app.aget_state(config)
        msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []
        for m in msgs:
            if hasattr(m, "content") and type(m).__name__ == "HumanMessage":
                raw = m.content
                if isinstance(raw, str):
                    content = raw
                elif isinstance(raw, list):
                    content = " ".join(
                        p.get("text", "") for p in raw if isinstance(p, dict) and p.get("type") == "text"
                    ) or ""
                else:
                    content = str(raw)
                if content.startswith("[系统触发]") or content.startswith("[外部学术会议邀请]") or content.startswith("[群聊"):
                    continue
                return content[:50]
    except Exception:
        pass
    return session_id


async def _broadcast_to_group(group_id: str, sender: str, content: str, exclude_user: str = "", exclude_session: str = "", mentions: list[str] | None = None):
    """向群内 agent 成员广播消息（异步 fire-and-forget）。
    如果 mentions 非空，只发给被 @ 的 agent，并强调这是专门发送的信息。
    """
    if group_id in _group_muted:
        print(f"[GroupChat] 群 {group_id} 已静音，跳过广播")
        return
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, session_id, is_agent FROM group_members WHERE group_id = ?",
            (group_id,),
        )
        members = await cursor.fetchall()

    for user_id, session_id, is_agent in members:
        if group_id in _group_muted:
            print(f"[GroupChat] 群 {group_id} 广播中途被静音，停止")
            return
        if not is_agent:
            continue  # 人类成员不需要异步通知
        if user_id == exclude_user and session_id == exclude_session:
            continue  # 不通知发送者自己

        member_key = f"{user_id}#{session_id}"

        # 如果有 mentions 列表，只发给被 @ 的 agent
        if mentions:
            if member_key not in mentions:
                continue

        # 获取目标 agent 的 title，让它知道自己的身份
        my_title = await _get_agent_title(user_id, session_id)
        # 用 system_trigger 异步投递
        trigger_url = f"http://127.0.0.1:{os.getenv('PORT_AGENT', '51200')}/system_trigger"

        if mentions and member_key in mentions:
            # 被 @ 的消息：强调这是专门发送的，必须回复
            msg_text = (f"[群聊 {group_id}] {sender} @你 说:\n{content}\n\n"
                        f"(⚠️ 这是专门 @你 的消息，你必须回复！"
                        f"你在群聊中的身份/角色是「{my_title}」，回复时请体现你的专业角色视角。"
                        f"请使用 send_to_group 工具回复，group_id={group_id}。)")
        else:
            # 普通广播消息
            msg_text = (f"[群聊 {group_id}] {sender} 说:\n{content}\n\n"
                        f"(你在群聊中的身份/角色是「{my_title}」，回复时请体现你的专业角色视角。"
                        f"仅当消息与你直接相关、点名你、向你提问、或面向所有人时，"
                        f"才使用 send_to_group 工具回复，group_id={group_id}。"
                        f"其他情况请忽略，不要回应。)")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    trigger_url,
                    headers={"X-Internal-Token": INTERNAL_TOKEN},
                    json={
                        "user_id": user_id,
                        "session_id": session_id,
                        "text": msg_text,
                    },
                )
        except Exception as e:
            print(f"[GroupChat] 广播到 {user_id}#{session_id} 失败: {e}")


# --- API 端点 ---

@app.post("/groups")
async def create_group(req: GroupCreateRequest, authorization: str | None = Header(None)):
    """创建群聊"""
    uid, _, _ = _parse_group_auth(authorization)
    group_id = f"g_{int(time.time()*1000)}_{secrets.token_hex(4)}"
    now = time.time()
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        await db.execute(
            "INSERT INTO groups (group_id, name, owner, created_at) VALUES (?, ?, ?, ?)",
            (group_id, req.name, uid, now),
        )
        # Owner 作为人类成员加入
        await db.execute(
            "INSERT INTO group_members (group_id, user_id, session_id, is_agent, joined_at) VALUES (?, ?, ?, 0, ?)",
            (group_id, uid, "default", now),
        )
        # 添加 agent 成员
        for m in req.members:
            m_uid = m.get("user_id", "")
            m_sid = m.get("session_id", "default")
            if m_uid:
                await db.execute(
                    "INSERT OR IGNORE INTO group_members (group_id, user_id, session_id, is_agent, joined_at) VALUES (?, ?, ?, 1, ?)",
                    (group_id, m_uid, m_sid, now),
                )
        await db.commit()
    return {"group_id": group_id, "name": req.name, "owner": uid}


@app.get("/groups")
async def list_groups(authorization: str | None = Header(None)):
    """列出用户所属的群聊"""
    uid, _, _ = _parse_group_auth(authorization)
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT g.group_id, g.name, g.owner, g.created_at,
                   (SELECT COUNT(*) FROM group_members WHERE group_id = g.group_id) as member_count,
                   (SELECT COUNT(*) FROM group_messages WHERE group_id = g.group_id) as message_count
            FROM groups g
            WHERE g.owner = ? OR g.group_id IN (
                SELECT group_id FROM group_members WHERE user_id = ?
            )
            ORDER BY g.created_at DESC
        """, (uid, uid))
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@app.get("/groups/{group_id}")
async def get_group(group_id: str, authorization: str | None = Header(None)):
    """获取群聊详情（含成员和最近消息）"""
    uid, _, _ = _parse_group_auth(authorization)
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # 群信息
        cursor = await db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
        group = await cursor.fetchone()
        if not group:
            raise HTTPException(status_code=404, detail="群聊不存在")
        # 成员列表
        cursor = await db.execute(
            "SELECT user_id, session_id, is_agent, joined_at FROM group_members WHERE group_id = ?",
            (group_id,),
        )
        members = [dict(r) for r in await cursor.fetchall()]

        # 为 agent 成员补充 session title
        for member in members:
            if not member.get("is_agent"):
                continue
            member["title"] = await _get_agent_title(member["user_id"], member["session_id"])

        # 最近 100 条消息
        cursor = await db.execute(
            "SELECT id, sender, sender_session, content, timestamp FROM group_messages WHERE group_id = ? ORDER BY id DESC LIMIT 100",
            (group_id,),
        )
        messages = [dict(r) for r in await cursor.fetchall()]
        messages.reverse()  # 按时间正序

    return {**dict(group), "members": members, "messages": messages}


@app.get("/groups/{group_id}/messages")
async def get_group_messages(group_id: str, after_id: int = 0, authorization: str | None = Header(None)):
    """获取群聊消息（支持增量获取 after_id）"""
    _parse_group_auth(authorization)
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, sender, sender_session, content, timestamp FROM group_messages WHERE group_id = ? AND id > ? ORDER BY id ASC LIMIT 200",
            (group_id, after_id),
        )
        messages = [dict(r) for r in await cursor.fetchall()]
    return {"messages": messages}


@app.post("/groups/{group_id}/messages")
async def post_group_message(group_id: str, req: GroupMessageRequest, authorization: str | None = Header(None),
                              x_internal_token: str | None = Header(None)):
    """发送群聊消息 — 人类用 Bearer auth，Agent 用 X-Internal-Token"""
    sender = ""
    sender_session = req.sender_session or ""

    if x_internal_token and x_internal_token == INTERNAL_TOKEN:
        # Agent 调用（通过 MCP 工具）
        sender = req.sender or "agent"
    else:
        uid, _, sid = _parse_group_auth(authorization)
        sender = uid
        sender_session = sid

    # 存入消息
    now = time.time()
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        # 校验群存在
        cursor = await db.execute("SELECT group_id FROM groups WHERE group_id = ?", (group_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="群聊不存在")
        cursor2 = await db.execute(
            "INSERT INTO group_messages (group_id, sender, sender_session, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (group_id, sender, sender_session, req.content, now),
        )
        msg_id = cursor2.lastrowid
        await db.commit()

    # 异步广播给群内 agent（如有 mentions 则只发给被 @ 的）
    # sender 可能是 "username#session_id" 格式，提取纯 user_id 用于排除
    exclude_uid = sender.split("#")[0] if "#" in sender else sender
    asyncio.create_task(_broadcast_to_group(group_id, sender, req.content, exclude_user=exclude_uid, exclude_session=sender_session, mentions=req.mentions))

    return {"status": "sent", "sender": sender, "timestamp": now, "id": msg_id}


@app.put("/groups/{group_id}")
async def update_group(group_id: str, req: GroupUpdateRequest, authorization: str | None = Header(None)):
    """更新群聊（改名、增删成员）"""
    uid, _, _ = _parse_group_auth(authorization)
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        # 验证所有者
        cursor = await db.execute("SELECT owner FROM groups WHERE group_id = ?", (group_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if row[0] != uid:
            raise HTTPException(status_code=403, detail="只有群主可以修改群设置")

        if req.name:
            await db.execute("UPDATE groups SET name = ? WHERE group_id = ?", (req.name, group_id))

        if req.members:
            now = time.time()
            for m in req.members:
                action = m.get("action", "add")
                m_uid = m.get("user_id", "")
                m_sid = m.get("session_id", "default")
                if not m_uid:
                    continue
                if action == "add":
                    await db.execute(
                        "INSERT OR IGNORE INTO group_members (group_id, user_id, session_id, is_agent, joined_at) VALUES (?, ?, ?, 1, ?)",
                        (group_id, m_uid, m_sid, now),
                    )
                elif action == "remove":
                    await db.execute(
                        "DELETE FROM group_members WHERE group_id = ? AND user_id = ? AND session_id = ?",
                        (group_id, m_uid, m_sid),
                    )
        await db.commit()
    return {"status": "updated"}


@app.delete("/groups/{group_id}")
async def delete_group(group_id: str, authorization: str | None = Header(None)):
    """删除群聊"""
    uid, _, _ = _parse_group_auth(authorization)
    async with aiosqlite.connect(_GROUP_DB_PATH) as db:
        cursor = await db.execute("SELECT owner FROM groups WHERE group_id = ?", (group_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if row[0] != uid:
            raise HTTPException(status_code=403, detail="只有群主可以删除群")
        await db.execute("DELETE FROM group_messages WHERE group_id = ?", (group_id,))
        await db.execute("DELETE FROM group_members WHERE group_id = ?", (group_id,))
        await db.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
        await db.commit()
    return {"status": "deleted"}


@app.post("/groups/{group_id}/mute")
async def mute_group(group_id: str, authorization: str | None = Header(None)):
    """静音群聊 — 立即停止广播"""
    _parse_group_auth(authorization)
    _group_muted.add(group_id)
    return {"status": "muted", "group_id": group_id}


@app.post("/groups/{group_id}/unmute")
async def unmute_group(group_id: str, authorization: str | None = Header(None)):
    """取消静音群聊 — 恢复广播"""
    _parse_group_auth(authorization)
    _group_muted.discard(group_id)
    return {"status": "unmuted", "group_id": group_id}


@app.get("/groups/{group_id}/mute_status")
async def group_mute_status(group_id: str, authorization: str | None = Header(None)):
    """查询群聊静音状态"""
    _parse_group_auth(authorization)
    return {"muted": group_id in _group_muted}


@app.get("/groups/{group_id}/sessions")
async def list_available_sessions(group_id: str, authorization: str | None = Header(None)):
    """列出可以加入群聊的 agent sessions（直接查 checkpoint DB）"""
    uid, pw, _ = _parse_group_auth(authorization)
    # 复用 mainagent 自身的 list_sessions 逻辑
    prefix = f"{uid}#"
    sessions = []
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(
                "SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE ? ORDER BY thread_id",
                (f"{prefix}%",),
            )
            rows = await cursor.fetchall()

        for (thread_id,) in rows:
            sid = thread_id[len(prefix):]
            # 获取摘要作为标题
            config = {"configurable": {"thread_id": thread_id}}
            snapshot = await agent.agent_app.aget_state(config)
            msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []

            first_human = ""
            for m in msgs:
                if hasattr(m, "content") and type(m).__name__ == "HumanMessage":
                    raw = m.content
                    if isinstance(raw, str):
                        content = raw
                    elif isinstance(raw, list):
                        content = " ".join(
                            p.get("text", "") for p in raw if isinstance(p, dict) and p.get("type") == "text"
                        ) or "(图片消息)"
                    else:
                        content = str(raw)
                    if content.startswith("[系统触发]") or content.startswith("[外部学术会议邀请]"):
                        continue
                    if not first_human:
                        first_human = content[:80]
                        break

            sessions.append({
                "session_id": sid,
                "title": first_human or f"Session {sid}",
            })
    except Exception as e:
        return {"sessions": [], "error": str(e)}

    return {"sessions": sessions}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT_AGENT", "51200")))
