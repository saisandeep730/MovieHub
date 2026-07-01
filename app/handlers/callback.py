from logging import getLogger

from pyrogram.errors import MessageNotModified

from app.core import CallbackAction, decode
from app.handlers.admin import show_admin_home, show_admin_placeholder
from app.handlers.home import show_home
from app.handlers.navigation import show_placeholder
from app.handlers.upload import start_upload_wizard
from app.wizard import wizard_manager

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

_STEP_ACTIONS = frozenset({
    CallbackAction.FILE_SELECT,
    CallbackAction.QUALITY_SELECT,
    CallbackAction.LANGUAGE_SELECT,
    CallbackAction.USE_ORIGINAL,
    CallbackAction.CUSTOM_INPUT,
    CallbackAction.PREVIEW_EDIT,
    CallbackAction.EDIT_TITLE,
    CallbackAction.EDIT_YEAR,
    CallbackAction.EDIT_POSTER,
    CallbackAction.MANAGE_FILES,
    CallbackAction.FILE_REMOVE,
    CallbackAction.BACK_TO_PREVIEW,
})

_DUPLICATE_ACTIONS = frozenset({
    CallbackAction.DUPLICATE_MERGE,
    CallbackAction.DUPLICATE_REPLACE,
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
        elif action == CallbackAction.SKIP:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_skip(client, callback_query)
            else:
                await callback_query.answer()
        elif action == CallbackAction.CONTINUE:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_continue(client, callback_query)
            else:
                await callback_query.answer()
        elif action == CallbackAction.WIZARD_BACK:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_back(client, callback_query)
            else:
                await callback_query.answer()
        elif action == CallbackAction.EDIT:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_edit(client, callback_query)
            else:
                await callback_query.answer()
        elif action == CallbackAction.SAVE_DRAFT:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_save_draft(client, callback_query)
            else:
                await callback_query.answer()
        elif action == CallbackAction.PUBLISH:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_publish(client, callback_query)
            else:
                await callback_query.answer()
        elif action in _STEP_ACTIONS:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_step_callback(client, callback_query, action, args)
            else:
                await callback_query.answer()
        elif action == CallbackAction.CANCEL:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if wizard:
                await wizard.handle_cancel(client, callback_query)
            else:
                await callback_query.answer()
        elif action in _DUPLICATE_ACTIONS:
            user_id = callback_query.from_user.id
            wizard = wizard_manager.get_active(user_id)
            if not wizard:
                await callback_query.answer("Session expired")
            elif action == CallbackAction.DUPLICATE_MERGE:
                await wizard.handle_duplicate_merge(client, callback_query)
            elif action == CallbackAction.DUPLICATE_REPLACE:
                await wizard.handle_duplicate_replace(client, callback_query)
        elif action == CallbackAction.ADMIN_MANAGE_DRAFTS:
            from app.handlers.admin import show_drafts_list
            await show_drafts_list(client, callback_query)
        elif action == CallbackAction.PUBLISH_DRAFT:
            from app.handlers.admin import handle_publish_draft
            await handle_publish_draft(client, callback_query, args[0] if args else "")
        elif action == CallbackAction.DELETE_DRAFT:
            from app.handlers.admin import handle_delete_draft
            await handle_delete_draft(client, callback_query, args[0] if args else "")
        elif action == CallbackAction.VIEW_MOVIE:
            from app.handlers.admin import show_draft_detail
            movie_id = args[0] if args else ""
            await show_draft_detail(client, callback_query, movie_id)
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
