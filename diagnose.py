#!/usr/bin/env python3
"""Diagnóstico não invasivo do Sober em Flatpak."""
import json
import subprocess

APP = "org.vinegarhq.Sober"

def command(*args):
    try:
        p = subprocess.run(args, text=True, capture_output=True, timeout=10)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None

def main():
    info = command("flatpak", "info", "--show-version", APP)
    ps = command("flatpak", "ps", "--columns=instance,application,pid")
    perms = command("flatpak", "info", "--show-permissions", APP)
    instances = []
    if ps:
        for line in ps.splitlines()[1:]:
            fields = line.split()
            if len(fields) >= 3 and fields[1] == APP:
                instances.append({"instance": fields[0], "pid": fields[2]})
    result = {
        "app_id": APP,
        "version": info,
        "running": bool(instances),
        "instances": instances,
        "flatpak_permissions": perms,
        "luau_execution_interface": "not established",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
