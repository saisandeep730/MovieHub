from logging import getLogger

from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, Message

from app.core import CallbackAction
from app.core.container import container
from app.ui import (
    admin_backup_placeholder,
    admin_broadcast_placeholder,
    admin_dashboard_screen,
    admin_health_placeholder,
    admin_manage_placeholder,
    admin_placeholder_screen,
    admin_requests_placeholder,
    admin_settings_placeholder,
    admin_stats_placeholder,
    admin_upload_placeholder,
    admin_users_placeholder,
    unauthorized_response,
)
from app.ui.icons import Icons
from app.ui.messages import about

logger = getLogger(__name__)

_ADMIN_PLACEHOLDER_MAP = {
    CallbackAction.ADMIN_UPLOAD: (f"{Icons.UPLOAD} Upload Movie", admin_upload_placeholder),
    CallbackAction.ADMIN_MANAGE: (f"{Icons.MANAGE} Manage Movies", admin_manage_placeholder),
    CallbackAction.ADMIN_REQUESTS: (f"{Icons.REQUEST} Movie Requests", admin_requests_placeholder),
    CallbackAction.ADMIN_BROADCAST: (f"{Icons.BROADCAST} Broadcast", admin_broadcast_placeholder),
    CallbackAction.ADMIN_USERS: (f"{Icons.USERS} Users", admin_users_placeholder),
    CallbackAction.ADMIN_STATS: (f"{Icons.STATS} Statistics", admin_stats_placeholder),
    CallbackAction.ADMIN_SETTINGS: (f"{Icons.SETTINGS} Settings", admin_settings_placeholder),
    CallbackAction.ADMIN_BACKUP: (f"{Icons.BACKUP} Backup", admin_backup_placeholder),
    CallbackAction.ADMIN_HEALTH: (f"{Icons.HEALTH} Health Dashboard", admin_health_placeholder),
}


async def _require_admin(user_id: int) -> bool:
    return await container.admin_service.is_admin(user_id)


async def show_admin_home(client: object, query_or_msg: Message | CallbackQuery, edit: bool = False) -> None:
    user_id = query_or_msg.from_user.id
    if not await _require_admin(user_id):
        logger.warning("Unauthorized admin access attempt by user %d", user_id)
        await query_or_msg.reply_text(**unauthorized_response())
        return

    user_mention = query_or_msg.from_user.mention
    bot_name = await container.config_service.get_bot_name()
    screen = await admin_dashboard_screen(bot_name, user_mention)
    text = screen["text"]
    reply_markup = screen["reply_markup"]

    if edit:
        try:
            await query_or_msg.edit_message_text(text, reply_markup=reply_markup)
        except MessageNotModified:
            pass
    else:
        await query_or_msg.reply_text(text, reply_markup=reply_markup)

    logger.info("Admin dashboard shown to user %d", user_id)


async def show_admin_placeholder(
    client: object,
    callback_query: CallbackQuery,
    action: CallbackAction,
    args: list[str],
) -> None:
    user_id = callback_query.from_user.id
    if not await _require_admin(user_id):
        logger.warning("Unauthorized admin page access by user %d (action: %s)", user_id, action.value)
        await callback_query.answer("Access denied")
        return

    entry = _ADMIN_PLACEHOLDER_MAP.get(action)
    if not entry:
        await callback_query.answer("Unknown page")
        return

    title, msg_fn = entry
    text = msg_fn() if msg_fn else title
    screen = await admin_placeholder_screen(text)

    try:
        await callback_query.edit_message_text(screen["text"], reply_markup=screen["reply_markup"])
    except MessageNotModified:
        pass
    await callback_query.answer()
