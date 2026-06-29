from logging import getLogger

from pyrogram.errors import MessageNotModified

from app.core.container import container
from app.ui import home_screen

logger = getLogger(__name__)


async def show_home(client: object, query_or_msg: object, edit: bool = False) -> None:
    bot_name = await container.config_service.get_bot_name()
    screen = await home_screen(bot_name)
    text = screen["text"]
    reply_markup = screen["reply_markup"]
    if edit:
        try:
            await query_or_msg.edit_message_text(text, reply_markup=reply_markup)
        except MessageNotModified:
            pass
    else:
        await query_or_msg.reply_text(text, reply_markup=reply_markup)
