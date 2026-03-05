#!/usr/bin/env python3
"""Monitora o histórico e atualiza o resumo antes de cada resposta."""
import os
import subprocess
import sys
import time
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HISTORY_PATH = os.path.join(BASE, "context", "history.txt")
SUMMARY_PATH = os.path.join(BASE, "context", "current-summary.md")
SCRIPT_PATH = os.path.join(BASE, "scripts", "context_gatekeeper.py")
LOG_PATH = os.path.join(BASE, "context", "auto-monitor.log")
CHECK_INTERVAL = 1.0


def log(message: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    line = f"[{now}] {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(line)
    print(line.strip(), flush=True)


def run_summary() -> None:
    args = [sys.executable, SCRIPT_PATH, "--history", HISTORY_PATH, "--summary", SUMMARY_PATH]
    log(f"Atualizando resumo ({' '.join(args)})")
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        log(f"Erro ao gerar resumo: {exc} | stdout={exc.stdout.strip()} stderr={exc.stderr.strip()}")
    else:
        output = result.stdout.strip()
        if output:
            log("Resumo atualizado com sucesso")
            if output:
                log(f"Resumo (amostr): {output.splitlines()[0][:120]}...")
        else:
            log("Resumo gerado mas sem saída" )


def main() -> None:
    log("Iniciando monitor de histórico")
    last_mtime = None
    while True:
        if os.path.exists(HISTORY_PATH):
            try:
                mtime = os.path.getmtime(HISTORY_PATH)
            except OSError:
                mtime = None
            if mtime and mtime != last_mtime:
                last_mtime = mtime
                run_summary()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
