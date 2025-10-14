from github import Github
from src.config import Config
from github.GithubException import GithubException


def get_client() -> Github:
    """Get GitHub client using the key from config"""
    config = Config()
    github_key = config.github_key
    client = Github(github_key)
    return client


def get_repository() -> list[str]:
    """Get list of repository names from config"""
    config = Config()
    repository = config.repository
    return repository


def get_repo_object(client: Github, repos: list[str]) -> list:
    """Safely get repository objects from the list of repository names"""
    repo_objects = []
    for repo_name in repos:
        try:
            repo = client.get_repo(repo_name)
            repo_objects.append(repo)
        except GithubException as e:
            print(
                f"Failed to fetch repo '{repo_name}': {e.status} - {e.data.get('message')}"
            )
    return repo_objects


# TODO use pagination to get all issues if there are many
def get_repo_issues(repo_objects: list) -> list:
    """Get all open issues from the list of repository objects"""
    all_issues = []

    for repo in repo_objects:
        try:
            issues = repo.get_issues(state="open")
            all_issues.extend(issues)
        except GithubException as e:
            print(
                f"Failed to fetch issues for repo '{repo.full_name}': {e.status} - {e.data.get('message')}"
            )
            continue

    return all_issues
