import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FileManager")

# 用户文件根目录：data/user_files/<username>/
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "user_files")


def _user_dir(username: str) -> str:
    """获取用户目录路径，自动创建"""
    # 防止路径穿越攻击
    safe_name = os.path.basename(username)
    user_path = os.path.join(BASE_DIR, safe_name)
    os.makedirs(user_path, exist_ok=True)
    return user_path


def _safe_path(username: str, filename: str) -> str:
    """拼接安全路径，防止路径穿越"""
    user_path = _user_dir(username)
    full_path = os.path.normpath(os.path.join(user_path, filename))
    # 确保路径在用户目录内
    if not full_path.startswith(user_path):
        raise ValueError(f"非法路径: {filename}")
    return full_path


@mcp.tool()
async def list_files(username: str) -> str:
    """
    列出当前用户的所有文件。
    :param username: 用户名（由系统自动注入，无需手动传递）
    """
    user_path = _user_dir(username)
    try:
        files = os.listdir(user_path)
        if not files:
            return "📂 你还没有任何文件。"
        result = "📂 你的文件列表：\n"
        for f in sorted(files):
            fpath = os.path.join(user_path, f)
            size = os.path.getsize(fpath)
            if size < 1024:
                size_str = f"{size} B"
            else:
                size_str = f"{size / 1024:.1f} KB"
            result += f"  - {f} ({size_str})\n"
        return result
    except Exception as e:
        return f"⚠️ 列出文件失败: {str(e)}"


@mcp.tool()
async def read_file(username: str, filename: str) -> str:
    """
    读取用户的指定文件内容。
    :param username: 用户名（由系统自动注入，无需手动传递）
    :param filename: 文件名
    """
    try:
        path = _safe_path(username, filename)
        if not os.path.exists(path):
            return f"❌ 文件 '{filename}' 不存在。"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if not content:
            return f"📄 文件 '{filename}' 是空的。"
        return f"📄 文件 '{filename}' 的内容：\n\n{content}"
    except ValueError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"⚠️ 读取文件失败: {str(e)}"


@mcp.tool()
async def write_file(username: str, filename: str, content: str) -> str:
    """
    创建或覆盖写入用户的指定文件。
    :param username: 用户名（由系统自动注入，无需手动传递）
    :param filename: 文件名
    :param content: 要写入的内容
    """
    try:
        path = _safe_path(username, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 文件 '{filename}' 已保存。"
    except ValueError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"⚠️ 写入文件失败: {str(e)}"


@mcp.tool()
async def append_file(username: str, filename: str, content: str) -> str:
    """
    向用户的指定文件末尾追加内容。
    :param username: 用户名（由系统自动注入，无需手动传递）
    :param filename: 文件名
    :param content: 要追加的内容
    """
    try:
        path = _safe_path(username, filename)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 内容已追加到 '{filename}'。"
    except ValueError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"⚠️ 追加文件失败: {str(e)}"


@mcp.tool()
async def delete_file(username: str, filename: str) -> str:
    """
    删除用户的指定文件。
    :param username: 用户名（由系统自动注入，无需手动传递）
    :param filename: 文件名
    """
    try:
        path = _safe_path(username, filename)
        if not os.path.exists(path):
            return f"❌ 文件 '{filename}' 不存在，无法删除。"
        os.remove(path)
        return f"🗑️ 文件 '{filename}' 已删除。"
    except ValueError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"⚠️ 删除文件失败: {str(e)}"


if __name__ == "__main__":
    mcp.run()
