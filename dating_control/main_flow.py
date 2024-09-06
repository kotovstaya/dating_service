from abc import ABC
from typing import Type

from dating_control.caches import RedisUserCache
from dating_control.db import append_request_response, init_database
from dating_control.user_flow import BaseUserFlow
from dating_control.utils import get_logger

init_database()

logger = get_logger("main_flow.py")


class BaseMainFlow(ABC):
    ...


class DefaultMainFlow(BaseMainFlow):
    def __init__(
        self,
        cache_host: str,
        cache_port: int,
        cache_store_seconds: int,
        user_flow_class_constructor: Type[BaseUserFlow],
    ) -> None:
        self._users_cache = RedisUserCache(
            host=cache_host,
            port=cache_port,
            sleep_seconds=cache_store_seconds,
        )
        self._user_flow_class_constructor = user_flow_class_constructor
        self._user_flow_class = None

    async def _get_user_flow(self, user_id: int):
        is_user_in_cache = await self._users_cache.is_key_in_cache(user_id)
        if is_user_in_cache:
            return await self._users_cache.get_value(user_id)
        else:
            return self._user_flow_class_constructor(user_id)

    async def run(self, user_id: int, request: str, save: bool = True) -> str:
        self._user_flow_class = await self._get_user_flow(user_id)
        response = await self._user_flow_class.run(request)
        if save:
            await append_request_response(user_id, request, response)
        await self._users_cache.update_cache(user_id, self._user_flow_class, is_serialized=False)
        return response
    
    async def is_user_in_cache(self, user_id: int) -> bool:
        return await self._users_cache.is_key_in_cache(user_id)
        
