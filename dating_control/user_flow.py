from abc import ABC

from dating_control.chats import LocalUserChat, HistorySummaryChat
from dating_control.utils import get_logger
from dating_control.db import get_user_previous_conversation


logger = get_logger("user_flow.py")


class BaseUserFlow(ABC):
    ...


class DefaultUserFlow(BaseUserFlow):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        prev_conversation = get_user_previous_conversation(user_id)
        history = None
        if prev_conversation:
            history = HistorySummaryChat().summary_chain.run(conversation=prev_conversation)
        logger.info(f"previous conversation as summary: {history}")
        self.chat = LocalUserChat(history)

    def run(self, request: str) -> str:
        return self.chat.main_chain.run(text=request)
