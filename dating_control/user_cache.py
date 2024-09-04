import pickle

from redis import Redis

from dating_control.user_flow import BaseUserFlow, DefaultUserFlow
from dating_control.utils import get_logger


logger = get_logger("user_cache.py")


class RedisUserCache:
    def __init__(self, host="cache", port: int = 6379, sleep_seconds: int = 10, db: int = 0) -> None:
        self._redis_client = Redis(host=host, port=port, db=db)
        self._store_seconds = sleep_seconds

    def _get_cached_flow(self, user_id: int) -> BaseUserFlow:
        serialized_flow_class = self._redis_client.get(str(user_id))
        self._redis_client.setex(str(user_id), self._store_seconds, serialized_flow_class)
        return pickle.loads(serialized_flow_class)

    def _insert_into_users_cache(self, user_id: int) -> None:
        flow_instance = DefaultUserFlow(user_id)
        self._redis_client.setex(str(user_id), self._store_seconds, pickle.dumps(flow_instance))
        logger.info(f"user: {user_id} has been inserted to the cache")

    def _is_user_in_users_cache(self, user_id: int) -> bool:
        serialized_object = self._redis_client.get(str(user_id))
        return bool(serialized_object)

    def get_user_flow(self, user_id: int) -> BaseUserFlow:
        if not self._is_user_in_users_cache(user_id):
            self._insert_into_users_cache(user_id)
        return self._get_cached_flow(user_id)
