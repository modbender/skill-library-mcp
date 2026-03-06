#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Native Multi-Agent Engine
通过 OpenClaw CLI 实现真正的多 Agent 并行编排

不需要任何 API key，直接复用 OpenClaw 内部模型路由。

Security Design Notes:
- This engine is a pipeline mode runner for the claw-multi-agent skill.
- Task descriptions are composed by the main OpenClaw agent (not raw user input),
  which is itself sandboxed by OpenClaw's permission model.
- Sub-agents run within the same OpenClaw session context and inherit the same
  permission boundaries as the main agent.
- The {file_path} placeholder in templates should always be a project-relative path.
  It is the responsibility of the orchestrating agent to validate paths before use.
- This skill does not introduce new attack surface beyond what OpenClaw already permits.
"""

import subprocess
import concurrent.futures
import json
import uuid
import time
import sys
import os
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("multiagent")


# 模型别名映射
# 设计原则：用户 OpenClaw 里配了什么模型，就用什么模型
# - 不传 model → openclaw agent CLI 使用用户自己的默认模型（推荐）
# - 传 None    → 同上
# - 传具体 id  → 使用指定模型（高级用法）
#
# 别名仅作为语义标记，方便在 task 里写 "fast"/"smart"/"best"
# 实际 model id 全部解析为 None（走用户默认），除非用户显式指定
MODEL_ALIASES: Dict[str, Optional[str]] = {
    "fast":  None,   # → 用户默认模型（轻量任务）
    "smart": None,   # → 用户默认模型（中等任务）
    "best":  None,   # → 用户默认模型（高质量任务）
    "default": None, # → 用户默认模型
}

# 角色 → 模型别名（都走用户默认，保持一致）
ROLE_MODEL_MAP: Dict[str, str] = {
    "researcher": "fast",
    "writer":     "smart",
    "coder":      "smart",
    "analyst":    "smart",
    "reviewer":   "fast",
    "planner":    "fast",
}

# 成本权重（语义用，实际都走同一个模型，保留供未来扩展）
MODEL_COST_TIER: Dict[str, int] = {
    "fast":    1,
    "smart":   3,
    "best":    5,
    "default": 3,
}


@dataclass
class AgentTask:
    """单个子任务定义"""
    task: str                          # 任务内容
    model: str = "kimi"               # 模型别名（见 MODEL_ALIASES）
    role: str = "assistant"           # 角色描述（会注入到 task 前缀）
    label: str = ""                   # 任务标签（便于追踪）
    thinking: str = "off"             # 思考模式：off/low/medium/high
    timeout: int = 300                # 超时秒数
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 隔离 session


@dataclass
class AgentResult:
    """子任务执行结果"""
    label: str
    model: str
    task: str
    output: str
    success: bool
    execution_time: float
    error: Optional[str] = None


class OrchestratorGuide:
    """
    指挥官模式使用指南
    提供 sessions_spawn 的最佳实践模板，供主 Agent 参考
    """
    
    # 预设角色定义（从 agent-swarm 迁移）
    PRESETS = {
        "planner": {
            "model": "glm",
            "description": "规划者：需求分析、任务拆解、优先级排序",
            "system_hint": "你是一个项目规划专家，擅长将复杂需求拆解为清晰的执行步骤。"
        },
        "researcher": {
            "model": "glm", 
            "description": "信息猎手：广度搜索、交叉验证、结构化输出（有 web_search 工具）",
            "system_hint": "你是一个专业研究员，擅长搜索和整理信息，输出结构化报告。"
        },
        "coder": {
            "model": "kimi",
            "description": "代码工匠：编码、调试、测试、重构（有 exec 工具）",
            "system_hint": "你是一个资深工程师，擅长编写高质量、可维护的代码。"
        },
        "writer": {
            "model": "gemini",
            "description": "文字工匠：文档、报告、文案、整理（有 write 工具）",
            "system_hint": "你是一个专业写作者，擅长将信息组织成清晰、有价值的文档。"
        },
        "reviewer": {
            "model": "glm",
            "description": "质量守门人：代码审查、内容审核、合规检查",
            "system_hint": "你是一个严格的审查员，客观指出问题并给出建设性改进意见。"
        },
        "analyst": {
            "model": "kimi",
            "description": "数据侦探：数据处理、统计分析、趋势预测（有 exec 工具）",
            "system_hint": "你是一个数据分析专家，擅长从数据中发现规律和洞察。"
        }
    }
    
    @staticmethod
    def get_preset_task_template(role: str, task: str, context: str = "") -> str:
        """生成适合 sessions_spawn 的 task 描述模板"""
        preset = OrchestratorGuide.PRESETS.get(role, {})
        hint = preset.get("system_hint", "")
        
        template = f"""{hint}

