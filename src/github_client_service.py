from github import Github
from src.config import Config
from github.GithubException import GithubException
from github.Issue import Issue


class GitHubClientServie:
    def __init__(self):
        self.__config = Config()
        self.__github_key = self.__config.github_key
        self.__client = self.__get_client()

    def __get_client(self) -> Github:
        """Get GitHub client using the key from config"""
        client = Github(self.__github_key)
        return client

    def __get_repositories(self) -> list[str]:
        """Get list of repository names from config"""
        repositories = self.__config.repository
        return repositories

    def __get_repo_objects(self) -> list:
        """Safely get repository objects from the list of repository names"""
        repo_objects = []
        for repo_name in self.__get_repositories():
            try:
                repo = self.__client.get_repo(repo_name)
                repo_objects.append(repo)
            except GithubException as e:
                print(
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
                print(
                    f"Failed to fetch issues for repo '{repo.full_name}': {e.status} - {e.data.get('message')}"
                )
                continue

        return all_issues
