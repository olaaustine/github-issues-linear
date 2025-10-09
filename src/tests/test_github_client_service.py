import pytest
from unittest.mock import patch, MagicMock
import github_client_service

# Test get_client
@patch('github_client_service.Config')
@patch('github_client_service.Github')
def test_get_client(mock_github, mock_config):
    mock_config_instance = MagicMock()
    mock_config_instance.get_github_key = 'fake_key'
    mock_config.return_value = mock_config_instance
    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance

    client = github_client_service.get_client()
    mock_config.assert_called_once()
    mock_github.assert_called_once_with('fake_key')
    assert client == mock_github_instance

# Test get_repository
@patch('github_client_service.Config')
def test_get_repository(mock_config):
    mock_config_instance = MagicMock()
    mock_config_instance.get_repository = ['repo1', 'repo2']
    mock_config.return_value = mock_config_instance

    repos = github_client_service.get_repository()
    mock_config.assert_called_once()
    assert repos == ['repo1', 'repo2']

# Test get_repo_object
@patch('github_client_service.Github')
def test_get_repo_object(mock_github):
    mock_client = MagicMock()
    mock_client.get_repo.side_effect = lambda name: f"repo_obj_{name}"
    repos = ['repo1', 'repo2']
    repo_objs = github_client_service.get_repo_object(mock_client, repos)
    assert repo_objs == ['repo_obj_repo1', 'repo_obj_repo2']
    assert mock_client.get_repo.call_count == 2

# Test get_repo_issues
def test_get_repo_issues():
    mock_repo1 = MagicMock()
    mock_repo2 = MagicMock()
    mock_issue1 = MagicMock()
    mock_issue2 = MagicMock()
    mock_issue3 = MagicMock()
    mock_repo1.get_issues.return_value = [mock_issue1, mock_issue2]
    mock_repo2.get_issues.return_value = [mock_issue3]
    repo_objects = [mock_repo1, mock_repo2]
    issues = github_client_service.get_repo_issues(repo_objects)
    assert issues == [mock_issue1, mock_issue2, mock_issue3]
    mock_repo1.get_issues.assert_called_once_with(state="open")
    mock_repo2.get_issues.assert_called_once_with(state="open")

