import pytest
from unittest.mock import patch, MagicMock
from src.linear_service import (
    return_headers,
    get_team_nodes,
    response_status_check,
    get_team_id_by_name,
    get_data_and_populate_variables,
    get_issues_from_json,
    get_issues_if_it_exists,
    run_query,
)
from src.variables import Variables
from src.errors import ResponseNot200Error, GraphQLError


# Test return_headers
def test_return_headers():
    api_key = "test_key"
    headers = return_headers(api_key)
    assert headers == {
        "Content-Type": "application/json",
        "Authorization": api_key,
    }


# Test get_team_nodes
def test_get_team_nodes_valid():
    response_json = {"data": {"teams": {"nodes": [{"id": 1}, {"id": 2}]}}}
    nodes = get_team_nodes(response_json)
    assert nodes == [{"id": 1}, {"id": 2}]


def test_get_team_nodes_invalid():
    response_json = {"data": {"teams": {"nodes": "notalist"}}}
    with pytest.raises(RuntimeError):
        get_team_nodes(response_json)


# Test response_status_check
def test_response_status_check_ok():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {}
    assert response_status_check(response) is None


def test_response_status_check_http_error():
    response = MagicMock()
    response.status_code = 400
    response.text = "Bad Request"
    with pytest.raises(ResponseNot200Error):
        response_status_check(response)


def test_response_status_check_graphql_error():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"errors": ["error"]}
    with pytest.raises(GraphQLError):
        response_status_check(response)


# Test get_team_id_by_name
@patch("src.linear_service.requests.post")
def test_get_team_id_by_name_found(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"teams": {"nodes": [{"id": "teamid", "name": "TeamA"}]}}
    }
    mock_post.return_value = mock_response
    with patch("src.linear_service.response_status_check") as mock_check:
        mock_check.return_value = None
        result = get_team_id_by_name("url", "TeamA", {})
        assert result == "teamid"


@patch("src.linear_service.requests.post")
def test_get_team_id_by_name_not_found(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"teams": {"nodes": []}}}
    mock_post.return_value = mock_response
    with patch("src.linear_service.response_status_check") as mock_check:
        mock_check.return_value = None
        with pytest.raises(RuntimeError):
            get_team_id_by_name("url", "TeamA", {})


# Test get_data_and_populate_variables
def test_get_data_and_populate_variables():
    issue1 = MagicMock()
    issue1.title = "t1"
    issue1.body = "b1"
    issue2 = MagicMock()
    issue2.title = "t2"
    issue2.body = "b2"
    team_id = "tid"
    result = get_data_and_populate_variables([issue1, issue2], team_id)
    assert all(isinstance(v, Variables) for v in result)
    assert result[0].title == "t1" and result[1].title == "t2"


# Test get_issues_from_json
def test_get_issues_from_json_valid():
    response_json = {"data": {"issues": {"nodes": [{"id": 1}, {"id": 2}]}}}
    issues = get_issues_from_json(response_json)
    assert issues == [{"id": 1}, {"id": 2}]


def test_get_issues_from_json_invalid():
    response_json = {"data": {"issues": {"nodes": "notalist"}}}
    with pytest.raises(RuntimeError):
        get_issues_from_json(response_json)


# Test get_issues_if_it_exists
@patch("src.linear_service.requests.post")
@patch("src.linear_service.get_team_id_by_name")
def test_get_issues_if_it_exists_true(mock_get_team_id, mock_post):
    mock_get_team_id.return_value = "tid"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"issues": {"nodes": [{"id": 1}]}}}
    mock_post.return_value = mock_response
    with patch("src.linear_service.response_status_check") as mock_check:
        mock_check.return_value = None
        assert get_issues_if_it_exists("title", "url", {}, "yathqqqqq") is True


@patch("src.linear_service.requests.post")
@patch("src.linear_service.get_team_id_by_name")
def test_get_issues_if_it_exists_false(mock_get_team_id, mock_post):
    mock_get_team_id.return_value = "tid"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"issues": {"nodes": []}}}
    mock_post.return_value = mock_response
    with patch("src.linear_service.response_status_check") as mock_check:
        mock_check.return_value = None
        assert get_issues_if_it_exists("title", "url", {}, "yathqqqqq") is False


# Test run_query
@patch("src.linear_service.requests.post")
@patch("src.linear_service.get_issues_if_it_exists")
def test_run_query_skips_existing(mock_exists, mock_post):
    var = MagicMock()
    var.title = "title"
    var.as_input.return_value = {"foo": "bar"}
    mock_exists.return_value = True
    run_query([var], {}, "url", "team")
    mock_post.assert_not_called()


@patch("src.linear_service.requests.post")
@patch("src.linear_service.get_issues_if_it_exists")
def test_run_query_creates_new(mock_exists, mock_post):
    var = MagicMock()
    var.title = "title"
    var.as_input.return_value = {"foo": "bar"}
    mock_exists.return_value = False
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    with patch("src.linear_service.response_status_check") as mock_check:
        mock_check.return_value = None
        run_query([var], {}, "url", "team")
        mock_post.assert_called_once()
