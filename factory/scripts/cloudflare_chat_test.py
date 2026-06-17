#!/usr/bin/env python3
"""Smoke-test Cloudflare Kimi K2.6 for the design factory.

Loads credentials from .env, then .env.local. Accepts either CLOUDFLARE_API_TOKEN
or CLOUDFLARE_API_KEY. Does not print secrets.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_env() -> str | None:
    for name in [".env", ".env.local"]:
        path = ROOT / name
        if not path.exists():
            continue
        for line in path.read_text(errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        return name
    return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="@cf/moonshotai/kimi-k2.6")
    parser.add_argument("--prompt", default="Reply with one short sentence confirming Cloudflare Kimi is ready for the BIP and landing page factory.")
    parser.add_argument("--max-tokens", type=int, default=512, help="Kimi may emit reasoning_content before final content; keep this high enough for a smoke test.")
    parser.add_argument("--out", default=".hermes/extracted/cloudflare-tests/kimi-smoke-test.json")
    args = parser.parse_args()

    loaded = load_env()
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = (os.getenv("CLOUDFLARE_API_TOKEN") or os.getenv("CLOUDFLARE_API_KEY") or "").strip()
    if not account_id or not token:
        print(json.dumps({"ok": False, "error": "Missing CLOUDFLARE_ACCOUNT_ID or token", "loaded_env": loaded}, indent=2))
        return 2

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions"
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
        "max_tokens": args.max_tokens,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        msg = data.get("choices", [{}])[0].get("message", {})
        result = {
            "ok": True,
            "loaded_env": loaded,
            "model": args.model,
            "content": msg.get("content"),
            "has_reasoning_content": bool(msg.get("reasoning_content")),
            "usage": data.get("usage"),
        }
    except urllib.error.HTTPError as e:
        result = {"ok": False, "status": e.code, "error": e.read().decode(errors="ignore")[:1000], "loaded_env": loaded, "model": args.model}
    except Exception as e:
        result = {"ok": False, "error": f"{type(e).__name__}: {e}", "loaded_env": loaded, "model": args.model}

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n")
    printable = dict(result)
    if printable.get("content"):
        printable["content"] = printable["content"][:240]
    print(json.dumps(printable, indent=2))
    return 0 if result.get("ok") else 1

if __name__ == "__main__":
    raise SystemExit(main())
