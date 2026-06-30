from datetime import UTC, datetime
from logging import getLogger

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message

from app.core.container import container
from app.states import state_manager
from app.ui import cancel_keyboard
from app.ui.keyboards import admin_dashboard_keyboard, poster_keyboard
from app.ui.messages import (
    admin_dashboard,
    upload_files_prompt,
    upload_title_invalid,
    upload_title_prompt,
    upload_title_success,
    upload_year_invalid,
    upload_year_success,
)
from app.utils import normalize_title

logger = getLogger(__name__)

UPLOAD_AWAITING_TITLE = "upload:awaiting_title"
UPLOAD_AWAITING_YEAR = "upload:awaiting_year"
UPLOAD_AWAITING_POSTER = "upload:awaiting_poster"
UPLOAD_AWAITING_FILES = "upload:awaiting_files"
UPLOAD_DATA_TITLE = "upload.title"
UPLOAD_DATA_YEAR = "upload.year"
UPLOAD_DATA_POSTER = "upload.poster"

YEAR_MIN = 1888


async def _ensure_admin(user_id: int) -> bool:
    return await container.admin_service.is_admin(user_id)


async def start_upload_wizard(client: object, callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    if not await _ensure_admin(user_id):
        logger.warning("Unauthorized upload attempt by user %d", user_id)
        await callback_query.answer("Access denied")
        return

    state_manager.set_state(user_id, UPLOAD_AWAITING_TITLE)
    await callback_query.edit_message_text(
        upload_title_prompt(),
        reply_markup=cancel_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await callback_query.answer()
    logger.info("Upload wizard started by admin %d", user_id)


async def handle_upload_message(client: object, message: Message) -> None:
    user_id = message.from_user.id
    current_state = state_manager.get_state(user_id)

    if current_state not in (UPLOAD_AWAITING_TITLE, UPLOAD_AWAITING_YEAR, UPLOAD_AWAITING_POSTER):
        return

    if not await _ensure_admin(user_id):
        logger.warning("Non-admin user %d in upload state — clearing", user_id)
        state_manager.clear_state(user_id)
        return

    if current_state == UPLOAD_AWAITING_TITLE:
        await _handle_title(message, user_id)
    elif current_state == UPLOAD_AWAITING_YEAR:
        await _handle_year(message, user_id)
    elif current_state == UPLOAD_AWAITING_POSTER:
        await _handle_poster_message(message, user_id)


async def _handle_title(message: Message, user_id: int) -> None:
    if not message.text or not message.text.strip():
        await message.reply_text(
            upload_title_invalid(),
            reply_markup=cancel_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        return

    raw_title = message.text.strip()
    normalized = normalize_title(raw_title)
    state_manager.update_data(user_id, {UPLOAD_DATA_TITLE: normalized})
    state_manager.set_state(user_id, UPLOAD_AWAITING_YEAR)

    await message.reply_text(
        upload_title_success(raw_title),
        reply_markup=cancel_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    logger.info("Admin %d set movie title: %s", user_id, normalized)


def _validate_year(text: str) -> int | None:
    text = text.strip()
    if not text.isdigit():
        return None
    year = int(text)
    year_max = datetime.now(UTC).year + 2
    if year < YEAR_MIN or year > year_max:
        return None
    return year


async def _handle_year(message: Message, user_id: int) -> None:
    if not message.text:
        await message.reply_text(
            upload_year_invalid(),
            reply_markup=cancel_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        return

    year = _validate_year(message.text)
    if year is None:
        await message.reply_text(
            upload_year_invalid(),
            reply_markup=cancel_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        return

    state_manager.update_data(user_id, {UPLOAD_DATA_YEAR: year})
    state_manager.set_state(user_id, UPLOAD_AWAITING_POSTER)

    await message.reply_text(
        upload_year_success(),
        reply_markup=poster_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    logger.info("Admin %d set release year: %d", user_id, year)


async def _handle_poster_message(message: Message, user_id: int) -> None:
    logger.debug("Poster upload not yet implemented for user %d", user_id)


async def skip_upload_poster(client: object, callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    if not await _ensure_admin(user_id):
        await callback_query.answer("Access denied")
        return

    state_manager.update_data(user_id, {UPLOAD_DATA_POSTER: None})
    state_manager.set_state(user_id, UPLOAD_AWAITING_FILES)

    await callback_query.edit_message_text(
        upload_files_prompt(),
        reply_markup=cancel_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await callback_query.answer()
    logger.info("Admin %d skipped poster upload", user_id)


async def cancel_upload(client: object, callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    state_manager.clear_state(user_id)

    bot_name = await container.config_service.get_bot_name()
    user_mention = callback_query.from_user.mention
    text = admin_dashboard(bot_name, user_mention)

    await callback_query.edit_message_text(
        text,
        reply_markup=admin_dashboard_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await callback_query.answer()
    logger.info("Upload cancelled by admin %d", user_id)


handlers = [
    (handle_upload_message, filters.text & filters.private),
]
