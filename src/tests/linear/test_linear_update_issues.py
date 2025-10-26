from unittest.mock import patch, MagicMock
from datetime import datetime
from src.linear.linear_update_issues import LinearUpdateIssueService
from src.linear.linear import LinearService


def test_check_all_linear_ticket_statuses_internal_mocks():
    linear = LinearService()
    # make these methods callables returning the expected values
    linear.get_ticket_if_it_exists = MagicMock(
        return_value=[{"identifier": "TICKET-1"}]
    )
    linear.get_ticket_status = MagicMock(return_value="Done")

    service = LinearUpdateIssueService(linear)

    # Mock redis_client.scan_iter and redis_client.get/set
    with patch("src.linear.linear_update_issues.redis_client") as mock_redis:
        mock_redis.scan_iter.return_value = ["github_issue:Test Issue"]
        mock_redis.get.return_value = {
            "linear_id": "TICKET-1",
            "linear_url": "https://linear.app/TICKET-1",
            "linear_status": "In Progress",
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Mock internal update method on the service instance
        with patch.object(
            service, "_LinearUpdateIssueService__update_ticket_status_in_redis"
        ) as mock_update:
            service.check_all_linear_ticket_statuses()
            # Assert update was called with correct arguments
            mock_update.assert_called_with("Test Issue", "Done")
