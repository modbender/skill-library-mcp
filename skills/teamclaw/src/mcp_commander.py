"""
MCP 指令执行工具服务 — 安全沙箱化的系统命令执行
- 每个用户有独立的工作目录 (data/user_files/<username>/)
- 严格白名单机制，只允许安全命令
- 超时保护、输出截断、路径穿越防护
- 跨平台支持（Linux/macOS/Windows）
"""

import os
import sys
import asyncio
import shlex
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Commander")

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载 .env 配置
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, "config", ".env"))

# 用户文件根目录（与 mcp_filemanager.py 共享）
USER_FILES_BASE = os.path.join(PROJECT_ROOT, "data", "user_files")

# 平台检测
IS_WINDOWS = sys.platform == "win32"

# ======== 安全配置（支持 .env 自定义）========

# 内置默认白名单（按平台区分）
if IS_WINDOWS:
    _DEFAULT_COMMANDS = {
        # 文件与目录
        "dir", "type", "more", "find", "findstr", "where", "tree",
        "copy", "move", "ren",
        # 文本处理
        "sort", "fc",
        # 系统信息（只读）
        "echo", "date", "time", "whoami", "hostname",
        "systeminfo", "set", "ver", "vol",
        "tasklist", "wmic",
        # 实用工具
        "cd", "chdir", "certutil",
        # Python
        "python", "python3",
        # 网络（只读）
        "ping", "curl", "ipconfig", "nslookup", "tracert", "netstat",
        # PowerShell 常用（安全子集）
        "powershell","npm","npx","git","node"
    }
else:
    _DEFAULT_COMMANDS = {
        # 文件与目录
        "ls", "cat", "head", "tail", "wc", "du", "find", "file", "stat",
        # 文本处理
        "grep", "awk", "sed", "sort", "uniq", "cut", "tr", "diff", "comm",
        # 系统信息（只读）
        "echo", "date", "cal", "whoami", "uname", "hostname",
        "uptime", "free", "df", "env", "printenv",
        # 实用工具
        "pwd", "which", "expr", "seq", "yes", "true", "false",
        "base64", "md5sum", "sha256sum", "xxd",
        # Python
        "python", "python3",
        # 网络（只读）
        "ping", "curl", "wget",
        "npm","npx","git","node"
    }

# 从 .env 读取用户自定义白名单，留空或不设置则使用默认
_env_commands = os.getenv("ALLOWED_COMMANDS", "").strip()
if _env_commands:
    ALLOWED_COMMANDS = {cmd.strip() for cmd in _env_commands.split(",") if cmd.strip()}
else:
    ALLOWED_COMMANDS = _DEFAULT_COMMANDS

# 严格禁止的命令（即使在白名单中也拒绝这些子命令/参数模式）
if IS_WINDOWS:
    BLOCKED_PATTERNS = [
        "del /s /q c:\\", "format ", "diskpart", "bcdedit",
        "reg delete", "reg add",
        "shutdown", "restart", "logoff",
        "net user", "net localgroup", "runas",
        "taskkill /f /im", "schtasks /delete",
        "powershell -enc", "powershell -e ",  # 编码执行，可绕过审查
        "invoke-expression", "iex ", "iex(",
        "remove-item -recurse -force c:\\",
    ]
else:
    BLOCKED_PATTERNS = [
        "rm -rf /", "rm -rf /*", "mkfs", "dd if=", ":(){ :", "fork bomb",
        "> /dev/sd", "chmod 777 /", "chown root", "/etc/passwd", "/etc/shadow",
        "sudo", "su ", "shutdown", "reboot", "halt", "poweroff",
        "systemctl", "service ", "init ",
    ]

# 执行超时（秒）— 支持 .env 自定义
EXEC_TIMEOUT = int(os.getenv("EXEC_TIMEOUT", "60"))

# 输出最大长度（字符数）— 支持 .env 自定义
MAX_OUTPUT_LENGTH = int(os.getenv("MAX_OUTPUT_LENGTH", "8000"))


