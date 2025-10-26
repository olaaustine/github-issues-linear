import requests
from loguru import logger
from uuid import UUID
from functools import cached_property
from src.config import Config
from src.errors import GraphQLError, ResponseNot200Error
from src.graph_query import TEAM_BY_NAME, QUERY_WITH_TEAM, GET_TICKETS_STATUS


def response_status_check(response: requests.Response):
    """Check the response status and return an exception if there's an error."""
    if response.status_code != 200:
        raise ResponseNot200Error(f"HTTP {response.status_code}: {response.text}")

    if "errors" in response.json():
        raise GraphQLError(f"GraphQL errors: {response.json().get('errors')}")


class LinearService:
    def __init__(self, config: Config):
        self._config = config

    @cached_property
    def team_id(self) -> UUID | None:
        return self.get_team_id_by_name()

    @cached_property
    def team_name(self) -> str:
        return self._config.team_id

    @cached_property
    def api_url(self) -> str:
        return self._config.linear_api_url

    @cached_property
    def headers(self) -> dict:
        return self.return_headers()

    @cached_property
    def linear_api_key(self) -> str:
        return self._config.linear_api_key

    def return_headers(self) -> dict:
        """Return headers for Linear API requests"""
        return {
            "Content-Type": "application/json",
            "Authorization": self.linear_api_key,
        }

    def get_team_id_by_name(self) -> UUID | None:
        """Fetch the team ID from Linear by team name."""

        def get_team_nodes(response_json: dict) -> list[dict]:
            """Extract team nodes from the JSON response."""
            teams = response_json.get("data", {}).get("teams", {}).get("nodes", [])
            if not isinstance(teams, list):
                raise ValueError(f"Unexpected teams format: {teams}")
            return teams

        payload = {"query": TEAM_BY_NAME, "variables": {"name": self.team_name}}
        resp = requests.post(
            self.api_url, json=payload, headers=self.headers, timeout=10
        )
        response_status_check(resp)
        body = resp.json()

        nodes = get_team_nodes(body)
        if len(nodes) == 0:
            raise RuntimeError(f"Warning : No teams found for name '{self.team_name}'")

        for node in nodes:
            if node["name"].strip().lower() == self.team_name.strip().lower():
                return node["id"]

        return None

    def get_ticket_if_it_exists(self, issue_title: str) -> list[dict]:
        """Check if a ticket with the given issue title already exists in Linear in the same team."""

        def get_ticket_from_json(response_json: dict) -> list[dict]:
            """Extract issues from the JSON response."""
            issues = response_json.get("data", {}).get("issues", {}).get("nodes", [])
            if not isinstance(issues, list):
                raise ValueError(f"Unexpected issues format: {issues}")
            return issues

        payload = {
            "query": QUERY_WITH_TEAM,
            "variables": {"title": issue_title, "teamId": str(self.team_id)},
        }
        response = requests.post(
            self.api_url, json=payload, headers=self.headers, timeout=10
        )
        response_status_check(response)
        body = response.json()

        ticket = get_ticket_from_json(body)

        return ticket

    def confirm_if_ticket_exists(self, issue_title: str) -> bool | None:
        """Check if a ticket with the given issue title already exists in Linear in the same team."""
        tickets = self.get_ticket_if_it_exists(issue_title)
        logger.info(
            f"Checked existence for title '{issue_title}': {len(tickets)} match(es)."
        )
        return len(tickets) > 0

    def get_ticket_status(self, ticket_identifier: str) -> str | None:
        """Fetch the current status of a Linear ticket by its identifier."""
        query = GET_TICKETS_STATUS
        resp = requests.post(
            self.api_url,
            json={"query": query, "variables": {"id": ticket_identifier}},
            headers=self.headers,
        )
        response_status_check(resp)
        data = resp.json()
        try:
            status = data.get("data", {}).get("issue", {}).get("state", {}).get("name")
            return status
        except (KeyError, TypeError) as e:
            logger.error(
                f"Failed to extract status for ticket '{ticket_identifier}': {e}"
            )
            return None
