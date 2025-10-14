import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    github_key: str = field(default_factory=lambda: os.getenv("GITHUB_KEY", ""))
    linear_api_key: str = field(default_factory=lambda: os.getenv("API_KEY", ""))
    linear_api_url: str = field(
        default_factory=lambda: os.getenv("API_URL", "https://api.linear.app/graphql")
    )
    repository: List[str] = field(
        default_factory=lambda: [
            repo.strip()
            for repo in os.getenv("REPOSITORIES", " ").split(",")
            if repo.strip()
        ]
    )
    team_id: str = field(default_factory=lambda: os.getenv("TEAM_ID", ""))
