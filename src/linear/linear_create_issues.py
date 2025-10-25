import requests
from github.Issue import Issue
from loguru import logger
from src.variables import Variables
from src.graph_query import mutation
from src.linear.linear import LinearService
from src.linear.linear import response_status_check
from src.linear.linear_cache import LinearCache


class LinearCreateIssueService:
    def __init__(self):
        self.linear_service = LinearService()

    def get_data_and_populate_variables(
        self, list_issues: list[Issue]
    ) -> list[Variables]:
        """Convert GitHub issues to Linear Variables."""
        variables = []
        for issue in list_issues:
            if self.linear_service.team_id is None:
                raise RuntimeError(
                    f"Invalid team ID: '{self.linear_service.team_name}'"
                )
            variables.append(
                Variables(
                    teamId=self.linear_service.team_id,
                    title=issue.title,
                    description=issue.body,
                )
            )

        return variables

    def run_query(self, variables: list) -> None:
        """Create issues in Linear from the provided variables."""
        for var in variables:
            input_obj = var.as_input()
            # TODO: Cache check can be added here to reduce API calls
            if self.linear_service.confirm_if_ticket_exists(var.title):
                logger.info(
                    f"Issue with title '{var.title}' already exists. Skipping creation."
                )
                continue
            resp = requests.post(
                self.linear_service.api_url,
                json={"query": mutation, "variables": input_obj},
                headers=self.linear_service.headers,
            )
            response_status_check(resp)
            body = resp.json()
            tickets = (body.get("data") or {}).get("issueCreate") or {}
            if not tickets.get("success"):
                # If creation failed, raise an error with details
                raise RuntimeError(
                    f"Create failed for '{input_obj.get('title')}': {body}"
                )

            ticket = tickets.get("issue")
            if ticket is None:
                raise RuntimeError(
                    f"Create failed for '{input_obj.get('title')}': No ticket data returned."
                )
            logger.success(f"Created {ticket.get('identifier')} → {ticket.get('url')}")
            LinearCache.cache_linear_ticket(var.title, ticket)
