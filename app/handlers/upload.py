from logging import getLogger

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from app.core.container import container
from app.wizard import wizard_manager
from app.wizard.upload import FilesStep, PosterStep, TitleStep, UploadContext, YearStep

logger = getLogger(__name__)

_MEDIA_FILTER = (
    filters.photo
    | filters.video
    | filters.document
    | filters.audio
    | filters.sticker
    | filters.animation
)

WIZARD_NAME = "upload"
WIZARD_TITLE = "Upload New Movie"


async def _ensure_admin(user_id: int) -> bool:
    return await container.admin_service.is_admin(user_id)


async def start_upload_wizard(client: object, callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    if not await _ensure_admin(user_id):
        logger.warning("Unauthorized upload attempt by user %d", user_id)
        await callback_query.answer("Access denied")
        return

    session = wizard_manager.create(
        user_id=user_id,
        chat_id=callback_query.message.chat.id,
        wizard_name=WIZARD_NAME,
        steps=[TitleStep(), YearStep(), PosterStep(), FilesStep()],
        context_factory=UploadContext,
        title=WIZARD_TITLE,
    )

    await session.render_current(client)
    await callback_query.answer()
    logger.info("Upload wizard started by admin %d", user_id)


async def handle_upload_message(client: object, message: Message) -> None:
    user_id = message.from_user.id
    session = wizard_manager.get_active(user_id)
    if session is None:
        return

    if not await _ensure_admin(user_id):
        logger.warning("Non-admin user %d in upload wizard — clearing", user_id)
        wizard_manager.remove(user_id)
        return

    await session.handle_message(client, message)


async def handle_upload_media(client: object, message: Message) -> None:
    user_id = message.from_user.id
    session = wizard_manager.get_active(user_id)
    if session is None:
        return

    if not await _ensure_admin(user_id):
        logger.warning("Non-admin user %d in upload wizard — clearing", user_id)
        wizard_manager.remove(user_id)
        return

    await session.handle_media(client, message)


handlers = [
    (handle_upload_message, filters.text & filters.private),
    (handle_upload_media, filters.private & _MEDIA_FILTER),
]