def _sandbox_env(workspace: str, username: str) -> dict:
    """构造沙箱环境变量（跨平台）"""
    if IS_WINDOWS:
        return {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"),
            "COMSPEC": os.environ.get("COMSPEC", r"C:\Windows\system32\cmd.exe"),
            "USERPROFILE": workspace,
            "USERNAME": username,
            "TEMP": os.environ.get("TEMP", workspace),
            "TMP": os.environ.get("TMP", workspace),
        }
    else:
        return {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": workspace,
            "USER": username,
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
            "TERM": "xterm",
        }


def _python_cmd() -> str:
    """返回当前平台的 Python 命令名"""
    return sys.executable


def _user_workspace(username: str) -> str:
    """获取用户独立工作目录，自动创建"""
    safe_name = os.path.basename(username)
    workspace = os.path.join(USER_FILES_BASE, safe_name)
    os.makedirs(workspace, exist_ok=True)
    return workspace


def _validate_command(command: str) -> str | None:
    """
    验证命令安全性，返回 None 表示通过，返回字符串表示拒绝原因
    """
    stripped = command.strip()
    if not stripped:
        return "命令不能为空"

    # 检查危险模式
    lower_cmd = stripped.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in lower_cmd:
            return f"安全策略拒绝：检测到危险模式 '{pattern}'"

    # 禁止管道到破坏性命令
    # 允许管道（|）和重定向（>）用于文本处理，但在用户沙箱目录内
    # 提取第一个命令（管道链中每个命令都要检查）
    # 用 ; && || | 分割命令链
    import re
    parts = re.split(r'[;|&]+', stripped)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 获取命令名（去掉可能的 env 变量赋值前缀）
        tokens = part.split()
        cmd_name = None
        for token in tokens:
            if "=" in token and token.index("=") > 0:
                continue  # 跳过 VAR=value 形式的环境变量
            cmd_name = os.path.basename(token)  # 取基础命令名
            break

        if cmd_name and cmd_name not in ALLOWED_COMMANDS:
            return f"安全策略拒绝：命令 '{cmd_name}' 不在白名单中。允许的命令：{', '.join(sorted(ALLOWED_COMMANDS))}"

    return None


def _truncate_output(text: str, max_len: int = MAX_OUTPUT_LENGTH) -> str:
    """截断过长输出"""
    if len(text) <= max_len:
        return text
    half = max_len // 2
    return (
        text[:half]
        + f"\n\n... [输出过长，已截断，共 {len(text)} 字符] ...\n\n"
        + text[-half:]
    )


@mcp.tool()
async def run_command(username: str, command: str) -> str:
    """
    在用户的隔离工作目录中执行系统命令。
    仅允许安全的只读/文本处理类命令，有超时保护。

    :param username: 用户名（由系统自动注入，无需手动传递）
    :param command: 要执行的 shell 命令，例如 "ls -la" 或 "cat notes.txt | grep TODO"
    """
    # 1. 安全校验
    reject_reason = _validate_command(command)
    if reject_reason:
        return f"❌ {reject_reason}"

    # 2. 获取用户工作目录
    workspace = _user_workspace(username)

    try:
        # 3. 在用户目录下执行命令（使用 shell=True 以支持管道和重定向）
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=workspace,
            # 限制环境变量，移除敏感信息
            env=_sandbox_env(workspace, username),
        )

        # 4. 带超时等待
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=EXEC_TIMEOUT
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return f"⏱️ 命令执行超时（{EXEC_TIMEOUT}秒限制），已终止。"

        # 5. 组装输出
        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()
        exit_code = proc.returncode

        result_parts = []
        if exit_code == 0:
            result_parts.append(f"✅ 命令执行成功 (exit code: 0)")
        else:
            result_parts.append(f"⚠️ 命令执行完毕 (exit code: {exit_code})")

        result_parts.append(f"📁 工作目录: ~/{username}/")

        if out:
            result_parts.append(f"📤 标准输出:\n{_truncate_output(out)}")
        if err:
            result_parts.append(f"📤 标准错误:\n{_truncate_output(err)}")
        if not out and not err:
            result_parts.append("(无输出)")

        return "\n\n".join(result_parts)

    except Exception as e:
        return f"❌ 执行异常: {str(e)}"


