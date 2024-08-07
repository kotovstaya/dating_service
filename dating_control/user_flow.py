from abc import ABC

from dating_control.chats import LocalUserChat
from dating_control.utils import StdOutHandler
import logging


logger = logging.getLogger("user_flow")
logger.addHandler(StdOutHandler)
logger.setLevel(logging.DEBUG)


class BaseUserFlow(ABC):
    ...


class DefaultUserFlow(BaseUserFlow):
    def __init__(self) -> None:
        super().__init__()
        self.chat = LocalUserChat()

    def run(self, context: str) -> str:
        logger.info(f"DefaultuserFlow context: {context}")
        response = self.chat.main_chain.run(context)
        return response