{'【上下文】' + chr(10) + context + chr(10) if context else ''}【你的任务】
{task}

【输出要求】
- 格式清晰，使用 Markdown
- 结果保存到指定路径（如有）
- 完成后简短总结做了什么"""
        return template
    
    @staticmethod
    def print_orchestrator_guide():
        """打印指挥官模式使用指南"""
        print("\n📋 指挥官模式 - 预设角色")
        print("=" * 60)
        for role, info in OrchestratorGuide.PRESETS.items():
            print(f"\n  {role} (默认模型: {info['model']})")
            print(f"    {info['description']}")
        print("\n" + "=" * 60)
        print("使用方式：在主 Agent 的对话中，使用 sessions_spawn 工具")
        print("详见 SKILL.md 中的「指挥官模式」章节")


class MultiAgentEngine:
    """
    OpenClaw 原生 Multi-Agent 引擎
    
    通过 `openclaw agent` CLI 并行触发多个 Agent，
    收集结果后进行聚合输出。
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        continue_on_error: bool = True,
        verbose: bool = False
    ):
        self.max_concurrent = max_concurrent
        self.continue_on_error = continue_on_error
        self.verbose = verbose

    def _resolve_model(self, model_alias: str) -> str:
        """将别名解析为 OpenClaw model id，None 表示使用用户默认模型
        解析顺序：
        1. 角色别名（researcher/writer 等）→ 模型别名
        2. 模型别名（fast/smart/best）→ None（用户默认）或具体 model id
        3. 其他字符串 → 直接当 model id 透传
        """
        # 如果是角色名，先映射到模型别名
        if model_alias in ROLE_MODEL_MAP:
            model_alias = ROLE_MODEL_MAP[model_alias]
        # 别名表里查，None 表示走用户默认
        if model_alias in MODEL_ALIASES:
            return MODEL_ALIASES[model_alias]  # 可能是 None
        # 不在别名表里，当作真实 model id 透传
        return model_alias

    def _run_agent(self, task: AgentTask) -> AgentResult:
        """
        通过 openclaw agent CLI 执行单个子任务
        """
        label = task.label or task.session_id[:8]
        model_id = self._resolve_model(task.model)

        # 构建完整 prompt（加入角色前缀）
        if task.role and task.role != "assistant":
            full_prompt = f"你现在扮演的角色是：{task.role}\n\n{task.task}"
        else:
            full_prompt = task.task

        # 构建 CLI 命令
        cmd = [
            "openclaw", "agent",
            "--session-id", task.session_id,
            "--message", full_prompt,
            "--json",
        ]
        if task.thinking != "off":
            cmd += ["--thinking", task.thinking]

        # model_id 为 None → 不传 --model，让 OpenClaw 用用户自己配置的默认模型
        # model_id 有值  → 透传给 CLI，使用指定模型
        env = {**os.environ}
        if model_id:
            env["OPENCLAW_AGENT_MODEL"] = model_id
            logger.info(f"[{label}] 启动 Agent (model={model_id}, thinking={task.thinking})")
        else:
            logger.info(f"[{label}] 启动 Agent (model=用户默认, thinking={task.thinking})")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=task.timeout,
                env=env
            )
            elapsed = time.time() - start_time

            if result.returncode != 0:
                err = result.stderr.strip() or result.stdout.strip()
                logger.warning(f"[{label}] 执行失败 ({elapsed:.1f}s): {err[:200]}")
                return AgentResult(
                    label=label, model=task.model, task=task.task,
                    output="", success=False, execution_time=elapsed,
                    error=err
                )

            # 解析 JSON 输出（openclaw agent --json 格式）
            output_text = ""
            try:
                data = json.loads(result.stdout)
                # openclaw agent --json 的标准输出格式
                payloads = (
                    data.get("result", {})
                        .get("payloads", [])
                )
                if payloads:
                    output_text = "\n".join(
                        p.get("text", "") for p in payloads if p.get("text")
                    )
                else:
                    # 兜底：尝试常见字段
                    output_text = (
                        data.get("reply") or
                        data.get("output") or
                        data.get("text") or
                        result.stdout.strip()
                    )
            except json.JSONDecodeError:
                output_text = result.stdout.strip()

            logger.info(f"[{label}] 完成 ({elapsed:.1f}s), 输出 {len(output_text)} 字符")
            return AgentResult(
                label=label, model=task.model, task=task.task,
                output=output_text, success=True, execution_time=elapsed
            )

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            logger.error(f"[{label}] 超时 ({task.timeout}s)")
            return AgentResult(
                label=label, model=task.model, task=task.task,
                output="", success=False, execution_time=elapsed,
                error=f"超时（{task.timeout}s）"
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{label}] 异常: {e}")
            return AgentResult(
                label=label, model=task.model, task=task.task,
                output="", success=False, execution_time=elapsed,
                error=str(e)
            )

    def run_parallel(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """
        并行执行多个任务，最多 max_concurrent 个同时运行
        所有任务收到相同（或各自定制的）任务描述，同时执行
        """
        logger.info(f"🚀 并行执行 {len(tasks)} 个任务 (max_concurrent={self.max_concurrent})")
        results = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent
        ) as executor:
            future_map = {
                executor.submit(self._run_agent, t): t
                for t in tasks
            }
            for future in concurrent.futures.as_completed(future_map):
                try:
                    r = future.result()
                    results.append(r)
                except Exception as e:
                    task = future_map[future]
                    logger.error(f"[{task.label}] 未捕获异常: {e}")
                    if not self.continue_on_error:
                        raise

        return results

    def run_sequential(
        self,
        tasks: List[AgentTask],
        pass_context: bool = True
    ) -> List[AgentResult]:
        """
        串行执行任务，前一个的输出可以作为后一个的上下文
        """
        logger.info(f"📋 串行执行 {len(tasks)} 个任务")
        results = []
        context = ""

        for i, task in enumerate(tasks):
            if pass_context and context and i > 0:
                task.task = (
                    f"【前序任务输出】\n{context}\n\n"
                    f"【当前任务】\n{task.task}"
                )
            r = self._run_agent(task)
            results.append(r)
            if r.success:
                context = r.output
            elif not self.continue_on_error:
                logger.error(f"串行任务失败，中止执行")
                break

        return results

    def run_hybrid(
        self,
        research_tasks: List[AgentTask],
        draft_task_template: str,
        num_drafts: int = 3,
        draft_models: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        混合模式：先并行搜索（依赖外部指挥官），再流水线并行生成多版草稿

        Phase 1: 并行执行 research_tasks（搜索/调研）
        Phase 2: 把 Phase 1 结果注入 context，并行生成 num_drafts 版草稿

        Args:
            research_tasks: Phase 1 调研任务列表
            draft_task_template: Phase 2 草稿任务模板，用 {research} 占位符注入调研结果
            num_drafts: Phase 2 草稿数量（默认 3）
            draft_models: Phase 2 每个草稿使用的模型列表（默认都用 default）

        Returns:
            {"research_results": [...], "draft_results": [...], "stats": {...}}
        """
        logger.info(f"🔀 混合模式启动: {len(research_tasks)} 调研任务 → {num_drafts} 版草稿")

        # Phase 1: 并行调研
        logger.info("📡 Phase 1: 并行调研中...")
        research_results = self.run_parallel(research_tasks)

        # 聚合调研结果
        research_summary = "\n\n".join([
            f"[{r.label}] {r.output}"
            for r in research_results if r.success
        ])

        if not research_summary:
            logger.warning("Phase 1 调研全部失败，跳过 Phase 2")
            return {
                "research_results": research_results,
                "draft_results": [],
                "stats": {"phase1_ok": 0, "phase2_ok": 0},
            }

        # Phase 2: 并行生成多版草稿
        logger.info(f"✍️  Phase 2: 并行生成 {num_drafts} 版草稿...")
        if draft_models is None:
            draft_models = ["default"] * num_drafts

        draft_tasks = []
        for i in range(num_drafts):
            model = draft_models[i] if i < len(draft_models) else "default"
            task_text = draft_task_template.format(research=research_summary)
            draft_tasks.append(AgentTask(
                task=task_text,
                model=model,
                role="writer",
                label=f"draft_{i+1}",
                timeout=300,
            ))

        draft_results = self.run_parallel(draft_tasks)

        return {
            "research_results": research_results,
            "draft_results": draft_results,
            "stats": {
                "phase1_ok": sum(1 for r in research_results if r.success),
                "phase1_total": len(research_results),
                "phase2_ok": sum(1 for r in draft_results if r.success),
                "phase2_total": len(draft_results),
            },
        }

    def aggregate(
        self,
        results: List[AgentResult],
        mode: str = "synthesize",
        original_task: str = ""
    ) -> str:
        """
        聚合多个结果

        mode:
          - concatenate: 简单拼接
          - synthesize:  生成综合摘要模板（供主 Agent 进一步处理）
          - compare:     并排对比
          - last:        只返回最后一个（串行场景）
        """
        successful = [r for r in results if r.success]

        if not successful:
            return "⚠️ 所有子任务均失败，无有效结果。"

        if mode == "concatenate":
            parts = []
            for r in successful:
                parts.append(f"### [{r.label}] ({r.model})\n\n{r.output}")
            return "\n\n---\n\n".join(parts)

        elif mode == "compare":
            lines = [f"## 模型对比结果\n\n**任务**: {original_task}\n"]
            for r in results:
                status = "✅" if r.success else "❌"
                lines.append(
                    f"### {status} {r.model} ({r.label})\n"
                    f"*耗时: {r.execution_time:.1f}s*\n\n"
                    + (r.output if r.success else f"错误: {r.error}")
                )
            return "\n\n".join(lines)

        elif mode == "last":
            return successful[-1].output if successful else ""

        else:  # synthesize（默认）
            parts = []
            for i, r in enumerate(successful, 1):
                parts.append(f"**子任务 {i}（{r.label} / {r.model}）**:\n{r.output}")
            combined = "\n\n".join(parts)
            return (
                f"## 子任务汇总（共 {len(successful)}/{len(results)} 成功）\n\n"
                f"原始任务：{original_task}\n\n"
                f"{combined}\n\n"
                f"---\n\n*请根据以上子任务结果，综合整理最终答案。*"
            )

    def print_stats(self, results: List[AgentResult]) -> None:
        """输出执行统计"""
        total = len(results)
        ok = sum(1 for r in results if r.success)
        total_time = sum(r.execution_time for r in results)
        max_time = max(r.execution_time for r in results) if results else 0

        print("\n" + "=" * 60)
        print("📊 Multi-Agent 执行统计")
        print("=" * 60)
        print(f"{'Agent':<20} {'模型':<15} {'状态':<6} {'耗时':>6}")
        print("-" * 60)
        for r in results:
            status = "✅" if r.success else "❌"
            print(f"{r.label:<20} {r.model:<15} {status:<6} {r.execution_time:>5.1f}s")
        print("-" * 60)
        print(f"总计: {ok}/{total} 成功 | 串行总时: {total_time:.1f}s | 并行节省约: {total_time - max_time:.1f}s")
        print("=" * 60)
