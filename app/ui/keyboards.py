from pyrogram.types import InlineKeyboardMarkup

from app.core import CallbackAction
from app.keyboards import Button, KeyboardBuilder
from app.ui.icons import Icons


def home_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .row(
            Button.action(f"{Icons.SEARCH} Search Movie", CallbackAction.SEARCH),
            Button.action(f"{Icons.LATEST} Latest Movies", CallbackAction.LATEST),
        )
        .row(
            Button.action(f"{Icons.REQUEST} Request Movie", CallbackAction.REQUEST_MOVIE),
            Button.action(f"{Icons.UPDATES} Updates", CallbackAction.UPDATES),
        )
        .row(
            Button.action(f"{Icons.CONTACT} Contact Admin", CallbackAction.CONTACT),
            Button.action(f"{Icons.ABOUT} About", CallbackAction.ABOUT),
        )
        .build()
    )


def admin_dashboard_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .row(
            Button.action(f"{Icons.UPLOAD} Upload Movie", CallbackAction.ADMIN_UPLOAD),
            Button.action(f"{Icons.MANAGE} Manage Movies", CallbackAction.ADMIN_MANAGE),
        )
        .row(
            Button.action(f"{Icons.REQUEST} Requests", CallbackAction.ADMIN_REQUESTS),
            Button.action(f"{Icons.BROADCAST} Broadcast", CallbackAction.ADMIN_BROADCAST),
        )
        .row(
            Button.action(f"{Icons.USERS} Users", CallbackAction.ADMIN_USERS),
            Button.action(f"{Icons.STATS} Statistics", CallbackAction.ADMIN_STATS),
        )
        .row(
            Button.action(f"{Icons.SETTINGS} Settings", CallbackAction.ADMIN_SETTINGS),
            Button.action(f"{Icons.BACKUP} Backup", CallbackAction.ADMIN_BACKUP),
        )
        .button(f"{Icons.HEALTH} Health Dashboard", CallbackAction.ADMIN_HEALTH)
        .build()
    )


def back_keyboard(action: CallbackAction = CallbackAction.HOME) -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .row(
            Button.action(f"{Icons.BACK} Back", action),
            Button.action(f"{Icons.HOME} Home", CallbackAction.HOME),
        )
        .build()
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
        .build()
    )


def poster_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .row(
            Button.action(f"{Icons.SKIP} Skip", CallbackAction.SKIP),
            Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL),
        )
        .build()
    )


def simple_keyboard(buttons: list[Button]) -> InlineKeyboardMarkup:
    kb = KeyboardBuilder()
    for btn in buttons:
        kb.row(btn)
    return kb.build()


def quality_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .row(
            Button.action("240p", CallbackAction.QUALITY_SELECT, "240p"),
            Button.action("360p", CallbackAction.QUALITY_SELECT, "360p"),
        )
        .row(
            Button.action("480p", CallbackAction.QUALITY_SELECT, "480p"),
            Button.action("576p", CallbackAction.QUALITY_SELECT, "576p"),
        )
        .row(
            Button.action("720p", CallbackAction.QUALITY_SELECT, "720p"),
            Button.action("1080p", CallbackAction.QUALITY_SELECT, "1080p"),
        )
        .row(
            Button.action("1440p", CallbackAction.QUALITY_SELECT, "1440p"),
            Button.action("4K", CallbackAction.QUALITY_SELECT, "4K"),
        )
        .row(
            Button.action("8K", CallbackAction.QUALITY_SELECT, "8K"),
            Button.action(f"{Icons.INFO} Custom", CallbackAction.CUSTOM_INPUT, "quality"),
        )
        .build()
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .row(
            Button.action("Hindi", CallbackAction.LANGUAGE_SELECT, "Hindi"),
            Button.action("English", CallbackAction.LANGUAGE_SELECT, "English"),
        )
        .row(
            Button.action("Tamil", CallbackAction.LANGUAGE_SELECT, "Tamil"),
            Button.action("Telugu", CallbackAction.LANGUAGE_SELECT, "Telugu"),
        )
        .row(
            Button.action("Malayalam", CallbackAction.LANGUAGE_SELECT, "Malayalam"),
            Button.action("Kannada", CallbackAction.LANGUAGE_SELECT, "Kannada"),
        )
        .row(
            Button.action("Japanese", CallbackAction.LANGUAGE_SELECT, "Japanese"),
            Button.action("Korean", CallbackAction.LANGUAGE_SELECT, "Korean"),
        )
        .row(
            Button.action("Chinese", CallbackAction.LANGUAGE_SELECT, "Chinese"),
            Button.action("Turkish", CallbackAction.LANGUAGE_SELECT, "Turkish"),
        )
        .button(f"{Icons.SKIP} Dual Audio", CallbackAction.LANGUAGE_SELECT, "Dual Audio")
        .button(f"Multi Audio", CallbackAction.LANGUAGE_SELECT, "Multi Audio")
        .button(f"{Icons.INFO} Custom", CallbackAction.CUSTOM_INPUT, "language")
        .build()
    )
