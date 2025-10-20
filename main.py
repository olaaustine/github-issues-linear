from loguru import logger
import sys
import signal
from apscheduler.schedulers.blocking import BlockingScheduler
from src.github_client_service import GitHubClientService
from src.linear.linear_create_issues import LinearCreateIssueService as LinearService
from src.linear.linear_update_issues import (
    LinearUpdateIssueService as LinearUpdateService,
)


def bootstrap():
    """Sync GitHub issues to Linear and update statuses."""
    try:
        github_client = GitHubClientService()
        linear_client = LinearService()

        issues = github_client.get_repo_issues()
        variables = linear_client.get_data_and_populate_variables(issues)
        linear_client.run_query(variables)

        logger.success(f"Successfully processed {len(issues)} GitHub issues")

        LinearUpdateService().check_all_linear_ticket_statuses()
        github_client.close_done_issues_from_redis()

    except Exception:
        logger.exception("Error syncing issues")  # More descriptive logging


def schedule_sync():
    """Schedule the sync to run daily at 8am"""
    scheduler = BlockingScheduler()
    scheduler.add_job(bootstrap, "cron", hour=8, minute=0)

    logger.info("GitHub to Linear sync scheduler started. Will run daily at 8:00 AM")

    def shutdown(signum: int, frame):
        logger.info(f"Received shutdown signal {signum}. Stopping scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    scheduler.start()


if __name__ == "__main__":
    schedule_sync()
