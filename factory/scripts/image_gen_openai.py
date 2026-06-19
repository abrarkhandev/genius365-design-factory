#!/usr/bin/env python3
"""image-asset-lab — OpenAI image executor (GPT Image 2).

Generate an image via the OpenAI Images API (model gpt-image-2) and save it.
Uses the team's existing OPENAI_API_KEY — no Cloudflare or OpenRouter needed.
Real, load-bearing text always stays HTML/SVG; this lane is for backgrounds and
illustration only. Never prints the key.

  uv run --no-project python factory/scripts/image_gen_openai.py \
    --prompt "abstract on-brand background, no text, no logos" \
    --out assets/bg.png --size 1536x1024
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERMES = Path.home() / ".hermes"
API = "https://api.openai.com/v1/images/generations"
# gpt-image sizes: square, landscape, portrait, or let the model choose.
SIZES = {"1024x1024", "1536x1024", "1024x1536", "auto"}


def load_env() -> None:
    for p in [ROOT / ".env", ROOT / ".env.local", HERMES / ".env"]:
        if not p.exists():
            continue
        for line in p.read_text(errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def api_key() -> str:
    k = os.getenv("OPENAI_API_KEY") or ""
    if not k.strip():
        raise SystemExit("Missing OPENAI_API_KEY (the OpenAI key you already use with Hermes)")
    return k.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="OpenAI image generation (GPT Image 2)")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, help="output image path")
    ap.add_argument("--model", default="gpt-image-2")
    ap.add_argument("--size", default="1536x1024",
                    help="1024x1024 | 1536x1024 (landscape) | 1024x1536 (portrait) | auto")
    ap.add_argument("--quality", default="high", help="low | medium | high | auto")
    ap.add_argument("--timeout", type=int, default=240)
    a = ap.parse_args()

    load_env()
    body = {"model": a.model, "prompt": a.prompt, "size": a.size, "quality": a.quality, "n": 1}
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")

    item = (data.get("data") or [{}])[0]
    b64 = item.get("b64_json")
    if b64:
        img = base64.b64decode(b64)
    elif item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=a.timeout) as r:
            img = r.read()
    else:
        raise SystemExit("No image in response: " + json.dumps(data)[:300])

    if img[:4] == b"\x89PNG":
        fmt = "png"
    elif img[:3] == b"\xff\xd8\xff":
        fmt = "jpeg"
    elif img[:4] == b"RIFF":
        fmt = "webp"
    else:
        fmt = "bin"
    out = Path(a.out)
    want = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}.get(fmt)
    if want and out.suffix.lower() not in ({want, ".jpeg"} if fmt == "jpeg" else {want}):
        out = out.with_suffix(want)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    print(json.dumps({"ok": True, "out": str(out), "bytes": out.stat().st_size,
                      "model": a.model, "size": a.size, "format": fmt}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
