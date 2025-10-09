import os


class Config:
    def __init__(self):
        """Initialize configuration from environment variables"""
        self.github_key = os.getenv("GITHUB_KEY", "default_secret_key")
        self.linear_api_key = os.getenv("API_KEY", "default_api_key")
        self.linear_api_url = os.getenv("API_URL", "https://api.linear.app/graphql")
        # Parse REPOSITORIES as a comma-separated string of owner/repo
        repo_env = os.getenv("REPOSITORIES", "Ensembl/ensembl-vep")
        if isinstance(repo_env, str):
            self.repository = [
                repo.strip() for repo in repo_env.split(",") if repo.strip()
            ]
        else:
            self.repository = []
        self.team_id = os.getenv("TEAM_ID", "OJA")

    @property
    def get_github_key(self):
        """Get GitHub key from environment variable"""
        return self.github_key

    @property
    def get_linear_api_key(self):
        """Get Linear API key from environment variable"""
        return self.linear_api_key

    @property
    def get_repository(self):
        """Get list of repositories from environment variable"""
        return self.repository

    @property
    def get_linear_api_url(self):
        """Get Linear API URL from environment variable"""
        return self.linear_api_url

    @property
    def get_team_id(self):
        """Get Linear Team ID from environment variable"""
        return self.team_id
