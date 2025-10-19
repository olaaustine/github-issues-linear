from loguru import logger
import sys
import signal
from apscheduler.schedulers.blocking import BlockingScheduler
from src.github_client_service import (
    GitHubClientService,
)
from src.linear_service import LinearService


def bootstrap():
    """Sync GitHub issues to Linear"""
    try:
        # Get GitHub client and repositories
        github_client = GitHubClientService()
        issues = github_client.get_repo_issues()

        # Convert to Linear variables and create issues
        linear_client = LinearService()
        variables = linear_client.get_data_and_populate_variables(issues)
        linear_client.run_query(variables)

        logger.success(f"Successfully processed {len(issues)} GitHub issues")

    except Exception as e:
        logger.error(f"Error syncing issues: {e}")


def schedule_sync():
    """Schedule the sync to run daily at 8am"""
    scheduler = BlockingScheduler()
    scheduler.add_job(bootstrap, "cron", hour=8, minute=0)

    logger.info("GitHub to Linear sync scheduler started. Will run daily at 8:00 AM")

    def shutdown(signum, frame):
        logger.info("Received shutdown signal. Stopping scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    scheduler.start()


if __name__ == "__main__":
    schedule_sync()
