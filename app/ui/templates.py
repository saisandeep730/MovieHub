from pyrogram.enums import ParseMode

from app.core import CallbackAction
from app.ui.keyboards import admin_dashboard_keyboard, back_keyboard, home_keyboard
from app.ui.messages import (
    about,
    admin_backup_placeholder,
    admin_broadcast_placeholder,
    admin_dashboard,
    admin_health_placeholder,
    admin_manage_placeholder,
    admin_requests_placeholder,
    admin_settings_placeholder,
    admin_stats_placeholder,
    admin_upload_placeholder,
    admin_users_placeholder,
    contact_placeholder,
    error_screen,
    latest_placeholder,
    request_placeholder,
    search_placeholder,
    unauthorized_access,
    updates_placeholder,
    welcome,
)


async def admin_dashboard_screen(bot_name: str, user_mention: str) -> dict:
    return {
        "text": admin_dashboard(bot_name, user_mention),
        "reply_markup": admin_dashboard_keyboard(),
        "parse_mode": ParseMode.HTML,
    }


async def admin_placeholder_screen(text: str) -> dict:
    return {
        "text": text,
        "reply_markup": back_keyboard(CallbackAction.ADMIN_HOME),
        "parse_mode": ParseMode.HTML,
    }


def unauthorized_response() -> dict:
    return {
        "text": unauthorized_access(),
        "parse_mode": ParseMode.HTML,
    }


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
