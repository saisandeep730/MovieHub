from logging import getLogger

from pyrogram.errors import MessageNotModified

from app.core import CallbackAction
from app.core.container import container
from app.ui import (
    about,
    back_keyboard,
    contact_placeholder,
    latest_placeholder,
    request_placeholder,
    search_placeholder,
    updates_placeholder,
)
from app.ui.icons import Icons

logger = getLogger(__name__)

_PLACEHOLDER_MAP = {
    CallbackAction.SEARCH: (f"{Icons.SEARCH} Search Movie", search_placeholder),
    CallbackAction.LATEST: (f"{Icons.LATEST} Latest Movies", latest_placeholder),
    CallbackAction.REQUEST_MOVIE: (f"{Icons.REQUEST} Request Movie", request_placeholder),
    CallbackAction.UPDATES: (f"{Icons.UPDATES} Updates Channel", updates_placeholder),
    CallbackAction.CONTACT: (f"{Icons.CONTACT} Contact Admin", contact_placeholder),
    CallbackAction.ABOUT: (f"{Icons.ABOUT} About", None),
}


async def show_placeholder(client: object, callback_query: object, action: CallbackAction, args: list[str]) -> None:
    if action == CallbackAction.ABOUT:
        bot_name = await container.config_service.get_bot_name()
        text = about(bot_name)
    else:
        entry = _PLACEHOLDER_MAP.get(action)
        if not entry:
            await callback_query.answer("Unknown page")
            return
        title, msg_fn = entry
        text = msg_fn() if msg_fn else ""

    keyboard = back_keyboard()
    try:
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except MessageNotModified:
        pass
    await callback_query.answer()
