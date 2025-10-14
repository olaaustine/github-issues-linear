from github import Github
from config import Config


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
    """Get repository objects from the list of repository names"""
    repo_objects = [client.get_repo(repo) for repo in repos]
    return repo_objects


# TODO use pagination to get all issues if there are many
def get_repo_issues(repo_objects: list) -> list:
    """Get all open issues from the list of repository objects"""
    all_issues = []
    for repo in repo_objects:
        issues = repo.get_issues(state="open")
        all_issues.extend(issues)
    return all_issues
