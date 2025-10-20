import pytest
from unittest.mock import patch, MagicMock
from src.linear.linear import LinearService, response_status_check


@patch("src.linear.linear.requests.post")
def test_get_team_id_by_name_success(mock_post):
    # Mock Config instance and assign to service
    mock_config = MagicMock()
    mock_config.linear_api_key = "token"
    mock_config.team_id = "MyTeam"
    mock_config.linear_api_url = "http://api"
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "team-uuid", "name": "MyTeam"}]}}
    }
    mock_post.return_value = mock_response

    service = LinearService.__new__(LinearService)
    service._config = mock_config
    service._linear_api_key = mock_config.linear_api_key
    service._team_id_str = mock_config.team_id
    service._api_url = mock_config.linear_api_url
    service._headers = {
        "Content-Type": "application/json",
        "Authorization": mock_config.linear_api_key,
    }
    # Now call the method
    team_id = LinearService.get_team_id_by_name(service)
    assert team_id == "team-uuid"


@patch("src.linear.linear.requests.post")
def test_get_team_id_by_name_no_team_found(mock_post):
    mock_config = MagicMock()
    mock_config.linear_api_key = "token"
    mock_config.team_id = "NoTeam"
    mock_config.linear_api_url = "http://api"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"teams": {"nodes": []}}}
    mock_post.return_value = mock_response

    service = LinearService.__new__(LinearService)
    service._config = mock_config
    service._linear_api_key = mock_config.linear_api_key
    service._team_id_str = mock_config.team_id
    service._api_url = mock_config.linear_api_url
    service._headers = {
        "Content-Type": "application/json",
        "Authorization": mock_config.linear_api_key,
    }
    with pytest.raises(RuntimeError):
        LinearService.get_team_id_by_name(service)


@patch("src.linear.linear.requests.post")
def test_get_ticket_if_it_exists_success(mock_post):
    mock_config = MagicMock()
    mock_config.linear_api_key = "token"
    mock_config.team_id = "MyTeam"
    mock_config.linear_api_url = "http://api"
    # First call: get_team_id_by_name, Second call: get_ticket_if_it_exists
    mock_team_response = MagicMock()
    mock_team_response.status_code = 200
    mock_team_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "team-uuid", "name": "MyTeam"}]}}
    }
    mock_ticket_response = MagicMock()
    mock_ticket_response.status_code = 200
    mock_ticket_response.json.return_value = {
        "data": {"issues": {"nodes": [{"identifier": "ISSUE-1"}]}}
    }
    # get_team_id_by_name is not called in this test, so only ticket response is needed
    mock_post.return_value = mock_ticket_response

    service = LinearService.__new__(LinearService)
    service._config = mock_config
    service._linear_api_key = mock_config.linear_api_key
    service._team_id_str = mock_config.team_id
    service._api_url = mock_config.linear_api_url
    service._headers = {
        "Content-Type": "application/json",
        "Authorization": mock_config.linear_api_key,
    }
    service._team_id = "team-uuid"
    tickets = LinearService.get_ticket_if_it_exists(service, "Some Issue")
    assert tickets == [{"identifier": "ISSUE-1"}]


def test_response_status_check_raises_on_non_200():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    with pytest.raises(Exception):
        response_status_check(mock_response)


def test_response_status_check_raises_on_graphql_error():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errors": ["Some error"]}
    with pytest.raises(Exception):
        response_status_check(mock_response)
