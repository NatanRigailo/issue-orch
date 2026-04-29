import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    number: int
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
    comments: int = 0
    milestone: str | None = None


def list_issues(repo_path: str) -> list[Issue]:
    result = subprocess.run(
        [
            "gh", "issue", "list",
            "--json", "number,title,body,labels,comments,milestone",
            "--limit", "50",
            "--state", "open",
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    raw = json.loads(result.stdout)
    issues = []
    for item in raw:
        labels = [lbl["name"] for lbl in item.get("labels", [])]
        milestone = item.get("milestone") or {}
        issues.append(Issue(
            number=item["number"],
            title=item["title"],
            body=item.get("body") or "",
            labels=labels,
            comments=len(item.get("comments", [])),
            milestone=milestone.get("title") if milestone else None,
        ))
    return issues


def prioritize(issues: list[Issue]) -> list[Issue]:
    agent_ready = [i for i in issues if "agent-ready" in i.labels]
    pool = agent_ready if agent_ready else issues

    def sort_key(issue: Issue):
        is_bug = "bug" in issue.labels
        has_body = len(issue.body.strip()) > 50
        return (not is_bug, not has_body, -issue.comments)

    eligible = [i for i in pool if len(i.body.strip()) > 50]
    return sorted(eligible, key=sort_key)


def build_prompt(repo_path: str, issue: Issue) -> str:
    prompt_file = Path(repo_path) / "orchestrator-prompt.md"
    if prompt_file.exists():
        template = prompt_file.read_text()
    else:
        template = _default_prompt()

    return template.format(
        issue_number=issue.number,
        issue_title=issue.title,
        issue_body=issue.body,
    )


def _default_prompt() -> str:
    return """You are an autonomous development agent. Your task is to implement a single GitHub issue.

Issue #{issue_number}: {issue_title}

Description:
{issue_body}

Instructions:
1. Read the CLAUDE.md in this repository to understand the project conventions
2. Explore the codebase to understand the context around this issue
3. Create a branch: feat/issue-{issue_number}
4. Implement the solution with atomic commits using Conventional Commits
5. Run available lint/test commands to validate before opening the PR
6. Open a PR: gh pr create --title "feat: {issue_title}" --body "Closes #{issue_number}"
7. Comment on the issue summarizing what was done: gh issue comment {issue_number} --body "..."
8. Stop. Do not pick another issue.
"""


def run_agent(repo_path: str, issue: Issue, timeout: int) -> bool:
    prompt = build_prompt(repo_path, issue)
    logger.info("spawning claude for repo=%s issue=#%d", repo_path, issue.number)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            cwd=repo_path,
            timeout=timeout,
            text=True,
        )
        success = result.returncode == 0
        if not success:
            logger.warning("claude exited with code %d for issue #%d", result.returncode, issue.number)
        return success
    except subprocess.TimeoutExpired:
        logger.error("claude timed out after %ds for issue #%d", timeout, issue.number)
        return False
    except FileNotFoundError:
        logger.error("claude CLI not found — is it installed and in PATH?")
        return False


def run_for_repo(repo_path: str, max_issues: int, timeout: int) -> None:
    logger.info("starting orchestration for repo=%s", repo_path)

    if not Path(repo_path).is_dir():
        logger.error("repo path does not exist: %s", repo_path)
        return

    try:
        issues = list_issues(repo_path)
    except subprocess.CalledProcessError as e:
        logger.error("failed to list issues for %s: %s", repo_path, e.stderr)
        return

    if not issues:
        logger.info("no open issues for repo=%s", repo_path)
        return

    candidates = prioritize(issues)
    if not candidates:
        logger.info("no eligible issues (all lack sufficient description) for repo=%s", repo_path)
        return

    implemented = 0
    for issue in candidates[:max_issues]:
        logger.info("picked issue #%d: %s", issue.number, issue.title)
        success = run_agent(repo_path, issue, timeout)
        if success:
            implemented += 1
            logger.info("completed issue #%d", issue.number)
        else:
            logger.warning("failed to implement issue #%d", issue.number)

    logger.info("done: %d/%d issues implemented for repo=%s", implemented, max_issues, repo_path)
