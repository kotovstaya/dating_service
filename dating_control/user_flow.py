from abc import ABC

from dating_control.chats import HistorySummaryChat, LocalUserChat
from dating_control.db import get_user_previous_conversation
from dating_control.utils import get_logger

logger = get_logger("user_flow.py")


class BaseUserFlow(ABC):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id


class DefaultUserFlow(BaseUserFlow):
    def __init__(self, user_id: int) -> None:
        super().__init__(user_id)
        self.chat = None

    async def _init_chat(self, user_id: int) -> None:
        prev_conversation = await get_user_previous_conversation(user_id)
        history = None
        if prev_conversation:
            history = HistorySummaryChat().summary_chain.run(conversation=prev_conversation)
        logger.info(f"previous conversation as summary: {history}")
        self.chat = LocalUserChat(history)

    async def run(self, request: str) -> str:
        if self.chat is None:
            await self._init_chat(self.user_id)
        return self.chat.main_chain.run(text=request)
