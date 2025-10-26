from github import Github
from typing import Set
from loguru import logger
import json
from functools import cached_property
from github.GithubException import GithubException
from github.Issue import Issue
from github.Repository import Repository
from src.config import Config
from src.redis import get_redis_client

redis_client = get_redis_client()


class GitHubClientService:
    def __init__(self, config: Config):
        self.__config = config

    @cached_property
    def github_key(self) -> str:
        """Get GitHub API key from config"""
        return self.__config.github_key

    @cached_property
    def client(self) -> Github:
        """Get GitHub client using the key from config"""
        return Github(self.github_key)

    def __get_repo_objects(self) -> Set[Repository]:
        """Safely get repository objects from the list of repository names"""

        repo_objects = set()
        for repo_name in self.__config.repository:
            try:
                repo = self.client.get_repo(repo_name)
                repo_objects.add(repo)
            except GithubException as e:
                logger.error(
                    f"Failed to fetch repo '{repo_name}': {e.status} - {e.data.get('message')}"
                )
        return repo_objects

    def get_repo_issues(self) -> list[Issue]:
        """Get all open issues from the list of repository objects"""
        all_issues = []

        for repo in self.__get_repo_objects():
            try:
                issues = repo.get_issues(state="open")
                all_issues.extend(issues)
            except GithubException as e:
                logger.error(
                    f"Failed to fetch issues for repo '{repo.full_name}': {e.status} - {e.data.get('message')}"
                )
                continue

        return all_issues

    # TODO: Use issue number instead of title for more reliable issue closing
    def __close_issue(self, issue_title: str) -> None:
        """Close a GitHub issue by its title in the specified repository"""
        for repo in self.__get_repo_objects():
            try:
                issues = repo.get_issues(state="open")
                for issue in issues:
                    if issue.title.strip().lower() == issue_title.strip().lower():
                        issue.edit(state="closed")
                        logger.info(
                            f"Issue '{issue_title}' in '{repo}' closed successfully."
                        )
                        return
                logger.warning(
                    f"No open issue with title '{issue_title}' found in '{repo}'."
                )
            except GithubException as e:
                logger.error(
                    f"Failed to close issue '{issue_title}' in '{repo}': {e.status} - {e.data.get('message')}"
                )

    def close_done_issues_from_redis(self):
        """Close GitHub issues whose Linear status is 'done' based on Redis cache."""
        for key in redis_client.scan_iter("github_issue:*"):
            data = redis_client.get(key)
            if not data:
                continue
            issue_info = json.loads(data)
            if (
                issue_info.get("linear_status")
                and issue_info.get("linear_status") == "Done"
            ):
                # Extract the issue title from the key
                issue_title = key.replace("github_issue:", "")
                self.__close_issue(issue_title)