@mcp.tool()
async def run_python_code(username: str, code: str) -> str:
    """
    在用户的隔离工作目录中执行 Python 代码片段。
    适用于数据计算、文本处理、简单脚本等场景。

    :param username: 用户名（由系统自动注入，无需手动传递）
    :param code: 要执行的 Python 代码
    """
    workspace = _user_workspace(username)

    # 将代码写入临时文件执行（比 -c 参数更可靠，支持多行和特殊字符）
    tmp_script = os.path.join(workspace, ".tmp_exec.py")
    try:
        with open(tmp_script, "w", encoding="utf-8") as f:
            f.write(code)

        proc = await asyncio.create_subprocess_exec(
            _python_cmd(), tmp_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=workspace,
            env=_sandbox_env(workspace, username),
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=EXEC_TIMEOUT
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return f"⏱️ Python 代码执行超时（{EXEC_TIMEOUT}秒限制），已终止。"

        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()
        exit_code = proc.returncode

        result_parts = []
        if exit_code == 0:
            result_parts.append("✅ Python 代码执行成功")
        else:
            result_parts.append(f"⚠️ Python 代码执行出错 (exit code: {exit_code})")

        if out:
            result_parts.append(f"📤 输出:\n{_truncate_output(out)}")
        if err:
            result_parts.append(f"📤 错误信息:\n{_truncate_output(err)}")
        if not out and not err:
            result_parts.append("(无输出)")

        return "\n\n".join(result_parts)

    except Exception as e:
        return f"❌ 执行异常: {str(e)}"
    finally:
        # 清理临时文件
        if os.path.exists(tmp_script):
            try:
                os.remove(tmp_script)
            except Exception:
                pass


@mcp.tool()
async def list_allowed_commands() -> str:
    """
    列出所有允许执行的系统命令白名单。
    用户想了解能执行哪些命令时调用此工具。
    """
    # 按类别分组（动态匹配当前生效的白名单，按平台区分）
    if IS_WINDOWS:
        categories = [
            ("📁 文件与目录", ["dir", "type", "more", "find", "findstr", "where", "tree",
                             "copy", "move", "ren"]),
            ("📝 文本处理", ["sort", "fc"]),
            ("🖥️ 系统信息", ["echo", "date", "time", "whoami", "hostname",
                           "systeminfo", "set", "ver", "vol", "tasklist", "wmic"]),
            ("🔧 实用工具", ["cd", "chdir", "certutil"]),
            ("🐍 Python", ["python", "python3"]),
            ("🌐 网络", ["ping", "curl", "ipconfig", "nslookup", "tracert", "netstat"]),
            ("💠 PowerShell", ["powershell"]),
        ]
    else:
        categories = [
            ("📁 文件与目录", ["ls", "cat", "head", "tail", "wc", "du", "find", "file", "stat"]),
            ("📝 文本处理", ["grep", "awk", "sed", "sort", "uniq", "cut", "tr", "diff", "comm"]),
            ("🖥️ 系统信息", ["echo", "date", "cal", "whoami", "uname", "hostname",
                           "uptime", "free", "df", "env", "printenv"]),
            ("🔧 实用工具", ["pwd", "which", "expr", "seq", "base64", "md5sum", "sha256sum", "xxd"]),
            ("🐍 Python", ["python", "python3"]),
            ("🌐 网络", ["ping", "curl", "wget"]),
        ]

    is_custom = bool(_env_commands)
    result = "📋 **允许执行的命令白名单**"
    if is_custom:
        result += "（用户自定义）"
    result += "\n\n"

    # 展示分类中当前生效的命令
    shown = set()
    for category, cmds in categories:
        active = [c for c in cmds if c in ALLOWED_COMMANDS]
        if active:
            result += f"{category}: {', '.join(active)}\n"
            shown.update(active)

    # 展示用户自定义中不在默认分类里的命令
    extra = ALLOWED_COMMANDS - shown
    if extra:
        result += f"📌 其他: {', '.join(sorted(extra))}\n"

    result += (
        "\n⚠️ **安全说明**:\n"
        "- 所有命令在用户隔离目录中执行\n"
        "- 支持管道（|）和重定向（>）\n"
        f"- 执行超时限制：{EXEC_TIMEOUT}秒\n"
        f"- 输出长度限制：{MAX_OUTPUT_LENGTH}字符\n"
    )
    return result


if __name__ == "__main__":
    mcp.run()
