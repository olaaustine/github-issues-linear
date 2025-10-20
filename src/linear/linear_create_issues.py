import requests
from github.Issue import Issue
from loguru import logger
import json
from src.variables import Variables
from src.graph_query import mutation
from src.linear.linear import LinearService
from src.redis import get_redis_client
from src.linear.linear import response_status_check

redis_client = get_redis_client()


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

    def __confirm_if_ticket_exists(self, issue_title: str) -> bool | None:
        """Check if a ticket with the given issue title already exists in Linear in the same team."""
        tickets = self.linear_service.get_ticket_if_it_exists(issue_title)
        logger.info(
            f"Checked existence for title '{issue_title}': {len(tickets)} match(es)."
        )
        return len(tickets) > 0

    def run_query(self, variables: list) -> None:
        """Create issues in Linear from the provided variables."""
        for var in variables:
            input_obj = var.as_input()
            # TODO: Cache check can be added here to reduce API calls
            if self.__confirm_if_ticket_exists(var.title):
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
            logger.success(f"Created {ticket.get('identifier')} → {ticket.get('url')}")
            self.__cache_linear_ticket(var.title, ticket)

    def __cache_linear_ticket(
        self, gt_issue_title: str, ticket: dict, ttl_seconds: int = 0
    ):
        key = f"github_issue:{gt_issue_title}"
        value = {
            "linear_id": ticket.get("identifier"),
            "linear_url": ticket.get("url"),
            "linear_status": ticket.get("state", {}).get("name"),
        }
        redis_client.set(key, json.dumps(value))
