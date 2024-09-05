import os
from abc import ABC

from dotenv import load_dotenv

from dating_control.caches import RedisUserCache
from dating_control.db import append_request_response, init_database
from dating_control.utils import get_logger

load_dotenv()
init_database()

logger = get_logger("main_flow.py")

CACHE_HOST = os.getenv("CACHE_HOST")
CACHE_STORE_SECONDS = int(os.getenv("CACHE_STORE_SECONDS"))
CACHE_PORT = int(os.getenv("CACHE_PORT"))


class BaseMainFlow(ABC):
    ...


class DefaultMainFlow(BaseMainFlow):
    def __init__(self, sleep_seconds: int = 10) -> None:
        self.users_cache = RedisUserCache(host=CACHE_HOST, port=CACHE_PORT, sleep_seconds=CACHE_STORE_SECONDS)

    def run(self, user_id: int, request: str, save: bool = True) -> str:
        current_user_flow = self.users_cache.get_user_flow(user_id)
        response = current_user_flow.run(request)
        if save:
            append_request_response(user_id, request, response)
        return response
