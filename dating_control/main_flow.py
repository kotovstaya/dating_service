import logging
from abc import ABC
from typing import Dict

from dotenv import load_dotenv

from dating_control.db import add_conversation, init_database
from dating_control.user_flow import BaseUserFlow, DefaultUserFlow
from dating_control.utils import StdOutHandler

load_dotenv()
init_database()

logger = logging.getLogger("main_flow")
logger.addHandler(StdOutHandler)
logger.setLevel(logging.DEBUG)


class BaseMainFlow(ABC):
    ...


class DefaultMainFlow(BaseMainFlow):
    cache: Dict[str, BaseUserFlow] = {}

    @classmethod
    def update_cache(cls, user_id: int):
        if user_id not in cls.cache.keys():
            cls.cache[user_id] = DefaultUserFlow()

    @classmethod
    def run(cls, user_id, context) -> None:
        if cls.cache.get(user_id, None) is None:
            cls.update_cache(user_id)
        current_user_flow = cls.cache[user_id]
        response = current_user_flow.run(context)
        add_conversation(user_id, context, response)
        return response
