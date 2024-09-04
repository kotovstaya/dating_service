import os
import asyncio
from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from dating_control.main_flow import DefaultMainFlow
from dating_control.utils import get_logger

TOKEN = os.getenv("TG_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT"))
WEBHOOK_PATH = '/webhook'
WEB_SERVER_HOST = "0.0.0.0"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


logger = get_logger("service_tg.py")
main_flow_object = DefaultMainFlow(10)

router = Router()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WEBHOOK_URL}")


# Функция для проверки условия и отправки сообщения
async def check_condition_and_send_message(chat_id: int):
    while True:
        await bot.send_message(chat_id, "Спам-спам")
        await asyncio.sleep(10)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # asyncio.create_task(check_condition_and_send_message(message.chat.id))
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@router.message(Command("cache"))
async def command_cache_handler(message: Message) -> None:
    obj = main_flow_object.users_cache._redis_client.get(str(message.from_user.id))
    if obj:
        await message.answer("cache exists")
    else:
        await message.answer("cache is empty")


@router.message()
async def message_handler(message: Message) -> None:
    try:
        response = main_flow_object.run(message.from_user.id, message.text, save=True)
        await message.answer(response)
    except TypeError as ex:
        await message.answer(str(ex))
        
        
async def send_custom_message(chat_id: int, text: str):
    await bot.send_message(chat_id, text)


def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
