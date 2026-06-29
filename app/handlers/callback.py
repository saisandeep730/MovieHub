from logging import getLogger

from pyrogram.errors import MessageNotModified

from app.core import CallbackAction, decode
from app.handlers.admin import show_admin_home, show_admin_placeholder
from app.handlers.home import show_home
from app.handlers.navigation import show_placeholder
from app.handlers.upload import cancel_upload, start_upload_wizard
from app.states import state_manager

logger = getLogger(__name__)

_ADMIN_ACTIONS = frozenset({
    CallbackAction.ADMIN_HOME,
    CallbackAction.ADMIN_MANAGE,
    CallbackAction.ADMIN_REQUESTS,
    CallbackAction.ADMIN_BROADCAST,
    CallbackAction.ADMIN_USERS,
    CallbackAction.ADMIN_STATS,
    CallbackAction.ADMIN_SETTINGS,
    CallbackAction.ADMIN_BACKUP,
    CallbackAction.ADMIN_HEALTH,
})

_USER_ACTIONS = frozenset({
    CallbackAction.SEARCH,
    CallbackAction.LATEST,
    CallbackAction.REQUEST_MOVIE,
    CallbackAction.UPDATES,
    CallbackAction.CONTACT,
    CallbackAction.ABOUT,
})


async def handle_callback(client: object, callback_query: object) -> None:
    data = callback_query.data
    try:
        action, args = decode(data)
    except (ValueError, KeyError):
        logger.warning("Invalid callback data: %s", data)
        await callback_query.answer("Invalid action")
        return

    try:
        if action == CallbackAction.HOME or action == CallbackAction.BACK:
            await show_home(client, callback_query, edit=True)
        elif action in _USER_ACTIONS:
            await show_placeholder(client, callback_query, action, args)
        elif action == CallbackAction.ADMIN_HOME:
            await show_admin_home(client, callback_query, edit=True)
        elif action in _ADMIN_ACTIONS:
            await show_admin_placeholder(client, callback_query, action, args)
        elif action == CallbackAction.ADMIN_UPLOAD:
            await start_upload_wizard(client, callback_query)
        elif action == CallbackAction.CANCEL:
            user_id = callback_query.from_user.id
            if state_manager.get_state(user_id) is not None:
                await cancel_upload(client, callback_query)
            else:
                await callback_query.answer()
        else:
            await callback_query.answer("Coming soon")
    except MessageNotModified:
        await callback_query.answer()
    except Exception:
        logger.exception("Error handling callback %s", data)
        await callback_query.answer("An error occurred")


handlers = [
    (handle_callback, None),
]
