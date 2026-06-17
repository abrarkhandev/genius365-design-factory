#!/usr/bin/env bash
# Install (first run) or update (later) every design-factory profile from this repo.
# Re-run after every `git pull` to fetch the latest souls + skills.
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"

PROFILES=(landing-page-studio business-pack-studio linkedin-studio email-newsletter-studio print-editorial-studio image-prompter image-asset-lab intake-strategist design-director design-qa)

for p in "${PROFILES[@]}"; do
  if hermes profile info "$p" >/dev/null 2>&1; then
    echo "==> updating $p"
    hermes profile update "$p" -y || true
  else
    echo "==> installing $p"
    hermes profile install "$REPO/profiles/$p" --alias -y
  fi
done

echo ""
echo "Done. If you have not yet: copy .env.example to ~/.hermes/.env and paste the keys."
echo "Recommended models + the shadcn MCP are documented in README.md (one-time setup)."
