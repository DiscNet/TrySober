#!/usr/bin/env python3
"""Diagnóstico não invasivo do Sober em Flatpak."""
import json
import subprocess

APP = "org.vinegarhq.Sober"

def command(*args):
    try:
        p = subprocess.run(args, text=True, capture_output=True, timeout=10)
        return {"ok": p.returncode == 0, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "stdout": "", "stderr": str(e)}

def main():
    installed = command("flatpak", "info", APP)
    version = command("flatpak", "info", "--show-version", APP)
    running = command("flatpak", "ps", "--columns=application,instance,pid")
    perms = command("flatpak", "info", "--show-permissions", APP)
    instances = []
    if running["ok"]:
        for line in running["stdout"].splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[0] == APP:
                instances.append({"instance": fields[1], "pid": fields[2]})
    result = {
        "app_id": APP,
        "installed": installed["ok"],
        "version": version["stdout"] if version["ok"] else None,
        "running": bool(instances),
        "instances": instances,
        "flatpak_permissions": perms["stdout"] if perms["ok"] else None,
        "diagnostic_errors": {
            name: result["stderr"] for name, result in {
                "installed": installed, "version": version, "processes": running, "permissions": perms
            }.items() if not result["ok"]
        },
        "luau_execution_interface": "not established",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
