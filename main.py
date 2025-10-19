from src.github_client_service import (
    GitHubClientService,
)
from src.linear_service import LinearService
from loguru import logger


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


# TODO: Uncomment to enable scheduling
# def schedule_sync():
#     """Schedule the sync to run daily at 8am"""
#     scheduler = BlockingScheduler()
#     scheduler.add_job(, "cron", hour=8, minute=0)
#
#     print("GitHub to Linear sync scheduler started. Will run daily at 8:00 AM")
#     logging.basicConfig(level=logging.INFO)
#
#     try:
#         scheduler.start()
#     except KeyboardInterrupt:
#         print("Scheduler stopped")


if __name__ == "__main__":
    bootstrap()
