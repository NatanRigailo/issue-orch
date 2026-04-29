# CLAUDE.md — `issue-orch`

> Gerado a partir do template `git/_templates/CLAUDE-projeto.md`
> Este agente roda via **Claude Code** e tem acesso ao filesystem e ferramentas de terminal.

---

## O que é este projeto

Serviço background que roda diariamente, lista as issues abertas de múltiplos repositórios GitHub e spawna um agente Claude Code para implementar a de maior prioridade — abrindo o PR automaticamente.

**Por que existe:** demonstra agentic workflows, automação de desenvolvimento, e orquestração de processos — tudo self-hosted, sem custo.

**Competências DevOps demonstradas:**
- Automação de workflows com agentes autônomos
- Agendamento e controle de processos (APScheduler)
- Integração com GitHub API via gh CLI
- Container non-root com Docker multi-stage
- CI/CD com pipeline multi-stage no GitHub Actions
- Logs estruturados em JSON

---

## Stack da aplicação

- **Linguagem/runtime:** Python 3.12
- **Scheduler:** APScheduler 3.x (BlockingScheduler)
- **Banco de dados:** nenhum — stateless, logs em stdout
- **Agente:** `claude -p` via subprocess

---

## Stack DevOps

- **CI/CD:** GitHub Actions
  - Stages: lint → hadolint → SAST (bandit) → build → scan (trivy) → auto-tag → publish GHCR
- **Registry:** GHCR (`ghcr.io/natanrigailo/issue-orch`)
- **Qualidade:** SonarCloud
- **Scan:** Trivy
- **Dependências:** Dependabot
- **Observabilidade:** logs estruturados JSON (dashboard previsto na v0.4.0)

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `REPOS` | — | Paths locais dos repos, separados por vírgula |
| `SCHEDULE` | `0 9 * * 1-5` | Cron expression do scheduler |
| `MAX_ISSUES_PER_RUN` | `1` | Máximo de issues por ciclo |
| `CLAUDE_TIMEOUT` | `1800` | Timeout do subprocess claude em segundos |
| `LOG_LEVEL` | `INFO` | Nível de log |

---

## Estrutura do projeto

```
issue-orch/
├── app/
│   ├── orchestrator.py     # listagem, priorização, spawn do agente
│   └── scheduler.py        # APScheduler + leitura de config
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # lint, SAST, build, scan
│   │   └── release.yml     # auto-tag, publish GHCR
│   └── dependabot.yml
├── deploy/
│   └── docker-compose.yml
├── orchestrator-prompt.md  # prompt base injetado no claude -p
├── Dockerfile
├── main.py
└── requirements.txt
```

---

## Roadmap

### v0.1.0 — MVP
- [ ] Core scheduler com APScheduler
- [ ] Listagem e priorização de issues via gh CLI
- [ ] Runner do subprocess claude com timeout
- [ ] Suporte multi-repo via REPOS env var
- [ ] Dockerfile non-root + docker-compose

### v0.2.0 — Robustez
- [ ] Filtro por label `agent-ready`
- [ ] Log de histórico de execuções em JSON
- [ ] Retry em falha do subprocess
- [ ] Prompt configurável por repo

### v0.3.0 — CI/CD
- [ ] GitHub Actions completo
- [ ] Auto-tag semver no merge para main
- [ ] Publish GHCR
- [ ] SonarCloud quality gate

### v0.4.0 — Observabilidade
- [ ] Endpoints `/healthz` e `/status`
- [ ] Dashboard web com histórico
- [ ] Notificação via webhook ao abrir PR

---

## Estado atual

**Versão:** v0.1.0 — em desenvolvimento

**O que já existe:**
- Estrutura base do projeto
- `orchestrator.py` com listagem, priorização e runner
- `scheduler.py` com APScheduler
- Dockerfile non-root multi-stage
- CI/CD workflows
- `orchestrator-prompt.md` base

**Próximo passo:**
- Criar issues no GitHub e começar a implementar v0.1.0

---

## Papel deste agente

Este agente é um **executor** — não apenas consultor.

### Fluxo de trabalho padrão

1. **Discussão** — alinhamos o que será feito
2. **Planejamento** — o agente propõe issues, aguarda aprovação
3. **Execução** — cria branch, implementa, abre PR linkando a issue
4. **Revisão** — eu reviso e faço o merge. O agente nunca faz merge.

### O que o agente faz autonomamente
- Ler estado do repositório
- Criar e trocar branches
- Escrever e editar arquivos
- Commits atômicos com Conventional Commits
- Criar issues e abrir PRs via gh CLI
- Rodar lint e build localmente antes do PR

### O que o agente nunca faz
- Merge de PRs
- Push direto em `main`
- Deletar branches remotas sem confirmação

---

## Convenções do repositório

- **Branches:** `feat/descricao-curta`, `fix/descricao-curta`, `chore/descricao-curta`
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`)
- **PRs:** título no formato Conventional Commits, `Closes #N` no body
- **Labels:** `feature`, `bug`, `ci`, `docs`, `security`, `infra`

---

## Referências

- Padrões gerais: `../CLAUDE.md`
- Projeto de referência: `../mfa-app`
