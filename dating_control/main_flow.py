import os
from abc import ABC

from dotenv import load_dotenv

from dating_control.caches import RedisUserCache
from dating_control.db import append_request_response, init_database
from dating_control.utils import get_logger

load_dotenv()
init_database()

logger = get_logger("main_flow.py")


class BaseMainFlow(ABC):
    ...


class DefaultMainFlow(BaseMainFlow):
    def __init__(self, cache_host: str, cache_port: int, cache_store_seconds: int) -> None:
        self.users_cache = RedisUserCache(host=cache_host, port=cache_port, sleep_seconds=cache_store_seconds)

    async def run(self, user_id: int, request: str, save: bool = True) -> str:
        current_user_flow = await self.users_cache.get_user_flow(user_id)
        response = current_user_flow.run(request)
        if save:
            append_request_response(user_id, request, response)
        return response
