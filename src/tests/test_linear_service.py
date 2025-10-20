import pytest
from unittest.mock import patch, MagicMock
from src.linear_service import LinearService


# Test for get_data_and_populate_variables
@patch("src.linear_service.requests.post")
def test_get_data_and_populate_variables_raises_exception(mock_post):
    # Do not mock team_id to simulate failure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data":{}}'
    mock_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "tid", "name": "tid"}]}}
    }
    mock_post.return_value = mock_response

    linear_service = LinearService()
    issue1 = MagicMock()
    issue1.title = "t1"
    issue1.body = "b1"
    issue2 = MagicMock()
    issue2.title = "t2"
    issue2.body = "b2"
    with pytest.raises(RuntimeError):
        linear_service.get_data_and_populate_variables([issue1, issue2])


@patch("src.linear_service.requests.post")
def test_get_data_and_populate_variables_success(mock_post):
    # Mock the response for team lookup
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"data":{}}'
    mock_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "mocked_team_id", "name": "tid"}]}}
    }
    mock_post.return_value = mock_response
    linear_service = LinearService()
    linear_service._LinearService__team_id = valid_uuid  # Mock team_id directly
    issue1 = MagicMock()
    issue1.title = "t1"
    issue1.body = "b1"
    issue2 = MagicMock()
    issue2.title = "t2"
    issue2.body = "b2"
    var_list = linear_service.get_data_and_populate_variables([issue1, issue2])
    assert len(var_list) == 2
    assert var_list[0].title == "t1"
    assert var_list[0].as_input() == {
        "input": {"title": "t1", "description": "b1", "teamId": valid_uuid}
    }
    assert var_list[1].title == "t2"


# Test for run_query_creates_new
@patch("src.linear_service.requests.post")
# TODO - move the patch to a mock
def test_run_query_creates_new(mock_post):
    # Mock the response for team lookup
    mock_team_response = MagicMock()
    mock_team_response.status_code = 200
    mock_team_response.text = '{"data":{}}'
    mock_team_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "tid", "name": "tid"}]}}
    }
    mock_post.side_effect = [
        mock_team_response,
        MagicMock(
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
        ),
    ]

    mock_exists = MagicMock()
    mock_exists.return_value = False

    linear_service = LinearService()
    linear_service._LinearService__get_issues_if_it_exists = mock_exists
    var = MagicMock()
    var.title = "title"
    var.as_input.return_value = {"foo": "bar"}

    with patch(
        "src.linear_service.LinearService._LinearService__response_status_check"
    ) as mock_check:
        mock_check.return_value = None
        linear_service.run_query([var])
        assert mock_post.call_count == 2
