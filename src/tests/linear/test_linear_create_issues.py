import pytest
from unittest.mock import patch, MagicMock
from src.linear.linear_create_issues import LinearCreateIssueService
from src.linear.linear import LinearService
from src.config import Config


# Test for get_data_and_populate_variables
@patch("src.linear.linear.requests.post")
def test_get_data_and_populate_variables_raises_exception(mock_post):
    # Do not mock team_id to simulate failure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data":{}}'
    mock_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "tid", "name": "tid"}]}}
    }
    mock_post.return_value = mock_response

    config = Config()
    service = LinearService(config)
    linear_service = LinearCreateIssueService(service)
    issue1 = MagicMock()
    issue1.title = "t1"
    issue1.body = "b1"
    issue2 = MagicMock()
    issue2.title = "t2"
    issue2.body = "b2"
    with pytest.raises(RuntimeError):
        linear_service.get_data_and_populate_variables([issue1, issue2])


@patch("src.linear.linear.requests.post")
def test_get_data_and_populate_variables_success(mock_post):
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data":{}}'
    mock_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": valid_uuid, "name": "tid"}]}}
    }
    mock_post.return_value = mock_response
    config = Config()
    linear = LinearService(config)
    linear.team_id = valid_uuid
    service = LinearCreateIssueService(linear)
    issue1 = MagicMock()
    issue1.title = "t1"
    issue1.body = "b1"
    issue2 = MagicMock()
    issue2.title = "t2"
    issue2.body = "b2"
    var_list = service.get_data_and_populate_variables([issue1, issue2])
    assert len(var_list) == 2
    assert var_list[0].title == "t1"
    assert var_list[0].as_input() == {
        "input": {"title": "t1", "description": "b1", "teamId": valid_uuid}
    }
    assert var_list[1].title == "t2"


@patch("src.linear.linear_cache.redis_client")
@patch("src.linear.linear_create_issues.requests.post")
def test_run_query_creates_new(mock_post, mock_redis):
    creation_response = MagicMock(
        status_code=200,
        json=MagicMock(
            return_value={
                "data": {
                    "issueCreate": {
                        "success": True,
                        "issue": {
                            "identifier": "ISSUE-1",
                            "url": "http://example.com",
                        },
                    }
                }
            }
        ),
    )
    mock_post.return_value = creation_response

    mock_exists = MagicMock()
    mock_exists.return_value = False
    config = Config()

    service = LinearService(config)
    service.confirm_if_ticket_exists = mock_exists
    linear_create = LinearCreateIssueService(service)
    var = MagicMock()
    var.title = "title"
    var.as_input.return_value = {"foo": "bar"}

    with patch("src.linear.linear.response_status_check") as mock_check:
        mock_check.return_value = None
        linear_create.run_query([var])
        assert mock_post.call_count == 1
