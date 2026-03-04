"""
API Patch 模块

提供 OpenAI API 格式适配功能：
- 标准模式（默认）：使用 type:"input_audio" 格式
- 非标准模式：使用 type:"file" + data URI 格式，并启用 MIME patch

环境变量：
    OPENAI_STANDARD_MODE: 设为 "false"/"0"/"no" 表示非标准模式
                          默认（不设置或设为其他值）为标准模式
"""

import os

_audio_mime_map = {
    "mp3": "audio/mp3", "wav": "audio/wav", "webm": "audio/webm",
    "ogg": "audio/ogg", "flac": "audio/flac", "aac": "audio/aac",
    "m4a": "audio/m4a", "mpeg": "audio/mpeg",
}


def is_standard_mode() -> bool:
    """判断是否为标准 OpenAI API 模式"""
    standard_mode = os.getenv("OPENAI_STANDARD_MODE", "").lower()
    return standard_mode not in ("false", "0", "no")


def build_audio_part(audio_b64: str, audio_fmt: str, audio_name: str = None) -> dict:
    """
    根据当前模式构建音频内容块。

    标准模式：返回 OpenAI 标准 input_audio 格式
    非标准模式：返回 type: "file" + data URI 格式

    Args:
        audio_b64: 音频的 base64 数据（可带或不带 data: 前缀）
        audio_fmt: 音频格式（wav/mp3/webm 等）
        audio_name: 文件名（非标准模式使用）

    Returns:
        dict: 符合当前模式的音频内容块
    """
    # 提取纯 base64（去掉 data: 前缀）
    if audio_b64.startswith("data:"):
        audio_b64 = audio_b64.split(",", 1)[-1]

    if is_standard_mode():
        # 标准模式：OpenAI input_audio 格式
        return {
            "type": "input_audio",
            "input_audio": {
                "data": audio_b64,
                "format": audio_fmt,
            },
        }
    else:
        # 非标准模式：type: "file" + data URI
        # 注意：需根据中转 API 的特殊格式设置，部分中转不支持 input_audio 格式
        mime = _audio_mime_map.get(audio_fmt, f"audio/{audio_fmt}")
        return {
            "type": "file",
            "file": {
                "filename": audio_name or f"audio.{audio_fmt}",
                "file_data": f"data:{mime};base64,{audio_b64}",
            },
        }


def patch_langchain_file_mime():
    """
    修复 LangChain 的 MIME 硬编码 bug（仅非标准模式）。

    注意：需根据中转 API 的特殊格式设置，部分中转 API 代理会强制替换 MIME 类型。

    问题：LangChain 在处理 type:"file" 格式的数据时，会忽略 data URI 中的
    真实 MIME 类型，强制替换为 "application/pdf"，导致音频等非 PDF 文件无法识别。

    解决：Monkey-patch _convert_openai_format_to_data_block 函数，
    让它使用 data URI 中解析出的实际 MIME type。
    """
    if is_standard_mode():
        print("[api_patch] 标准OpenAI模式（默认），跳过 MIME patch")
        return

    try:
        import langchain_core.messages.block_translators.openai as _oai_mod
        _original_fn = _oai_mod._convert_openai_format_to_data_block

        def _patched_convert(block):
            # 仅拦截 base64-style file block，修正 mime_type
            if (
                isinstance(block, dict)
                and block.get("type") == "file"
                and "file_data" in block.get("file", {})
            ):
                parsed = _oai_mod._parse_data_uri(block["file"]["file_data"])
                if parsed and parsed.get("mime_type"):
                    # 调用原函数，但之后修正 mime_type
                    result = _original_fn(block)
                    # result 可能是 dict（透传）或 ContentBlock
                    if hasattr(result, "mime_type"):
                        object.__setattr__(result, "mime_type", parsed["mime_type"])
                    elif isinstance(result, dict) and "mime_type" in result:
                        result["mime_type"] = parsed["mime_type"]
                    return result
            return _original_fn(block)

        _oai_mod._convert_openai_format_to_data_block = _patched_convert
        print("[api_patch] ✅ LangChain file MIME 硬编码已修复（非标准模式）")
    except Exception as e:
        print(f"[api_patch] ⚠️ Patch 失败（不影响非音频功能）: {e}")
