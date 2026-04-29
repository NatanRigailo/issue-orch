# issue-orch

[![CI](https://github.com/NatanRigailo/issue-orch/actions/workflows/ci.yml/badge.svg)](https://github.com/NatanRigailo/issue-orch/actions/workflows/ci.yml)
[![GHCR](https://ghcr-badge.egpl.dev/natanrigailo/issue-orch/latest_tag?color=%2344cc11&label=ghcr)](https://github.com/NatanRigailo/issue-orch/pkgs/container/issue-orch)

Autonomous issue orchestrator — a background service that runs daily, picks the highest-priority open issue from your GitHub repositories, and spawns a Claude Code agent to implement it and open a PR.

## Quick start

```bash
docker run -d \
  -e REPOS=/repos/my-app \
  -e SCHEDULE="0 9 * * 1-5" \
  -v $HOME/git:/repos:ro \
  -v $HOME/.config/gh:/home/appuser/.config/gh:ro \
  -v $HOME/.claude:/home/appuser/.claude:ro \
  ghcr.io/natanrigailo/issue-orch:latest
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `REPOS` | — | Comma-separated absolute paths to local repo clones |
| `SCHEDULE` | `0 9 * * 1-5` | Cron expression for the orchestration cycle |
| `MAX_ISSUES_PER_RUN` | `1` | Max issues to implement per cycle |
| `CLAUDE_TIMEOUT` | `1800` | Timeout in seconds for the claude subprocess |
| `LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |

## How it works

```
Scheduler (cron)
      ↓
  For each repo:
    - List open issues via gh CLI
    - Prioritize: bug > feature, milestone proximity, detail quality
    - Skip issues without enough description
    - Spawn: claude -p "$(cat orchestrator-prompt.md)" in the repo dir
      ↓
  Claude Code agent:
    - Reads the repo's CLAUDE.md
    - Creates a branch
    - Implements the issue
    - Opens a PR + comments on the issue
```

## Prioritization criteria

1. `bug` label before `feature`
2. Issues with `agent-ready` label take precedence (if any exist)
3. Issues linked to the nearest milestone first
4. More comments = higher perceived impact
5. Issues without sufficient description are skipped

## Local development

```bash
cp .env.example .env
# edit .env with your repo paths

pip install -r requirements.txt
make run
```

## Roadmap

### v0.1.0 — MVP
- [ ] Core scheduler with APScheduler
- [ ] Issue listing and prioritization via gh CLI
- [ ] Claude subprocess runner with timeout
- [ ] Multi-repo support via REPOS env var
- [ ] Dockerfile non-root + docker-compose

### v0.2.0 — Robustness
- [ ] `agent-ready` label filter
- [ ] Execution history log (JSON)
- [ ] Retry on subprocess failure
- [ ] Configurable per-repo orchestrator prompt

### v0.3.0 — CI/CD
- [ ] GitHub Actions: lint → SAST → build → scan
- [ ] Auto-tag semver on merge to main
- [ ] Publish to GHCR
- [ ] SonarCloud quality gate

### v0.4.0 — Observability
- [ ] `/healthz` and `/status` endpoints
- [ ] Web dashboard with execution history
- [ ] Webhook notification on PR open
