import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.orchestrator import run_for_repo

logger = logging.getLogger(__name__)


def _get_repos() -> list[str]:
    raw = os.environ.get("REPOS", "")
    return [r.strip() for r in raw.split(",") if r.strip()]


def _get_config() -> dict:
    return {
        "schedule": os.environ.get("SCHEDULE", "0 9 * * 1-5"),
        "max_issues": int(os.environ.get("MAX_ISSUES_PER_RUN", "1")),
        "timeout": int(os.environ.get("CLAUDE_TIMEOUT", "1800")),
    }


def orchestrate() -> None:
    config = _get_config()
    repos = _get_repos()

    if not repos:
        logger.error("no repos configured — set the REPOS environment variable")
        return

    logger.info("running orchestration cycle for %d repo(s)", len(repos))
    for repo in repos:
        run_for_repo(repo, config["max_issues"], config["timeout"])


def start() -> None:
    config = _get_config()
    repos = _get_repos()

    if not repos:
        logger.error("REPOS is not set — nothing to orchestrate")
        return

    logger.info(
        "starting scheduler | repos=%d schedule=%s max_issues=%d",
        len(repos),
        config["schedule"],
        config["max_issues"],
    )

    scheduler = BlockingScheduler()
    scheduler.add_job(
        orchestrate,
        CronTrigger.from_crontab(config["schedule"]),
        id="orchestrate",
        name="issue-orch",
        max_instances=1,
        coalesce=True,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("scheduler stopped")
