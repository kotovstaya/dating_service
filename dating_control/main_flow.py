from abc import ABC

from dotenv import load_dotenv


from dating_control.db import append_request_response, init_database
from dating_control.utils import get_logger
from dating_control.user_cache import UserCache

load_dotenv()
init_database()

logger = get_logger("main_flow.py")


class BaseMainFlow(ABC):
    ...


class DefaultMainFlow(BaseMainFlow):
    def __init__(self, sleep_seconds: int = 10) -> None:
        self.users_cache = UserCache(sleep_seconds)
        self.users_cache.start()

    def run(self, user_id: int, request: str, save: bool = True) -> str:
        current_user_flow = self.users_cache.get_user_flow(user_id)
        response = current_user_flow.run(request)
        if save:
            append_request_response(user_id, request, response)
        return response
