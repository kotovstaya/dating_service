import pickle
from typing import Any

import aioredis

from dating_control.user_flow import BaseUserFlow
from dating_control.utils import get_logger

logger = get_logger("caches.py")


class RedisUserCache:
    def __init__(
        self,
        host: str = "cache",
        port: int = 6379,
        sleep_seconds: int = 10,
        db: int = 0,
    ) -> None:
        self._client = aioredis.from_url(f"redis://{host}:{port}/{db}")
        self._store_seconds = sleep_seconds

    @staticmethod
    def _cast_key_type(key: Any) -> str:
        return key if isinstance(key, str) else str(key)

    async def is_key_in_cache(self, key: Any) -> bool:
        return bool(await self._client.get(self._cast_key_type(key)))

    async def get_value(self, key: Any) -> BaseUserFlow:
        return pickle.loads(await self._client.get(self._cast_key_type(key)))

    async def update_cache(self, key: Any, value: BaseUserFlow, is_serialized: bool = False) -> None:
        if not is_serialized:
            value = pickle.dumps(value)
        await self._client.setex(self._cast_key_type(key), self._store_seconds, value)
        logger.info(f"object: {key} has been inserted to the cache")


class RedisUserLongMissingNotifier:
    def __init__(self, host: str = "cache", port: int = 6379, sleep_seconds: int = 10, db: int = 0) -> None:
        self.client = None
        self.host = host
        self.port = port
        self.db = db
        self._store_seconds = sleep_seconds

    async def _init_client(self) -> None:
        self.client = await aioredis.from_url(f'redis://{self.host}:{self.port}/{self.db}')
        await self.client.config_set('notify-keyspace-events', 'KEx')

    async def handle_events(self, bot) -> None:
        await self._init_client()
        try:
            pubsub = self.client.pubsub()
            await pubsub.psubscribe(f'__keyevent@{self.db}__:expired', f'__keyevent@{self.db}__:del')
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None and message['type'] == 'pmessage':
                    channel = message['channel'].decode()
                    key = message['data'].decode()
                    event_type = channel.split(':')[-1]
                    if event_type == 'del':
                        await bot.send_message(key, f"Пользователь {key} был удален из кэша")
                    if event_type == 'expired':
                        await bot.send_message(key, f"Ключ {key} пользователя в кэше истек")
        finally:
            await self.client.close()
