from unittest.mock import MagicMock
from github import GithubException
from src.github_client_service import GitHubClientService


def test_get_client_returns_github_instance():
    mock_config = MagicMock()
    mock_config.github_key = "fake_key"
    mock_config.return_value = mock_config
    mock_github = MagicMock()
    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance

    # new lets me skip real insantiation logic
    service = GitHubClientService.__new__(GitHubClientService)
    service._GitHubClientService__config = mock_config
    service._GitHubClientService__client = mock_github("fake_key")
    assert service._GitHubClientService__client is mock_github_instance


def test_get_repo_objects_returns_valid_repos():
    mock_config_instance = MagicMock()
    mock_config_instance.github_key = "fake_key"
    mock_config_instance.repository = ["repo1", "repo2"]
    mock_config_instance.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github_instance.return_value = mock_github_instance
    mock_repo1 = MagicMock()
    mock_repo2 = MagicMock()
    mock_github_instance.get_repo.side_effect = (mock_repo1, mock_repo2)

    service = GitHubClientService.__new__(GitHubClientService)
    service._GitHubClientService__config = mock_config_instance
    service._GitHubClientService__client = mock_github_instance
    repos = service._GitHubClientService__get_repo_objects()
    assert repos == {mock_repo1, mock_repo2}
    assert mock_github_instance.get_repo.call_count == 2


def test_get_repo_objects_handles_exceptions():
    mock_config_instance = MagicMock()
    mock_config_instance.github_key = "fake_key"
    mock_config_instance.repository = ["repo1", "repo2"]
    mock_config_instance.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github_instance.return_value = mock_github_instance
    mock_repo1 = MagicMock()
    mock_github_instance.get_repo.side_effect = [
        mock_repo1,
        GithubException(404, {"message": "Not Found"}),
    ]

    service = GitHubClientService.__new__(GitHubClientService)
    service._GitHubClientService__config = mock_config_instance
    service._GitHubClientService__client = mock_github_instance
    repos = service._GitHubClientService__get_repo_objects()
    assert repos == {mock_repo1}


def test_get_repo_issues_returns_all_open_issues():
    mock_config_instance = MagicMock()
    mock_config_instance.repository = ["repo1"]
    mock_config_instance.return_value = mock_config_instance

    mock_github_instance = MagicMock()
    mock_github_instance.return_value = mock_github_instance
    mock_repo = MagicMock()
    mock_issue1 = MagicMock()
    mock_issue2 = MagicMock()
    mock_repo.get_issues.return_value = [mock_issue1, mock_issue2]
    mock_github_instance.get_repo.return_value = mock_repo

    service = GitHubClientService.__new__(GitHubClientService)
    service._GitHubClientService__config = mock_config_instance
    service._GitHubClientService__client = mock_github_instance
    issues = service.get_repo_issues()
    assert issues == [mock_issue1, mock_issue2]
    mock_repo.get_issues.assert_called_once_with(state="open")
