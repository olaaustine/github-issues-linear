from unittest.mock import patch, MagicMock
from github import GithubException
from src.github_client_service import GitHubClientServie


@patch("src.github_client_service.Config")
@patch("src.github_client_service.Github")
def test_get_client_returns_github_instance(mock_github, mock_config):
    mock_config_instance = MagicMock()
    mock_config_instance.github_key = "fake_key"
    mock_config.return_value = mock_config_instance
    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance

    service = GitHubClientServie()
    assert isinstance(service._GitHubClientServie__client, MagicMock)
    mock_config.assert_called_once()
    mock_github.assert_called_once_with("fake_key")


@patch("src.github_client_service.Github")
@patch("src.github_client_service.Config")
def test_get_repo_objects_returns_valid_repos(mock_config, mock_github):
    mock_config_instance = MagicMock()
    mock_config_instance.repository = ["repo1", "repo2"]
    mock_config.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance
    mock_repo1 = MagicMock()
    mock_repo2 = MagicMock()
    mock_github_instance.get_repo.side_effect = [mock_repo1, mock_repo2]

    service = GitHubClientServie()
    repos = service._GitHubClientServie__get_repo_objects()
    assert repos == [mock_repo1, mock_repo2]
    assert mock_github_instance.get_repo.call_count == 2


@patch("src.github_client_service.Github")
@patch("src.github_client_service.Config")
def test_get_repo_objects_handles_exceptions(mock_config, mock_github):
    mock_config_instance = MagicMock()
    mock_config_instance.repository = ["repo1", "repo2"]
    mock_config.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance
    mock_repo1 = MagicMock()
    mock_github_instance.get_repo.side_effect = [
        mock_repo1,
        GithubException(404, {"message": "Not Found"}),
    ]

    service = GitHubClientServie()
    repos = service._GitHubClientServie__get_repo_objects()
    assert repos == [mock_repo1]


@patch("src.github_client_service.Github")
@patch("src.github_client_service.Config")
def test_get_repo_issues_returns_all_open_issues(mock_config, mock_github):
    mock_config_instance = MagicMock()
    mock_config_instance.repository = ["repo1"]
    mock_config.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance
    mock_repo = MagicMock()
    mock_issue1 = MagicMock()
    mock_issue2 = MagicMock()
    mock_repo.get_issues.return_value = [mock_issue1, mock_issue2]
    mock_github_instance.get_repo.return_value = mock_repo

    service = GitHubClientServie()
    issues = service.get_repo_issues()
    assert issues == [mock_issue1, mock_issue2]
    mock_repo.get_issues.assert_called_once_with(state="open")


@patch("src.github_client_service.Github")
@patch("src.github_client_service.Config")
def test_get_repo_issues_skips_repos_on_exception(mock_config, mock_github):
    mock_config_instance = MagicMock()
    mock_config_instance.repository = ["repo1", "repo2"]
    mock_config.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance
    mock_repo1 = MagicMock()
    mock_repo2 = MagicMock()
    mock_issue = MagicMock()
    mock_repo1.get_issues.return_value = [mock_issue]
    mock_repo2.get_issues.side_effect = GithubException(
        500, {"message": "Server Error"}
    )
    mock_github_instance.get_repo.side_effect = [mock_repo1, mock_repo2]

    service = GitHubClientServie()
    issues = service.get_repo_issues()
    assert issues == [mock_issue]
    mock_repo1.get_issues.assert_called_once_with(state="open")
    mock_repo2.get_issues.assert_called_once_with(state="open")
