import asyncio
import os

from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from dating_control.caches import RedisUserLongMissingNotifier
from dating_control.main_flow import DefaultMainFlow
from dating_control.user_flow import DefaultUserFlow
from dating_control.utils import get_logger

load_dotenv()

TOKEN = os.getenv("TG_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT"))
WEBHOOK_PATH = '/webhook'
WEB_SERVER_HOST = "0.0.0.0"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

CACHE_HOST = os.getenv("CACHE_HOST")
CACHE_STORE_SECONDS = int(os.getenv("CACHE_STORE_SECONDS"))
CACHE_PORT = int(os.getenv("CACHE_PORT"))


logger = get_logger("service_tg.py")


router = Router()


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

main_flow_object = DefaultMainFlow(
    cache_host=CACHE_HOST, cache_port=CACHE_PORT, cache_store_seconds=CACHE_STORE_SECONDS,
    user_flow_class_constructor=DefaultUserFlow,
)


missing_cache_notifier = RedisUserLongMissingNotifier(
    host=CACHE_HOST, port=CACHE_PORT, sleep_seconds=CACHE_STORE_SECONDS, db=0,
)


async def on_startup(bot: Bot) -> None:
    asyncio.create_task(missing_cache_notifier.handle_events(bot))
    await bot.set_webhook(f"{WEBHOOK_URL}")


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@router.message(Command("cache"))
async def command_cache_handler(message: Message) -> None:
    obj = await main_flow_object.is_user_in_cache(message.from_user.id)
    if obj:
        await message.answer("cache exists")
    else:
        await message.answer("cache is empty")


@router.message()
async def message_handler(message: Message) -> None:
    try:
        response = await main_flow_object.run(message.from_user.id, message.text, save=True)
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
