import pytest
from unittest.mock import patch, MagicMock
import linear_service
from variables import Variables

# Test return_headers
def test_return_headers():
    api_key = 'test_key'
    headers = linear_service.return_headers(api_key)
    assert headers == {
        'Content-Type': 'application/json',
        'Authorization': api_key,
    }

# Test get_team_nodes
def test_get_team_nodes_valid():
    response_json = {'data': {'teams': {'nodes': [{'id': 1}, {'id': 2}]}}}
    nodes = linear_service.get_team_nodes(response_json)
    assert nodes == [{'id': 1}, {'id': 2}]

def test_get_team_nodes_invalid():
    response_json = {'data': {'teams': {'nodes': 'notalist'}}}
    with pytest.raises(RuntimeError):
        linear_service.get_team_nodes(response_json)

# Test response_status_check
def test_response_status_check_ok():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {}
    assert linear_service.response_status_check(response) is None

def test_response_status_check_http_error():
    response = MagicMock()
    response.status_code = 400
    response.text = 'Bad Request'
    assert isinstance(linear_service.response_status_check(response), Exception)

def test_response_status_check_graphql_error():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'errors': ['error']}
    assert isinstance(linear_service.response_status_check(response), Exception)

# Test get_team_id_by_name
@patch('linear_service.requests.post')
def test_get_team_id_by_name_found(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': {'teams': {'nodes': [{'id': 'teamid', 'name': 'TeamA'}]}}
    }
    mock_post.return_value = mock_response
    with patch('linear_service.response_status_check') as mock_check:
        mock_check.return_value = None
        result = linear_service.get_team_id_by_name('url', 'TeamA', {})
        assert result == 'teamid'

@patch('linear_service.requests.post')
def test_get_team_id_by_name_not_found(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': {'teams': {'nodes': []}}}
    mock_post.return_value = mock_response
    with patch('linear_service.response_status_check') as mock_check:
        mock_check.return_value = None
        with pytest.raises(RuntimeError):
            linear_service.get_team_id_by_name('url', 'TeamA', {})

# Test get_data_and_populate_variables
def test_get_data_and_populate_variables():
    issue1 = MagicMock()
    issue1.title = 't1'
    issue1.body = 'b1'
    issue2 = MagicMock()
    issue2.title = 't2'
    issue2.body = 'b2'
    team_id = 'tid'
    result = linear_service.get_data_and_populate_variables([issue1, issue2], team_id)
    assert all(isinstance(v, Variables) for v in result)
    assert result[0].title == 't1' and result[1].title == 't2'

# Test get_issues_from_json
def test_get_issues_from_json_valid():
    response_json = {'data': {'issues': {'nodes': [{'id': 1}, {'id': 2}]}}}
    issues = linear_service.get_issues_from_json(response_json)
    assert issues == [{'id': 1}, {'id': 2}]

def test_get_issues_from_json_invalid():
    response_json = {'data': {'issues': {'nodes': 'notalist'}}}
    with pytest.raises(RuntimeError):
        linear_service.get_issues_from_json(response_json)

# Test get_issues_if_it_exists
@patch('linear_service.requests.post')
@patch('linear_service.get_team_id_by_name')
def test_get_issues_if_it_exists_true(mock_get_team_id, mock_post):
    mock_get_team_id.return_value = 'tid'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': {'issues': {'nodes': [{'id': 1}]}}}
    mock_post.return_value = mock_response
    with patch('linear_service.response_status_check') as mock_check:
        mock_check.return_value = None
        assert linear_service.get_issues_if_it_exists('team', 'title', 'url', {}) is True

@patch('linear_service.requests.post')
@patch('linear_service.get_team_id_by_name')
def test_get_issues_if_it_exists_false(mock_get_team_id, mock_post):
    mock_get_team_id.return_value = 'tid'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': {'issues': {'nodes': []}}}
    mock_post.return_value = mock_response
    with patch('linear_service.response_status_check') as mock_check:
        mock_check.return_value = None
        assert linear_service.get_issues_if_it_exists('team', 'title', 'url', {}) is False

# Test run_query
@patch('linear_service.requests.post')
@patch('linear_service.get_issues_if_it_exists')
def test_run_query_skips_existing(mock_exists, mock_post):
    var = MagicMock()
    var.title = 'title'
    var.as_input.return_value = {'foo': 'bar'}
    mock_exists.return_value = True
    linear_service.run_query([var], {}, 'url', 'team')
    mock_post.assert_not_called()

@patch('linear_service.requests.post')
@patch('linear_service.get_issues_if_it_exists')
def test_run_query_creates_new(mock_exists, mock_post):
    var = MagicMock()
    var.title = 'title'
    var.as_input.return_value = {'foo': 'bar'}
    mock_exists.return_value = False
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    with patch('linear_service.response_status_check') as mock_check:
        mock_check.return_value = None
        linear_service.run_query([var], {}, 'url', 'team')
        mock_post.assert_called_once()

