import asyncio
import time
from typing import Dict
import datetime
from dating_control.user_flow import BaseUserFlow, DefaultUserFlow
from dating_control.utils import get_logger


logger = get_logger("user_cache.py")


class UserCache:
    def __init__(self, sleep_seconds: int) -> None:
        self._user_2_time: Dict[int, datetime.datetime] = {}
        self._user_2_flow: Dict[int, BaseUserFlow] = {}
        self._loop = asyncio.get_event_loop()
        self._sleep_seconds = sleep_seconds

    def _update_time_cache(self, user_id: int) -> None:
        self._user_2_time[user_id] = time.time()

    def _insert_into_users_cache(self, user_id: int) -> None:
        self._update_time_cache(user_id)
        self._user_2_flow[user_id] = DefaultUserFlow(user_id)
        logger.info(f"user: {user_id} has been inserted to the cache")

    def _is_user_in_users_cache(self, user_id: int) -> bool:
        return bool(self._user_2_flow.get(user_id))

    def get_user_flow(self, user_id: int) -> BaseUserFlow:
        if not self._is_user_in_users_cache(user_id):
            self._insert_into_users_cache(user_id)
        self._update_time_cache(user_id)
        return self._user_2_flow[user_id]

    async def cleanup_cache(self) -> None:
        while True:
            current_time = time.time()
            for user_id, last_activity in self._user_2_time.items():
                if current_time - last_activity > self._sleep_seconds:
                    del self._user_2_time[user_id]
                    del self._user_2_flow[user_id]
                    logger.info(f"user: {user_id} has been removed from the cache")
            await asyncio.sleep(self._sleep_seconds)

    def start(self) -> None:
        self._loop.create_task(self.cleanup_cache())
