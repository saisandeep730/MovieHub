from logging import getLogger

from pyrogram import filters
from pyrogram.types import Message

from app.core.container import container
from app.ui import home_screen

logger = getLogger(__name__)


async def start_command(client: object, message: Message) -> None:
    bot_name = await container.config_service.get_bot_name()
    screen = await home_screen(bot_name)
    await message.reply_text(**screen)
    logger.info("User %d started the bot", message.from_user.id)


handlers = [
    (start_command, filters.command("start")),
]
