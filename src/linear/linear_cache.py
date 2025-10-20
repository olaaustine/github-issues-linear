import json
from datetime import datetime
from loguru import logger
from src.redis import get_redis_client

redis_client = get_redis_client()


class LinearCache:
    @staticmethod
    def get_ticket_data(key: str) -> dict:
        raw = redis_client.get(key)
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in Redis key: {key}")
            return {}

    @staticmethod
    def update_ticket_status(key: str, status: str) -> None:
        data = LinearCache.get_ticket_data(key)
        data["linear_status"] = status
        redis_client.set(key, json.dumps(data))

    # TODO: Add a different key in the cache, this name is not foolproof
    @staticmethod
    def cache_linear_ticket(gt_issue_title: str, ticket: dict, ttl_seconds: int = 0):
        key = f"github_issue:{gt_issue_title}"
        value = {
            "linear_id": ticket.get("identifier"),
            "linear_url": ticket.get("url"),
            "linear_status": ticket.get("state", {}).get("name"),
            "updated_at": datetime.utcnow().isoformat(),
        }
        redis_client.set(key, json.dumps(value))
