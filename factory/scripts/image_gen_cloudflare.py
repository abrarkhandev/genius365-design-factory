#!/usr/bin/env python3
"""image-asset-lab — Cloudflare Workers AI image executor (prototype lane).

Free/cheap prototype lane, no new key. Default is FLUX.2 [dev] (quality,
multi-reference capable, multipart schema); flux-1-schnell remains the legacy
fast 8-step model (JSON schema). For LICENSED delivery (Nano Banana Pro /
FLUX.2 [pro]) use the delivery executor instead.

Reads CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_KEY from env or the profile .env.
Never prints the key.

Models (pass via --model):
  @cf/black-forest-labs/flux-2-dev      quality, multipart, optional --reference (DEFAULT)
  @cf/black-forest-labs/flux-1-schnell  legacy 8-step prototype (JSON)

FLUX.2 [dev] takes prompt/steps/width/height as multipart form fields and an
optional reference image (--reference) for on-brand consistency. schnell takes
a JSON {prompt, steps} body.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERMES = Path.home() / ".hermes"
DEFAULT_MODEL = "@cf/black-forest-labs/flux-2-dev"
BOUNDARY = "----DesignFactoryBoundaryT9c1f2a4"


def load_env() -> None:
    for p in [ROOT / ".env", ROOT / ".env.local", HERMES / ".env",
              HERMES / "profiles" / "landing-page-studio" / ".env"]:
        if not p.exists():
            continue
        for line in p.read_text(errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def steps_for(model: str, requested: int) -> int:
    """schnell is a distilled 8-step model; flux-2-dev converges higher."""
    is_schnell = "schnell" in model
    cap = 8 if is_schnell else 50
    default = 8 if is_schnell else 28
    n = requested if requested > 0 else default
    return max(1, min(n, cap))


def encode_multipart(fields: dict, files: dict | None = None) -> tuple[bytes, str]:
    """Minimal multipart/form-data encoder (stdlib only). files maps
    field -> (filename, bytes, content_type)."""
    parts: list[bytes] = []
    for k, v in fields.items():
        parts.append(f"--{BOUNDARY}".encode())
        parts.append(f'Content-Disposition: form-data; name="{k}"'.encode())
        parts.append(b"")
        parts.append(str(v).encode())
    for k, (fname, fbytes, ctype) in (files or {}).items():
        parts.append(f"--{BOUNDARY}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{k}"; filename="{fname}"'.encode())
        parts.append(f"Content-Type: {ctype}".encode())
        parts.append(b"")
        parts.append(fbytes)
    parts.append(f"--{BOUNDARY}--".encode())
    parts.append(b"")
    return b"\r\n".join(parts), f"multipart/form-data; boundary={BOUNDARY}"


def extract_image_bytes(raw: bytes) -> bytes:
    """Cloudflare FLUX returns JSON {"result": {"image": "<base64>"}} (and some
    variants put image at top level); some models return raw image bytes."""
    try:
        data = json.loads(raw.decode())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return raw  # already a binary image
    b64 = None
    result = data.get("result")
    if isinstance(result, dict):
        b64 = result.get("image")
    elif isinstance(result, str):
        b64 = result
    if not b64:
        b64 = data.get("image")  # top-level fallback
    if not b64:
        raise SystemExit("No image in response: " + json.dumps(data)[:400])
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    try:
        return base64.b64decode(b64)
    except binascii.Error as e:
        raise SystemExit(f"Bad base64 image: {e}")


def post(url: str, key: str, body: bytes, content_type: str, timeout: int) -> bytes:
    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": content_type},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def build_request(model: str, prompt: str, steps: int, width: int, height: int,
                  reference: str | None) -> tuple[bytes, str]:
    if "flux-2" in model:  # multipart schema
        fields = {"prompt": prompt, "steps": steps, "width": width, "height": height}
        files = None
        if reference:
            rp = Path(reference)
            ctype = "image/jpeg" if rp.suffix.lower() in (".jpg", ".jpeg") else "image/png"
            files = {"image": (rp.name, rp.read_bytes(), ctype)}
        return encode_multipart(fields, files)
    # schnell JSON schema
    body = {"prompt": prompt, "steps": steps}
    return json.dumps(body).encode(), "application/json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloudflare Workers AI image generation (prototype lane)")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, help="output image path (.png)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--steps", type=int, default=0, help="0 = model default")
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--reference", default=None, help="reference image for on-brand consistency (flux-2 only)")
    ap.add_argument("--timeout", type=int, default=180)
    a = ap.parse_args()

    load_env()
    acct = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    key = os.getenv("CLOUDFLARE_API_KEY") or os.getenv("CLOUDFLARE_API_TOKEN")
    if not acct or not key:
        raise SystemExit("Missing CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_KEY")

    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{a.model}"
    steps = steps_for(a.model, a.steps)
    body, ctype = build_request(a.model, a.prompt, steps, a.width, a.height, a.reference)

    try:
        raw = post(url, key, body, ctype, a.timeout)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")

    img = extract_image_bytes(raw)
    if img[:4] == b"\x89PNG":
        fmt = "png"
    elif img[:3] == b"\xff\xd8\xff":
        fmt = "jpeg"
    else:
        fmt = "bin"
    out = Path(a.out)
    # FLUX.2 returns JPEG; keep the file extension honest to its content.
    if fmt == "jpeg" and out.suffix.lower() not in (".jpg", ".jpeg"):
        out = out.with_suffix(".jpg")
    elif fmt == "png" and out.suffix.lower() != ".png":
        out = out.with_suffix(".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    result = {"ok": True, "out": str(out), "bytes": out.stat().st_size,
              "model": a.model, "steps": steps, "format": fmt}
    if reference := a.reference:
        result["reference"] = reference
    if fmt == "bin" or out.stat().st_size < 1000:
        result["warn"] = "output may not be a valid image"
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
