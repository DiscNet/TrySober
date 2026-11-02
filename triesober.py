#!/usr/bin/env python3
"""TrySober: diagnóstico e carregamento local (não execução) de Luau."""
import argparse
import json
import pathlib
import subprocess
import sys
import urllib.request

APP_ID = "org.vinegarhq.Sober"
REPO = "DiscNet/Monarca"
DEST = pathlib.Path.home() / ".local" / "share" / "triesober" / "monarca"

def run_command(*args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=12, check=False)
        return {"available": p.returncode == 0, "output": p.stdout.strip(), "error": p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"available": False, "error": str(e)}

def status():
    flatpak = run_command("flatpak", "info", APP_ID)
    running = run_command("flatpak", "ps", "--columns=application")
    installed = flatpak["available"]
    active = running["available"] and APP_ID in running.get("output", "").splitlines()
    print(json.dumps({"sober_installed": installed, "sober_running": active, "flatpak_info": flatpak.get("error", "") if not installed else ""}, indent=2))

def request_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TrySober/0.1", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def fetch_monarca():
    info = request_json(f"https://api.github.com/repos/{REPO}")
    branch = info["default_branch"]
    tree = request_json(f"https://api.github.com/repos/{REPO}/git/trees/{branch}?recursive=1")
    files = [item["path"] for item in tree.get("tree", []) if item.get("type") == "blob" and item["path"].lower().endswith((".lua", ".luau"))]
    DEST.mkdir(parents=True, exist_ok=True)
    for path in files:
        target = (DEST / path).resolve()
        if not target.is_relative_to(DEST.resolve()):
            raise ValueError("Caminho de arquivo inseguro")
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://raw.githubusercontent.com/{REPO}/{branch}/{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "TrySober/0.1"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError(f"Arquivo muito grande: {path}")
        target.write_bytes(data)
    print(f"{len(files)} arquivos Luau/Lua baixados para {DEST} (não executados)")

def open_monarca():
    if not DEST.exists():
        print("Ainda não há arquivos. Execute: python triesober.py fetch-monarca")
        return
    paths = sorted(list(DEST.rglob("*.lua")) + list(DEST.rglob("*.luau")))
    if not paths:
        print("Nenhum arquivo Lua/Luau encontrado.")
        return
    print("Arquivos disponíveis:")
    for path in paths:
        print(" -", path.relative_to(DEST))

def main():
    parser = argparse.ArgumentParser(description="TrySober - diagnóstico local para Sober")
    parser.add_argument("action", choices=("status", "fetch-monarca", "open-monarca"))
    args = parser.parse_args()
    try:
        {"status": status, "fetch-monarca": fetch_monarca, "open-monarca": open_monarca}[args.action]()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
