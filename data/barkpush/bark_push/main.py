from __future__ import annotations

import argparse
import sys

from .command_handler import handle_cli_args


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bark-push", add_help=True)
    p.add_argument("--config", type=str, default="", help="配置文件路径（默认自动查找/创建）")

    ops = p.add_argument_group("操作")
    ops.add_argument("--update", type=str, default="", help="更新指定 push_id")
    ops.add_argument("--delete", type=str, default="", help="删除指定 push_id")
    ops.add_argument("--list-users", action="store_true", help="列出所有用户")
    ops.add_argument("--list-groups", action="store_true", help="列出所有分组")
    ops.add_argument("--list-history", action="store_true", help="列出历史记录")
    ops.add_argument("--history-limit", type=int, default=20, help="历史列表返回条数")
    ops.add_argument("--help-skill", dest="help", action="store_true", help="显示技能帮助")

    basic = p.add_argument_group("基础参数")
    basic.add_argument("--user", "-u", type=str, default="", help="用户别名，多个用逗号分隔，或 all")
    basic.add_argument("--title", "-t", type=str, default="", help="标题")
    basic.add_argument("--subtitle", type=str, default="", help="副标题")
    basic.add_argument("--content", "-c", type=str, default="", help="内容（文本/链接/图片/混合）")
    basic.add_argument("--group", type=str, default="", help="分组")

    params = p.add_argument_group("推送参数")
    params.add_argument("--level", type=str, default="", help="passive/active/time-sensitive/critical")
    params.add_argument("--volume", type=int, default=None, help="0-10（critical 时生效）")
    params.add_argument("--badge", type=int, default=None, help="角标数字")
    params.add_argument("--call", type=str, default="", help="1/0/true/false")
    params.add_argument("--autoCopy", type=str, default="", help="1/0/true/false")
    params.add_argument("--copy", type=str, default="", help="复制内容")
    params.add_argument("--sound", type=str, default="", help="铃声名称")
    params.add_argument("--icon", type=str, default="", help="图标 URL")
    params.add_argument("--isArchive", type=str, default="", help="1/0/true/false")
    params.add_argument("--action", type=str, default="", help='action="none" 或自定义动作字符串')
    params.add_argument("--ciphertext", type=str, default="", help="加密密文（可选）")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if isinstance(args.update, str) and args.update.strip() == "":
        args.update = None
    if isinstance(args.delete, str) and args.delete.strip() == "":
        args.delete = None
    if isinstance(args.config, str) and args.config.strip() == "":
        args.config = None

    result = handle_cli_args(args)
    sys.stdout.write(result.format_text() + "\n")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
