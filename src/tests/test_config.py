import pytest
from config import Config  # Fixed import for test discovery

def test_default_config():
    config = Config()
    assert config.get_github_key == "default_secret_key"
    assert config.get_linear_api_key == "default_api_key"
    assert config.get_linear_api_url == "https://api.linear.app/graphql"
    assert config.get_repository == ["Ensembl/ensembl-vep"]
    assert config.get_team_id == "OJA"


def test_env_config(monkeypatch):
    monkeypatch.setenv("GITHUB_KEY", "gh_test")
    monkeypatch.setenv("API_KEY", "lin_test")
    monkeypatch.setenv("API_URL", "https://custom.linear.app/graphql")
    monkeypatch.setenv("REPOSITORIES", "repo1/one,repo2/two , repo3/three ")
    monkeypatch.setenv("TEAM_ID", "TEAM42")
    config = Config()
    assert config.get_github_key == "gh_test"
    assert config.get_linear_api_key == "lin_test"
    assert config.get_linear_api_url == "https://custom.linear.app/graphql"
    assert config.get_repository == ["repo1/one", "repo2/two", "repo3/three"]
    assert config.get_team_id == "TEAM42"


def test_empty_repositories(monkeypatch):
    monkeypatch.setenv("REPOSITORIES", "   ")
    config = Config()
    assert config.get_repository == []


def test_single_repository(monkeypatch):
    monkeypatch.setenv("REPOSITORIES", "repo1/one")
    config = Config()
    assert config.get_repository == ["repo1/one"]
