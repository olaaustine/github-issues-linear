import requests
from uuid import UUID
from github.Issue import Issue
from loguru import logger
from src.variables import Variables
from src.graph_query import mutation, QUERY_WITH_TEAM, TEAM_BY_NAME
from src.errors import GraphQLError, ResponseNot200Error
from src.config import Config


class LinearService:
    def __init__(self):
        self.__config = Config()
        self.__linear_api_key = self.__config.linear_api_key
        self.__api_url = self.__config.linear_api_url
        self.__team_id_str = self.__config.team_id
        self.__headers = self.__return_headers()
        self.__team_id = self.__get_team_id_by_name()

    def __return_headers(self) -> dict:
        """Return headers for Linear API requests"""
        return {
            "Content-Type": "application/json",
            "Authorization": self.__linear_api_key,
        }

    def __response_status_check(self, response: requests.Response):
        """Check the response status and return an exception if there's an error."""
        if response.status_code != 200:
            raise ResponseNot200Error(f"HTTP {response.status_code}: {response.text}")

        if "errors" in response.json():
            raise GraphQLError(f"GraphQL errors: {response.json().get('errors')}")

    def __get_team_id_by_name(self) -> UUID | None:
        """Fetch the team ID from Linear by team name."""

        def get_team_nodes(response_json: dict) -> list[dict]:
            """Extract team nodes from the JSON response."""
            teams = response_json.get("data", {}).get("teams", {}).get("nodes", [])
            if not isinstance(teams, list):
                raise ValueError(f"Unexpected teams format: {teams}")
            return teams

        payload = {"query": TEAM_BY_NAME, "variables": {"name": self.__team_id_str}}
        resp = requests.post(
            self.__api_url, json=payload, headers=self.__headers, timeout=10
        )
        self.__response_status_check(resp)
        body = resp.json()

        nodes = get_team_nodes(body)
        if len(nodes) == 0:
            raise RuntimeError(
                f"Warning : No teams found for name '{self.__team_id_str}'"
            )

        for node in nodes:
            if node["name"].strip().lower() == self.__team_id_str.strip().lower():
                return node["id"]

        return None

    def get_data_and_populate_variables(
        self, list_issues: list[Issue]
    ) -> list[Variables]:
        """Convert GitHub issues to Linear Variables."""
        variables = []
        for issue in list_issues:
            if self.__team_id is None:
                raise RuntimeError(f"Invalid team ID: '{self.__team_id_str}'")
            variables.append(
                Variables(
                    teamId=self.__team_id, title=issue.title, description=issue.body
                )
            )

        return variables

    def __get_issues_if_it_exists(self, issue_title: str) -> bool | None:
        """Check if an issue with the given title already exists in Linear in the same team."""

        def get_issues_from_json(response_json: dict) -> list[dict]:
            """Extract issues from the JSON response."""
            issues = response_json.get("data", {}).get("issues", {}).get("nodes", [])
            if not isinstance(issues, list):
                raise ValueError(f"Unexpected issues format: {issues}")
            return issues

        payload = {
            "query": QUERY_WITH_TEAM,
            "variables": {"title": issue_title, "teamId": str(self.__team_id)},
        }
        response = requests.post(
            self.__api_url, json=payload, headers=self.__headers, timeout=10
        )
        self.__response_status_check(response)
        body = response.json()

        issues = get_issues_from_json(body)
        logger.info(
            f"Checked existence for title '{issue_title}': {len(issues)} match(es)."
        )
        return len(issues) > 0

    def run_query(self, variables: list) -> None:
        """Create issues in Linear from the provided variables."""
        for var in variables:
            input_obj = var.as_input()
            if self.__get_issues_if_it_exists(var.title):
                logger.info(
                    f"Issue with title '{var.title}' already exists. Skipping creation."
                )
                continue
            resp = requests.post(
                self.__api_url,
                json={"query": mutation, "variables": input_obj},
                headers=self.__headers,
            )
            self.__response_status_check(resp)
            body = resp.json()

            result = (body.get("data") or {}).get("issueCreate") or {}
            if not result.get("success"):
                # If creation failed, raise an error with details
                raise RuntimeError(
                    f"Create failed for '{input_obj.get('title')}': {body}"
                )

            issue = result.get("issue")
            logger.success(f"Created {issue.get('identifier')} → {issue.get('url')}")
