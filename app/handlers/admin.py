from logging import getLogger

from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, Message

from app.core import CallbackAction
from app.core.container import container
from app.ui import (
    admin_backup_placeholder,
    admin_broadcast_placeholder,
    admin_dashboard_keyboard,
    admin_dashboard_screen,
    back_keyboard,
    admin_health_placeholder,
    admin_manage_placeholder,
    admin_placeholder_screen,
    admin_requests_placeholder,
    admin_settings_placeholder,
    admin_stats_placeholder,
    admin_upload_placeholder,
    admin_users_placeholder,
    draft_actions_keyboard,
    draft_detail_message,
    drafts_list_keyboard,
    no_drafts_message,
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


async def show_drafts_list(client: object, callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    if not await _require_admin(user_id):
        await callback_query.answer("Access denied")
        return

    drafts = await container.upload_service.get_drafts(limit=50)
    if not drafts:
        await callback_query.edit_message_text(
            no_drafts_message(),
            reply_markup=back_keyboard(CallbackAction.ADMIN_HOME),
        )
        await callback_query.answer()
        return

    kb = drafts_list_keyboard(drafts)
    text = (
        f"{Icons.FILE} <b>Saved Drafts</b>\n\n"
        f"Found {len(drafts)} draft(s).\n"
        f"Select a draft to view details."
    )
    await callback_query.edit_message_text(text, reply_markup=kb)
    await callback_query.answer()


async def show_draft_detail(client: object, callback_query: CallbackQuery, movie_id: str) -> None:
    user_id = callback_query.from_user.id
    if not await _require_admin(user_id):
        await callback_query.answer("Access denied")
        return

    movie = await container.upload_service.get_movie_by_id(movie_id)
    if not movie:
        await callback_query.answer("Movie not found")
        return

    text = draft_detail_message(movie)
    kb = draft_actions_keyboard(movie_id)
    await callback_query.edit_message_text(text, reply_markup=kb)
    await callback_query.answer()


async def handle_publish_draft(client: object, callback_query: CallbackQuery, movie_id: str) -> None:
    user_id = callback_query.from_user.id
    if not await _require_admin(user_id):
        await callback_query.answer("Access denied")
        return

    movie = await container.upload_service.publish_draft(movie_id, published_by=user_id)
    if not movie:
        await callback_query.answer("Draft not found or already published")
        return

    bot_name = await container.config_service.get_bot_name()
    mention = callback_query.from_user.mention
    text = (
        f"\u2705 <b>Draft Published!</b>\n\n"
        f"Movie ID: <code>{movie_id}</code>\n"
        f"Title: {movie.get('title', 'Unknown')}"
    )
    await callback_query.edit_message_text(text, reply_markup=admin_dashboard_keyboard(bot_name, mention))
    await callback_query.answer()


async def handle_delete_draft(client: object, callback_query: CallbackQuery, movie_id: str) -> None:
    user_id = callback_query.from_user.id
    if not await _require_admin(user_id):
        await callback_query.answer("Access denied")
        return

    deleted = await container.upload_service.delete_movie(movie_id)
    if not deleted:
        await callback_query.answer("Movie not found")
        return

    await callback_query.edit_message_text(
        f"\u2705 <b>Draft Deleted</b>\n\nMovie ID: <code>{movie_id}</code>",
        reply_markup=back_keyboard(CallbackAction.ADMIN_HOME),
    )
    await callback_query.answer()
