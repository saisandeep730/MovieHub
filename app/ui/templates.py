from pyrogram.enums import ParseMode

from app.ui.keyboards import back_keyboard, home_keyboard
from app.ui.messages import (
    about,
    contact_placeholder,
    error_screen,
    latest_placeholder,
    request_placeholder,
    search_placeholder,
    updates_placeholder,
    welcome,
)


async def home_screen(bot_name: str) -> dict:
    return {
        "text": welcome(bot_name),
        "reply_markup": home_keyboard(),
        "parse_mode": ParseMode.HTML,
    }


async def placeholder_screen(
    title: str,
    description: str,
    back_action: str | None = None,
) -> dict:
    return {
        "text": f"<b>{title}</b>\n\n{description}",
        "reply_markup": back_keyboard(),
        "parse_mode": ParseMode.HTML,
    }


def error_response() -> dict:
    return {
        "text": error_screen(),
        "parse_mode": ParseMode.HTML,
    }
