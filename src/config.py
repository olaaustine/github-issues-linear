import os


class Config:
    def __init__(self):
        """Initialize configuration from environment variables"""
        self._github_key = os.getenv("GITHUB_KEY", "default_secret_key")
        self._linear_api_key = os.getenv("API_KEY", "default_api_key")
        self._linear_api_url = os.getenv("API_URL", "https://api.linear.app/graphql")
        # Parse REPOSITORIES as a comma-separated string of owner/repo
        repo_env = os.getenv("REPOSITORIES", "Ensembl/ensembl-vep")
        if isinstance(repo_env, str):
            self._repository = [
                repo.strip() for repo in repo_env.split(",") if repo.strip()
            ]
        else:
            self._repository = []
        self._team_id = os.getenv("TEAM_ID", "OJA")

    @property
    def github_key(self):
        """Get GitHub key from environment variable"""
        return self._github_key

    @github_key.setter
    def github_key(self, value):
        self._github_key = value

    @property
    def linear_api_key(self):
        """Get Linear API key from environment variable"""
        return self._linear_api_key

    @linear_api_key.setter
    def linear_api_key(self, value):
        self._linear_api_key = value

    @property
    def repository(self):
        """Get list of repositories from environment variable"""
        return self._repository

    @repository.setter
    def repository(self, value):
        self._repository = value

    @property
    def linear_api_url(self):
        """Get Linear API URL from environment variable"""
        return self._linear_api_url

    @linear_api_url.setter
    def linear_api_url(self, value):
        self._linear_api_url = value

    @property
    def team_id(self):
        """Get Linear Team ID from environment variable"""
        return self._team_id

    @team_id.setter
    def team_id(self, value):
        self._team_id = value
