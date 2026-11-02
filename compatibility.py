#!/usr/bin/env python3
"""Monarca compatibility inventory. Static analysis only: never runs Lua code."""
import argparse
import json
from pathlib import Path
import re

DEFAULT_ROOT = Path.home() / ".local/share/triesober/monarca"
PATTERNS = {
    "dynamic_code": r"\b(?:loadstring|load)\s*\(",
    "executor_http": r"(?:\bgame\s*:\s*HttpGet\s*\(|\b(?:http_request|syn\.request|request)\s*\()",
    "executor_env": r"\b(?:getgenv|getrenv|gethui|getgc|getconnections|hookfunction|hookmetamethod)\s*\(",
    "filesystem": r"\b(?:readfile|writefile|isfile|makefolder|listfiles|delfile)\s*\(",
    "executor_misc": r"\b(?:setclipboard|sethiddenproperty|firetouchinterest|fireproximityprompt|queue_on_teleport)\s*\(",
}
NOTE = {
    "dynamic_code": "Dynamic code loading is not an arbitrary-client-script API in standard Roblox experiences.",
    "executor_http": "game:HttpGet and executor request functions cannot be assumed available in a standard LocalScript.",
    "executor_env": "Executor-specific helpers require an execution environment beyond documented Roblox LocalScript capabilities.",
    "filesystem": "Direct local filesystem functions are not part of standard Roblox LocalScript APIs.",
    "executor_misc": "Executor-specific helper APIs may be unavailable in a standard Roblox experience.",
}

def scan(root: Path):
    if not root.is_dir():
        raise FileNotFoundError(f"{root} does not exist. Run 'python triesober.py fetch-monarca' first.")
    result = {key: [] for key in PATTERNS}
    files = sorted([*root.rglob("*.lua"), *root.rglob("*.luau")])
    for path in files:
        relative = str(path.relative_to(root))
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            # Static heuristic: mentions in comments or strings may be false positives.
            for key, expression in PATTERNS.items():
                if re.search(expression, line):
                    result[key].append({"file": relative, "line": lineno})
    return {"files_scanned": len(files), "caveat": "Heuristic pattern matching; review results manually (strings/comments can match).", "api_groups": {k: {"matches": len(v), "locations": v[:30], "note": NOTE[k]} for k, v in result.items()}}

def main():
    parser = argparse.ArgumentParser(description="Inventory Monarca compatibility requirements without running its scripts")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    print(json.dumps(scan(args.root.expanduser()), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
