#!/usr/bin/env python3
"""Smoke-test NVIDIA NIM chat models for the Design Hermes factory.

Loads NVIDIA_API_KEY from project env files, Hermes default env, or a named
Hermes profile env. Never prints secrets.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERMES_HOME = Path.home() / ".hermes"
API_BASE = "https://integrate.api.nvidia.com/v1"


def load_env_file(path: Path, *, override: bool = False) -> list[str]:
    loaded: list[str] = []
    if not path.exists():
        return loaded
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, val = s.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if override or key not in os.environ:
            os.environ[key] = val
            loaded.append(key)
    return loaded


def load_env(profile: str | None = None) -> list[str]:
    sources: list[str] = []
    for path in [ROOT / ".env", ROOT / ".env.local", HERMES_HOME / ".env"]:
        if load_env_file(path):
            sources.append(str(path))
    if profile:
        p = HERMES_HOME / "profiles" / profile / ".env"
        if load_env_file(p):
            sources.append(str(p))
    # Profiles in this project already carry NVIDIA_API_KEY; load as fallback only.
    for p in [
        HERMES_HOME / "profiles" / "business-pack-studio" / ".env",
        HERMES_HOME / "profiles" / "landing-page-studio" / ".env",
        HERMES_HOME / "profiles" / "designer" / ".env",
    ]:
        if "NVIDIA_API_KEY" not in os.environ and load_env_file(p):
            sources.append(str(p))
    return sources


def nvidia_key() -> str:
    key = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY") or ""
    if not key.strip():
        raise SystemExit("Missing NVIDIA_API_KEY / NVIDIA_NIM_API_KEY in project or Hermes env files")
    return key.strip()


def request_json(path: str, payload: dict | None = None, timeout: int = 90) -> dict:
    key = nvidia_key()
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    data = None
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
        method = "POST"
    req = urllib.request.Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:1200]
        return {"ok": False, "status": e.code, "error": body}


def list_models(pattern: str | None = None) -> dict:
    data = request_json("/models", timeout=60)
    models = data.get("data", []) if isinstance(data, dict) else []
    ids = [m.get("id") for m in models if isinstance(m, dict) and m.get("id")]
    if pattern:
        rx = re.compile(pattern, re.I)
        ids = [m for m in ids if rx.search(m)]
    return {"ok": True, "count": len(ids), "models": ids}


def chat(model: str, prompt: str, *, max_tokens: int, temperature: float, timeout: int) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    started = time.time()
    data = request_json("/chat/completions", payload, timeout=timeout)
    elapsed = round(time.time() - started, 2)
    if data.get("ok") is False:
        data["seconds"] = elapsed
        data["model"] = model
        return data
    msg = (data.get("choices") or [{}])[0].get("message", {})
    return {
        "ok": bool(msg.get("content")),
        "model": model,
        "seconds": elapsed,
        "content": msg.get("content"),
        "has_reasoning_content": bool(msg.get("reasoning_content")),
        "usage": data.get("usage"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="NVIDIA NIM smoke-test for Design Hermes")
    ap.add_argument("--profile", help="Optional Hermes profile env to load first")
    ap.add_argument("--model", default="minimaxai/minimax-m3")
    ap.add_argument("--prompt", default="Reply with exactly: OK NVIDIA NIM")
    ap.add_argument("--max-tokens", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--filter", default="minimax|qwen|kimi|llama|nemotron|deepseek")
    ap.add_argument("--out", help="Optional JSON output path")
    args = ap.parse_args()

    sources = load_env(args.profile)
    if args.list_models:
        result = list_models(args.filter)
    else:
        result = chat(
            args.model,
            args.prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
        )
    result["env_sources_checked"] = [str(Path(s).expanduser()) for s in sources]
    if args.out:
        out = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
