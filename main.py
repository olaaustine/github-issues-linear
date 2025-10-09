from src.github_client_service import (
    get_client,
    get_repository,
    get_repo_object,
    get_repo_issues,
)
from src.linear_service import (
    get_data_and_populate_variables,
    run_query,
    return_headers,
    get_team_id_by_name,
)
from src.config import Config
from apscheduler.schedulers.blocking import BlockingScheduler
import logging


def make_everything_work_together():
    """Sync GitHub issues to Linear"""
    try:
        # Get GitHub client and repositories
        client = get_client()
        repos = get_repository()

        # Get repository objects and their issues
        repo_objects = get_repo_object(client, repos)
        issues = get_repo_issues(repo_objects)

        # Convert to Linear variables and create issues
        config = Config()
        headers = return_headers(config.get_linear_api_key)
        team_id = get_team_id_by_name(
            config.get_linear_api_url, config.get_team_id, headers
        )
        variables = get_data_and_populate_variables(issues, team_id)
        run_query(variables, headers, config.get_linear_api_url, config.get_team_id)

        print(f"Successfully processed {len(issues)} GitHub issues")

    except Exception as e:
        print(f"Error syncing issues: {e}")


def schedule_sync():
    """Schedule the sync to run daily at 8am"""
    scheduler = BlockingScheduler()
    scheduler.add_job(make_everything_work_together, "cron", hour=8, minute=0)

    print("GitHub to Linear sync scheduler started. Will run daily at 8:00 AM")
    logging.basicConfig(level=logging.INFO)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Scheduler stopped")


if __name__ == "__main__":
    # Run once immediately for testing
    # main()

    # Start the scheduler
    make_everything_work_together()
