import requests
from loguru import logger
import json
from src.graph_query import GET_TICKETS_STATUS
from src.redis import get_redis_client
from src.linear.linear import LinearService, response_status_check

redis_client = get_redis_client()


class LinearUpdateIssueService:
    def __init__(self):
        self.linear_service = LinearService()

    def check_all_linear_ticket_statuses(self) -> None:
        """Check and update the Linear ticket status for all issues in Redis."""
        for key in redis_client.scan_iter("github_issue:*"):
            issue_title = key.replace("github_issue:", "")
            ticket = self.linear_service.get_ticket_if_it_exists(issue_title)
            if ticket:
                logger.info(
                    f"Found Linear ticket for issue '{issue_title}'. Checking status..."
                )
                identifier = ticket[0].get("identifier")
                status = self.__get_ticket_status(identifier)
                if status in ["In Progress", "Done"]:
                    logger.info(
                        f"Updating status for issue '{issue_title}' to '{status}'"
                    )
                    self.__update_ticket_status_in_redis(issue_title, status)

    def __get_ticket_status(self, ticket_identifier: str) -> str | None:
        """Fetch the current status of a Linear ticket by its identifier."""
        query = GET_TICKETS_STATUS
        resp = requests.post(
            self.linear_service.api_url,
            json={"query": query, "variables": {"id": ticket_identifier}},
            headers=self.linear_service.headers,
        )
        response_status_check(resp)
        data = resp.json()
        try:
            status = data["data"]["issue"]["state"]["name"]
            return status
        except (KeyError, TypeError) as e:
            logger.error(
                f"Failed to extract status for ticket '{ticket_identifier}': {e}"
            )
            return None

    def __update_ticket_status_in_redis(self, ticket_title: str, status: str) -> None:
        """Update the ticket status in Redis cache."""
        redis_key = f"github_issue:{ticket_title}"
        existing = redis_client.get(redis_key)
        data = {}
        if existing:
            try:
                data = json.loads(existing)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from Redis for key '{redis_key}'")
                data = {}
            except Exception as e:
                logger.error(
                    f"Unexpected error while reading Redis key '{redis_key}': {e}"
                )
                data = {}
        data["linear_status"] = status
        redis_client.set(redis_key, json.dumps(data))
