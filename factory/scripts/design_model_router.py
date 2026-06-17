#!/usr/bin/env python3
"""Role-based model router for the Design Hermes factory.

Defaults to OpenRouter (the wired provider) and falls back across a chain of
models per role. NVIDIA NIM is still supported via --provider nvidia for when a
free NIM tenant is available. This is for cheap internal design passes:
source-truth review, DESIGN.md drafts, system-spec extraction, craft critique,
anti-slop QA, distinctive-move generation.

Key rule baked into routing: the critique/anti-slop roles use a DIFFERENT model
family than the M3 builders (self-bias guard). It never prints API keys.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERMES_HOME = Path.home() / ".hermes"
PROMPTS = ROOT / "factory" / "prompts"

# Provider endpoints + the env vars that hold their keys.
PROVIDERS: dict[str, dict] = {
    "openrouter": {
        "base": "https://openrouter.ai/api/v1",
        "key_envs": ["OPENROUTER_API_KEY", "OPENROUTER_KEY"],
        "extra_headers": {"HTTP-Referer": "https://design-hermes.local/", "X-Title": "Design Hermes Router"},
    },
    "nvidia": {
        "base": "https://integrate.api.nvidia.com/v1",
        "key_envs": ["NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY"],
        "extra_headers": {},
    },
}
DEFAULT_PROVIDER = "openrouter"

# Role -> ordered fallback chain, per provider. OpenRouter slugs verified or
# self-healing (each chain ends in a confirmed-working model). Critic/anti-slop
# roles deliberately lead with a non-MiniMax family.
ROLE_MODELS: dict[str, dict[str, list[str]]] = {
    "openrouter": {
        "design-critic": ["z-ai/glm-5.1", "anthropic/claude-sonnet-4.6", "minimax/minimax-m3"],
        "anti-slop-review": ["z-ai/glm-5.1", "anthropic/claude-sonnet-4.6", "minimax/minimax-m3"],
        "distinctive-move": ["minimax/minimax-m3", "anthropic/claude-sonnet-4.6"],
        "design-md": ["minimax/minimax-m3", "anthropic/claude-sonnet-4.6"],
        "reference-system-spec": ["google/gemini-3-flash-preview", "minimax/minimax-m3"],
        "greenfield-draft": ["minimax/minimax-m3", "anthropic/claude-sonnet-4.6"],
        "final-polish": ["anthropic/claude-sonnet-4.6", "anthropic/claude-opus-4.8"],
        "general": ["minimax/minimax-m3", "anthropic/claude-sonnet-4.6"],
    },
    "nvidia": {
        "design-critic": ["minimaxai/minimax-m3", "moonshotai/kimi-k2.6", "meta/llama-3.3-70b-instruct"],
        "anti-slop-review": ["minimaxai/minimax-m3", "moonshotai/kimi-k2.6", "meta/llama-3.3-70b-instruct"],
        "distinctive-move": ["minimaxai/minimax-m3", "moonshotai/kimi-k2.6"],
        "design-md": ["minimaxai/minimax-m3", "qwen/qwen3.5-122b-a10b", "moonshotai/kimi-k2.6"],
        "reference-system-spec": ["qwen/qwen3.5-122b-a10b", "minimaxai/minimax-m3", "moonshotai/kimi-k2.6"],
        "greenfield-draft": ["minimaxai/minimax-m3", "moonshotai/kimi-k2.6", "qwen/qwen3.5-122b-a10b"],
        "final-polish": ["minimaxai/minimax-m3"],
        "general": ["minimaxai/minimax-m3", "qwen/qwen3.5-122b-a10b", "meta/llama-3.3-70b-instruct"],
    },
}

ROLE_TEMPLATES: dict[str, str] = {
    "design-critic": "minimax-design-critic.md",
    "anti-slop-review": "minimax-anti-slop-review.md",
    "distinctive-move": "minimax-distinctive-move.md",
    "reference-system-spec": "qwen-reference-system-spec.md",
}

SYSTEM_RULES = """You are operating inside the Design Hermes factory.
Follow these non-negotiable rules:
- Use supplied source truth only. Do not invent metrics, testimonials, client logos, certifications, case studies, pricing, or performance results.
- Flag missing proof as missing proof. Do not fill the gap with plausible claims.
- Apply the founder anti-slop gate: no default indigo/purple, no generic purple-blue hero gradients, no emoji feature icons, no wrong display type family, no rounded card with coloured left-border accents, no invented metrics, no filler/lorem copy.
- Aim for 80% proven patterns plus 20% one distinctive brand move.
- Australian English. No contractions. Keep output practical and implementation-ready.
"""


def load_env_file(path: Path) -> list[str]:
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
        if key not in os.environ:
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
    # Pull provider keys from known design profiles if still unset.
    for p in [
        HERMES_HOME / "profiles" / "landing-page-studio" / ".env",
        HERMES_HOME / "profiles" / "business-pack-studio" / ".env",
        HERMES_HOME / "profiles" / "designer" / ".env",
    ]:
        need = not (os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY"))
        if need and load_env_file(p):
            sources.append(str(p))
    return sources


def provider_key(provider: str) -> str:
    cfg = PROVIDERS[provider]
    for env in cfg["key_envs"]:
        v = os.getenv(env)
        if v and v.strip():
            return v.strip()
    raise SystemExit(f"Missing API key for provider '{provider}'. Set one of: {', '.join(cfg['key_envs'])}")


def read_text(path: str, *, max_chars: int) -> str:
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = ROOT / p
    return p.read_text(errors="replace")[:max_chars]


def load_template(role: str, explicit: str | None) -> str:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_absolute():
            path = ROOT / explicit
        return path.read_text(errors="replace")
    name = ROLE_TEMPLATES.get(role)
    if not name:
        return ""
    path = PROMPTS / name
    return path.read_text(errors="replace") if path.exists() else ""


def build_prompt(args: argparse.Namespace) -> str:
    parts: list[str] = []
    template = load_template(args.role, args.template)
    if template:
        parts.append("# Role Template\n" + template.strip())
    if args.prompt:
        parts.append("# User Task\n" + args.prompt.strip())
    for ctx in args.context_file or []:
        text = read_text(ctx, max_chars=args.max_context_chars)
        parts.append(f"# Context file: {ctx}\n```\n{text}\n```")
    if not parts:
        raise SystemExit("Provide --prompt, --context-file, or a role with a template")
    return "\n\n".join(parts)


def chat_once(provider: str, model: str, prompt: str, *, max_tokens: int, temperature: float, timeout: int) -> dict:
    cfg = PROVIDERS[provider]
    key = provider_key(provider)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"}
    headers.update(cfg.get("extra_headers", {}))
    req = urllib.request.Request(
        f"{cfg['base']}/chat/completions",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        msg = (data.get("choices") or [{}])[0].get("message", {})
        return {
            "ok": bool(msg.get("content")),
            "provider": provider,
            "model": model,
            "seconds": round(time.time() - started, 2),
            "content": msg.get("content"),
            "has_reasoning_content": bool(msg.get("reasoning_content")),
            "usage": data.get("usage"),
        }
    except urllib.error.HTTPError as e:
        return {"ok": False, "provider": provider, "model": model, "seconds": round(time.time() - started, 2), "status": e.code, "error": e.read().decode(errors="ignore")[:1200]}
    except Exception as e:
        return {"ok": False, "provider": provider, "model": model, "seconds": round(time.time() - started, 2), "error": f"{type(e).__name__}: {e}"}


def route(args: argparse.Namespace) -> dict:
    prompt = build_prompt(args)
    role_map = ROLE_MODELS[args.provider]
    models = [args.model] if args.model else role_map.get(args.role, role_map["general"])
    attempts = []
    for model in models:
        result = chat_once(args.provider, model, prompt, max_tokens=args.max_tokens, temperature=args.temperature, timeout=args.timeout)
        attempts.append({k: v for k, v in result.items() if k != "content"})
        if result.get("ok") and result.get("content"):
            result["role"] = args.role
            result["attempts"] = attempts
            return result
        if args.no_fallback:
            result["role"] = args.role
            result["attempts"] = attempts
            return result
    return {"ok": False, "role": args.role, "provider": args.provider, "content": None, "attempts": attempts, "error": "All route models failed or returned empty content"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Design Hermes role-based model router (OpenRouter default)")
    ap.add_argument("--role", default="general", choices=sorted(ROLE_MODELS[DEFAULT_PROVIDER]))
    ap.add_argument("--provider", default=DEFAULT_PROVIDER, choices=sorted(PROVIDERS))
    ap.add_argument("--model", help="Override route model (uses --provider for endpoint/key)")
    ap.add_argument("--template", help="Override prompt template path")
    ap.add_argument("--prompt", help="Task prompt")
    ap.add_argument("--context-file", action="append", help="Context file to append; may repeat")
    ap.add_argument("--max-context-chars", type=int, default=20000)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--profile", help="Optional Hermes profile env to load")
    ap.add_argument("--out", help="Write content to markdown/text file")
    ap.add_argument("--json-out", help="Write full JSON result to file")
    ap.add_argument("--no-fallback", action="store_true")
    args = ap.parse_args()

    sources = load_env(args.profile)
    result = route(args)
    result["env_sources_checked"] = sources

    if args.out and result.get("content"):
        out = Path(args.out).expanduser()
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result["content"].rstrip() + "\n")
        result["out"] = str(out)
    if args.json_out:
        jout = Path(args.json_out).expanduser()
        if not jout.is_absolute():
            jout = ROOT / jout
        jout.parent.mkdir(parents=True, exist_ok=True)
        jout.write_text(json.dumps(result, indent=2) + "\n")
        result["json_out"] = str(jout)

    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
