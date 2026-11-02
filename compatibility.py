#!/usr/bin/env python3
"""Static Monarca compatibility audit. No Roblox process access and no Lua execution."""
import argparse
import json
from pathlib import Path
import re

DEFAULT_ROOT = Path.home() / ".local/share/triesober/monarca"

API_GROUPS = {
    "dynamic_code": {
        "names": ("loadstring",),
        "impact": "requires a nonstandard client-side execution environment",
        "reason": "In regular Roblox experiences loadstring is server-only when enabled.",
    },
    "executor_http": {
        "names": ("game:HttpGet", "http_request", "syn.request"),
        "impact": "requires a nonstandard client-side execution environment",
        "reason": "The Monarca bootstrap downloads and compiles modules at runtime.",
    },
    "executor_environment": {
        "names": ("getgenv", "gethui", "getcustomasset", "getsynasset", "identifyexecutor"),
        "impact": "requires executor APIs or code adaptation",
        "reason": "These names are not available as standard Roblox LocalScript helpers.",
    },
    "executor_filesystem": {
        "names": ("readfile", "writefile", "makefolder", "isfolder", "isfile", "listfiles", "delfile"),
        "impact": "requires executor APIs or alternative persistence",
        "reason": "Local filesystem helpers are not part of standard Roblox LocalScript APIs.",
    },
    "executor_hooks": {
        "names": ("hookfunction", "hookmetamethod", "getgc", "getconnections", "getrawmetatable", "sethiddenproperty"),
        "impact": "requires a privileged environment",
        "reason": "The regular Roblox client API does not expose these executor hooks.",
    },
}

# 'request' alone is intentionally excluded: in Monarca it is also the name
# of ordinary local functions for RemoteEvents and RemoteFunctions.
NAME_PATTERN = re.compile(
    r"(?<![\w.:])(?:"
    + "|".join(re.escape(name) for group in API_GROUPS.values() for name in group["names"])
    + r")(?![\w])"
)

def blank_noncode(source: str) -> str:
    """Keep line numbers while stripping Lua strings and comments.

    Covers single/double quoted strings, -- line comments, and Lua long
    brackets with optional equal signs. This is a heuristic lexer, not a
    complete Luau parser; results must be reviewed before making changes.
    """
    out = list(source)
    i, n = 0, len(source)

    def blank(a, b):
        for j in range(a, b):
            if source[j] != "\n":
                out[j] = " "

    def long_start(at):
        match = re.match(r"\[(=*)\[", source[at:])
        return match.group(1) if match else None

    while i < n:
        if source.startswith("--", i):
            equals = long_start(i + 2)
            if equals is not None:
                start = i + 2
                closer = "]" + equals + "]"
                end = source.find(closer, start + 2 + len(equals))
                j = n if end == -1 else end + len(closer)
            else:
                end = source.find("\n", i)
                j = n if end == -1 else end
            blank(i, j)
            i = j
            continue
        equals = long_start(i) if source[i] == "[" else None
        if equals is not None:
            closer = "]" + equals + "]"
            end = source.find(closer, i + 2 + len(equals))
            j = n if end == -1 else end + len(closer)
            blank(i, j)
            i = j
            continue
        if source[i] in ("'", '"'):
            quote = source[i]
            j = i + 1
            while j < n:
                if source[j] == "\\":
                    j += 2
                elif source[j] == quote:
                    j += 1
                    break
                else:
                    j += 1
            j = min(j, n)
            blank(i, j)
            i = j
            continue
        i += 1
    return "".join(out)

def audit(root: Path) -> dict:
    if not root.is_dir():
        raise FileNotFoundError(
            f"{root} not found. Run 'python triesober.py fetch-monarca' first."
        )
    found = {key: [] for key in API_GROUPS}
    files = sorted(set(root.rglob("*.lua")) | set(root.rglob("*.luau")))
    for path in files:
        clean = blank_noncode(path.read_text(encoding="utf-8", errors="replace"))
        for line_number, line in enumerate(clean.splitlines(), 1):
            for match in NAME_PATTERN.finditer(line):
                name = match.group()
                for group, meta in API_GROUPS.items():
                    if name in meta["names"]:
                        found[group].append({
                            "file": str(path.relative_to(root)),
                            "line": line_number,
                            "api": name,
                        })
                        break
    return {
        "files_scanned": len(files),
        "entrypoint": "Monarca.lua",
        "client_execution": "NOT_AVAILABLE: no Sober Luau execution interface established",
        "caveat": "Heuristic static audit, not a Luau compiler or live executor test.",
        "api_groups": {
            key: {
                "matches": len(found[key]),
                "locations": found[key][:50],
                "impact": meta["impact"],
                "reason": meta["reason"],
            }
            for key, meta in API_GROUPS.items()
        },
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--format", choices=("json", "summary"), default="json")
    args = parser.parse_args()
    result = audit(args.root.expanduser())
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Monarca: {result['files_scanned']} arquivos; entrada: {result['entrypoint']}")
        print("Execução no Sober: NÃO DEMONSTRADA (sem interface Luau confirmada)")
        for group, meta in result["api_groups"].items():
            print(f"- {group}: {meta['matches']} ocorrências; {meta['impact']}")
            for loc in meta["locations"][:4]:
                print(f"    {loc['file']}:{loc['line']} ({loc['api']})")
        print("Aviso: análise estática; não foi realizada execução no cliente.")

if __name__ == "__main__":
    main()
