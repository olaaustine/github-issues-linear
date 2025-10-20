from unittest.mock import patch, MagicMock
from src.linear.linear_update_issues import LinearUpdateIssueService


def test_check_all_linear_ticket_statuses_internal_mocks():
    service = LinearUpdateIssueService()

    # Mock redis_client.scan_iter and redis_client.get/set
    with patch("src.linear.linear_update_issues.redis_client") as mock_redis:
        mock_redis.scan_iter.return_value = ["github_issue:Test Issue"]
        mock_redis.get.return_value = '{"foo": "bar"}'

        # Mock internal methods on the service instance
        service.linear_service = MagicMock()
        service.linear_service.get_ticket_if_it_exists.return_value = [
            {"identifier": "TICKET-1"}
        ]
        with (
            patch.object(
                service,
                "_LinearUpdateIssueService__get_ticket_status",
                return_value="Done",
            ),
            patch.object(
                service, "_LinearUpdateIssueService__update_ticket_status_in_redis"
            ) as mock_update,
        ):
            service.check_all_linear_ticket_statuses()
            # Assert update was called with correct arguments
            mock_update.assert_called_with("Test Issue", "Done")
