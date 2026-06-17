# Genius365 Design Factory

The shared Hermes design factory: specialist profiles (souls + skills), the design
constitution, and the production/QA scripts. Distributed as **Hermes profile
distributions** so the whole team installs once and pulls updates with one command.

## What is in here
- `profiles/<name>/` — each design profile as an installable distribution
  (`SOUL.md`, `references/DESIGN-OS.md`, its SOP skill, `distribution.yaml`).
- `factory/scripts/` — the generation + deterministic-QA scripts.
- `souls/` — the constitution (`DESIGN-OS.md`) and the source souls.
- `plan/` — the master plan and the team walkthrough.
- `sync.sh` — installs/updates every profile.
- `.env.example` — the keys you need (filled locally, never committed).

## Secrets — read first
**No API keys are in this repo.** Keys live only in your local `~/.hermes/.env`,
which `hermes profile update` never touches. Get the values from the team
password manager.

```bash
cp .env.example ~/.hermes/.env   # then paste the real keys
```

## First-time setup (each member, ~5 min)
1. Install Hermes (see hermes-agent.nousresearch.com) and confirm `hermes --version` (>= 0.16.0).
2. Clone this repo, then:
   ```bash
   ./sync.sh                      # installs all profiles + aliases
   cp .env.example ~/.hermes/.env # paste keys from the password manager
   ```
3. (One-time, recommended settings — not shipped, to keep secrets out of git):
   ```bash
   # point the web builder at the validated model
   #   edit ~/.hermes/profiles/landing-page-studio/config.yaml -> model.default: z-ai/glm-5.2
   # add the shadcn component MCP to the web + reference profiles
   landing-page-studio mcp add shadcn --command npx --args -y shadcn@latest mcp
   intake-strategist  mcp add shadcn --command npx --args -y shadcn@latest mcp
   ```

## Getting updates (the streamlined flow)
When the maintainer pushes new souls/skills:
```bash
git pull
./sync.sh        # runs `hermes profile update` for every profile
```
Your keys, memories and sessions are preserved — only the souls/skills update.

## Using a profile
```bash
landing-page-studio -z "build a landing page for ..."   # one-shot
landing-page-studio chat                                  # interactive
# deliver-grade override: append  -m anthropic/claude-opus-4.8 --provider openrouter
```

## Maintainer — publishing an update
1. Make the change in your live profile (e.g. edit a SOUL or skill).
2. Re-run the repo build (or copy the changed file into `profiles/<name>/`).
3. Bump `version:` in the changed `profiles/<name>/distribution.yaml`.
4. `git add . && git commit -m "vX.Y.Z: <what changed>" && git push`.
5. Team runs `git pull && ./sync.sh`.
