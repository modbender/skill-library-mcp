#!/usr/bin/env python3
"""Gera resumo compacto e lista de pendências a partir do histórico de conversas."""
import argparse
import os
import re
import sys
from datetime import datetime, timezone

KEYWORDS = [
    "todo",
    "tarefa",
    "pendência",
    "próximo passo",
    "follow",
    "seguir",
    "action",
    "status",
    "pendentes",
    "continuar",
]

SENTENCE_SPLIT_PATTERN = r'(?<=[.!?])\s+'


def split_sentences(text: str) -> list[str]:
    sentences = [sent.strip() for sent in re.split(SENTENCE_SPLIT_PATTERN, text) if sent.strip()]
    return sentences


def parse_history(raw: str) -> list[dict]:
    entries = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        role, message = line.split(":", 1)
        entries.append({
            "role": role.strip().upper(),
            "text": message.strip(),
        })
    return entries


def collect_summary(entries: list[dict], limit: int) -> list[str]:
    sentences = []
    for entry in entries:
        sentences.extend(split_sentences(entry["text"]))
    if not sentences:
        return []
    if limit <= 0:
        return []
    if len(sentences) <= limit:
        return sentences
    half = limit // 2
    first_chunk = sentences[:half]
    last_chunk = sentences[-(limit - half) :]
    return first_chunk + last_chunk


def collect_pendencies(entries: list[dict], limit: int) -> list[str]:
    tasks = []
    for entry in entries:
        for sentence in split_sentences(entry["text"]):
            lowered = sentence.lower()
            if any(keyword in lowered for keyword in KEYWORDS):
                trimmed = sentence.strip()
                if trimmed and trimmed not in tasks:
                    tasks.append(trimmed)
    return tasks[:limit]


def format_recent(entries: list[dict], count: int) -> list[str]:
    recent = entries[-count:] if count > 0 else []
    formatted = [f"{entry['role']}: {entry['text']}" for entry in recent]
    return formatted


def build_markdown(summary: list[str], pendings: list[str], recent: list[str]) -> str:
    catalyst = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sections = ["# Context Gatekeeper", f"_Gerado: {catalyst}_", ""]
    if summary:
        sections.append("## Resumo compacto")
        sections.extend(f"- {sent}" for sent in summary)
        sections.append("")
    else:
        sections.append("## Resumo compacto")
        sections.append("- Sem conteúdo suficiente para resumir.")
        sections.append("")
    if pendings:
        sections.append("## Pendências e próximos passos")
        sections.extend(f"- {task}" for task in pendings)
        sections.append("")
    else:
        sections.append("## Pendências e próximos passos")
        sections.append("- Nenhuma pendência identificada no histórico recente.")
        sections.append("")
    if recent:
        sections.append("## Últimos turnos")
        sections.extend(f"- {line}" for line in recent)
    else:
        sections.append("## Últimos turnos")
        sections.append("- Sem turnos registrados.")
    return "\n".join(sections)


def ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compacta o histórico em um resumo token-friendly.")
    parser.add_argument("--history", help="Arquivo com as trocas (ROLE: texto).", type=str)
    parser.add_argument(
        "--summary",
        help="Arquivo de destino para o resumo (markdown).",
        type=str,
        default="skills/context-gatekeeper/context/current-summary.md",
    )
    parser.add_argument("--max-summary-sents", type=int, default=6)
    parser.add_argument("--max-recent-turns", type=int, default=4)
    parser.add_argument("--max-pendings", type=int, default=6)
    args = parser.parse_args()

    if args.history:
        try:
            with open(args.history, "r", encoding="utf-8") as handle:
                raw = handle.read()
        except FileNotFoundError:
            print(f"Histórico não encontrado: {args.history}")
            sys.exit(1)
    else:
        raw = sys.stdin.read()

    entries = parse_history(raw)
    summary_sentences = collect_summary(entries, args.max_summary_sents)
    pendings = collect_pendencies(entries, args.max_pendings)
    recent = format_recent(entries, args.max_recent_turns)

    output = build_markdown(summary_sentences, pendings, recent)
    ensure_parent(args.summary)
    with open(args.summary, "w", encoding="utf-8") as out:
        out.write(output)
    print(output)


if __name__ == "__main__":
    main()
