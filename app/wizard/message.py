from logging import getLogger

from pyrogram.errors import MessageDeleteForbidden, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup

logger = getLogger(__name__)


async def delete_message_safe(client: object, chat_id: int, message_id: int) -> None:
    try:
        await client.delete_messages(chat_id, message_id)
    except MessageDeleteForbidden:
        logger.debug("Cannot delete message %d in chat %d", message_id, chat_id)
    except Exception:
        logger.debug("Failed to delete message %d in chat %d", message_id, chat_id)


async def edit_or_send(
    client: object,
    chat_id: int,
    message_id: int | None,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> int:
    if message_id is not None:
        try:
            await client.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
            )
            return message_id
        except MessageNotModified:
            return message_id
        except Exception:
            logger.debug("Edit failed for message %d, sending new", message_id)

    sent = await client.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
    )
    return sent.id
