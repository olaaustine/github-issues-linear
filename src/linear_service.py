import requests
from src.variables import Variables
from src.graph_query import mutation, QUERY_WITH_TEAM, TEAM_BY_NAME
from uuid import UUID
from src.errors import GraphQLError, ResponseNot200Error


def return_headers(api_key: str) -> dict:
    """Return headers for Linear API requests"""
    return {
        "Content-Type": "application/json",
        "Authorization": api_key,
    }


def get_team_nodes(response_json: dict) -> list[dict]:
    """Extract team nodes from the JSON response."""
    teams = response_json.get("data", {}).get("teams", {}).get("nodes", [])
    if not isinstance(teams, list):
        raise RuntimeError(f"Unexpected teams format: {teams}")
    return teams


def response_status_check(response: requests.Response) -> None:
    """Check the response status and return an exception if there's an error."""
    if response.status_code != 200:
        raise ResponseNot200Error(f"HTTP {response.status_code}: {response.text}")

    if "errors" in response.json():
        raise GraphQLError(f"GraphQL errors: {response.json().get('errors')}")

    return None


def get_team_id_by_name(api_url: str, team_id: str, headers: dict) -> UUID | None:
    """Fetch the team ID from Linear by team name."""
    payload = {"query": TEAM_BY_NAME, "variables": {"name": team_id}}
    resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
    response_status_check(resp)
    body = resp.json()

    nodes = get_team_nodes(body)
    if len(nodes) == 0:
        raise RuntimeError(f"Warning : No teams found for name '{team_id}'")

    for node in nodes:
        if node["name"].strip().lower() == team_id.strip().lower():
            return node["id"]

    return None


def get_data_and_populate_variables(
    list_issues: list, team_id: UUID
) -> list[Variables]:
    """Convert GitHub issues to Linear Variables."""
    variables = []
    for issue in list_issues:
        variables.append(
            Variables(teamId=team_id, title=issue.title, description=issue.body)
        )

    return variables


def get_issues_from_json(response_json: dict) -> list[dict]:
    """Extract issues from the JSON response."""
    issues = response_json.get("data", {}).get("issues", {}).get("nodes", [])
    if not isinstance(issues, list):
        raise RuntimeError(f"Unexpected issues format: {issues}")
    return issues


def get_issues_if_it_exists(
    issue_title: str,
    API_URL: str,
    headers: dict,
    team_id: UUID,
) -> bool | None:
    """Check if an issue with the given title already exists in Linear in the same team."""

    payload = {
        "query": QUERY_WITH_TEAM,
        "variables": {"title": issue_title, "teamId": team_id},
    }
    response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
    response_status_check(response)
    body = response.json()

    issues = get_issues_from_json(body)
    print(f"Checked existence for title '{issue_title}': {len(issues)} match(es).")
    return len(issues) > 0


def run_query(variables: list, headers: dict, API_URL: str, team: UUID) -> None:
    """Create issues in Linear from the provided variables."""
    for var in variables:
        input_obj = var.as_input()
        if get_issues_if_it_exists(var.title, API_URL, headers, team):
            print(f"Issue with title '{var.title}' already exists. Skipping creation.")
            continue
        resp = requests.post(
            API_URL, json={"query": mutation, "variables": input_obj}, headers=headers
        )
        response_status_check(resp)
        body = resp.json()

        result = (body.get("data") or {}).get("issueCreate") or {}
        if not result.get("success"):
            # If creation failed, raise an error with details
            raise RuntimeError(f"Create failed for '{input_obj.get('title')}': {body}")

        issue = result.get("issue")
        print(f"Created {issue.get('identifier')} → {issue.get('url')}")
