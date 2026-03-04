import os
import json
import time
from dotenv import load_dotenv

# 加载 .env 文件
_chatbot_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_chatbot_dir)
load_dotenv(dotenv_path=os.path.join(_project_root, "config", ".env"))

# --- 配置区 ---
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")
AI_URL = os.getenv("AI_API_URL", "http://127.0.0.1:51200/v1/chat/completions")
AI_MODEL = os.getenv("AI_MODEL_TG", "gemini-2.0-flash")

# --- 白名单：从 data/telegram_whitelist.json 加载 ---
# 白名单格式: {"allowed": [{"username": "系统用户名", "chat_id": "TG数字ID", "tg_username": "TG用户名"}]}
# TG Bot 收到消息后，根据发送者 chat_id 查找对应的系统 username，
# 然后用 INTERNAL_TOKEN:username:TG 作为 Bearer token 调用 Agent（管理员级认证）
WHITELIST_FILE = os.path.join(_project_root, "data", "telegram_whitelist.json")
_WHITELIST_RELOAD_INTERVAL = 30  # 每 30 秒重新加载白名单

# 缓存: chat_id(int) -> {"username": str, "tg_username": str}
_whitelist_cache: dict = {"entries": {}, "tg_name_map": {}, "loaded_at": 0}


def _reload_whitelist():
    """从白名单文件加载用户映射。自动缓存，每 30 秒最多重新读取一次。"""
    now = time.time()
    if now - _whitelist_cache["loaded_at"] < _WHITELIST_RELOAD_INTERVAL:
        return

    entries: dict[int, dict] = {}      # chat_id(int) -> entry
    tg_name_map: dict[str, dict] = {}  # tg_username(lower) -> entry

    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                wl = json.load(f)
            for entry in wl.get("allowed", []):
                cid = entry.get("chat_id", "")
                if cid:
                    try:
                        entries[int(cid)] = entry
                    except ValueError:
                        pass
                tg_name = entry.get("tg_username", "")
                if tg_name:
                    tg_name_map[tg_name.lower()] = entry
        except (json.JSONDecodeError, OSError) as e:
            print(f"[白名单] ⚠️ 加载失败: {e}")

    _whitelist_cache["entries"] = entries
    _whitelist_cache["tg_name_map"] = tg_name_map
    _whitelist_cache["loaded_at"] = now


def _lookup_user(update) -> dict | None:
    """根据 TG 用户查白名单，返回对应的白名单条目（含 username），未找到返回 None。"""
    _reload_whitelist()
    user = update.effective_user
    if not user:
        return None

    # 优先按 chat_id 匹配
    entry = _whitelist_cache["entries"].get(user.id)
    if entry:
        return entry

    # 其次按 tg_username 匹配
    if user.username:
        entry = _whitelist_cache["tg_name_map"].get(user.username.lower())
        if entry:
            return entry

    return None


import logging
import httpx
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def download_as_b64(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    """下载 Telegram 文件并转换为 Base64 字符串"""
    file = await context.bot.get_file(file_id)
    async with httpx.AsyncClient() as client:
        response = await client.get(file.file_path)
        return base64.b64encode(response.content).decode('utf-8')


async def handle_multimodal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 查白名单：找到对应的系统用户
    entry = _lookup_user(update)

    if entry is None:
        # 白名单为空时允许所有人（但只能用默认身份）
        _reload_whitelist()
        if _whitelist_cache["entries"] or _whitelist_cache["tg_name_map"]:
            # 白名单非空，但此用户不在其中
            user = update.effective_user
            uid = user.id if user else "unknown"
            uname = f"@{user.username}" if user and user.username else ""
            logging.warning(f"Blocked unauthorized user: {uid} {uname}")
            await update.message.reply_text("⛔ 你没有权限使用此机器人。\n请先在 Agent 中设置 Telegram chat_id。")
            return
        else:
            # 白名单为空 → 无法确定用户身份，拒绝
            await update.message.reply_text("⛔ 白名单未配置，请先通过 Agent 设置 Telegram chat_id。")
            return

    sys_username = entry.get("username", "")
    if not sys_username:
        await update.message.reply_text("⛔ 白名单配置错误：缺少系统用户名。请重新通过 Agent 设置 Telegram。")
        return

    if not INTERNAL_TOKEN:
        await update.message.reply_text("⛔ 系统未配置 INTERNAL_TOKEN，无法调用 Agent。")
        return

    chat_id = update.effective_chat.id
    user_text = update.message.caption or update.message.text or "请分析此内容"

    # 1. 立即显示"正在输入..."
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # 2. 构建 OpenAI 格式的 content 列表
    content_list = [{"type": "text", "text": user_text}]

    try:
        # 3. 处理图片
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            b64_image = await download_as_b64(file_id, context)
            content_list.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
            })

        # 4. 处理语音
        elif update.message.voice:
            file_id = update.message.voice.file_id
            b64_audio = await download_as_b64(file_id, context)
            content_list.append({
                "type": "input_audio",
                "input_audio": {
                    "data": b64_audio,
                    "format": "wav",
                }
            })

        # 5. 以该用户身份调用 Agent
        # 使用 INTERNAL_TOKEN:username:TG 格式（管理员级认证 + 指定用户 + session=TG）
        api_key = f"{INTERNAL_TOKEN}:{sys_username}:TG"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                AI_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "user", "content": content_list}
                    ]
                }
            )

            if response.status_code != 200:
                raise Exception(f"AI 接口报错 ({response.status_code}): {response.text}")

            res_json = response.json()
            ai_reply = res_json["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"Error for user {sys_username}: {e}")
        ai_reply = f"❌ 发生错误: {str(e)}"

    # 6. 回复用户
    await update.message.reply_text(ai_reply)


if __name__ == '__main__':
    if not TG_TOKEN:
        print("❌ 未设置 TELEGRAM_BOT_TOKEN，无法启动。")
        exit(1)

    application = ApplicationBuilder().token(TG_TOKEN).build()

    handler = MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VOICE) & (~filters.COMMAND),
        handle_multimodal
    )
    application.add_handler(handler)

    # 初始加载白名单
    _reload_whitelist()

    print("--- Telegram 机器人已启动 (轮询模式) ---")
    print("支持：文字 / 图片 / 语音 (OpenAI 多模态格式)")
    print(f"Agent 接口: {AI_URL}")
    print(f"认证方式: INTERNAL_TOKEN + 用户隔离（每个 TG 用户映射到独立的系统用户）")
    entries = _whitelist_cache["entries"]
    if entries:
        print(f"🔒 白名单已启用，{len(entries)} 个用户:")
        for cid, entry in entries.items():
            print(f"   chat_id={cid} → {entry.get('username', '?')}")
        print(f"   白名单每 {_WHITELIST_RELOAD_INTERVAL} 秒自动重载")
    else:
        print("⚠️ 白名单为空（请先通过 Agent 设置用户的 Telegram chat_id）")

    application.run_polling(drop_pending_updates=True)
