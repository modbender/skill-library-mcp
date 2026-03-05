"""
基金持仓管理系统 - 环境检查和初始化
"""
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any

from .config import (
    QIEMAN_API_KEY,
    get_api_key,
    is_api_key_configured,
    get_qieman_mcp_config
)


class EnvChecker:
    """环境检查和初始化"""

    MCPORTER_CONFIG_PATH = Path.home() / ".mcporter" / "mcporter.json"
    REQUIRED_MCP_SERVER = "qieman-mcp"

    def __init__(self):
        self.results: Dict[str, Any] = {}

    def check_mcporter_installed(self) -> bool:
        """检查mcporter是否安装"""
        result = shutil.which("mcporter") is not None
        self.results["mcporter_installed"] = result
        return result

    def check_mcporter_config_exists(self) -> bool:
        """检查mcporter配置文件是否存在"""
        result = self.MCPORTER_CONFIG_PATH.exists()
        self.results["config_exists"] = result
        return result

    def check_qieman_mcp_configured(self) -> bool:
        """检查qieman-mcp是否已配置"""
        if not self.MCPORTER_CONFIG_PATH.exists():
            self.results["qieman_mcp_configured"] = False
            return False

        try:
            with open(self.MCPORTER_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)

            mcp_servers = config.get("mcpServers", {})
            result = self.REQUIRED_MCP_SERVER in mcp_servers
            self.results["qieman_mcp_configured"] = result
            return result
        except Exception as e:
            self.results["qieman_mcp_configured"] = False
            self.results["config_error"] = str(e)
            return False

    def check_api_key_configured(self) -> bool:
        """检查环境变量中的 API Key 是否已配置"""
        result = is_api_key_configured()
        self.results["api_key_configured"] = result
        return result

    def setup_qieman_mcp_config(self, force: bool = False) -> bool:
        """
        配置qieman-mcp服务器

        Args:
            force: 是否强制重新配置

        Returns:
            是否成功
        """
        # 如果已配置且不强制，则跳过
        if not force and self.check_qieman_mcp_configured():
            self.results["setup_skipped"] = True
            return True

        # 确保配置目录存在
        config_dir = self.MCPORTER_CONFIG_PATH.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        # 读取现有配置或创建新配置
        config = {"mcpServers": {}, "imports": []}
        if self.MCPORTER_CONFIG_PATH.exists():
            try:
                with open(self.MCPORTER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                pass

        # 添加qieman-mcp配置
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"][self.REQUIRED_MCP_SERVER] = get_qieman_mcp_config()

        # 保存配置
        try:
            with open(self.MCPORTER_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.results["setup_success"] = True
            return True
        except Exception as e:
            self.results["setup_error"] = str(e)
            return False

    def test_mcp_connection(self) -> bool:
        """测试MCP服务连接"""
        try:
            cmd = [
                "mcporter", "call",
                "qieman-mcp.BatchGetFundsDetail",
                "--args", json.dumps({"fundCodes": ["000001"]}),
                "--output", "json"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.results["mcp_connection"] = "success"
                return True
            else:
                self.results["mcp_connection"] = f"failed: {result.stderr}"
                return False
        except subprocess.TimeoutExpired:
            self.results["mcp_connection"] = "timeout"
            return False
        except Exception as e:
            self.results["mcp_connection"] = f"error: {str(e)}"
            return False

    def init_environment(self, force: bool = False) -> Dict[str, Any]:
        """
        完整环境初始化

        Args:
            force: 是否强制重新配置

        Returns:
            状态报告
        """
        self.results = {}

        # 1. 检查mcporter安装
        mcporter_ok = self.check_mcporter_installed()
        if not mcporter_ok:
            self.results["status"] = "error"
            self.results["message"] = "mcporter未安装，请先安装mcporter"
            return self.results

        # 2. 检查配置文件
        self.check_mcporter_config_exists()

        # 3. 检查qieman-mcp是否已配置
        qieman_configured = self.check_qieman_mcp_configured()

        # 4. 如果未配置，检查 API Key 环境变量
        if not qieman_configured:
            api_key_ok = self.check_api_key_configured()
            if not api_key_ok:
                self.results["status"] = "error"
                self.results["message"] = f"环境变量 {QIEMAN_API_KEY} 未配置，请设置 API Key"
                return self.results

            # 5. 配置qieman-mcp
            self.setup_qieman_mcp_config(force)

        # 6. 测试连接
        connection_ok = self.test_mcp_connection()

        # 生成状态报告
        if connection_ok:
            self.results["status"] = "success"
            self.results["message"] = "环境初始化成功"
        else:
            self.results["status"] = "warning"
            self.results["message"] = "环境配置完成，但MCP连接测试失败"

        return self.results

    def check_environment(self) -> Dict[str, Any]:
        """
        仅检查环境状态，不做修改

        Returns:
            状态报告
        """
        self.results = {}

        self.check_mcporter_installed()
        self.check_api_key_configured()
        self.check_mcporter_config_exists()
        self.check_qieman_mcp_configured()

        # 汇总状态
        all_ok = (
            self.results.get("mcporter_installed", False) and
            self.results.get("api_key_configured", False) and
            self.results.get("qieman_mcp_configured", False)
        )

        self.results["status"] = "ok" if all_ok else "error"
        self.results["message"] = "环境检查完成" if all_ok else "环境配置不完整"

        return self.results

    def get_report(self) -> str:
        """获取格式化的状态报告"""
        lines = []
        lines.append("=" * 50)
        lines.append("环境状态报告")
        lines.append("=" * 50)

        # mcporter安装状态
        status = "✓" if self.results.get("mcporter_installed") else "✗"
        lines.append(f"[{status}] mcporter安装")

        # API Key 环境变量状态
        status = "✓" if self.results.get("api_key_configured") else "✗"
        lines.append(f"[{status}] {QIEMAN_API_KEY} 环境变量")

        # 配置文件状态
        status = "✓" if self.results.get("config_exists") else "✗"
        lines.append(f"[{status}] 配置文件存在")

        # qieman-mcp配置状态
        status = "✓" if self.results.get("qieman_mcp_configured") else "✗"
        lines.append(f"[{status}] qieman-mcp配置")

        # MCP连接状态
        connection = self.results.get("mcp_connection", "未测试")
        if connection == "success":
            lines.append(f"[✓] MCP连接测试")
        else:
            lines.append(f"[✗] MCP连接测试: {connection}")

        lines.append("-" * 50)
        lines.append(f"状态: {self.results.get('status', 'unknown')}")
        lines.append(f"消息: {self.results.get('message', '')}")
        lines.append("=" * 50)

        return "\n".join(lines)