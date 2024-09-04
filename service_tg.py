import os
from aiohttp import web
from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import Message

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


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WEBHOOK_URL}")


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@router.message(Command("cache"))
async def command_cache_handler(message: Message) -> None:
    obj = main_flow_object.users_cache._redis_client.get(str(message.from_user.id))
    if obj:
        await message.answer("cache exists")
    else:
        await message.answer("cache is empty")


# @router.message(Command("clear_cache"))
# async def command_clear_cache_handler(message: Message) -> None:
#     del main_flow_object.users_cache._user_2_time[message.from_user.id]
#     del main_flow_object.users_cache._user_2_flow[message.from_user.id]

#     await message.answer("cache was cleared")


@router.message()
async def message_handler(message: Message) -> None:
    try:
        response = main_flow_object.run(message.from_user.id, message.text, save=True)
        await message.answer(response)
    except TypeError as ex:
        await message.answer(str(ex))


def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
