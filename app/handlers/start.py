from logging import getLogger

from pyrogram import filters
from pyrogram.types import Message

from app.core.container import container
from app.ui import home_screen
from app.handlers.admin import show_admin_home

logger = getLogger(__name__)


async def start_command(client: object, message: Message) -> None:
    user_id = message.from_user.id
    if await container.admin_service.is_admin(user_id):
        logger.info("Admin login by user %d", user_id)
        await show_admin_home(client, message, edit=False)
        return

    bot_name = await container.config_service.get_bot_name()
    screen = await home_screen(bot_name)
    await message.reply_text(**screen)
    logger.info("User %d started the bot", user_id)


handlers = [
    (start_command, filters.command("start")),
]
