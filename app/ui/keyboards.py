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
