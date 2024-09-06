import pickle

import aioredis

from dating_control.user_flow import BaseUserFlow, DefaultUserFlow
from dating_control.utils import get_logger

logger = get_logger("caches.py")


class RedisUserCache:
    def __init__(self, host:str = "cache", port: int = 6379, sleep_seconds: int = 10, db: int = 0) -> None:
        self._redis_client = aioredis.from_url(f"redis://{host}:{port}/{db}")
        self._store_seconds = sleep_seconds

    async def _get_cached_flow(self, user_id: int) -> BaseUserFlow:
        serialized_flow_class = await self._redis_client.get(str(user_id))
        await self._redis_client.setex(str(user_id), self._store_seconds, serialized_flow_class)
        return pickle.loads(serialized_flow_class)

    async def _insert_into_users_cache(self, user_id: int) -> None:
        flow_instance = DefaultUserFlow(user_id)
        await self._redis_client.setex(str(user_id), self._store_seconds, pickle.dumps(flow_instance))
        logger.info(f"user: {user_id} has been inserted to the cache")

    async def _is_user_in_users_cache(self, user_id: int) -> bool:
        serialized_object = await self._redis_client.get(str(user_id))
        return bool(serialized_object)

    async def get_user_flow(self, user_id: int) -> BaseUserFlow:
        is_user_in_cache = await self._is_user_in_users_cache(user_id)
        if not is_user_in_cache:
            await self._insert_into_users_cache(user_id)
        return await self._get_cached_flow(user_id)


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
