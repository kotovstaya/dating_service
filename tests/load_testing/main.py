
import logging
import asyncio
import time
import random
from telethon import TelegramClient


api_id = "23186240"
api_hash = "80f15c49a2862c0abb86a2c92d0c7309"
bot_token = "7066254216:AAElXzcf-2mvhPVGvXXsUDQm8RY46fMBiDY"

chat_id = "@anton_my_work"
NUM_USERS = 3

MESSAGES_PER_USER = 1

clients = []

async def create_clients():
    for i in range(NUM_USERS):
        client = TelegramClient(f'user_session_{i}', api_id, api_hash)
        await client.start(bot_token=bot_token)
        clients.append(client)


async def send_messages(client, message_count):
    for i in range(message_count):
        try:
            message = f"Test message {i} from {client.session.filename}"
            await client.send_message(chat_id, message)
            print(f"Sent message: {message}")
            await asyncio.sleep(random.uniform(0.1, 0.5))
        except Exception as e:
            time.sleep(2)

# Основная функция для запуска нагрузочного тестирования
async def run_load_test():
    await create_clients()

    tasks = []
    for client in clients:
        task = send_messages(client, MESSAGES_PER_USER)
        tasks.append(task)
    await asyncio.gather(*tasks)

    for client in clients:
        await client.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_load_test())
